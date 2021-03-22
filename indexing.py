import os
import re
import json
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
from collections import defaultdict
from simhash import compare_simhashes
from simhash import get_simhash
from urllib.parse import urlparse
from urllib.parse import urldefrag

# Writes partial index to text file in sorted order
def partial_index_tofile(tfile, pindex):
    with open(tfile, 'a', encoding='utf-8') as f:
        for key in sorted(pindex):
            f.write(str(key) + ';' + str(pindex[key]) + '\n')


# merges two partial indeces in O(x+y) time into a index saved in endfile
def merge(file1, file2, endfile):
    with open(file1, "r", encoding='utf-8') as f, open(file2, "r", encoding='utf-8') as f2, open(endfile, "w", encoding='utf-8') as final:
        line = f.readline() # line by line
        line2 = f2.readline()
        while line or line2:
            if not line:
                sline2 = line2.split(";")
                final.write(sline2[0] + ";" + str(eval(sline2[1])) + "\n")
                line2 = f2.readline()
            elif not line2:
                sline = line.split(";")
                final.write(sline[0] + ";" + str(eval(sline[1])) + "\n")
                line = f.readline()
            else:
                sline = line.split(";")
                sline2 = line2.split(";")
                if sline[0] < sline2[0]:
                    final.write(sline[0] + ";" + str(eval(sline[1])) + "\n")
                    line = f.readline()
                elif sline[0] > sline2[0]:
                    final.write(sline2[0] + ";" + str(eval(sline2[1])) + "\n")
                    line2 = f2.readline()
                else:
                    final.write(sline[0] + ";" + str(eval(sline[1]) + eval(sline2[1])) + "\n")
                    line = f.readline()
                    line2 = f2.readline()

# Utility
def computeWordFrequencies(tokens):
    result = defaultdict(int)   
    for word in tokens:
        stemmed_word = ps.stem(word)     
        result[stemmed_word] += 1   
    return result

# Start of program
docids = dict()
index = defaultdict(list) # buffer/temporary dictionary to hold the index part
m = 0 # m is to assign docIDs
n = 0 # n is used for off-loading the index
ps = PorterStemmer()

duplicate_journal = set()
similarity_journal = set()
current_domain = ""

for root,dirs,files in os.walk("."): # goes into DEV folder and grabs all the webpages files
    if re.search('uci',root):
        domain = root.split('\\')[-1] 
        for f in files:

            # Offload
            if n == 13850:
                partial_index_tofile("index_part1.txt", index) # offload the index into txt file
                index = defaultdict(list) # wiped
            if n == 27700:
                partial_index_tofile("index_part2.txt", index)
                index = defaultdict(list)
            if n == 41550:
                partial_index_tofile("index_part3.txt", index)
                index = defaultdict(list)

            with open(root +"\\"+ f) as webpage: # open the webpage file into data 
                data = json.load(webpage) 

                if urlparse(data['url']).netloc != current_domain: # clearing similarity_journal in order to only do simhash within one domain 
                    current_domain = urlparse(data['url']).netloc
                    similarity_journal = set()

                if urldefrag(data['url']).url in duplicate_journal: # checking duplicate by fragment ics.uci.edu/ = ics.uci.edu/#1
                    print(data['url'] + " is a duplicate by FRAGMENT!")
                    n += 1
                    continue

                soup = BeautifulSoup(data["content"], 'lxml') # library to extract text from a webpage, web parser
                
                this_simh = get_simhash(soup.get_text()) # compare simhash
                isDuplicate = False
                for other_simh in similarity_journal:
                    if compare_simhashes(this_simh, other_simh) > 0.985: # threshhold
                        print(data['url'] + " is a duplicate by SIMILARITY!")
                        isDuplicate = True
                        break
                if isDuplicate:
                    n += 1
                    continue

                similarity_journal.add(this_simh)
                print("N: "+ str(m) + " Parsing:", data['url']) # remove before submitting
                
                # USE data["url"] to get current url 
                
                text = soup.get_text()
                # text now contains all the parsed text from url BUT could be improvecd to retireve more text
                
                #TOKENIZE
                tokenizer = RegexpTokenizer(r"[a-zA-Z0-9]{2,}")
                tokens = tokenizer.tokenize(text.lower())
                #print(tokens)

                if soup.title != None:
                    title_tokens = {ps.stem(t) for t in tokenizer.tokenize(soup.title.get_text().lower())}
                
                text = ""
                for i in soup.find_all(re.compile('^h[1-6]$')):
                    text += i.get_text().lower() + " "
                header_tokens = {ps.stem(t) for t in tokenizer.tokenize(text.lower())}

                text = ""
                for i in soup.find_all('b'):
                    text += i.get_text().lower() + " "
                bold_tokens = {ps.stem(t) for t in tokenizer.tokenize(text.lower())}

                #Index
                tokens = computeWordFrequencies(tokens) # tokens is now a dictionary that maps word : count
                for token in tokens:
                    posting = {'id': m, 'tf': tokens[token]}
                    if token in title_tokens:
                        posting['t'] = 1
                    if token in header_tokens:
                        posting['h'] = 1
                    if token in bold_tokens:
                        posting['b'] = 1
                    index[token].append(posting)

                docids[m] = urldefrag(data['url']).url
                duplicate_journal.add(urldefrag(data['url']).url)
                m += 1
                n += 1
            
partial_index_tofile("index_part4.txt", index) # writes partial index to text file

# Each index entry is saved in this format: 'word; [{'id': int, 'tf': int}, ...]'

# Merging partial indices
print("Merging index parts...")
merge("index_part1.txt", "index_part2.txt", "merged_12.txt")
merge("index_part3.txt", "index_part4.txt", "merged_34.txt")
merge("merged_12.txt", "merged_34.txt", "inverted_index.txt")

# Saving docids
with open('docids.json', 'w') as f:
    print("Saving doc IDs...")
    json.dump(docids, f)

#Index of index
word_index = dict() 
with open("inverted_index.txt", "r", encoding='utf-8') as f2: #open the inverted index
    print("Creating index of index...")
    pos = f2.tell()
    line = f2.readline()
    parsedline = line.split(";")
    word_index[parsedline[0]] = pos
    while line:
        pos = f2.tell()
        line = f2.readline()
        if line != "":
            parsedline = line.split(";")
            word_index[parsedline[0]] = pos

with open('index_of_index.json','w') as f3:
    json.dump(word_index,f3)



            
            
    
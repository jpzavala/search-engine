from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
from timeit import default_timer as timer
from queue import PriorityQueue
import itertools
import json
import math
import sys

# common finds the intersection of all lists in posting_lists
def common(posting_lists): 
    temp = []
    for lst in posting_lists:
        s = {i['id'] for i in lst} # next(iter(dict())) is a fast trick to get the key in a dict with just one key such as our postings
        if len(s):
            temp.append(s)
    
    if len(temp):
        result = temp[0].intersection(*temp[1:])
        if len(result) < 10:
            i = len(temp) - 1
            while len(result) < 10 and i > 0:
                for combo in itertools.combinations(temp, i):
                    result = result.union(combo[0].intersection(*combo[1:]))
                i -= 1
        if len(result) < 10:
            for i in range(40000):
                result.add(i)
                if len(result) >= 10:
                    break
        return result
    else:
        return set()

# getter uses binary search to find the value mapped to the specified docID in a list of postings fast
# ex getter(1, [{1:2}, {3:7}]) returns 2
def getter(docID, posting_list):
    l = 0
    r = len(posting_list) - 1
    while l <= r:
        mid = l + (r - l) // 2
        if posting_list[mid]['id'] == docID:
            return posting_list[mid]
        elif posting_list[mid]['id'] < int(docID):
            l = mid + 1
        else:
            r = mid - 1
    return {'tf': 0}

def computeWordFrequencies(tokens):
    result = dict.fromkeys(tokens, 0)   
    for word in tokens:     
        result[word] += 1   
    return result

def process_stopwords(tokens):
    if len(tokens) <= 1: # return if query is one word
        return tokens
    else:
        processed = [t for t in tokens if t not in {'for', 'by', 'are', 'of', 'the', 'is', 'at', 'and', 'in', 'on', 'to'}]
        if len(processed) == 0: # query is only stop words
            return [tokens[0]]
        else: # query has at least one good word
            return processed
                
def tfidf_ranking(terms, termsnfreqs, posting_lists):
    ranking = PriorityQueue()
    idfs = dict() # holds idfs
    query_vector = list()

    if len(posting_lists) == 1:
        in_common = {p['id'] for p in posting_lists[0]}
        if len(in_common) < 10:
            for i in range(40000):
                in_common.add(i)
                if len(in_common) >= 10:
                    break
        query_vector.append(1 + math.log(termsnfreqs.get(terms[0])))
    else:
        in_common = common(posting_lists) # only postings that have ALL query terms
    
        for i in range(len(terms)):
            try:
                idfs[terms[i]] = math.log(float(53792)/len(posting_lists[i]))
            except ZeroDivisionError:
                idfs[terms[i]] = 0

        # Query vector
        for term in terms:
            query_vector.append((1 + math.log(termsnfreqs.get(term))) * idfs.get(term))
        query_length = math.sqrt(sum([i**2 for i in query_vector]))
        query_vector = [i/query_length for i in query_vector]

    #For each document, create document vector then compute score
    for n in in_common: 
        doc_vector = list()
        score = 0
        for i in range(len(terms)):
            pos = getter(n, posting_lists[i])
            if pos['tf'] > 0:
                if 't' in pos:
                    doc_vector.append((1 + math.log(pos['tf'])))
                    score += 250
                elif 'h' in pos:
                    doc_vector.append((1 + math.log(pos['tf'])))
                    score += 50
                elif 'b' in pos:
                    doc_vector.append((1 + math.log(pos['tf'])))
                    score += 25
                else:
                    doc_vector.append(1 + math.log(pos['tf']))
            else:
                doc_vector.append(0)
        if sum(doc_vector) > 0:
            doc_length = math.sqrt(sum([i**2 for i in doc_vector]))
            doc_vector = [i/doc_length for i in doc_vector]
            score += sum([query_vector[i] * doc_vector[i] for i in range(len(query_vector))])
        else:
            score = 0
        ranking.put((-1 * score, n))
    
    #Get the docIDs of the highest score values found
    answer = [ranking.get()[1] for i in range(10) if not ranking.empty()]
    return answer
    
    
def retrieval(query):
    index_of_index = {}
    with open("index_of_index.json",'r') as f4:
        index_of_index = json.load(f4)
    with open('inverted_index.txt', 'r', encoding='utf-8') as f2, open('docids.json', 'r') as f3:
        ids = json.load(f3)
        ps = PorterStemmer()
        terms_list = []
        start = timer()
        tokenizer = RegexpTokenizer(r"[a-zA-Z0-9]{2,}")
        terms = tokenizer.tokenize(query.lower()) ## make all str lowercase? change in indexer as well
        termsnfreqs = computeWordFrequencies(terms)
        terms = list(termsnfreqs.keys())
        terms = process_stopwords(terms)
    
        for term in terms: ## search for posting that contain term and add them to corresponging list
            position = index_of_index.get(ps.stem(term), -1) # find position in index_of_index txt file
            if position >= 0:
                f2.seek(position)
                line = f2.readline()
                l = line.split(';') # l is just a list containing the key(word) and value(list of postings) AS STRINGS of our index
                lst = json.loads(l[1].replace('\'', '\"')) #turn posting string to a list 
                terms_list.append(lst) # terms list is a list of lists containing each term's list from Inverted Index
            else:
                terms_list.append([])

    # NEED TO RUN THROUGH terms_list and obtain the intersection of all lists
        results = [ids[str(pageid)] for pageid in tfidf_ranking(terms, termsnfreqs, terms_list)]
        end = timer()
        return results, ((end - start) * 1000)
        
        
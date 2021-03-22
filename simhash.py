import re
import hashlib

def hashed(word):
    result = int(hashlib.sha256(word.encode('utf-8')).hexdigest(), 16) % (2**62)
    return format(result, '0>64b')[-64:]

def computeWordFrequencies(text):
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    result = dict.fromkeys(tokens, 0)  
    for word in tokens:    
        result[word] += 1   
    return result

def computeWordHashes(words):
    result = dict.fromkeys(words.keys(), "")
    for word in result:
        result[word] = hashed(word)
    return result

def get_simhash(text):
    freqs = computeWordFrequencies(text)
    hashes = computeWordHashes(freqs)
    vector = []
    for i in range(64):
        sum = 0
        for word in freqs:
            if hashes[word][i] == "0":
                sum -= 1 * freqs[word]
            else:
                sum += 1 * freqs[word]
        vector.append(sum)
    result = ""
    for num in vector:
        if num > 0:
            result += "1"
        else:
            result += "0"
    return result

def compare_simhashes(f1, f2):
    sum = 0
    if len(f1) != len(f2):
        return sum
    for i in range(len(f1)):
        if f1[i] == f2[i]:
            sum += 1
    return sum/len(f1)
'''
import pandas as pd
import quandl

df = quandl.get('WIKI/GOOGL')
df = df[['Adj. Open','Adj. High','Adj. Low','Adj. Close','Adj. Volume']]
df['HL_PCT'] = (df['Adj. High'] - df['Adj. Close']) /df['Adj. Close'] * 100
df['CHG_PCT'] = (df['Adj. Close'] - df['Adj. Open']) /df['Adj. Open'] * 100
df = df[['Adj. Open','HL_PCT','CHG_PCT','Adj. Close','Adj. Volume']]
print(df)
'''

from nltk.tokenize import sent_tokenize, PunktSentenceTokenizer, word_tokenize
from nltk.corpus import abc
from nltk.corpus import wordnet

# sample text
sample = abc.raw("science.txt")

tok = sent_tokenize(sample)

for x in range(5):
    print(tok[x])
    
words = word_tokenize(sample)

synonyms = []
antonyms = []

g_score = 0
b_score = 0
totalWords = 0

for syn in wordnet.synsets("bullish"):
    print(syn)
    for l in syn.lemmas():
        synonyms.append(l.name())
        if l.antonyms():
            antonyms.append(l.antonyms()[0].name())

print(set(synonyms))
print(set(antonyms))

for word in words:
    totalWords += 1
    if word in set(synonyms):
        g_score += 1
    else:
        if word in set(antonyms):
            b_score -= 1     

print(totalWords)
print(g_score) 
print(b_score)           
print(g_score + b_score)
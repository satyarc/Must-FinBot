'''
Created on 6 Apr 2017

# @author: Satya
'''
import urllib.request
import urllib.parse
import re
import json
import requests
import sys
import collections

import nltk

from newsapi.commands import Sources, headlines
from newsapi.commands import Headlines

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

from nltk.stem import PorterStemmer     

path  = 'C:\Users\user\AppData\Roaming\nltk_data'
  
def fetchNewsFrom(newsSource):
    apiKey = 'a892420deb3f46dea3c5f5c0b9863bf3'
    url = "https://newsapi.org/v1/articles?apiKey=" + apiKey + "&source=" + newsSource
    response = requests.get(url)
    data = response.json()
    textFromAllArticles = ""
    if data["status"] != "error":
        articles = data["articles"]
        for article in articles:
            if article["description"] is not None:
                with open('newsextract', 'a') as out:
                    out.write(article["title"])
                    description = article["description"]
                    textFromAllArticles += description
                    out.write(description)
                    out.write(article["url"])
    else:
        print("Invalid news source.")
        
    return textFromAllArticles

sources = ['financial-times','busines-insider-uk','techcrunch','business-insider','google-news','the-times-of-india','usa-today'] 
textFromAllSources = "" 
for source in sources:      
    textFromAllSources += fetchNewsFrom(source)
    
sentences = sent_tokenize(textFromAllSources)
print('SENTENCES :')
print(sentences)

stopWords = set(stopwords.words("english"))
words = word_tokenize(textFromAllSources)
filteredSentence = [w for w in words if not w in stopWords]

print('FILTERED SENTENCES :')
for filSentence in filteredSentence:
    print(filSentence)

print('BAG OF WORDS :')
commonBagOfWords =  collections.Counter(re.findall(r'\w+', textFromAllSources))
mostCommonWords = commonBagOfWords.most_common(500)

mostCommonWords = nltk.FreqDist(words)
print(mostCommonWords['share'])
'''
with open('bags', 'a') as bagout:
    for word in mostCommonWords:
        uprint('word :' + str(word[0]) + ' count :' + str(word[1]),file=bagout)        
'''
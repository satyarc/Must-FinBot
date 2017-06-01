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
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

from newsapi.commands import Sources, headlines
from newsapi.commands import Headlines

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import PorterStemmer  
import numpy as np   

  
def fetchNewsFrom(newsSource):
    apiKey = 'dummydummydummydummydummydummy'
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
  
def fetchNewsFromSources():
    url = "https://newsapi.org/v1/sources?language=en&category=business"
    response = requests.get(url)
    data = response.json()
    textFromAllSources = "" 
    textFromCurrentSource = ""
    sourceids = []
    xar = []
    yar = []
 
    if data["status"] != "error":
        sources = data["sources"]
        for source in sources:
            g_score = 0
            b_score = 0
            totalWords = 0
            sourceids.append(source["id"])  
            textFromCurrentSource = fetchNewsFrom(source["id"])
            print(source["id"])  
            print(textFromCurrentSource) 

            words = word_tokenize(textFromCurrentSource)
            for word in words:
                totalWords += 1
                if word in set(synonyms):
                    g_score += 1
                else:
                    if word in set(antonyms):
                        b_score -= 1    
            xar.append(totalWords)   
            yar.append(g_score + b_score)     
            textFromAllSources += textFromCurrentSource
    else:
        print("Invalid news source.")
    
    style.use("ggplot")
    width = 0.8
    index = np.arange(len(sourceids))
    print (yar)
    rects = plt.bar(index, yar,width,color='green', label='Market sentiment')
    plt.xlabel('Sources')
    plt.ylabel('Sentiment')
    plt.title('Market sentiment')
    plt.xticks(index, sourceids)
    plt.legend()
    plt.tight_layout()
    plt.show() 
    return textFromAllSources

synonyms = []
antonyms = []

indicators =['bullish','up','demand','interest','invest','enter','hold']
for indicator in indicators:
    for syn in wordnet.synsets(indicator):
        for l in syn.lemmas():
            synonyms.append(l.name())
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())

fetchNewsFromSources()
               
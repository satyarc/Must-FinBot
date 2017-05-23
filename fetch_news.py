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

from newsapi.commands import Sources, headlines
from newsapi.commands import Headlines

def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)
        
        
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
                    uprint(article["title"], file=out)
                    description = article["description"]
                    textFromAllArticles += description
                    uprint(description, file=out)
                    uprint(article["url"], file=out)
    else:
        uprint("Invalid news source.")
        
    return textFromAllArticles

sources = ['financial-times','busines-insider-uk','techcrunch','business-insider','google-news','the-times-of-india','usa-today'] 
textFromAllSources = "" 
for source in sources:      
    textFromAllSources += fetchNewsFrom(source)

commonBagOfWords =  collections.Counter(re.findall(r'\w+', textFromAllSources))
mostCommonWords = commonBagOfWords.most_common(50)

with open('bags', 'a') as bagout:
    for word in mostCommonWords:
        uprint('word :' + str(word[0]) + ' count :' + str(word[1]),file=bagout)        

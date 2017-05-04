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

from bs4 import BeautifulSoup

USER_AGENT_SATYA = 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
VALID_URL = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
SOURCE = 'https://www.google.com/search?hl=en&gl=in&tbm=nws&authuser=0&q='

def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)
        
def fetchNewsRelatedTo(symbol):
    headers = {}
    headers['User-Agent'] = USER_AGENT_SATYA
    url = SOURCE + symbol
    req = urllib.request.Request(url,headers=headers)
    resp = urllib.request.urlopen(req)
    respData = resp.read()
    urls = re.findall(VALID_URL, str(respData))
    contextUrls = list(filter(lambda url:symbol in url, urls))
    newsAlerturls = list(filter(lambda url:'news' in url or 'alert' in url or 'market' in url, contextUrls))
    return newsAlerturls

def fetchNewsContent(symbol):
    newsUrls = fetchNewsRelatedTo(symbol)
    newsItemTexts = []
    for newsurl in newsUrls :
        page = requests.get(newsurl)
        soup = BeautifulSoup(page.content, 'html.parser')
        newsitems = soup.find_all('p')
        for newsitem in newsitems:
            newsItemTexts.append(newsitem.get_text()) 
    return newsItemTexts
    
symbols = ['indiabulls','koltepatil']   

for symbol in symbols:
    uprint('symbol:' + symbol)
    newsitems = fetchNewsContent(symbol)
    for newsitem in newsitems:
        uprint(newsitem)

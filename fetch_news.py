'''
Created on 6 Apr 2017

# @author: Satya
'''
import urllib.request
import urllib.parse
import re
import json

USER_AGENT_SATYA = 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
VALID_URL = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
SOURCE = 'https://www.google.com/search?q='

def fetchNewsRelatedTo(symbol):
    headers = {}
    headers['User-Agent'] = USER_AGENT_SATYA
    url = SOURCE + symbol
    req = urllib.request.Request(url,headers=headers)
    resp = urllib.request.urlopen(req)
    respData = resp.read()
    urls = re.findall(VALID_URL, str(respData))
    contextUrls = list(filter(lambda url:symbol in url, urls))
    json_data = json.dumps(contextUrls)
    return json_data

print(fetchNewsRelatedTo('kolte'))
print(fetchNewsRelatedTo('sbi'))
print(fetchNewsRelatedTo('unitec'))
print(fetchNewsRelatedTo('nifty'))
print(fetchNewsRelatedTo('NYSE'))
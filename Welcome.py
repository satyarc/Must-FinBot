# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from flask import Flask, jsonify
import requests

synonyms = ['bullish','up','demand','interest','invest','enter','hold']
antonyms = ['bearish','down','supply','take out', 'exit','sell']

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
                 description = article["description"]
                 textFromAllArticles += description

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
    scores = {}
    if data["status"] != "error":
        sources = data["sources"]
        
        for source in sources:
            netScore = 0 
            g_score = 0
            b_score = 0
            totalWords = 0
            sourceids.append(source["id"])  
            textFromCurrentSource = fetchNewsFrom(source["id"])
            print(source["id"])  
            words = textFromCurrentSource.split()
            for word in words:
                totalWords += 1
                if word in set(synonyms):
                    g_score += 1
                else:
                    if word in set(antonyms):
                        b_score -= 1  
            
            netScore = g_score + b_score
            if(netScore == 0):
                scores[source["id"]] = "HOLD" 
            elif(netScore < 0):
                scores[source["id"]] = "SELL"
            elif(netScore > 0):
                scores[source["id"]] = "BUY"
            textFromAllSources += textFromCurrentSource
         	
    else:
        print("Invalid news source.")
    return scores


app = Flask(__name__)

@app.route('/')
def Welcome():
    return app.send_static_file('index.html')

@app.route('/myapp')
def WelcomeToMyapp():
    return 'Welcome again to my app running on Bluemix!'

@app.route('/api/people')
def GetPeople():
    list = [
        {'name': 'John', 'age': 28},
        {'name': 'Bill', 'val': 26}
    ]
    return jsonify(results=list)
    
@app.route('/api/sentiment')
def GetSentiment():
    sentiments = fetchNewsFromSources()
    return jsonify(results=sentiments)

@app.route('/api/people/<name>')
def SayHello(name):
    message = {
        'message': 'Hello ' + name
    }
    return jsonify(results=message)


if __name__ == "__main__":
	app.run()

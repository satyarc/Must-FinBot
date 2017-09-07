'''
Created on 6 Aug 2017

# @author: Satya
'''
import spacy
import en_core_web_md
import json
import requests
from collections import Counter
import numpy as np
from keras.models import model_from_json,Sequential

noisy_pos_tags = ["PROP","DET","PART","CCONJ","ADP","PRON","VERB","ADJ"]
min_token_length = 2

def isNoise(token):     
    is_noise = False
    if token.pos_ in noisy_pos_tags:
        is_noise = True 
    elif token.is_stop == True:
        is_noise = True
    elif len(token.string) <= min_token_length:
        is_noise = True
    return is_noise 

def cleanup(token, lower = True):
    if lower:
       token = token.lower()
    return token.strip()

class SentimentAnalyser(object):
    @classmethod
    def load(cls,  nlp):
        model = Sequential()
        '''
        with open('model','rb') as file_:
            lstm_weights = pickle.load(file_)
        embeddings = get_embeddings(nlp.vocab)
        model.set_weights([embeddings] + lstm_weights)
        '''
        return cls(model)

    def __init__(self, model):
        self._model = model

    def __call__(self, doc):
        X = get_features([doc], self.max_length)
        y = self._model.predict(X)
        self.set_sentiment(doc, y)

    def pipe(self, docs, batch_size=1000, n_threads=2):
        for minibatch in cytoolz.partition_all(batch_size, docs):
            Xs = get_features(minibatch)
            ys = self._model.predict(Xs)
            for i, doc in enumerate(minibatch):
                doc.sentiment = ys[i]

    def set_sentiment(self, doc, y):
        doc.sentiment = float(y[0])
        
def count_entity_sentiment(nlp, texts):
    '''Compute the net document sentiment for each entity in the texts.'''
    entity_sentiments = Counter()
    for doc in nlp.pipe(texts, batch_size=1000, n_threads=4):
        for ent in doc.ents:
            entity_sentiments[ent.text] += doc.sentiment
    return entity_sentiments

def load_nlp():
    def create_pipeline(nlp):
        return [nlp.tagger, nlp.entity, SentimentAnalyser.load(nlp)]
    return spacy.load('en', create_pipeline=create_pipeline)

def get_features(docs, max_length = 2):
    Xs = np.zeros((len(docs), max_length), dtype='int32')
    for i, token in enumerate(docs):
         Xs[i] = token.rank if token.has_vector else 0
    return Xs

def fetchNewsFrom(newsSource):
    apiKey = 'a892420deb3f46dea3c5f5c0b9863bf3'
    url = "https://newsapi.org/v1/articles?apiKey=" + apiKey + "&source=" + newsSource
    response = requests.get(url)
    data = response.json()
    docFromSource = ""

    if data["status"] != "error":
        articles = data["articles"]
        for article in articles:
            if article["description"] is not None:
                description = article["description"]
                docFromSource += description
    else:
        print("Invalid news source.")
    return docFromSource
    
def fetchNewsFromSources():
    url = "https://newsapi.org/v1/sources?language=en&category=business"
    response = requests.get(url)
    data = response.json()
    docFromSources = ""
    
    if data["status"] != "error":
        sources = data["sources"]
        for source in sources:
            docFromSources += fetchNewsFrom(source["id"])
    else:
        print("Invalid news source.")
        
    return docFromSources

nlp = en_core_web_md.load()  
load_nlp()
print(count_entity_sentiment(nlp, fetchNewsFromSources()))

#print(get_features(nlp(fetchNewsFromSources())))
    
'''               
cleaned_list = [cleanup(word.string) for word in doc if not isNoise(word)]               
print(Counter(cleaned_list).most_common(20))
'''

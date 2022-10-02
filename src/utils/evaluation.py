# -*- coding: utf-8 -*-

import numpy as np
from scipy import spatial
import os
from pathlib import Path
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import gensim.downloader as api
corpus = api.load('text8')

import inspect
#print(inspect.getsource(corpus.__class__))
#print(inspect.getfile(corpus.__class__))

from gensim.models.word2vec import Word2Vec
import stringdist
import spacy
nlp = spacy.load('en_core_web_lg')

word2vec_model_path = Path(os.path.dirname(__file__)+"/../../word2vec.model")

if word2vec_model_path.is_file():
    model = Word2Vec.load(os.path.dirname(__file__)+"/../../word2vec.model")

else: 
    model = Word2Vec(corpus)
    model.save(os.path.dirname(__file__)+"/../../word2vec.model")

#print(model.most_similar('tree'))
index2word_set = set(model.wv.index2word)

def avg_feature_vector(sentence, model, num_features, index2word_set):
    words = sentence.split()
    feature_vec = np.zeros((num_features, ), dtype='float32')
    n_words = 0
    for word in words:
        if word in index2word_set:
            n_words += 1
            feature_vec = np.add(feature_vec, model[word])
    if (n_words > 0):
        feature_vec = np.divide(feature_vec, n_words)
    return feature_vec

def word2vec(text1, text2):
    #print(text1)
    #print(text2)
    s1_afv = avg_feature_vector(text1, model=model, num_features=100, index2word_set=index2word_set)
    s2_afv = avg_feature_vector(text2, model=model, num_features=100, index2word_set=index2word_set)
    if np.sum(s1_afv) == 0 or np.sum(s2_afv) == 0:
        text1 = nlp(text1)
        text2 = nlp(text2)
        sim = text1.similarity(text2)
    else:
        sim = 1 - spatial.distance.cosine(s1_afv, s2_afv)
    
    return sim

def distance_levenshtein(text1, text2):
    dist = stringdist.levenshtein_norm(text1, text2)
    return dist

if __name__== "__main__":
    text1 = 'i love you'
    text2 = 'i want you'

    print(distance_levenshtein(text1,text2))
    print(distance_levenshtein('The French Revolution','French Revolution'))
    print(distance_levenshtein('The French Revolution','French'))
    print(distance_levenshtein('The French Revolution','Revolution'))
    print(distance_levenshtein('cat','dog'))

    a = nlp('cat')
    b = nlp('dog')
    print(a.similarity(b))
# -*- coding: utf-8 -*-

import json
import nltk
nltk.download('wordnet')
import os 

from copy import deepcopy
import itertools
from itertools import combinations

import re
import dateutil.parser as dparser

import pycountry
from geotext import GeoText
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer

#from verbs import cojugVerb

import spacy
nlp = spacy.load('en_core_web_sm')
from spacy import displacy

def request_questions(nr_questions):
    test = [["Who was de the first King of Portugal?", 51, 10, "Afonso"], 
            ["Who was the son of Henry of Burgundy and Teresa?", 51, 19, "Afonso"],
            ["Who conquered Portugal?", 51, 19, "Afonso"],
            ["Who was Countess and Queen of Portugal?", 51, 19, "Teresa"],
            ["Who was the illegitimate daughter of King Alfonso VI and Castile by Jimena?", 51, 19, "Teresa"],
            ["Who reigned jointly as count and countess of Portugal?", 51, 19, "[‘Henry’,’Teresa’]"],
            ["Who was providing military assistance to his father-in-law against the Muslims on the Portuguese march?", 51, 19, "Henry"],
            ["Who disliked the alliance between Galicia and Portugal and rallied around Afonso?", 51, 19, "The Portuguese nobility"]]
    return questions_from_file(os.path.dirname(__file__) + "/texts/" + str(nr_questions) + ".txt")



def question_list_to_json(qs_list):
    qs_json = []
    for qs in qs_list:
        i = 0
        q_json = {}
        for q in qs:
            if i == 0:
                q_json['question'] = q
            elif i == 1:
                q_json['n_file'] = q
            elif i == 2:
                q_json['n_para'] = q
            elif i == 3:
                q_json['answer'] = q
            i += 1
        qs_json.append(q_json)
    #qs_json = json.dumps(qs_json)
    return qs_json

# Spacy Pos Tagging & Dependency Parse
def tagging_spacy(sentence):
    result = []
    doc = nlp(sentence)
    for token in doc:
        result.append([token.text, token.pos_, token.dep_, token.lemma_])
    return result

# Spacy Entities
def ner_spacy(sentence):
    result = []
    doc = nlp(sentence)
    tokens_sent = tokenize_words(sentence)
    for ent in doc.ents:
        result.append([ent.text, ent.start_char, ent.end_char, ent.label_, ent.start, ent.end])
    return result


# Tokenize Sentences
def tokenize_sentences(text):
    sentences = nltk.sent_tokenize(text)
    return sentences

# Tokenize words
def tokenize_words(sentence):
    words = nltk.word_tokenize(sentence)
    return words

# Tagging Sentences
def tagging_sentences(sentences):
    result = []
    for sentence in sentences:
        result.append(tagging_spacy(sentence))
    return result

# Ner Sentences
def ner_sentences(sentences):
    result = []
    for sentence in sentences:
        result.append(ner_spacy(sentence))
    return result

# Sentence Selection
def sentence_selection(my_sentences, ner_sentences):
    sents_ners = []
    for index, ners in enumerate(ner_sentences):
        if len(ners) >= 0:
            sents_ners.append(index)
    return sents_ners

#pre_processing
def pre_processing(text):

    #List of sentences from given text
    my_sentences = tokenize_sentences(text)

    #List of words given a sentence
    my_words = []
    for sentence in my_sentences:

        sentence_tokenized = tokenize_words(sentence)

        #Ignore sentences with < 3 words
        if len(sentence_tokenized) >= 4:
            my_words.append(sentence_tokenized)
        else:
            my_sentences.remove(sentence)

    return my_sentences, my_words

def create_expression(type_tag, pos_int_sents):
    expression = ""

    for idx, pos_sent in enumerate(pos_int_sents):
        expression = expression + "<" + pos_sent[type_tag] + ">"

    return expression

# https://stackoverflow.com/questions/17870544/find-starting-and-ending-indices-of-sublist-in-list
def find_sub_list(sl,l):
    sll=len(sl)
    for ind in (i for i,e in enumerate(l) if e==sl[0]):
        if l[ind:ind+sll]==sl:
            return ind,ind+sll-1

def retrieve_indexMath(pattern, pos_int_sents, tag_type):
    a = re.compile("><").split(pattern)
    a[0] = a[0].replace('<', '')
    a[len(a)-1] = a[len(a)-1].replace('>', '')

    b=[]
    for sec in pos_int_sents:
        b.append(sec[tag_type])

    result1 = find_sub_list(a,b)

    i = result1[0]
    match_indxs = []
    while i <= result1[1]:
        match_indxs.append(i)
        i += 1
    return a, match_indxs

def gen_ner_date_question(word_ner, pos_sents_idx, info):
    result = -1
    find = 0

    pos_int_sents = deepcopy(pos_sents_idx)

    for index, pos_tag in enumerate(pos_int_sents):
        if pos_tag[0] == word_ner[0]:
            find = 1
            pos_int_sents[index][1] = word_ner[3]

    if find == 0:
        return result

    expression = create_expression(1,pos_int_sents)

    pattern_match1 = re.findall("<ADP><DATE><PUNCT><(?:PROPN|PRON)><AUX><VERB>.*?<PUNCT>", expression) #active
    pattern_match2 = re.findall("<ADP><DATE><PUNCT><(?:PROPN|PRON)><VERB>.*?<PUNCT>", expression) #active
    pattern_match3 = re.findall("<PROPN><AUX><NOUN><ADP><DATE><PUNCT>", expression) 
    pattern_match4 = re.findall("<PROPN><AUX><VERB><ADP><DATE><PUNCT>", expression) 


    if pattern_match1:
        #verify
        match, list_idx = retrieve_indexMath(pattern_match1[0], pos_int_sents, 1)

        question = "When" + " " + retrieve_from_string([list_idx[4]], pos_int_sents) + " " + retrieve_from_string([list_idx[3]], pos_int_sents) + retrieve_from_string([list_idx[5],list_idx[-1]-1], pos_int_sents) + "?"
        result = [question, info[0], info[1], word_ner[0]]

    if pattern_match2:
        #verify
        match, list_idx = retrieve_indexMath(pattern_match2[0], pos_int_sents, 1)

        change_verb = "change_verb"

        question = "When " +  retrieve_from_string([list_idx[3]], pos_int_sents) + retrieve_from_string([list_idx[4], list_idx[-1]-1], pos_int_sents) + "?" 
        result = [question, info[0], info[1], word_ner[0]]

    if pattern_match3:
        #verify
        match, list_idx = retrieve_indexMath(pattern_match3[0], pos_int_sents, 1)

        question = "When " + retrieve_from_string([list_idx[1]], pos_int_sents) + " " + retrieve_from_string([list_idx[0]], pos_int_sents) + " " + retrieve_from_string([list_idx[2]], pos_int_sents) + "?"
        result = [question, info[0], info[1], word_ner[0]]

    if pattern_match4:
        #verify
        match, list_idx = retrieve_indexMath(pattern_match4[0], pos_int_sents, 1)

        question = "When " + retrieve_from_string([list_idx[1]], pos_int_sents) + " " + retrieve_from_string([list_idx[0]], pos_int_sents) + " " + retrieve_from_string([list_idx[2]], pos_int_sents) + "?"
        result = [question, info[0], info[1], word_ner[0]]

    return result

def gen_ner_per_question(word_ner, pos_sents_idx, info):
    result = -1
    find = 0
    pos_int_sents = deepcopy(pos_sents_idx)
    for index, pos_tag in enumerate(pos_int_sents):
        if pos_tag[0] == word_ner[0]:
            find = 1
            pos_int_sents[index][1] = word_ner[3]

    if find == 0:
        return result
    expression = create_expression(1,pos_int_sents)

    pattern_match1 = re.findall("<PERSON><(?:AUX|VERB)>.*?<PUNCT>", expression) #active
    pattern_match2 = re.findall("<DET><NOUN><AUX><VERB><ADP><PERSON>.*?<PUNCT>", expression) #Passive

    if pattern_match1:
        #verify
        match, list_idx = retrieve_indexMath(pattern_match1[0], pos_int_sents, 1)
        # remove case with 'and' PERSON
        if list_idx[0]-2 >= 0:
            if pos_sents_idx[list_idx[0]-2][1] == "CCONJ":
                return -1

        #current_verb = pos_int_sents[list_idx[1]][3]
        #current_tense = nltk.pos_tag([current_verb])
        #root_verb = (WordNetLemmatizer().lemmatize(current_verb,'v'))

        changed_verb = "verb"
        #if current_tense[0][1] == 'VBD' and root_verb != 'be':
            #changed_verb = "did " + root_verb
        #elif current_tense[0][1] == 'VBD' and root_verb == 'be':
            #changed_verb = current_verb
        question = "Who" + retrieve_from_string([list_idx[1],list_idx[-1]-1], pos_int_sents) + "?"
        result = [question, info[0], info[1], word_ner[0]]

    if pattern_match2:
        match, list_idx = retrieve_indexMath(pattern_match2[0], pos_int_sents, 1)
        # remove case with 'and' PERSON
        if pos_sents_idx[list_idx[6]][1] == "CCONJ":
            return -1

        current_verb = pos_int_sents[list_idx[3]][0]
        current_tense = nltk.pos_tag([current_verb])
        root_verb = (WordNetLemmatizer().lemmatize(current_verb,'v'))

        question = "Who did" + " " + root_verb + " " + retrieve_from_string([list_idx[0]], pos_int_sents).lower() + " " + retrieve_from_string([list_idx[1]], pos_int_sents).lower() + "?"
        result = [question, info[0], info[1], word_ner[0]]
    return result

def gen_ner_money_question(word_ner, pos_sents_idx, info):
    result = -1
    find = 0
    pos_int_sents = deepcopy(pos_sents_idx)
    for index, pos_tag in enumerate(pos_int_sents):
        if pos_tag[0] == word_ner[0]:
            find = 1
            pos_int_sents[index][1] = word_ner[3]

    if find == 0:
        return result
    expression = create_expression(1, pos_int_sents)

    pattern_match1 = re.findall("<DET><NOUN><VERB><MONEY><PUNCT>", expression) 
    pattern_match2 = re.findall("<NOUN><NOUN><VERB><MONEY><PUNCT>", expression) 

    if pattern_match1:
        #verify
        match, list_idx = retrieve_indexMath(pattern_match1[0], pos_int_sents, 1)
        question = "How much " + retrieve_from_string([list_idx[2]], pos_int_sents) + retrieve_from_string([list_idx[0], list_idx[1]], pos_int_sents) + "?"
        result = [question, info[0], info[1], word_ner[0]]
    if pattern_match2:
        #verify
        match, list_idx = retrieve_indexMath(pattern_match2[0], pos_int_sents, 1)
        question = "How much " + retrieve_from_string([list_idx[2]], pos_int_sents) + " the" + retrieve_from_string([list_idx[0], list_idx[1]], pos_int_sents) + "?"
        result = [question, info[0], info[1], word_ner[0]]
    return result

def gen_ner_event_question(word_ner, pos_sents_idx, info):
    result = -1
    find = 0
    pos_int_sents = deepcopy(pos_sents_idx)
    for index, pos_tag in enumerate(pos_int_sents):
        if pos_tag[0] == word_ner[0]:
            find = 1
            pos_int_sents[index][1] = word_ner[3]

    if find == 0:
        return result
    expression = create_expression(1, pos_int_sents)

    pattern_match1 = re.findall("<EVENT><(?:AUX|VERB)>.*?<PUNCT>", expression) 

    if pattern_match1:
        match, list_idx = retrieve_indexMath(pattern_match1[0], pos_int_sents, 1)
        question = "Which event" + retrieve_from_string([list_idx[1],list_idx[-1]-1], pos_int_sents) + "?"
        result = [question, info[0], info[1], word_ner[0]]

    return result

def gen_ner_gpe_question(word_ner, pos_sents_idx, info):
    result = -1
    find = 0
    pos_int_sents = deepcopy(pos_sents_idx)
    for index, pos_tag in enumerate(pos_int_sents):
        if pos_tag[0] == word_ner[0]:
            find = 1
            pos_int_sents[index][1] = word_ner[3]

    if find == 0:
        return result
    expression = create_expression(1, pos_int_sents)

    places = GeoText(word_ner[0])

    if(len(places.cities)) > 0:
        startQuest = "Which city"
    elif(len(places.countries)) > 0:
        startQuest = "Which country"
    else:
        startQuest = "Which location"

    pattern_match1 = re.findall("<(?:GPE|LOC)><(?:AUX|VERB)>.*?<PUNCT>", expression)
    pattern_match2 = re.findall("<PRON><VERB><VERB><NOUN><ADP><GPE><PUNCT>", expression)
    pattern_match3 = re.findall("<NOUN><PRON><AUX><DET><NOUN><ADP><GPE><PUNCT>", expression)

    if pattern_match1:
        match, list_idx = retrieve_indexMath(pattern_match1[0], pos_int_sents, 1)
        question = startQuest + retrieve_from_string([list_idx[1],list_idx[-1]-1], pos_int_sents) + "?"
        result = [question, info[0], info[1], word_ner[0]]
    if pattern_match2:
        match, list_idx = retrieve_indexMath(pattern_match2[0], pos_int_sents, 1)
        question = startQuest + " " + retrieve_from_string([list_idx[1]], pos_int_sents) + " " + retrieve_from_string([list_idx[0]], pos_int_sents) + retrieve_from_string([list_idx[2], list_idx[3]], pos_int_sents) + "?"
        result = [question, info[0], info[1], word_ner[0]]
    if pattern_match3:
        match, list_idx = retrieve_indexMath(pattern_match3[0], pos_int_sents, 1)
        question = startQuest + " " + retrieve_from_string([list_idx[2]], pos_int_sents) + " " + retrieve_from_string([list_idx[1]], pos_int_sents) + retrieve_from_string([list_idx[3], list_idx[4]], pos_int_sents) + "?"
        result = [question, info[0], info[1], word_ner[0]]
    return result

def gen_ner_org_question(word_ner, pos_sents_idx, info):
    result = -1
    find = 0
    pos_int_sents = deepcopy(pos_sents_idx)
    for index, pos_tag in enumerate(pos_int_sents):
        if pos_tag[0] == word_ner[0]:
            find = 1
            pos_int_sents[index][1] = word_ner[3]

    if find == 0:
        return result
    expression = create_expression(1, pos_int_sents)

    pattern_match1 = re.findall("<ORG><(?:AUX|VERB)>.*?<PUNCT>", expression)
    pattern_match2 = re.findall("<DET><ADJ><NOUN><AUX><ORG><PUNCT>", expression)
    pattern_match3 = re.findall("<NOUN><PRON><VERB><VERB><ADP><ORG><PUNCT>", expression)

    if pattern_match1:
        match, list_idx = retrieve_indexMath(pattern_match1[0], pos_int_sents, 1)
        question = "Which organization" + retrieve_from_string([list_idx[1], list_idx[-1]-1], pos_int_sents) + "?"
        result = [question, info[0], info[1], word_ner[0]]
    if pattern_match2:
        match, list_idx = retrieve_indexMath(pattern_match2[0], pos_int_sents, 1)
        question = "Which organization" + " " + retrieve_from_string([list_idx[3]], pos_int_sents) + retrieve_from_string([list_idx[0], list_idx[2]], pos_int_sents) + "?"
        result = [question, info[0], info[1], word_ner[0]]
    if pattern_match3:
        match, list_idx = retrieve_indexMath(pattern_match3[0], pos_int_sents, 1)
        question = "Which organization" + " " + retrieve_from_string([list_idx[2]], pos_int_sents) + " " + retrieve_from_string([list_idx[1]], pos_int_sents) + " " + retrieve_from_string([list_idx[3]], pos_int_sents) + " " + retrieve_from_string([list_idx[0]], pos_int_sents) + "?"
        result = [question, info[0], info[1], word_ner[0]]
    return result

def gen_per_per_question(first_ner, second_ner, pos_sents_idx, info):
    result = -1
    find1 = 0
    find2 = 0
    pos_int_sents = deepcopy(pos_sents_idx)
    for index, pos_tag in enumerate(pos_int_sents):
        if pos_tag[0] == first_ner[0]:
            find1 = 1
            pos_int_sents[index][1] = first_ner[3]
        if pos_tag[0] == second_ner[0]:
            find2 = 1
            pos_int_sents[index][1] = second_ner[3]         

    if find1 == 0 or find2 == 0:
        return result

    expression = create_expression(1, pos_int_sents)

    pattern_match1 = re.findall("<PERSON><CCONJ><PERSON><(?:AUX|VERB)>.*?<PUNCT>", expression)
    pattern_match2 = re.findall("<DET><NOUN><AUX><VERB><ADP><PERSON><CCONJ><PERSON><PUNCT>", expression)

    if pattern_match1:
        match, list_idx = retrieve_indexMath(pattern_match1[0], pos_int_sents, 1)

        current_verb = pos_int_sents[list_idx[4]][3]
        changed_verb = "CHANGE_VERB"

        question = "What people" + retrieve_from_string([list_idx[3],list_idx[-1]-1], pos_int_sents) + "?"
        result = [question, info[0], info[1], [first_ner[0], second_ner[0]]]
    if pattern_match2:
        match, list_idx = retrieve_indexMath(pattern_match2[0], pos_int_sents, 1)

        current_verb = pos_int_sents[list_idx[4]][3]
        changed_verb = "CHANGE_VERB"

        question = "What people " + retrieve_from_string([list_idx[3]], pos_int_sents) + retrieve_from_string([list_idx[0],list_idx[1]], pos_int_sents) + "?"
        result = [question, info[0], info[1], [first_ner[0], second_ner[0]]]
    return result

def gen_per_gpe_question(first_ner, second_ner, pos_sents_idx, info):
    result = -1
    find1 = 0
    find2 = 0
    pos_int_sents = deepcopy(pos_sents_idx)
    for index, pos_tag in enumerate(pos_int_sents):
        if pos_tag[0] == first_ner[0]:
            find1 = 1
            pos_int_sents[index][1] = first_ner[3]
        if pos_tag[0] == second_ner[0]:
            find2 = 1
            pos_int_sents[index][1] = second_ner[3]         

    if find1 == 0 or find2 == 0:
        return result

    expression = create_expression(1, pos_int_sents)

    pattern_match1 = re.findall("<PERSON><(?:AUX|VERB)>.*?<ADP><(?:GPE|LOC)><PUNCT>", expression)

    if pattern_match1:
        match, list_idx = retrieve_indexMath(pattern_match1[0], pos_int_sents, 1)
        question = "Where " + retrieve_from_string([list_idx[1]], pos_int_sents).lower() + " " + retrieve_from_string([list_idx[0]], pos_int_sents) + "?"
        result = [question, info[0], info[1], second_ner[0]]
    return result

def retrieve_from_string(range, pos_int_sents):
    concat = ""

    if(len(range) == 2):
        i = range[0]
        j = range[1]
        while i <= j:
            concat = concat + " " + pos_int_sents[i][0]
            i+=1
    if(len(range) == 1):
        concat = pos_int_sents[range[0]][0]

    return concat

def gen_dep_question(my_sent, tag_sent, ner_sent, info):
    concat = []
    
    expression = create_expression(2, tag_sent)

    pattern_match1 = re.findall("<nsubj><ROOT><det><dobj><punct>", expression)
    pattern_match2 = re.findall("<nsubj><ROOT><det><amod><dobj><prep><pobj><punct>", expression)
    pattern_match3 = re.findall("<nsubj><ROOT><poss><dative><det><appos><punct>", expression)
    pattern_match4 = re.findall("<nsubj><ROOT>.*?<det><amod><dobj><punct>", expression)
    pattern_match5 = re.findall("<nsubj><ROOT><poss><dative><det><amod><dobj><punct>", expression)

    if pattern_match1:
        match, list_idx = retrieve_indexMath(pattern_match1[0], tag_sent, 2)
        current_verb = retrieve_from_string([list_idx[1]], tag_sent)
        root_verb = (WordNetLemmatizer().lemmatize(current_verb,'v'))
        question = "What did " + retrieve_from_string([list_idx[0]], tag_sent) + " " + root_verb + "?"
        concat.append([question, info[0], info[1], retrieve_from_string([list_idx[2],list_idx[3]], tag_sent)])
    if pattern_match2:
        match, list_idx = retrieve_indexMath(pattern_match2[0], tag_sent, 2)
        current_verb = retrieve_from_string([list_idx[1]], tag_sent)
        root_verb = (WordNetLemmatizer().lemmatize(current_verb,'v'))
        question = "What did " + retrieve_from_string([list_idx[0]], tag_sent) + " " + root_verb + "?"
        concat.append([question, info[0], info[1], retrieve_from_string([list_idx[2],list_idx[4]], tag_sent)])
    if pattern_match3:
        match, list_idx = retrieve_indexMath(pattern_match3[0], tag_sent, 2)
        current_verb = retrieve_from_string([list_idx[1]], tag_sent)
        root_verb = (WordNetLemmatizer().lemmatize(current_verb,'v'))
        question = "What did " + retrieve_from_string([list_idx[0]], tag_sent) + " " + root_verb + " to" + retrieve_from_string([list_idx[2], list_idx[3]], tag_sent) + "?"
        concat.append([question, info[0], info[1], retrieve_from_string([list_idx[-3],list_idx[-2]], tag_sent)])
    if pattern_match4:
        match, list_idx = retrieve_indexMath(pattern_match4[0], tag_sent, 2)
        current_verb = retrieve_from_string([list_idx[1]], tag_sent)
        root_verb = (WordNetLemmatizer().lemmatize(current_verb,'v'))
        question = "What did " + retrieve_from_string([list_idx[0]], tag_sent) + " " + root_verb + "?"
        concat.append([question, info[0], info[1], retrieve_from_string([list_idx[-4],list_idx[-2]], tag_sent)])
    if pattern_match5:
        match, list_idx = retrieve_indexMath(pattern_match5[0], tag_sent, 2)
        current_verb = retrieve_from_string([list_idx[1]], tag_sent)
        root_verb = (WordNetLemmatizer().lemmatize(current_verb,'v'))
        question = "To whom did " + retrieve_from_string([list_idx[0]], tag_sent) + " " + root_verb + retrieve_from_string([list_idx[4], list_idx[6]], tag_sent) + "?"
        concat.append([question, info[0], info[1], retrieve_from_string([list_idx[2],list_idx[3]], tag_sent)])
    return concat

def question_deps_formation(my_sents, file_name, tag_sents, ner_sents):
    questions = []
    for idx, my_sent in enumerate(my_sents):
        new_quests = gen_dep_question(my_sent, tag_sents[idx], ner_sents[idx], [file_name, idx])
        if len(new_quests) > 0:
            questions.append(new_quests)
    return questions

def question_ners_formation(file_name, ner_sents, sents_ner_idx, pos_sents):
    questions = []
    new_quest = -1
    for ner_idx in sents_ner_idx:
        ner_sent = ner_sents[ner_idx] 
        #one entity
        comb1 = combinations(ner_sent, 1)
        for word_ner in list(comb1):
            # People, including fictional.
            if word_ner[0][3] == "PERSON":
                new_quest = gen_ner_per_question(word_ner[0], pos_sents[ner_idx], [file_name, ner_idx])
            # Countries, cities, states.
            elif word_ner[0][3] == "GPE" or word_ner[0][3] == "LOC":
                new_quest = gen_ner_gpe_question(word_ner[0], pos_sents[ner_idx], [file_name, ner_idx])
            # Companies, agencies, institutions, etc.
            elif word_ner[0][3] == "ORG":
                new_quest = gen_ner_org_question(word_ner[0], pos_sents[ner_idx], [file_name, ner_idx])
            elif word_ner[0][3] == "DATE":
                new_quest = gen_ner_date_question(word_ner[0], pos_sents[ner_idx], [file_name, ner_idx])
            elif word_ner[0][3] == "EVENT":
                new_quest = gen_ner_event_question(word_ner[0], pos_sents[ner_idx], [file_name, ner_idx])
            elif word_ner[0][3] == "MONEY":
                new_quest = gen_ner_money_question(word_ner[0], pos_sents[ner_idx], [file_name, ner_idx])
            if new_quest != -1 and new_quest[3] not in new_quest[0]:
                questions.append(new_quest)
                new_quest=-1
        #two entities
        new_quest = -1
        comb2 = combinations(ner_sent, 2)
        for word_ner in list(comb2):
            if word_ner[0][3] == "PERSON" and word_ner[1][3] == "PERSON":
                new_quest = gen_per_per_question(word_ner[0], word_ner[1], pos_sents[ner_idx], [file_name, ner_idx])
            elif word_ner[0][3] == "PERSON" and (word_ner[1][3] == "GPE" or word_ner[1][3] == "LOC"):
                new_quest = gen_per_gpe_question(word_ner[0], word_ner[1], pos_sents[ner_idx], [file_name, ner_idx])
            if new_quest != -1:
                questions.append(new_quest)
                new_quest=-1
    return questions

def createList(r1, r2): 
    return [item for item in range(r1, r2+1)]

def init_qg(file_name, all_text_content):
    # (1) Pre-Processing phase
    my_sents, my_words = pre_processing(all_text_content)

    print("(1) Pre Processing concluded")

    #Request Pos Tagging for all sentences
    tag_sents = tagging_sentences(my_sents)

    print("(2) Part of Speech concluded")

    #Request Ner for all sentences
    ner_sents = ner_sentences(my_sents)

    save_idx = []
    for idx, ner_sent in enumerate(ner_sents):
        save_idx = []
        for ner in ner_sent:
            if(ner[5]-ner[4] > 1):
                i = ner[4]
                j = ner[5]
                to_delete = createList(i+1,j-1)
                save_idx.append(to_delete)
                merge = tag_sents[idx][ner[4]][0]
                while i < j-1:
                    merge = merge + ' ' + tag_sents[idx][i+1][0]
                    tag_sents[idx][ner[4]][0] = merge
                    i = i + 1
        save_idx = [item for sublist in save_idx for item in sublist]
        for i in reversed(save_idx):
            del tag_sents[idx][i]

    print("(3) Ner concluded")

    # (2) Sentence Selection phase
    sents_ner_idx = sentence_selection(my_sents, ner_sents)

    # (3) Question Formation for NERs
    questions_ners = question_ners_formation(file_name, ner_sents, sents_ner_idx, tag_sents)

    # (4) Question Formation for DEPs
    questions_dep = question_deps_formation(my_sents, file_name, tag_sents, ner_sents)

    return questions_ners, questions_dep


def questions_from_file(file_name):

    # Open a file: file
    file = open(file_name,mode='r',encoding="utf-8")
    
    # read all lines at once
    all_text_content = file.read()
    
    # close the file
    file.close()

    #Gen Questions
    result_ner_questions, result_dep_questions = init_qg(file_name, all_text_content)

    for ques in result_ner_questions:
        print(ques)
        print("\n")

    for ques in result_dep_questions:
        print(ques)
        print("\n")

    return result_ner_questions, result_dep_questions


def main():        
    result = questions_from_file("texts/1.txt")
    #print("Question: This is the script that will gen new questions searching multiple text files.")

if __name__== "__main__":
    main()
from questiongen import request_questions, question_list_to_json
from openie import StanfordOpenIE
from utils.handle_files import read_file
import json
import spacy
import nltk
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from operator import itemgetter
import pandas as pd
from utils.evaluation import word2vec
from nltk.stem.wordnet import WordNetLemmatizer
#import utils.rdf_liaison as liaison
#nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
import os

nlp = spacy.load('en_core_web_lg')

stop_words = set(line.strip() for line in open(os.path.dirname(__file__)+"/../stop_words.txt"))
print(stop_words)
print("it" in stop_words)
lemmatizer = WordNetLemmatizer() 
stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def list_to_text(sentences):
    text = ''
    if not isinstance(sentences, list):
        return sentences
    elif len(sentences) == 0:
        return ''

    for s in sentences:
        text += s[0]
        text += ' '
    return text

def triple_extraction(sentence, client):
    triples = client.annotate(sentence)

    if len(triples) == 0:
        return triples
        s, p, o = liaison.multi_liaison(sentence, output = 'relation')
        triple = {}
        triple['subject'] = list_to_text(s)
        triple['relation'] = list_to_text(p)
        triple['object'] = list_to_text(o)
        triples.append(triple)
    return triples

def pretty_print(triples):
    for triple in triples:
        print('|-', triple)

def get_lines_with_entities(ents, lines):
    new_lines = {}
    for count,line in lines.items():
        flag = True
        for e in ents:
            if str(e) not in line:
                flag = False
        if flag:
            new_lines[count] = line

    if len(new_lines) == 0:
        for count,line in lines.items():
            new_lines[count] = line
    return new_lines

def get_most_relevant_triple(sentence, lines):
    best = -1
    c = ""
    l = ""
    for count, line in lines.items():
        ''' 
            way to divide into phrases
            doc = nlp(line)
            sentences = [sent.string.strip() for sent in doc.sents]
            print(sentences)        
            for s in sentences:
        '''
        '''
            TODO:
            search_doc_no_stop_words = nlp(' '.join([str(t) for t in search_doc if not t.is_stop]))
            main_doc_no_stop_words = nlp(' '.join([str(t) for t in main_doc if not t.is_stop]))
        '''
        li = nlp(line)
        value = sentence.similarity(li)
        if value > best:
            best = value
            c = count
            l = line
    return c, l

def get_answer(triple, ents):
    attributes = {'subject' : True,
                  'relation': True,
                  'object'  : True,
                  }
    for ent in ents:
        ent = str(ent)
        for key in attributes:
            if ent in triple[key]:
                attributes[key] = False
    miss_key = ""
    len = 0
    for key in attributes:
        if attributes[key]:
            len += 1
            miss_key = key           
    #print(triple)
    if len == 1:
        return triple[miss_key]
    return "Wrong Triple"

def triple_selection(triples, ents):
    clean_triples = []
    for t in triples:
        check = 0
        for ent in ents:
            ent = str(ent)
            if ent in t['subject']:
                check += 1
            if ent in t['relation']:
                check += 1
            if ent in t['object']:
                check += 1
        if check == len(ents):
            clean_triples.append(t)
    return clean_triples

def triple_similarity(triples, sentence):
    final_triple = ''
    final_similarity = 0
    for t in triples:
        triple_sentence = ''
        triple_sentence += t['subject']
        triple_sentence += ' ' 
        triple_sentence += t['relation']
        triple_sentence += ' '
        triple_sentence += t['object']
        triple_sentence = nlp(triple_sentence)
        similarity = sentence.similarity(triple_sentence)
        #print(similarity)
        if similarity > final_similarity:
            final_similarity = similarity
            final_triple = t
    return final_triple

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

'''remove punctuation, lowercase, stem'''
def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')

def cosine_sim(text1, text2):
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]

def triple_cosine_sim(triples, sentence):
    final_triple = ''
    final_similarity = 0
    triple_dics = []
    for t in triples:
        triple_dic = {}
        triple_sentence = ''
        triple_sentence += t['subject']
        triple_sentence += ' ' 
        triple_sentence += t['relation']
        triple_sentence += ' '
        triple_sentence += t['object']
        similarity = cosine_sim(sentence.text,triple_sentence)
        #print(similarity)
        triple_dic['score'] = similarity
        triple_dic['triple'] = t
        triple_dics.append(triple_dic)
        if similarity > final_similarity:
            final_similarity = similarity
            final_triple = t
    
    triple_dics = sorted(triple_dics, key=itemgetter('score'), reverse=True)
    triple_dics = triple_dics[0:min(5,len(triple_dics))]
    print(triple_dics)
    filter = []
    for t in triple_dics:
        filter.append(t['triple'])

    return filter

def get_best_answer(triples, question, best_line):
    answer_singular = []
    answer_triples = []

    question_l = ''
    for q in question:
        try:
            question_l += lemmatizer.lemmatize(q.string) + ' '
        except:
            question_l += q.norm_

    for triple in triples:
        attributes = {'subject' : True,
            'relation': True,
            'object'  : True,
            }
        sum = 0
        for key in attributes: 
            triple_nlp = nlp(triple[key])
            aux = 0
            for token in triple_nlp:
                
                if key == 'relation':
                    token = token.prefix_

                if str(token) in question.text:
                    aux += 1
                    attributes[key] = False
            if not attributes[key]:
                sum += 1

        if sum == 2:
            for key in attributes:
                if attributes[key]:
                    #if key == 'relation'  or triple[key] in stop_words:# or triple[key] == 'born':
                    #    continue
                    #else:
                    answer_singular.append(triple[key])
            answer_triples.append(triple)

    if len(answer_singular) == 0 and len(triples) != 0:
        best_line = nlp(best_line)
        ents = best_line.ents
        print("")
        print(question)
        print(ents)
        print(question.ents)
        print("")
        for e in ents:
            e = str(e)
            if e not in question.text:
                answer_singular.append(e)
                return answer_singular, answer_triples
        s = 1.1
        a = ''
        for t in triples[0]:
            tt = nlp(triples[0][t])
            score = tt.similarity(question)
            if score < s:
                s = score
                a = triples[0][t]
            answer_triples.append(triples[0])
        answer_singular.append(a)
    elif len(triples) == 0:
        answer_singular.append('Not found')
        answer_triples.append('Not found')
    
    return answer_singular, answer_triples      

def clean_answer(answer):
    answer = list(dict.fromkeys(answer))
    return answer[0]

def calc_score(all_answers):
    score = 0
    for answer in all_answers:

        if isinstance(answer['y_test'], list):
            aux = ''
            for a in answer['y_test']:
                aux += a 
                aux += ' '
            answer['y_test'] = aux

        if isinstance(answer['y_pred'], list):
            aux = ''
            for a in answer['y_pred']:
                aux += a 
                aux += ' '
            answer['y_pred'] = aux

        print('\nQuestion:' + answer['question'] + '\nAnswer: ' + answer['y_pred'] + '\tResposta: ' + answer['y_test'])

        sim = word2vec(answer['y_pred'], answer['y_test'])
        score += sim
    acc = 0
    for answer in all_answers:
        if answer['y_test'] in answer['y_pred'] or answer['y_pred'] in answer['y_test']:
            acc += 1
    print('RESULT BABY: ' + str(acc/len(all_answers)))
    return (score/len(all_answers))

def flatten_list(list_):
    flatten = ''
    for l in list_:
        flatten += l
        if l != '':
            flatten += ' '
    return flatten

def remove_duplicates(list_):
    answer = list(dict.fromkeys(list_))
    if isinstance(answer, list):
        for i in range(len(answer)):
            for j in range(len(answer)):
                if j == i:
                    continue
                if answer[i] in answer[j]:
                    answer[i] = ''
                    break
    answer = flatten_list(answer)
    return answer

def main(file = ''):
    print("Answer: This is the script that will answer provided questions from text files.\n")
    
    # Request 2 questions
    questions_ner = []
    questions_dep = []
    
    # For Live Demo
    if file != '':
        result_ner_questions, result_dep_questions = request_questions(file)
        questions_ner += result_ner_questions
    else:
        for i in range(53, 54):
            result_ner_questions, result_dep_questions = request_questions('{:02}'.format(i))
            if len(result_dep_questions) != 0:
                for deps in result_dep_questions:                
                    for dep in deps:
                        if isinstance(dep[0],list):
                            for d in dep:
                                questions_dep.append(d)
                        else:
                            questions_dep.append(dep)
            questions_ner += result_ner_questions

    #questions_ner += questions_dep
    questions = question_list_to_json(questions_ner)

    for q in questions:
        print(q)

    all_answers = []

    # https://stanfordnlp.github.io/CoreNLP/openie.html#api
    # Default value of openie.affinity_probability_cap was 1/3.
    properties = {
        'openie.affinity_probability_cap': 2 / 3,
    }

    with StanfordOpenIE(properties=properties) as client:
        for q in questions:
            if '\n' in q['question']:
                continue
            q_nlp = nlp(q['question'])
            sum = 0
            for check in q_nlp:
                sum += 1
            if sum < 5:
                continue
            print(q['question'])
            print(q_nlp.ents)
            lines = read_file(q['n_file'])
            rel_lines = get_lines_with_entities(q_nlp.ents, lines)
            #print(" Lines: ")
            #print(rel_lines)
            best_count, best_line = get_most_relevant_triple(q_nlp, rel_lines)
            triples = triple_extraction(best_line, client)
            if len(triples) == 0:
                continue
            #print("Triple Extraction")
            #print(triples)
            best_triple = triple_selection(triples, q_nlp.ents)
            print(triples)
            triples = triple_cosine_sim(triples, q_nlp) #selects top 5 triples
            #print('Triple Selection')
            #print(triples)
            #print('Best Triple')
            #print(best_triple)
            #print(best_line)
            #print(q_nlp.ents)
            #for t in triples:
            #    answer = get_answer(t, q_nlp.ents)
            #    print(answer)
            print("_________________")
            answer_singular, answer_triples = get_best_answer(triples, q_nlp, best_line)

            # Remove Duplicates
            #answer_singular = clean_answer(answer_singular)
            answer_singular = remove_duplicates(answer_singular)

            print(answer_singular)
            print(answer_triples)
            final_answer = {}
            final_answer['question'] = q['question'] 
            final_answer['y_pred'] = answer_singular
            final_answer['y_test'] = q['answer']
            final_answer['n_line'] = q['n_para']
            final_answer['n_file'] = q['n_file']
            all_answers.append(final_answer)
            ("_________________")
            print("---------------------------------")
            #exit(0)
    print("RESULTS:")
    score = calc_score(all_answers)
    print(score)
    print("\n Extraction Finished\n")
    return all_answers, score

if __name__== "__main__":
    main()
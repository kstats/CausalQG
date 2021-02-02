import csv
import json
import os
import operator
from itertools import compress 
import numpy as np
import copy 

#loading human generated questions, answers, paragraphs from squad
root_dir = '/Users/tonytu/desktop/old_stuff/berkeley/fall2020/research/CausalQG'
def load(dataset):
    filepath = os.path.join(root_dir, dataset)
    with open(filepath) as file:
        data = json.load(file)
    print('succesfully loaded {} articles from squad dataset'.format(len(data['data'])))
    print(filepath)
    return data['data']
    #print data by paragraphs
    
def parse(data):
    #extract all paragraphs from json 
    titles = []
    paragraphs = []
    questions = []
    final_questions = []
    answers = []
    for i in range(len(data)):
        title = data[i]['title']
        titles.append(title)
        for j in range(len(data[i]['paragraphs'])):
            if j == 0:
                paragraphs.append([])
                questions.append([])
                answers.append([])
#             print(data[i]['paragraphs'][j]['qas'])
            questions[-1].append(data[i]['paragraphs'][j]['qas'])
            answers[-1].append(data[i]['paragraphs'][j]['qas'])
            paragraphs[-1].append(data[i]['paragraphs'][j]['context'])
    for i in range(len(questions)):
        for j in range(len(questions[i])):
            temp = questions[i][j]
#             print(temp)
            questions[i][j] = []
            answers[i][j] = []
            for k in range(len(temp)):
                questions[i][j].append(temp[k]['question']) 
                if len(temp[k]['answers']) != 0:
                    answers[i][j].append(temp[k]['answers'][0])
                else:
                    answers[i][j].append('')
    return titles, paragraphs, questions, answers

squad_2_dev = load('dev-v2.0.json')
squad_2_train = load('train-v2.0.json')
squad_1_dev = load('dev-v1.1.json')
squad_1_train = load('train-v1.1.json')
# squad_2_dev = json.load()
# squad_2_train
# squad_1_dev
# squad_1_train
titles, paragraphs, questions, answers = parse(squad_2_train)
assert len(paragraphs) == len(questions) == len(answers)

def longest_common_substring(s1, s2):
    m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in range(1, 2):
        for y in range(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest: x_longest]

def longest_common_opener(s1, s2):
    common_string = ''
    s1_split = s1.split(" ")
    s2_split = s2.split(" ")
    for i in range(len(s1_split)):
        if s1_split[i] == s2_split[i]:
            common_string += s1_split[i]
            common_string += " "
            continue
        else:
            break
    return common_string

def longest_common_sentence(s1, s2):
    s1_words = s1.split(' ')
    s2_words = s2.split(' ')  
    return ' '.join(longest_common_substring(s1_words, s2_words))

def extract_sentences(file_path):
#     with open('textbooktony.csv', 'r') as file:
    with open(file_path, 'r') as file:
        texts = []
        causes = []
        effects = []
        cause_questions = []
        effect_questions = []
        reader = csv.reader(file)
        for row in reader:
            text = row[7]
            cause = row[8]
            effect = row[9]
            cause_question = row[10]
            effect_question = row[11]
#             text = row[4]
#             cause = row[5]
#             effect = row[6]
#             cause_question = row[7]
#             effect_question = row[8]
            texts.append(text)
            causes.append(cause)
            effects.append(effect)
            cause_questions.append(cause_question)
            effect_questions.append(effect_question)
    return texts, causes, effects, cause_questions, effect_questions

def flatten(t):
    #flattening list
    flat_list = [item for sublist in t for item in sublist]
    return flat_list

def CountFrequency(my_list): 
    # Creating an empty dictionary
    freq = {}
    for item in my_list:
        if (item in freq):
            freq[item] += 1
        else: 
            freq[item] = 1
    return freq
    for key, value in freq.items():
        print ((key, value))

def is_causal(question, causal_openers):
    return any(question.lower().startswith(opener) for opener in causal_openers)

#get indices of questions which are causal
def get_indices(paragraphs, questions, causal_openers):
    indices = copy.deepcopy(paragraphs)
    for i in range(len(paragraphs)):
        for j in range(len(paragraphs[i])):
            for k in range(len(questions[i][j])):
                if is_causal(questions[i][j][k], causal_openers):
#                     print(questions[i][j][k])
                    indices[i][j][k] = True
                else:
                    indices[i][j][k] = False
    return indices

#creating 1D lists of all the paragraphs, questions, answers and the indices of the causal questions
paragraphs = flatten(flatten(paragraphs))
questions = flatten(flatten(questions))
answers = flatten(flatten(answers))

#most common sentence openers from the squad gold dataset
common_substrings = []
for i in range(len(questions)-1):
    for j in range(i+1, len(questions)):
        common_sentence = longest_common_opener(questions[i], questions[j])
        common_substrings.append(common_sentence)

cause_counts = CountFrequency(common_substrings)
cause_frequencies = sorted(cause_counts.items(),key=operator.itemgetter(1),reverse=True)
cause_frequencies

#grouping
def classifier(frequencies):
    #binary classifier used to classify the questions as causal
    #or non-causal, if the question starts with why, or any variation
    #of what happens, or contain the token "effect" or "cause", it will
    #be classified as a causal question, otherwise non-causal.
    openers = []
    for i in range(len(frequencies)):
        openers.append(frequencies[i][0])
    cutoff = int(len(frequencies) / 3)
    most_common_openers = openers[:cutoff]
    
    #classification
    causal_openers = []
    non_causal_openers = []
    unclassified = []
    for opener in most_common_openers:
        if opener.lower().startswith('why'):
            causal_openers.append(opener)
            #if opener does not start with why 
        elif opener.lower().startswith('what happens') or \
            opener.lower().startswith('what would happen') or \
            opener.lower().startswith('what will happen') or \
            opener.lower().startswith('what happened') or \
            opener.lower().startswith('what can happen') or \
            opener.lower().startswith('what could happen') or \
            opener.lower().startswith('what led to') or \
            opener.lower().startswith('what can lead to'):
            causal_openers.append(opener)
        elif opener.lower().find('effect') != -1 or opener.lower().find('cause') != -1 or opener.lower().find('result') != -1 or opener.lower().find('purpose') != -1:
            causal_openers.append(opener)
        elif opener.lower().startswith('how') or opener.lower().startswith('what') or opener.lower().startswith('when') or opener.lower().startswith('where') or opener.lower().startswith('who'):
            non_causal_openers.append(opener)
        else:
            unclassified.append(opener)
#     for i in range(20):
#         causal_openers.append(frequencies[i][0])
    return causal_openers, non_causal_openers, unclassified

causal_openers, non_causal_openers, unclassified = classifier(cause_frequencies)

















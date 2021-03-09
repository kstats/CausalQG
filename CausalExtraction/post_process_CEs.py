# evaluating the cause/effect pairs extracted from the pipeline. 
# post-processing on the textbook and squad as well as set up a manual evaluation pipeline
# Filter out questions, figure references , etc from being included in causal extraction
import argparse
import numpy as np
import pandas as pd
import nltk
from nltk import sent_tokenize
from nltk.tokenize import word_tokenize
nltk.download('averaged_perceptron_tagger')
from nltk.tag import pos_tag
from collections import Counter
import csv
import codecs

def add_space_period(txt):
    return txt.replace('.', '. ')

def view_df(df):
    for i, row in df.iterrows():
        print(i,"-------------------------")
        print('Text:')
        print(row['Text'])
        print('Cause:')
        print(row['Cause'])
        print('Effect:')
        print(row['Effect'])

def is_question(txt):
    sents = sent_tokenize(txt)
    if len(sents) >1:
        return "?" in sents[1]
    return False

def cue_is_CC_IN(txt, cues):
    # is so is conjunction or subordinate conjunction
    sents = sent_tokenize(txt)
    first_slen = len(word_tokenize(sents[0]))
    seen_cue = False
    if len(sents) ==3:
        word_lst = word_tokenize(txt)
        tags = pos_tag(word_lst)
        for i,tup in enumerate(tags):#('So', 'CC')
            if tup[0] in cues and i>=first_slen:
                if not seen_cue and tup[1] in ['CC', 'IN'] and i>=first_slen:
                    return True
                seen_cue = True
    elif len(sents) ==2:
        word_lst = word_tokenize(txt)
        tags = pos_tag(word_lst)
        for i,tup in enumerate(tags):#('So', 'CC')
            if tup[0] in cues:
                if not seen_cue and tup[1] in ['CC', 'IN']:
                    return True
                seen_cue = True
    return False

def as_at_start_CE(txt, iscause):
    #new as pattern 145: As &C, &R
    sents = sent_tokenize(txt)
    target = ''
    if len(sents) ==3:
        target = sents[1]
    else:
        for sent in sents:
            if "As" in sent or 'as' in sent:
                target = sent 
    if "As" in word_tokenize(target) and ',' in word_tokenize(target):
        ind = target.find(',')
        cause, effect = ' '.join(word_tokenize(target[:ind])[1:]), target[ind+1:].strip() #todo
        return cause if iscause else effect
    return ''

def as_at_start(txt): 
    #returns if as at start, filter out cause that are NP
    sents = sent_tokenize(txt)
    target = ''
    if len(sents) ==3:
        target = sents[1]
    else:
        for sent in sents:
            if "As" in sent or 'as' in sent:
                target = sent 
    if "As" in word_tokenize(target) and ',' in word_tokenize(target):
        return True
    return False

def process_df(ce):
    print("original", len(ce))
    df = pd.merge(ce, patterns, left_on="PatternID", right_on="pid")
    df = df[~df['Cause'].str.contains("Figure")&~df['Effect'].str.contains("Figure")]
    print("no figure", len(df))

    df = df[df['Text'].apply(is_question) == False]
    print("no question", len(df))

    df = df[(df['pid']!=0) | (df['Text'].apply(cue_is_CC_IN, cues=['So', 'so']) == True)] #669-399
    print("process so", len(df))

    df = df[(df['pid']!=80)|(df['Text'].apply(cue_is_CC_IN, cues=['As', 'as']) == True)] #493-475
    print("process as", len(df))

    df = df[((df['pid']!=79) & (df['pid']!=78)) | (df['Text'].apply(cue_is_CC_IN, cues=['Since', 'since']) == True)] #
    print("process since", len(df))
    return df

def as_new_df(df, newpid):
    #takes in just pattern 80
    df = df[df['pid']==80]
    df = df[df['Text'].apply(as_at_start) == True] #
    df['Cause'] = df['Text'].apply(as_at_start_CE, iscause=True)
    df['Effect'] = df['Text'].apply(as_at_start_CE, iscause=False)
    df['PatternID'] = newpid
    return df[['PatternID', 'Text','Cause', 'Effect']]

def replace_as_new(ce, newpid):
    for i, row in ce.iterrows():
        if ce['pid'][i]==80 and as_at_start(ce['Text'][i]):
            ce['Cause'][i] = as_at_start_CE(ce['Text'][i], True)
            ce['Effect'][i] = as_at_start_CE(ce['Text'][i], False)
            ce['PatternID'][i] = newpid
    return ce

if __name__ == "__main__":
    patterns = pd.read_csv('patterns.csv')

    parser = argparse.ArgumentParser(description="Script to post-process CEs")
    parser.add_argument("--infile", type=str, help="path to ce input file") #'CSVs/Textbook/textbook_ce.csv' 'CSVs/SQuAD/squad_ce.csv'
    parser.add_argument("--outfile", type=str, help="path to ce output file") # "CSVs/Textbook/textbook_ce_processed.csv" "CSVs/SQuAD/squad_ce_processed.csv"
    args = parser.parse_args()
    if args.infile and args.outfile:
        ce = pd.read_csv(args.infile)
        new_pattern_id = 145
        processed_ce = process_df(ce)
        as_ce = as_new_df(processed_ce, new_pattern_id)
        print('as new pattern length', len(as_ce))
        final_ce = replace_as_new(processed_ce, new_pattern_id)
        final_ce[['PatternID', 'Text', 'Cause', 'Effect']].to_csv(args.outfile)
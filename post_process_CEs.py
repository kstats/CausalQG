# evaluating the cause/effect pairs extracted from the pipeline. 
# post-processing on the textbook and squad as well as set up a manual evaluation pipeline
# Filter out questions, figure references , etc from being included in causal extraction
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
textbook_ce = pd.read_csv('CSVs/Textbook/textbook_ce.csv')
squad_ce = pd.read_csv('CSVs/SQuAD/squad_ce.csv')
#preprocess squad data
squad_ce.rename({'Pattern_id': 'PatternID'}, axis=1, inplace=True)
new_pattern_id = 145

def add_space_period(txt):
    return txt.replace('.', '. ')

# squad_ce['Text'] = squad_ce['Text'].transform(add_space_period)
# df = pd.read_csv('squad_ce.csv')
# patterns = pd.read_csv('CE_extractor--Patterns_Based/CE_extractor/patterns.csv')
patterns = pd.read_csv('patterns.csv')
#pid join PatternID	

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

def as_at_start(txt): #(169/475)
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
    # merged 3977

    #-cause figure: 3851, -effect3724
    df = df[~df['Cause'].str.contains("Figure")&~df['Effect'].str.contains("Figure")]
    print("no figure", len(df))
    # merged[merged['maintoken'].str.contains("'so'")]
    #as: pattern 80 has 603 rows
    # merged[merged['pid']==80]

    #When question generated is the same for both cause and effect, 
    #potential indication of poor causal relation extraction
    #188 this is evaluation
    # df = df[~(df['cause_question'] == df['effect_question'])]

    #filter out questions from CE 3887 !!!!! if middle sentence has ? instead
    # df = df[~df['Cause'].str.contains("\?")&~df['Effect'].str.contains("\?")]
    df = df[df['Text'].apply(is_question) == False]
    print("no question", len(df))
    #effect and cause are the same 0
    # df[df['Cause'] == df['Effect']]
    # print(df['pid'].value_counts())
    # df['textbook_freq'] = df.groupby('pid')['pid'].transform('count')
    
    #SO pattern 0 POS filter
    df = df[(df['pid']!=0) | (df['Text'].apply(cue_is_CC_IN, cues=['So', 'so']) == True)] #669-399
    print("process so", len(df))
    #AS pattern 80 POS filter
    df = df[(df['pid']!=80)|(df['Text'].apply(cue_is_CC_IN, cues=['As', 'as']) == True)] #493-475
    print("process as", len(df))
    #Since pattern 79 78 POS filter
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

processed_tce = process_df(textbook_ce)
processed_sce = process_df(squad_ce)

as_squad_ce = as_new_df(processed_sce, new_pattern_id)
print('as new pattern in squad', len(as_squad_ce))
as_textbook_ce = as_new_df(processed_tce, new_pattern_id)
print('as new pattern in textbook', len(as_textbook_ce))


# pd.set_option('display.max_rows', None)
# new_df.to_csv("new_as_pattern_CE_textbook.csv")
# print(textbook_ce['PatternID'].max())
#------------------------
def replace_as_new(ce, newpid):
#     ce[(ce['pid']==80) &(ce['Text'].apply(as_at_start) == True)]['Cause'] = 
#     ce['Cause'] = ce['Text'].apply(as_at_start_CE, iscause=True)
#     ce['Effect'] = ce['Text'].apply(as_at_start_CE, iscause=False)
#     df['PatternID'] = newpid
    for i, row in ce.iterrows():
        if ce['pid'][i]==80 and as_at_start(ce['Text'][i]):
            ce['Cause'][i] = as_at_start_CE(ce['Text'][i], True)
            ce['Effect'][i] = as_at_start_CE(ce['Text'][i], False)
            ce['PatternID'][i] = newpid
    return ce

# print(len(as_squad_ce))
    
# print(squad_ce['PatternID'].value_counts())
# processed_sce['PatternID'].value_counts()
# as_squad_ce.to_csv("new_as_pattern_CE_squad.csv")
final_textbook = replace_as_new(processed_tce, new_pattern_id)
#final_textbook[['PatternID', 'Text', 'Cause', 'Effect']].to_csv("CSVs/Textbook/textbook_ce_processed.csv")

#view_df(final_textbook[final_textbook['PatternID']==145])
# len(final_textbook)
final_squad = replace_as_new(processed_sce, new_pattern_id)
#final_squad[['PatternID', 'Text', 'Cause', 'Effect']].to_csv("CSVs/SQuAD/squad_ce_processed.csv")
#!/usr/bin/env python
# coding: utf-8

# In[ ]:


ClauseHead = ['that', 'whether', 'if', 'what', 'whatever', 'who', 'whoever', 'whom', 'whose', 'which', 'when', 'where', 'how', 'why']
THIS = ['this', 'that', 'these', 'those', 'it', 'which']
this = ['this', 'that', 'these', 'those']
AND = ['and', 'but', 'so', 'also']
BE = ['be', 'being', 'been', 'have been', 'is', 'am', 'are', 'was', 'were']
CAN = ['can', 'could', 'may', 'might', 'will', 'would', 'must', 'should', 'ought to']
ADJ = ['direct', 'same', 'main', 'seperate', 'final', 'alone', 'important', 'major', 'key', 'biggest', 'possible', 'only', 'primary']
ADV = ['just', 'also', 'only', 'merely', 'all', 'alone', 'often', 'simply']
ONE = ['the', 'a', 'an', 'one', 'another']


# In[2]:


from nltk.tokenize import word_tokenize
def add_space_btw_tokens(s) -> str:
    return ' '.join(word_tokenize(s)) #asdf . dska


# In[24]:



def TXT2Patterns():
    causaltxt = open('causal_links.txt', "r").read()
    causal_txt_lines = causaltxt.splitlines()
    Patterns = []
    ptid = 0
    for txt in causal_txt_lines:
        ### ---- if a line is a empty string, skip it ----
        if len(txt) == 0 or re.match(r"[\s]+$", txt):
            continue
        ### ---- if a line started with '#', it is a comment line, skip it ----
        if re.match(r"#", txt):
            continue
        ### ---- get the 3-level type for each pattern ----
        ptidx = [int(i) for i in list((re.match(r'(\d+) (\d+) (\d+) (\d+) (\d+)', txt)).groups())]
        ### ---- get pattern text for each pattern ----
        ptxt = re.search(r'(?<={)(.+)(?=})', txt).group(0)
        ### ---- get example text list for each pattern ---- 
        etxt = re.findall(r'(?<=\[)([^\]]+)(?=\])', txt) #alist
        if etxt == []:
            etxt = ''
        else:
            etxt = ' '.join(word_tokenize('. '+etxt[0]))
        ### ---- create a 'pattern' type object and append it into "Patterns" list ----
#         Patterns.append(pattern(ptidx[0], ptidx[1], ptidx[2:], ptxt, etxt, ptid))
        main_token, constraints = ProcessPattern(ptxt)
        regex, causefirst = MainTokenRegExp(main_token, constraints) #return regex not regex compiled
        Patterns.append((ptxt, regex, causefirst, etxt)) #etxt is spaced
        ptid += 1
    return Patterns

def match_example_text(patterns): #takes in list of (regex, causefirst, etxt) 
    total = 0
    matched = 0 #if returns anything
    for ptxt, regex, causefirst, etxt in patterns:
        if etxt != '':
            r = re.compile(regex, re.I)
            matches = r.findall(etxt)
            print(ptxt)
            print(regex)
            print(etxt)
            print(matches)
            if matches != []:
                matched += 1
            total+=1
                
    return total, matched

def match_string(pattern, s): # takes in (ptxt, regex, causefirst, etxt) and returns list of [cause, effect] matches
    # s need to be preprocessed to have space between each token
    ptxt, regex, causefirst, etxt = pattern
    r = re.compile(regex, re.I)
    matches = r.findall(etxt)
    return matches
    
    


# In[25]:


import os
import re
import operator
p =TXT2Patterns()
match_example_text(p)


# In[8]:


def DelEmptyString(strlist):
    i = 0
    while i < len(strlist):
        if strlist[i] == None or len(strlist[i]) == 0:
            del strlist[i]
        else:
            i += 1
    return strlist

def ProcessPattern(ptxt):
    main_token = []
    constraints = []
    ### --- if ptxt == None or ptxt = "", return ---
    if not ptxt or len(ptxt.strip()) == 0:
        return main_token, constraints
    ### --- split pattern_txt into words & delete the empty words ----
    pwords = DelEmptyString(ptxt.split(' '))
    ### --- divide the words into main_tokens and constraints ---
    i = 0
    while i < len(pwords):
        temp_main = []
        temp_constraints = []
        ### ------- if current word is a constrain ----------
        while i < len(pwords):
            p = pwords[i]
            ### if current word start with '&', append it into temp constraints;
            if p[0] == '&':
                temp_constraints.append(p)
                i += 1
            ### if current word start with '(', find the whole ignore pieces, append it into temp constraints
            elif p[0] == '(':
                if p[-1] == ')':
                    temp_constraints.append(p)
                    i += 1
                else:
                    for j in range(i + 1, len(pwords)):
                        p = p + ' ' + pwords[j]
                        if pwords[j][-1] == ')':
                            temp_constraints.append(p)
                            i = j + 1
                            break
            else:
                break
        ### ------ if current word is a main_tokens --------
        while i < len(pwords):
            p = pwords[i]
            if p[0] not in ['(', '&']:
                ### ----- delete '/' ------
                if '/' in p:
                    temp_main.append(DelEmptyString(p.split('/')))
                else:
                    temp_main.append(p)
                i += 1
            else:
                break
        constraints.append(temp_constraints)
        if len(temp_main) > 0:
            main_token.append(temp_main)

    return main_token, constraints


# In[9]:


main_token, constraints = ProcessPattern('&C (,/;/./--) (&AND) for (&this) reason/reasons (,/that) &R')
#emily woke up late, and for this reason, she was late to class


# In[62]:


main_token


# In[63]:


constraints


# In[12]:


def optional_regex_from_list(tokens): #[, ; . --]
    #(?:(\s,|\s;|\s\.|\s--)?)
    #(?:(?:\s,|\s;|\s\.|\s--)?)
    r = ''
    r += r'(?:(?:'
    for i in range(len(tokens)):
        r += r'\s'  
        if tokens[i] in ['.', '?', ':']:
            r = r + '\\'
        r += tokens[i]
        if i < len(tokens)-1:
            r += r'|'
    r += r')?)'
    return r

def non_optional_regex_from_list(tokens):
    #'this|that|these|those|it|which'
    return '(?:' + '|'.join(tokens) + ')'
    
print(non_optional_regex_from_list(['and', 'or', 'so']))
print(optional_regex_from_list(['and', 'or', 'so']))


# In[22]:


import os
import nltk
import re
import operator
### 'MainTokenRegExp' intend to: create regular expression list for all patterns
### ---- in order to check whether the sentence contains a pattern's main_token ---
### ---- notice that the capture group (.*) is in accordance with Patterns constraints ----
# THIS = r'this|that|these|those|it|which'
# AND = r'and|but|so|also'
# this = r'this|that|these|those'
# clausehead = r'that|whetherif|what|whatever|who|whoever|whom|whose|which|when|where|how|why'
# BE = r'be|is|are|was|were|being|been|have been'
# MODNUM = r'at least|at most'
punc = [',',';','.','--']
clausehead = ['that', 'whether', 'if', 'what', 'whatever', 'who', 'whoever', 'whom', 'whose', 'which', 'when', 'where', 'how', 'why']
THIS = ['this', 'that', 'these', 'those', 'it', 'which']
this = ['this', 'that', 'these', 'those']
AND = ['and', 'but', 'so', 'also']
BE = ['be', 'being', 'been', 'have been', 'is', 'am', 'are', 'was', 'were']
CAN = ['can', 'could', 'may', 'might', 'will', 'would', 'must', 'should', 'ought to']
ADJ = ['direct', 'same', 'main', 'seperate', 'final', 'alone', 'important', 'major', 'key', 'biggest', 'possible', 'only', 'primary']
ADV = ['just', 'also', 'only', 'merely', 'all', 'alone', 'often', 'simply']
ONE = ['the', 'a', 'an', 'one', 'another']
MODNUM = ['at least', 'at most']



# this = [this, that, these, those]
def MainTokenRegExp(main_token, constraints):
    ### current Regular Expression for current patterns\
    ### if current pattern only have one main_token, find the first appearance of this main_token ----
    
    found = False # if one of &C or &R is found
    causefirst = False
    
    curRegExp = ''
    for pi in range(len(constraints)):
        ### ---- if current constraint pieces has a class constraint piece, add " " ----            
        for cp in constraints[pi]: #cp is string
            
            if cp[0] == '&': #TODO distinguish &C and &R
                curRegExp += r' '
                if (cp == '&C' or cp == '&R'):
                    if not found:
                        found = True
                        causefirst = (cp == '&C')
                    if (cp == '&C' and causefirst) or (cp == '&R' and not causefirst):
                        curRegExp = curRegExp + r'[.|;|!] (.*?)'
                    else:
                        curRegExp = curRegExp + r'(.*?) [.|;|!]'
                elif cp == '&THIS': 
                    curRegExp += non_optional_regex_from_list(THIS)
                elif cp == '&AND':
                    curRegExp += non_optional_regex_from_list(AND)
                elif cp == '&this':
                    curRegExp += non_optional_regex_from_list(this)
                elif cp == '&ClauseHead':
                    curRegExp += non_optional_regex_from_list(clausehead)
                elif cp == '&BE':
                    curRegExp += non_optional_regex_from_list(BE)
                elif cp == '&MODNUM':
                    curRegExp += non_optional_regex_from_list(MODNUM)
                else:
                    curRegExp += '[^\s]+'
                    
            elif cp[0] == '(' and cp[-1] == ')': #not add space before, add \s in between TODO (.*)(?:\s,|\s;|\s\.|\s--) 
                #curRegExp += r' ' #del
                if cp[1:-1].find('/') != -1:
                    tokens = cp[1:-1].split('/')
                    curRegExp += optional_regex_from_list(tokens)
                elif cp.find('&') != -1:
                    if cp[1:-1] == '&THIS': 
                        curRegExp += optional_regex_from_list(THIS)
                    elif cp[1:-1] == '&AND':
                        curRegExp += optional_regex_from_list(AND)
                    elif cp[1:-1] == '&this':
                        curRegExp += optional_regex_from_list(this)
                    elif cp[1:-1] == '&ClauseHead':
                        curRegExp += optional_regex_from_list(clausehead)
                    elif cp[1:-1] == '&BE':
                        curRegExp += optional_regex_from_list(BE)
                    elif cp[1:-1] == '&MODNUM':
                        curRegExp += optional_regex_from_list(MODNUM) 
                    else:
                        curRegExp += '[^\s]+'
                else:
                    curRegExp += optional_regex_from_list(cp[1:-1])
        ### ---- add current main_token pieces into current Regular Expression -- curRegExp ----
        curRegExp += ' '
        if pi < len(main_token):
            for ti in range(len(main_token[pi])):
                if ti > 0:
                    curRegExp += r' '
                tokens = main_token[pi][ti]
                ### if current token is a string, add it into curRegExp directly
                if type(tokens) == str:
                    if tokens in ['.', '?', ':']:
                        curRegExp += '\\'  #.encode('utf-8') !! python3 return as bytes
                    curRegExp += tokens#.encode('utf-8')
                ### if current token is a list, create a "no capture group" (?:token[0]|token[1]|...) for it
                #eg reason/reasons
                else:
                    curRegExp = curRegExp + r'(?:'
                    for tempt in range(len(tokens)):
                        if tempt > 0:
                            curRegExp = curRegExp + r'|'
                        if tokens[tempt] in ['.', '?', ':']:
                            curRegExp = curRegExp + '\\'#.encode('utf-8')
                        curRegExp = curRegExp + tokens[tempt]#.encode('utf-8')
                    curRegExp = curRegExp + r')'

    #return re.compile(curRegExp, re.I), causefirst  ###re.I means ignore upper or lower cases
    return curRegExp.strip(), causefirst

#     Dumppickle(os.path.join(DICpkdir, 'mtRegExpList.pk'), mtRegExpList)


# In[23]:


print(main_token)
print(constraints)
regex, causefirst = MainTokenRegExp(main_token, constraints)
print(regex)
print('causefirst = ', causefirst)
txt = 'ssdf . emily woke up late , and for this reason , she was late to class . sdj'
# matches = regex.findall(txt)
# print(matches)
# [.|;|!] (.*) (?:,|;|\.|--) (?:and|but|so|also) (as a [^\s]+ result) (?:,) (.*) [.|;|!]


# In[68]:


#(?:,|;|.|--)
r = '[.|;|!](.*)(?:,|;|.|--)(?:and|but|so|also) (therefore) (.*)[.|;|!]'
regex = re.compile(r)
txt = 'aaskdjfkajsdfk. emily woke up late, and therefore she woke up late. skdjhfaksdjf'
matches = regex.findall(txt)
print(matches)


# In[ ]:


#manov script
import argparse
import re
import csv
#{&C (,/;/./--) consequently (,) &R}
def parse(input_file, output_file):
    txt = ''
    with open(input_file, 'r', encoding='utf-8') as f:
        txt = ''.join(f.readlines())
    
    ptrn = re.compile("[.?!\s]?([a-zA-z][a-zA-z\s]+[.?!\s]?) ([cC]onsequently), ([a-zA-z\s]+[.?!])")
    matches = ptrn.findall(txt)

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Cause", "Connector", "Effect"])
        writer.writerows([[matches[0], matches[1], matches[2]] for matches in matches])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parsing arguments')
    parser.add_argument('--input', type=str, help='The path to the input file         or directory')
    parser.add_argument('--output', type=str, help='The path to the output file         or directory')
    
    args = parser.parse_args()
    
    parse(args.input, args.output)


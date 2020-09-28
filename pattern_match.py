ClauseHead = ['that', 'whether', 'if', 'what', 'whatever', 'who', 'whoever', 'whom', 'whose', 'which', 'when', 'where', 'how', 'why']
THIS = ['this', 'that', 'these', 'those', 'it', 'which']
this = ['this', 'that', 'these', 'those']
AND = ['and', 'but', 'so', 'also']
BE = ['be', 'being', 'been', 'have been', 'is', 'am', 'are', 'was', 'were']
CAN = ['can', 'could', 'may', 'might', 'will', 'would', 'must', 'should', 'ought to']
ADJ = ['direct', 'same', 'main', 'seperate', 'final', 'alone', 'important', 'major', 'key', 'biggest', 'possible', 'only', 'primary']
ADV = ['just', 'also', 'only', 'merely', 'all', 'alone', 'often', 'simply']
ONE = ['the', 'a', 'an', 'one', 'another']

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
        etxt = re.findall(r'(?<=\[)([^\]]+)(?=\])', txt)
        ### ---- create a 'pattern' type object and append it into "Patterns" list ----
#         Patterns.append(pattern(ptidx[0], ptidx[1], ptidx[2:], ptxt, etxt, ptid))
        main_token, constraints = ProcessPattern(ptxt)
        regex, causefirst = MainTokenRegExp(main_token, constraints) #return regex not regex compiled
        Patterns.append((regex, causefirst))
        ptid += 1
    return Patterns

import os
import re
import operator
TXT2Patterns()

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

main_token, constraints = ProcessPattern('&C (,/;/./--) (&AND) for (&this) reason/reasons (,/that) &R')
#emily woke up late, and for this reason, she was late to class

import os
import nltk
import re
import operator
### 'MainTokenRegExp' intend to: create regular expression list for all patterns
### ---- in order to check whether the sentence contains a pattern's main_token ---
### ---- notice that the capture group (.*) is in accordance with Patterns constraints ----
THIS = r'this|that|these|those|it|which'
AND = r'and|but|so|also'
this = r'this|that|these|those'
clausehead = r'that|whetherif|what|whatever|who|whoever|whom|whose|which|when|where|how|why'
BE = r'be|is|are|was|were|being|been|have been'
MODNUM = r'at least|at most'
punc = [',',';','.','--']

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
            curRegExp += r' '
            if cp[0] == '&': #TODO distinguish &C and &R
                if (cp == '&C' or cp == '&R'):
                    if not found:
                        found = True
                        causefirst = (cp == '&C')
                    if (cp == '&C' and causefirst) or (cp == '&R' and not causefirst):
                        curRegExp = curRegExp + r'[.|;|!] (.*)'
                    else:
                        curRegExp = curRegExp + r'(.*) [.|;|!]'
                elif cp == '&THIS': 
                    curRegExp += r'(?:'+ THIS + r')'
                elif cp == '&AND':
                    curRegExp += r'(?:'+ AND + r')'
                elif cp == '&this':
                    curRegExp += r'(?:'+ this + r')'
                elif cp == '&ClauseHead':
                    curRegExp += r'(?:'+ clausehead + r')'
                elif cp == '&BE':
                    curRegExp += r'(?:'+ BE + r')'
                elif cp == '&MODNUM':
                    curRegExp += r'(?:'+ MODNUM + r')'  
                else:
                    curRegExp += '[^\s]+'
            elif cp[0] == '(' and cp[-1] == ')':
                if cp[1:-1].find('/') != -1:
                    tokens = cp[1:-1].split('/')
                    curRegExp = curRegExp + r'(?:'
                    for tempt in range(len(tokens)):
                        if tempt > 0:
                            curRegExp = curRegExp + r'|'
                        if tokens[tempt] in ['.', '?', ':']:
                            curRegExp = curRegExp + '\\' #.encode('utf-8')
                        curRegExp = curRegExp + tokens[tempt]#.encode('utf-8')
                    curRegExp = curRegExp + r')'
                elif cp.find('&') != -1:
                    if cp[1:-1] == '&THIS': 
                        curRegExp += r'(?:'+ THIS + r')'
                    elif cp[1:-1] == '&AND':
                        curRegExp += r'(?:'+ AND + r')'
                    elif cp[1:-1] == '&this':
                        curRegExp += r'(?:'+ this + r')'
                    elif cp[1:-1] == '&ClauseHead':
                        curRegExp += r'(?:'+ clausehead + r')'
                    elif cp[1:-1] == '&BE':
                        curRegExp += r'(?:'+ BE + r')'
                    elif cp[1:-1] == '&MODNUM':
                        curRegExp += r'(?:'+ MODNUM + r')'  
                    else:
                        curRegExp += '[^\s]+'
                else:
                    curRegExp += '(?:' + cp[1:-1] + ')'

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
    return curRegExp, causefirst

#     Dumppickle(os.path.join(DICpkdir, 'mtRegExpList.pk'), mtRegExpList)

print(main_token)
print(constraints)
regex, causefirst = MainTokenRegExp(main_token, constraints)
print(regex)
print('causefirst = ', causefirst)
txt = 'ssdf . emily woke up late , and for this reason , she was late to class . sdj'
matches = regex.findall(txt)
print(matches)
# [.|;|!] (.*) (?:,|;|\.|--) (?:and|but|so|also) (as a [^\s]+ result) (?:,) (.*) [.|;|!]


#(?:,|;|.|--)
r = '[.|;|!](.*)(?:,|;|.|--)(?:and|but|so|also) (therefore) (.*)[.|;|!]'
regex = re.compile(r)
txt = 'aaskdjfkajsdfk. emily woke up late, and therefore she woke up late. skdjhfaksdjf'
matches = regex.findall(txt)
print(matches)




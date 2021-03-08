# -*- coding: UTF-8 -*-
# -- This file defines all Classes --
from cmyToolkit import *

#######################################################################################
# ------------------------------ cmy Paper related Classes -------------------------- #
#######################################################################################
# -------- paper file class --------
class Paper:
    def __init__(self, ID):
        self.Ftag = ID
        self.Ftitle = None
        self.author = None
        self.auinfo = []
        self.c_num = 0
        self.p_num = 0
        self.s_num = 0
        self.C_list = []
        self.P_list = []
        self.S_list = []
        self.Abstract = []  # abstract is a sent list
        self.KeyW = []  # keyword is a str list
        self.Refer = []  # refer is a refer str list


class Paper1:
    def __init__(self, ID):
        self.Ftag = ID
        self.Ftitle = None
        self.author = None
        self.auinfo = []
        self.c_num = 0
        self.p_num = 0
        self.s_num = 0
        self.C_list = []
        self.P_list = []
        self.S_list = []
        self.man_CE_list = []  # a list: stores manual labeled cause-effect links
        self.mance_sent_id_dict = {}  # a dict: map a sentence id to a manual labeled ce link id
        self.sys_CE_list = []  # a list: stores pattern matched cause-effect links
        self.sysce_sent_id_dict = {}  # a dict: map a sentence id to a pattern matched ce link id
        self.Abstract = []  # abstract is a sent list
        self.KeyW = []  # keyword is a str list
        self.Refer = []  # refer is a refer list


# ------------- Section class ---------------
class Sec:
    def __init__(self, ID, title):
        self.Ctag = ID
        self.Ctitle = title
        self.sc_num = 0
        self.sclist = []
        self.p_num = 0
        self.plist = []


# ---------- Sub-section class ------------
class SubSec:
    def __init__(self, CID, SCID, title):
        self.Ctag = CID
        self.SCtag = SCID
        self.SCtitle = title
        self.p_num = 0
        self.plist = []


# ---------- Paragraph class ----------
class Parag:
    def __init__(self, c, sc, p, num, slist):
        self.Ctag = c
        self.SCtag = sc
        self.Ptag = p
        self.sent_num = num
        self.slist = slist


# ---------- Sentence class ----------
class Sent:
    def __init__(self, c, sc, p, s, t):
        self.Ctag = c
        self.SCtag = sc
        self.Ptag = p
        self.Stag = s
        self.text = t
        self.PTree = []


# ---------- Sentence class ----------
class Sent1:
    def __init__(self, c, sc, p, s, t):
        self.Ctag = c
        self.SCtag = sc
        self.Ptag = p
        self.Stag = s
        self.text = t
        self.manCEidlst = []
        self.sysCEidlst = []


# ------ Reference class --------
class Refer:
    def __init__(self, r, t):
        self.Rtag = r
        self.text = t

#######################################################################################
# --------------------------- cmy Cause-Effect related Classes ---------------------- #
#######################################################################################
### ---- 'Cause&Effect links pattern' class ----
class pattern:
    # --- tlist contains the name of all pattern types. It has 3 levels.
    # --- use [self.tlist[0][tnum[0]-1],self.tlist[1][tnum[0]-1][tnum[1]-1],self.tlist[2][tnum[0]-1][tnum[1]-1][tnum[2]-1]] to visit
    tlist = ([
        ['ADVERBIAL', 'PREPOSITIONAL', 'SUBORDINATION', 'CLAUSE-INTEGRATION'],
        [['Anaphoric', 'Cataphoric'], ['Adverbial', 'Postmodifying'],
         ['Subordinator', 'Non-finite ing-clause', 'Correlative comparative'], ['Rhematic link', 'Thematic link']],
        [[['Implicit', 'Pronominal', 'Pronominal+Lexical'], ['']],
         [[''], ['']],
         [[''], [''], ['']],
         [['Clause-internal', 'Anaphoric pronominal subject', 'Anaphoric nominal subject', 'Non-anaphoric subject',
           'Cleft constructions', 'Retrospective reinforcement', 'Mediating', 'Prospective:thematic first member',
           'Prospective:rhematic first member'], ['Anaphoric', 'Mediating']]
         ],
    ])

    # --- ProcessPattern function using to parse the pattern_text into pattern_main_token and pattern_main_constraints
    def ProcessPattern(self, ptxt):
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

    ### ---- 'pattern' object initiation function ----
    ### ---- each 'pattern' object has 6 members:
    ### -------- pfreq: a int number, storing the frequency of a pattern
    ### -------- moresent: moresent = 1 means pattern can deal with more than one sentence, otherwise moresent = 0
    ### -------- ptype: a 1D list witch containing 3 number, storing the 3-level type for each pattern
    ### -------- main_token: a at most 3D list, storing the main tokens for each pattern
    ### -------- constraints: a 2D list, storing the constian tokens for each pattern
    ### -------- cases: a 1D list, storing the example strings for each pattern
    def __init__(self, frequence, moresent, ptidx, ptxt, etxt, ptid):
        self.pfreq = frequence
        self.moresent = moresent
        self.ptype = ptidx
        (self.main_token, self.constraints) = self.ProcessPattern(ptxt)
        self.cases = etxt
        self.id = ptid

    ### ---- 'pattern' object equal justify function ----
    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                (self.pfreq, self.ptype, self.main_token, self.constraints) == (
                    other.pfreq, other.ptype, other.main_token, other.constraints))

    ### ---- 'pattern' object self < other justify function ----
    def __lt__(self, other):
        self_mtlen = 0
        other_mtlen = 0
        self_cnslst = ListFlatten(self.constraints)
        other_cnslst = ListFlatten(other.constraints)
        self_cnslen = 0
        other_cnslen = 0

        for mt in self.main_token:
            self_mtlen += len(mt)
        for mt in other.main_token:
            other_mtlen += len(mt)
        for cns in self_cnslst:
            if cns[0] != '(':
                self_cnslen += 1
        for cns in other_cnslst:
            if cns[0] != '(':
                other_cnslen += 1

        if not isinstance(other, pattern):
            raise TypeError('Both the Comparing objects should be a object of pattern!')
        if self_mtlen != other_mtlen:
            return self_mtlen < other_mtlen
        elif len(self.main_token) != len(other.main_token):
            return len(self.main_token) < len(other.main_token)
        elif self_cnslen != other_cnslen:
            return self_cnslen < other_cnslen
        else:
            return self.pfreq < other.pfreq

    __ne__ = lambda self, other: not self == other
    __gt__ = lambda self, other: not (self < other or self == other)
    __le__ = lambda self, other: self < other or self == other
    __ge__ = lambda self, other: not self < other


### ---- 'Cause or Effect' class ----
class CorE:
    def __init__(self, parserTree, leaveSpan):
        self.PTree = parserTree
        self.span = leaveSpan

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                (self.span, self.PTree) == (other.span, other.PTree))


### ---- 'Cause&Effect link' class ----
class CELink:
    def __init__(self, pt, parserTree, cause, effect):
        self.pt = pt
        self.PTreelst = parserTree
        self.cause = cause
        self.effect = effect
        self.sInfo = []  # the Sent_class(see cmyPreprocess.py) object list constructing this CElink;

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                (self.PTreelst, self.pt, self.cause, self.effect) == (
                    other.PTreelst, other.pt, other.cause, other.effect))


### ---- pattern matched 'Cause&Effect link' class ----
class CELink1:
    def __init__(self, sysid, pt):
        self.sysCEid = sysid
        self.pt = pt
        self.cw_span = []
        self.ew_span = []
        self.Staglst = []  # the Sent1.Stag list, which construct this cause-effect link


### ---- manual labeled 'Cause&Effect link' class ----
class CELink2:
    def __init__(self, manid, maintoken):
        self.manCEid = manid
        self.main_token = maintoken
        self.cw_span = []
        self.ew_span = []
        self.Staglst = []  # the Sent1.Stag list, which construct this cause-effect link


#######################################################################################
# ------------------- cmy Common Words Comparing related Classes -------------------- #
#######################################################################################

class FText:
    def __init__(self, ftag, abs_text, conc_text, ce_text):
        self.Ftag = ftag
        self.AbsText = abs_text  # store the text in Abstract section
        self.ConcText = conc_text  # store the text in Conclusion section
        self.CEText = ce_text  # store the sentences' text which contains cause-effect link
        self.CE_A_Text = []   # store the cause texts for each cause-effect links.
        self.CE_B_Text = []   # store the effect texts for each cause-effect links.
        #  The corresponding between cause texts and effect texts lies in their location in the list.


class FWordDic:
    def __init__(self, ftag, absworddic, concworddic, acworddic, ceworddic):
        self.Ftag = ftag
        self.AbsWordDic = absworddic  # dic object, key is words in Abstract, and value is the occurrence frequency of the word.
        self.ConcWordDic = concworddic  # dic object, key is words in Conclusion, and value is the occurrence frequency of the word.
        self.A_CWordDic = acworddic  # dic object, merge words and their occurrence frequency in AbsWordDic and ConcWordDic.
        self.CEWordDic = ceworddic  # dic object, key is words in cause-effect sentences, and value is the occurrence frequency.


class CoWords:
    def __init__(self, FWDic, OnAbs, Abs2CE, OnConc, Conc2CE, OnAC, AC2CE, wAbs, wConc, wAC, comwonabs, comwonconc,
                 comwonac):
        self.FWDic = FWDic  # The FWordDic object for the paper.
        self.OnAbs = OnAbs  # The common words occurrence frequency in Abstract section
        self.OnConc = OnConc  # The common words occurrence frequency in Conclusion section
        self.OnAC = OnAC  # The common words occurrence frequency in both Abstract and Conclusion section
        self.Abs2CE = Abs2CE  # The occurrence frequency in CElinks of common words with Abstract
        self.Conc2CE = Conc2CE  # The occurrence frequency in CElinks of common words with Conclusion
        self.AC2CE = AC2CE  # The occurrence frequency in CElinks of common words with both Abstract and Conclusion
        self.WAbs = wAbs  # The percentage of common words on Abstract, i.e. how many words in Abstract are common words
        self.WConc = wConc  # The percentage of common words on Conclusion, i.e. how many words in Conclusion are common words
        self.WAC = wAC  # The percentage of common words on both Abstract and Conclusion
        self.ComWOnAbs = comwonabs  # The common words list with Abstract
        self.ComWOnConc = comwonconc  # The common words list with Conclusion
        self.ComWOnAC = comwonac  # The common words list with both Abstract and Conclusion

#######################################################################################
# ---------------------------- KG Further Test Related Classes ---------------------- #
#######################################################################################
class CEonSec:
    def __init__(self, cid, ctitle):
        self.Ctag = cid
        self.Ctitle = ctitle
        self.Slist = []
        self.CElist = []
        self.CEsent = []


class ManCESec:
    def __init__(self, ftag):
        self.Ftag = ftag
        self.CESeclst = []


class PaperTest:
    def __init__(self, paperinfo):
        self.Paperinfo = paperinfo   # store the Paper object
        self.CESeclst = []   # store the CEonSec object list
        self.ftext = None   # store the FText object
        self.CE_AC_WDic = None  # store the FWordDic object list
        self.CE_AC_CoWord = None  # store the CoWords object list

#######################################################################################
# -------------------------- WORDS & POS_TAG & Frequency ---------------------------- #
#######################################################################################
class WPF:
    def __init__(self):
        self.W_Pdic = {}  # key为words，value为该words对应的pos-tag组成的list对象
        self.W_Fdic = {}  # key为words,value为该words在一篇文章中出现的词频
        self.WP_Fdic = {}  # key为(words,pos-tag)构成的tuple, value是一篇文章中该words取该postag时的词频

#######################################################################################
# -------------------------- Patterns usage in some files --------------------------- #
#######################################################################################
class PtsCount:
    def __init__(self, CEpklst, ptscount):
        self.CEpkLst = CEpklst  # store the pickle file-paths of several documents' CELink list
        self.PtsNums = ptscount  # a list store each patterns usage times in CEpklst.
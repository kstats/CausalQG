import codecs
import csv
import json
import re
import os
import nltk
import operator
import spacy
from nltk.parse import stanford
from nltk.tree import *
from nltk.corpus import wordnet as wn
from tqdm import tqdm

from cmyPatternMatching import *

f1 = codecs.open("squad_parse_errors.txt", "w", encoding="utf-8")
mem_errors, encoding_errors, count = 0, 0, 0


def ptree(sent):
    global mem_errors, f1
    try:
        return parser.raw_parse(sent)
    except:
        mem_errors += 1
        f1.write("M: ")
        f1.write(sent)
        f1.write("\n")
        return [emptyTree]


def clean_text(text):
    return (
        text.replace(" ,", ",")
        .replace(" .", ".")
        .replace(" !", "!")
        .replace(" ?", "?")
        .replace(" :", ":")
        .replace(" ;", ";")
        .replace(" %", "%")
        .replace("`` ", '"')
        .replace(" ''", '"')
        .replace("-LRB-", "(")
        .replace("-RRB-", ")")
        .replace("( ", "(")
        .replace(" )", ")")
        .replace("can not", "cannot")
        .replace(" o ", "o ")
        .replace(" x,", "x,")
        .replace(" -", "-")
        .replace("- ", "-")
        .replace("+ ", "+")
        .replace(" +", "+")
        .replace(" >", ">")
        .replace("> ", ">")
        .replace("  ", " ")
    )


nlp = spacy.load("en_core_web_sm")

Patterns = TXT2Patterns()
Patterns = OrderPatterns(Patterns, True)
mtRegExplst = MainTokenRegExp(Patterns)
emptyTree = Tree("ROOT", [])

with codecs.open("squad_ce.csv", "w", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["PatternID", "Text", "Cause", "Effect"])
    with codecs.open("dev-v2.0.json", "r", encoding="utf-8") as f:
        data = json.load(f)["data"]
        total = sum([len(article["paragraphs"]) for article in data])
        with tqdm(total=total) as pbar:
            for article in data:
                paras = article["paragraphs"]
                for para in paras:
                    text = para["context"]
                    sentences = [i.text for i in nlp(text).sents]
                    tlen = len(sentences)
                    for ti in tqdm(range(len(sentences))):
                        count += 1
                        prev_sent = "" if ti < 1 else sentences[ti - 1]
                        next_sent = "" if ti > tlen - 2 else sentences[ti + 1]
                        sent = sentences[ti]
                        pppt = ptree(sent)
                        if pppt == []:
                            continue
                        curPT = pppt[0]
                        prePT = (
                            emptyTree
                            if ti < 1 or ptree(sentences[ti - 1]) == []
                            else ptree(sentences[ti - 1])[0]
                        )
                        nextPT = (
                            emptyTree
                            if ti > tlen - 2 or ptree(sentences[ti + 1]) == []
                            else ptree(sentences[ti + 1])[0]
                        )
                        sentCEset = GettingCEcases(
                            Patterns, mtRegExplst, prePT, curPT, nextPT
                        )
                        if sentCEset == []:
                            continue
                        for ce in sentCEset:
                            try:
                                context = (
                                    clean_text(" ".join(prePT.leaves()))
                                    + " "
                                    + clean_text(" ".join(curPT.leaves()))
                                    + " "
                                    + clean_text(" ".join(nextPT.leaves()))
                                )
                                cause = clean_text(
                                    u" ".join(ce.cause.PTree.leaves())
                                ).strip(".,!?'\"-'` ")
                                effect = clean_text(
                                    u" ".join(ce.effect.PTree.leaves())
                                ).strip(".,!?'\"-'` ")
                                writer.writerow([ce.pt.id, context, cause, effect])
                            except:
                                encoding_errors += 1
                                f1.write("E: ")
                                f1.write(sent)
                                f1.write("\n")
                    pbar.update(1)

print(mem_errors, encoding_errors, count)
f1.write("{}, {}, {}".format(mem_errors, encoding_errors, count))
f1.close()

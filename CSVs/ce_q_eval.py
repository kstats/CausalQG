"""Heavily inspired by the official SQuAD evaluation script"""

import argparse
from collections import Counter, defaultdict
import re
import string
import os

import numpy as np
import pandas as pd

def normalize_answer(s):
    """Lower text and remove punctuation, articles and extra whitespace."""

    def remove_articles(text):
        regex = re.compile(r"\b(a|an|the)\b", re.UNICODE)
        return re.sub(regex, " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def compute_recall(phrase, question):
    phrase_toks = normalize_answer(phrase).split()
    question_toks = normalize_answer(question).split()
    common = Counter(phrase_toks) & Counter(question_toks)
    num_same = sum(common.values())
    if len(phrase_toks) == 0 or len(question_toks) == 0:
        return int(phrase_toks == question_toks)
    if num_same == 0:
        return 0
    return num_same / len(phrase_toks)


def ce_recall_eval(inputfile):
    df = pd.read_csv(inputfile)
    patterns = pd.read_csv("patterns.csv")
    cause_recalls, effect_recalls = [], []
    cause_recalls_typology, effect_recalls_typology, typology_counts = (
        defaultdict(lambda: 0),
        defaultdict(lambda: 0),
        defaultdict(lambda: 0),
    )
    for i, row in df.iterrows():
        cause_recall = compute_recall(row["Cause"], row["effect_question"])
        effect_recall = compute_recall(row["Effect"], row["cause_question"])
        cause_recalls.append(cause_recall)
        effect_recalls.append(effect_recall)
        pattern = patterns.loc[patterns["pid"] == row["PatternID"]].iloc[0]
        cause_recalls_typology[
            (pattern["table"], pattern["line"], pattern["col"])
        ] += cause_recall
        effect_recalls_typology[
            (pattern["table"], pattern["line"], pattern["col"])
        ] += effect_recall
        typology_counts[(pattern["table"], pattern["line"], pattern["col"])] += 1

    for key in sorted(typology_counts.keys()):
        print(f"{key}: {typology_counts[key]}")
        print(f"Recall: {(cause_recalls_typology[key] + effect_recalls_typology[key]) / 2 / typology_counts[key]}")
        print("=" * 50)
    
    for i in range(1, 5):
        count = np.sum([typology_counts[key] for key in typology_counts if key[0] == i])
        total = np.sum([
                    (cause_recalls_typology[key] + effect_recalls_typology[key]) / 2 
                    for key in typology_counts 
                    if key[0] == i
                ])
        print(f"Typology Category {i}: {count}")
        print(f"Average Recall: {total/count}")



    df["cause_recalls"] = cause_recalls
    df["effect_recalls"] = effect_recalls
    df.to_csv(inputfile)


def qa_typology(inputfile):
    qa = pd.read_csv(inputfile)

    df = None
    if os.path.split(inputfile)[0] == "SQuAD":
        df = pd.read_csv("SQuAD/squad_ce_processed.csv")
    elif os.path.split(inputfile)[0] == "Textbook":
        df = pd.read_csv("Textbook/textbook_ce_processed.csv")
    else:
        print("Unsupported Directory!")
        return
    
    predicted_cause_score, predicted_effect_score = [], []
    for i, row in qa.iterrows():
        if i % 2 == 0:
            predicted_cause_score.append(row["score"])
        else:
            predicted_effect_score.append(row["score"])
    
    df["cause_score"], df["effect_score"] = predicted_cause_score, predicted_effect_score
    patterns = pd.read_csv("patterns.csv")

    scores, counts = defaultdict(lambda: 0), defaultdict(lambda: 0)
    for i, row in df.iterrows():
        pattern = patterns.loc[patterns["pid"] == row["PatternID"]].iloc[0]
        scores[(pattern["table"], pattern["line"], pattern["col"])] += row["cause_score"] + row["effect_score"]
        counts[(pattern["table"], pattern["line"], pattern["col"])] += 2

    print("=" * 50)
    for key in sorted(counts.keys()):
        print(f"# of Pattern {key}: {counts[key]}")
        print(f"Average Score: {scores[key] / counts[key]}")
        print("=" * 50)
    
    for i in range(1, 5):
        count = np.sum([counts[key] for key in counts if key[0] == i])
        total = np.sum([
                    scores[key] 
                    for key in scores 
                    if key[0] == i
                ])
        print(f"Typology Category {i}: {count}")
        print(f"Average F1: {total/count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parsing arguments")
    parser.add_argument("--input", type=str, help="path to data")
    parser.add_argument("--ce_recall", action="store_true", help="calculate cause/effect recall")
    parser.add_argument("--qa_typology", action="store_true", help="analyze QA scores for questions broken down by typology")
    args = parser.parse_args()

    if not args.input:
        print("Must specify input file")
        exit(-1)
    if args.ce_recall:
        ce_recall_eval(args.input)
    if args.qa_typology:
        qa_typology(args.input)

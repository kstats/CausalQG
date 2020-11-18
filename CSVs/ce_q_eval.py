"""Heavily inspired by the official SQuAD evaluation script"""

import argparse
from collections import Counter, defaultdict
import re
import string

import pandas as pd
from latextable import *

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


def main(inputfile):
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

    typology_table = [["Pattern", "Count", "Average Cause Recall", "Average Effect Recall"]]
    for key in typology_counts:
        print(f"{key}: {typology_counts[key]}")
        print(f"Cause: {cause_recalls_typology[key] / typology_counts[key]}")
        print(f"Effect: {effect_recalls_typology[key] / typology_counts[key]}")
        print("=" * 50)
        typology_table.append([key, typology_counts[key], cause_recalls_typology[key] / typology_counts[key], effect_recalls_typology[key] / typology_counts[key]])
    
    table = Texttable()
    table.add_rows(typology_table)
    print(table.draw() + "\n")
    print(draw_latex(table, caption="An example table.") + "\n")


    df["cause_recalls"] = cause_recalls
    df["effect_recalls"] = effect_recalls
    df.to_csv(inputfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parsing arguments")
    parser.add_argument("--input", type=str, help="path to data")
    args = parser.parse_args()
    if args.input:
        main(args.input)

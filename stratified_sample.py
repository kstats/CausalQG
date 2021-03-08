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
import matplotlib.pyplot as plt


#takes in ce from in_filename, and outputs in out_filename n stratified samples based on typology. 
def sample_ce(in_filename, n, out_filename):
    #textbook_ce is not nessesarily textbook ce, can be any ce provided by in_filename
    textbook_ce = pd.read_csv(in_filename)
    textbook_ce = textbook_ce[['PatternID', 'Text','Cause', 'Effect']]
    textbook_ce = pd.merge(textbook_ce, patterns, left_on="PatternID", right_on="pid")
    textbook_ce.groupby(['table', 'line', 'col']).size()

    #ensure there is min(size(category), 2) sample from each category
    textbook_small_sample_init = textbook_ce.groupby(['table', 'line', 'col']).apply(lambda x: x.sample(min(len(x), 2)))

    textbook_ce_rest = pd.concat([textbook_ce, textbook_small_sample_init, textbook_small_sample_init]).drop_duplicates(keep=False)

    textbook_small_sample = textbook_ce_rest.groupby(['table', 'line', 'col']).apply(lambda x: x.sample(int(np.rint((n-len(textbook_small_sample_init))*len(x)/len(textbook_ce_rest))))).sample(frac=1)

    textbook_small_sample = textbook_small_sample.append(textbook_small_sample_init, ignore_index=False)

    textbook_small_sample = textbook_small_sample.sample(frac=1)[['Text','Cause', 'Effect']]
    textbook_small_sample = textbook_small_sample.reset_index(level='line', drop=True)
    textbook_small_sample = textbook_small_sample.reset_index(level='col', drop=True)
    textbook_small_sample = textbook_small_sample.reset_index(level='table')

    textbook_small_sample.to_csv(out_filename, index=False)

if __name__ == "__main__":
    patterns = pd.read_csv('CSVs/patterns_typology.csv')

    parser = argparse.ArgumentParser(description="Script to generate n stratified samples based on typology")
    parser.add_argument("--infile", type=str, help="path to ce input file")
    parser.add_argument("--outfile", type=str, help="path to ce output file")
    parser.add_argument("--n", type=str, help="number of samples")
    args = parser.parse_args()
    if args.infile and args.outfile and args.n:
        sample_ce(args.infile, int(args.n), args.outfile)
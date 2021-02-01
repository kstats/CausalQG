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



def sample_ce(in_filename, n, out_filename):
    #!! textbook_ce is not nessesarily textbook_ce, can be any ce provided by in_filename
    textbook_ce = pd.read_csv(in_filename)
    textbook_ce = textbook_ce[['PatternID', 'Text','Cause', 'Effect']]
    textbook_ce = pd.merge(textbook_ce, patterns, left_on="PatternID", right_on="pid")
    textbook_ce.groupby(['table', 'line', 'col']).size()
    # textbook_ce['PatternID'].value_counts().plot(kind='bar')
    # plt.show()

    def stratified_sample_df(df, cols, n_samples):
        n = min(n_samples, df[cols].value_counts().min())
        df_ = df.groupby(cols).apply(lambda x: x.sample(n))
        df_.index = df_.index.droplevel(0)
        return df_

    # small_sample = stratified_sample_df(textbook_ce, ['table', 'line', 'col'], 100)
    # small_sample

    # textbook_small_sample = textbook_ce.groupby(['table', 'line', 'col']).apply(lambda x: x.sample(min(len(x), 100)))
    # n = textbook_ce.shape[0]
    # textbook_small_sample = textbook_ce.groupby(['table', 'line', 'col']).apply(lambda x: x.sample(frac=len(x)/n))
    # textbook_small_sample = textbook_ce.sample(n=100, weights=[['table', 'line', 'col']])

    textbook_small_sample_init = textbook_ce.groupby(['table', 'line', 'col']).apply(lambda x: x.sample(min(len(x), 2)))
    print(textbook_small_sample_init.groupby(['table', 'line', 'col']).size())

    # textbook_ce_rest = textbook_ce[~textbook_ce.isin(textbook_small_sample_init)].dropna()
    textbook_ce_rest = pd.concat([textbook_ce, textbook_small_sample_init, textbook_small_sample_init]).drop_duplicates(keep=False)

    textbook_small_sample = textbook_ce_rest.groupby(['table', 'line', 'col']).apply(lambda x: x.sample(int(np.rint((n-len(textbook_small_sample_init))*len(x)/len(textbook_ce_rest))))).sample(frac=1)

    textbook_small_sample = textbook_small_sample.append(textbook_small_sample_init, ignore_index=False)

    print(textbook_ce.groupby(['table', 'line', 'col']).size())
    print(textbook_small_sample.groupby(['table', 'line', 'col']).size())

    textbook_small_sample = textbook_small_sample.sample(frac=1)[['Text','Cause', 'Effect']]
    # textbook_small_sample = textbook_small_sample.reset_index(level='table', drop=True)
    textbook_small_sample = textbook_small_sample.reset_index(level='line', drop=True)
    textbook_small_sample = textbook_small_sample.reset_index(level='col', drop=True)
    textbook_small_sample = textbook_small_sample.reset_index(level='table')
    print(len(textbook_small_sample))

    # manav_tce=textbook_small_sample.iloc[0:50]
    # katie_tce=textbook_small_sample.iloc[25:75]
    # emily_tce=textbook_small_sample.iloc[50:100]
    # tony_tce=textbook_small_sample.iloc[pd.np.r_[0:25, 75:100]]

    # manav_tce.to_csv("CausalQG/CSVs/annotations/manov_tce.csv")
    # katie_tce.to_csv("CausalQG/CSVs/annotations/katie_tce.csv")
    # emily_tce.to_csv("CausalQG/CSVs/annotations/emily_tce.csv")
    # tony_tce.to_csv("CausalQG/CSVs/annotations/tony_tce.csv")
    textbook_small_sample.to_csv(out_filename, index=False)

if __name__ == "__main__":
    patterns = pd.read_csv('patterns.csv')
    #textbook_in = 'CSVs/Textbook/textbook_ce_processed.csv'
    #textbook_out = "CSVs/Textbook/tce_stratified_sample.csv"
#     sample_ce(textbook_ib, 500, textbook_out)
    #squad_in'CSVs/SQuAD/squad_ce_processed.csv'
    #squad_out"CSVs/SQuAD/sce_stratified_sample.csv"
    ### TEST
    # s1 = pd.read_csv('CSVs/SQuAD/sce_synqg.csv')
    # s2 = pd.read_csv('CSVs/SQuAD/sce_synqg_2.csv')
    # s3 = pd.read_csv('CSVs/SQuAD/sce_synqg_3.csv')
    # print(s1.groupby(["Table"]).size())
    # print(s2.groupby(["Table"]).size())
    # print(s3.groupby(["Table"]).size())
    # t1 = pd.read_csv('CSVs/Textbook/tce_synqg.csv')
    # print(t1.groupby(["Table"]).size())
import pandas as pd
import argparse

def clean(inputfile):
    def fix(text):
        return (
            text.replace(" ,", ",")
            .replace(" .", ".")
            .replace(" !", "!")
            .replace(" ?", "?")
            .replace(" :", ":")
            .replace(" ;", ";")
            .replace(" %", "%")
            .replace("`` ", "\"")
            .replace(" \'\'", "\"")
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


    df = pd.read_csv(inputfile)

    contexts, causes, effects = [], [], []
    for i, row in df.iterrows():
        contexts.append(fix(row["Text"]))
        causes.append(fix(row["Cause"]).strip(".,!?\'\"-'` "))
        effects.append(fix(row["Effect"]).strip(".,!?\'\"-'` "))

    df["Text"], df["Cause"], df["Effect"] = contexts, causes, effects
    df.to_csv(inputfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to clean the datasets to ensure consistency between parsed causes/effects and original text. If there are issues finding exact answer spans, use this script to clean the dataset.")
    parser.add_argument("--input", type=str, help="path to data")
    args = parser.parse_args()
    if args.input:
        clean(args.input)
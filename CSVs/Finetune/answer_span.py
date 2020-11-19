import pandas as pd
import argparse


def format(inputfile):
    df = pd.read_csv(inputfile)
    start_idx, end_idx = [], []
    for i, row in df.iterrows():
        text, answer = row["context"], row["answer"]

        answer_start = text.find(answer)
        start_idx.append(answer_start)
        end_idx.append(answer_start + len(answer) - 1)

    df["start_idx"] = start_idx
    df["end_idx"] = end_idx
    df.to_csv(inputfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parsing arguments")
    parser.add_argument("--input", type=str, help="path to data")
    args = parser.parse_args()
    if args.input:
        format(args.input)

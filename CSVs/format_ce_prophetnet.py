import argparse
import os


import pandas as pd


def format(inputfile):
    df = pd.read_csv(inputfile)
    contexts, questions, answers, start_idx, end_idx = [], [], [], [], []
    for i, row in df.iterrows():
        contexts.extend([row["Text"], row["Text"]])
        questions.extend([row["cause_question"], row["effect_question"]])
        answers.extend([row["Cause"], row["Effect"]])

        cause_start = row["Text"].find(row["Cause"])
        start_idx.append(cause_start)
        end_idx.append(cause_start + len(row["Cause"]) - 1)

        effect_start = row["Text"].find(row["Effect"])
        start_idx.append(effect_start)
        end_idx.append(effect_start + len(row["Effect"]) - 1)

    df_out = pd.DataFrame()
    df_out["context"] = contexts
    df_out["answer"] = answers
    df_out["question"] = questions
    df_out["start_idx"] = start_idx
    df_out["end_idx"] = end_idx
    outfile = list(os.path.split(inputfile))
    outfile[-1] = f"qa_{outfile[-1]}"
    outfile = os.path.join(*outfile)
    print(outfile)
    df_out.to_csv(outfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parsing arguments")
    parser.add_argument("--input", type=str, help="path to data")
    args = parser.parse_args()
    if args.input:
        format(args.input)

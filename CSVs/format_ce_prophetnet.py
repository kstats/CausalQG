import argparse
import os


import pandas as pd


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


def format(inputfile, model):
    df = pd.read_csv(inputfile)
    contexts, questions, answers, start_idx, end_idx = [], [], [], [], []
    for i, row in df.iterrows():
        text, cause, effect = (
            clean_text(row["Text"]),
            clean_text(row["Cause"]).strip(".,!?'\"-'` "),
            clean_text(row["Effect"]).strip(".,!?'\"-'` "),
        )
        contexts.extend([text, text])
        questions.extend([row["cause_question"], row["effect_question"]])
        answers.extend([cause, effect])

        cause_start = text.find(cause)
        start_idx.append(cause_start)
        end_idx.append(cause_start + len(cause) - 1)

        effect_start = text.find(effect)
        start_idx.append(effect_start)
        end_idx.append(effect_start + len(effect) - 1)

    df_out = pd.DataFrame()
    df_out["context"] = contexts
    df_out["answer"] = answers
    df_out["question"] = questions
    df_out["start_idx"] = start_idx
    df_out["end_idx"] = end_idx
    outfile = list(os.path.split(inputfile))
    outfile[-1] = f"qa_{model}_{outfile[-1]}"
    outfile = os.path.join(*outfile)
    df_out.to_csv(outfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parsing arguments")
    parser.add_argument("--input", type=str, help="path to data")
    parser.add_argument("--model", type=str, help="path to data")
    args = parser.parse_args()
    if args.input:
        format(args.input, args.model)

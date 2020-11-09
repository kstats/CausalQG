import argparse


import pandas as pd
from transformers import AutoModelForQuestionAnswering, AutoTokenizer
import torch
from tqdm import tqdm


def predict(filename, model_checkpoint):
    df = pd.read_csv(filename)

    tokenizer = AutoTokenizer.from_pretrained(
        "deepset/bert-large-uncased-whole-word-masking-squad2"
    )
    model = AutoModelForQuestionAnswering.from_pretrained(model_checkpoint)
    answers = []
    with tqdm(total=len(df)) as pbar:
        for i, row in tqdm(df.iterrows()):
            inputs = tokenizer(
                row["context"],
                row["question"],
                add_special_tokens=True,
                return_tensors="pt",
            )
            input_ids = inputs["input_ids"].tolist()[0]
            text_tokens = tokenizer.convert_ids_to_tokens(input_ids)
            answer_start_scores, answer_end_scores = model(**inputs)
            answer_start = torch.argmax(answer_start_scores)
            answer_end = torch.argmax(answer_end_scores) + 1
            answer = tokenizer.convert_tokens_to_string(
                tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end])
            )
            answers.append(answer)
            pbar.update(1)

    df["predicted_answer"] = answers
    df.to_csv(filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parsing arguments")
    parser.add_argument("--input", type=str, help="path to input file")
    parser.add_argument(
        "--model",
        type=str,
        default="deepset/bert-large-uncased-whole-word-masking-squad2",
        help="model checkpoints",
    )
    args = parser.parse_args()
    if args.input:
        predict(args.input, args.model)

import argparse


import pandas as pd
from transformers import AutoModelForQuestionAnswering, AutoTokenizer
from transformers.data.metrics.squad_metrics import compute_f1
import torch
import numpy as np
from tqdm import tqdm


def predict(filename, model_checkpoint, batch_size=8):
    tokenizer = AutoTokenizer.from_pretrained(
        "deepset/bert-large-uncased-whole-word-masking-squad2"
    )
    model = AutoModelForQuestionAnswering.from_pretrained(model_checkpoint)

    df = pd.read_csv(filename)
    df = df.dropna()
    contexts = df["context"].tolist()
    questions = df["question"].tolist()
    answers = df["answer"].tolist()

    encodings = tokenizer(
        contexts,
        questions,
        add_special_tokens=True,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True,
    )

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = model.to(device)
    predicted_answers, scores = [], []
    for i in tqdm(range(0, len(answers), batch_size)):
        batch_ids, batch_attn_masks, batch_ttids = (
            encodings["input_ids"][i : i + batch_size].to(device),
            encodings["attention_mask"][i : i + batch_size].to(device),
            encodings["token_type_ids"][i : i + batch_size].to(device),
        )

        outputs = model(
            input_ids=batch_ids,
            attention_mask=batch_attn_masks,
            token_type_ids=batch_ttids,
        )
        answer_starts = torch.argmax(outputs.start_logits, axis=1)
        answer_ends = torch.argmax(outputs.end_logits, axis=1) + 1
        for j in range(batch_size):
            if i + j >= len(answers):
                break
            answer_start, answer_end = answer_starts[j].item(), answer_ends[j].item()
            input_ids = encodings["input_ids"][i + j].tolist()
            answer = tokenizer.convert_tokens_to_string(
                tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end])
            )
            predicted_answers.append(answer)
            scores.append(compute_f1(answers[i + j], answer))

    df["predicted_answer"] = predicted_answers

    if scores:
        df["score"] = scores
        print("=" * 50)
        print(filename)
        print("Cause Score: ", round(np.mean(scores[::2]), 2))
        print("Effect Score: ", round(np.mean(scores[1::2]), 2))
        print("Total Score: ", round(np.mean(scores), 2))
        print("=" * 50)
    df.to_csv(filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to run QA inference on a given csv of questions")
    parser.add_argument("--input", type=str, help="path to input file")
    parser.add_argument(
        "--model",
        type=str,
        default="deepset/bert-large-uncased-whole-word-masking-squad2",
        help="model checkpoints",
    )
    parser.add_argument("--batch_size", type=int, default=8, help="how large of a batch size to use")
    args = parser.parse_args()
    if args.input:
        predict(args.input, args.model, args.batch_size)

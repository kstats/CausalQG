import argparse
import os


import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from transformers import (
    AutoTokenizer,
    AutoModelForQuestionAnswering,
    Trainer,
    TrainingArguments,
)


class CausalDataset(torch.utils.data.Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __getitem__(self, idx):
        return {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}

    def __len__(self):
        return len(self.encodings.input_ids)


def char_to_token(tokenizer, encodings, i, answer):
    answer_encoding = tokenizer(answer)["input_ids"][1:-1]
    context_encoding = encodings["input_ids"][i]
    for i in range(len(context_encoding) - len(answer_encoding)):
        if context_encoding[i : i + len(answer_encoding)] == answer_encoding:
            return i, i + len(answer_encoding) - 1
    return None, None


def add_token_positions(encodings, answers, tokenizer):
    start_positions = []
    end_positions = []
    for i in range(len(answers)):
        start, end = char_to_token(tokenizer, encodings, i, answers[i]["text"])
        start_positions.append(start)
        end_positions.append(end)
        # if None, the answer passage has been truncated
        if start_positions[-1] is None:
            start_positions[-1] = 511
        if end_positions[-1] is None:
            end_positions[-1] = 511
    encodings.update(
        {"start_positions": start_positions, "end_positions": end_positions}
    )


def parse_data(filename):
    df = pd.read_csv(filename)
    df = df.dropna()
    contexts = df["context"].tolist()
    questions = df["question"].tolist()

    answers = []
    for _, row in df.iterrows():
        answers.append(
            {
                "text": row["answer"],
                "answer_start": row["start_idx"],
                "answer_end": row["end_idx"],
            }
        )

    return contexts, questions, answers


def finetune(args):
    tokenizer = AutoTokenizer.from_pretrained(
        "deepset/bert-large-uncased-whole-word-masking-squad2"
    )
    train_contexts, train_questions, train_answers = parse_data(args.train_data)
    if args.valid_data:
        val_contexts, val_questions, val_answers = parse_data(args.valid_data)
    else:
        (
            train_contexts,
            val_contexts,
            train_questions,
            val_questions,
            train_answers,
            val_answers,
        ) = train_test_split(
            train_contexts, train_questions, train_answers, test_size=0.2, random_state=42
        )
    train_encodings = tokenizer(
        train_contexts, train_questions, truncation=True, max_length=512, padding=True
    )
    val_encodings = tokenizer(
        val_contexts, val_questions, truncation=True, max_length=512, padding=True
    )
    add_token_positions(train_encodings, train_answers, tokenizer)
    add_token_positions(val_encodings, val_answers, tokenizer)
    train_dataset = CausalDataset(train_encodings)
    val_dataset = CausalDataset(val_encodings)

    model = AutoModelForQuestionAnswering.from_pretrained(
        "deepset/bert-large-uncased-whole-word-masking-squad2"
    )
    training_args = TrainingArguments(
        output_dir=f"{args.output_dir}/results",  # output directory
        num_train_epochs=args.num_iters,  # total number of training epochs
        per_device_train_batch_size=args.train_batch_size,  # batch size per device during training
        per_device_eval_batch_size=args.valid_batch_size,  # batch size for evaluation
        warmup_steps=500,  # number of warmup steps for learning rate scheduler
        weight_decay=0.01,  # strength of weight decay
        logging_dir=f"{args.output_dir}/logs",  # directory for storing logs
        logging_steps=100,
        label_names=["start_positions", "end_positions"],
    )
    trainer = Trainer(
        model=model,  # the instantiated 🤗 Transformers model to be trained
        args=training_args,  # training arguments, defined above
        train_dataset=train_dataset,  # training dataset
        eval_dataset=val_dataset,  # evaluation dataset
    )
    trainer.train()
    trainer.save_model(f"{args.output_dir}/checkpoints")
    print(trainer.evaluate())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to finetune a QA model of a given set of data")
    parser.add_argument("--train_data", type=str, help="path to training data")
    parser.add_argument("--valid_data", type=str, help="path to validation data")
    parser.add_argument(
        "--train_batch_size", type=int, default=4, help="size of training batch"
    )
    parser.add_argument(
        "--num_iters", type=int, default=10, help="size of training batch"
    )
    parser.add_argument(
        "--valid_batch_size", type=int, default=4, help="size of validation batch"
    )
    parser.add_argument("--output_dir", type=str, default="", help="output directory")
    args = parser.parse_args()
    finetune(args)

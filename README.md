# CausalQG

This repo provides the code for reproducing the experiments in Automatically Generating Cause-and-Effect Questions from Passages. In the paper, we propose a novel pipeline for generating causal questions from unstructured text.

## Pipeline

There are two steps in our pipeline:

### 1) Causal Relationship Extraction

We perform the causal relationship extraction using an approach from [Cao et al](https://ieeexplore.ieee.org/document/7815074). We simplify the [repo](https://github.com/Angela7126/CE_extractor--Patterns_Based) they provided and add scripts to parse the datasets we ran our experiments on.

To begin the pipeline, move into the `CausalExtraction` directory and follow all of the setup instructions. Then run the parsing scripts for the TQA/SQuAD datasets. This should create two csvs: `squad_ce.csv` and `textbook_ce.csv`. Move these into `CSVs/SQuAD/` and `CSVs/Textbook/`, respectively.

#TODO: Add steps for processing new as pattern. This will produce `squad_ce_processed.csv` and `textbook_ce_processed.csv`. Move these into `CSVs/SQuAD/` and `CSVs/Textbook/`, respectively, as well.

### 2) Question Generation

We perform question generation using ProphetNet. We created a [fork](https://github.com/ManavR123/ProphetNet/tree/CausalQG) of the [microsoft/ProphetNet](https://github.com/microsoft/ProphetNet) repo with scripts to recreate our outputs. Follow the documentation provided in the forked repo to reproduce our generated questions.

In our experiments, we generated 4 sets of questions using 4 different versions of ProphetNet:

1) ProphetNet-Base. You should label the csv of questions generated from this version as `squad_ce_processed_prophetnet.csv` or `textbook_ce_processed_prophetnet.csv`.

2) ProphetNet finetuned on SQuAD causal questions. You should label the csv of questions generated from this version as `squad_ce_processed_prophetnet_squad_gold.csv` or `textbook_ce_processed_prophetnet_squad_gold.csv`.

3) ProphetNet finetuned on questions generated from SynQG. You should label the csv of questions generated from this version as `squad_ce_processed_prophetnet_synqg.csv` or `textbook_ce_processed_prophetnet_synqg.csv`.

4) ProphetNet finetuned on a combined set of SQuAD and SynQG questions. You should label the csv of questions generated from this version as `squad_ce_processed_prophetnet_combined.csv` or `textbook_ce_processed_prophetnet_combined.csv`.

5) You can use the squad_read.py script to preprocess the SQUAD data to produce 3-sentence chunks, which are used causal extraction. 

The data used for finetuning ProphetNet can be found in `CSVs/Finetune`. Follow the steps in the above repo to run the finetuning process.

Move these into their respective folders in `CSVs/`.

## Evaluation

we evaluate our system using two approaches:

### 1) Question-Answering

We hypothesize that a good cause/effect question will be able to be answered by a strong QA system. We use 4 different QA models to evaluate the quality of our causal questions. The base model is provided by deepset and hosted by HuggingFace/tranformers. We then finetune this model on three datasets of causal questions: the sames ones used to fine tune the QG model. To perform the finetuning move into the `QA/` directory and use the `finetune_qa.py` script.

Then, to use the various models to generate answers for a given csv of questions, use `QA/predict.py`. To prepare the ProphetNet questions for the QA input, use `format_ce_prophetnet.py`. In this step, you will produce 4 output csvs beginning with `qa_` for each csv of questions generated in the question-generation step.

You can then use the `ce_q_eval.py` scripts found in `CSVs/` to get an analysis of QA performance broken down by typology.

### 2) Cause/Effect in Answer Recall

We also hypothesize that a good causal question will include the cause/effect in its text when asking about the other i.e. a question asking about the cause will mention the effect and a question asking about effect will mention the cause. These calculations are done by `ce_q_eval.py`. Move into the `CSVs` directory and run `python ce_q_eval.py --input <path_to_input_file> --ce_recall` to calculate the recall scores. This will also print out an analysis of these scores based on typology.

## How to Cite

If you extend or use this work, please cite the paper where it was introduced:

#TODO: add bibtex citation

Let us know if you have any questions!

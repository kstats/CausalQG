# CausalQG

This repo provides the code for reproducing the experiments in Automatically Generating Cause-and-Effect Questions from Passages. In the paper, we propose a novel pipeline for generating causal questions from unstructured text.

## Pipeline

There are two steps in our pipeline:

### 1) Causal Relationship Extraction

We perform the causal relationship extraction using an approach from [Cao et al](https://ieeexplore.ieee.org/document/7815074). We simplify the [repo](https://github.com/Angela7126/CE_extractor--Patterns_Based) they provided and add scripts to parse the datasets we ran our experiments on.

To begin the pipeline, move into the `CausalExtraction` directory and follow all of the setup instructions. Then run the parsing scripts for the TQA/SQuAD datasets. This should create two csvs: `squad_ce.csv` and `textbook_ce.csv`. Move these into `CSVs/SQuAD/` and `CSVs/Textbook/`, respectively.

Next, to post-process the CEs, run `post_process_CEs.py`. This will reproduce `squad_ce_processed.csv` and `textbook_ce_processed.csv`. Move these into `CSVs/SQuAD/` and `CSVs/Textbook/`, respectively, as well.

To generate CE stratified sampling on typology, first run `get_patterns_typology.py` to get new patterns csv with typology, or use our provided `CausalExtraction/patterns_typology.csv`, then run `stratified_sample.py`.

### 2) Question Generation

We perform question generation using ProphetNet. We created a [fork](https://github.com/ManavR123/ProphetNet/tree/CausalQG) of the [microsoft/ProphetNet](https://github.com/microsoft/ProphetNet) repo with scripts to recreate our outputs. Follow the documentation provided in the forked repo to reproduce our generated questions.

In our experiments, we generated 2 sets of questions using 2 different versions of ProphetNet:

1) ProphetNet-Base. You should label the csv of questions generated from this version as `squad_ce_processed_prophetnet.csv` or `textbook_ce_processed_prophetnet.csv`.

2) ProphetNet finetuned on questions generated from SynQG. You should label the csv of questions generated from this version as `squad_ce_processed_prophetnet_synqg.csv` or `textbook_ce_processed_prophetnet_synqg.csv`.

The data used for finetuning ProphetNet can be found in `CSVs/Finetune`. Follow the steps in the above repo to run the finetuning process.

Move these into their respective folders in `CSVs/`.

## Evaluation

we evaluate our system using three approaches:

### 1) Question-Answering

We hypothesize that a good cause/effect question will be able to be answered by a strong QA system. We use 2 different QA models to evaluate the quality of our causal questions. The base model is provided by deepset and hosted by HuggingFace/tranformers. We then finetune this model on a dataset of causal questions: the sames one used to fine tune the QG model. To perform the finetuning move into the `QA/` directory and use the `finetune_qa.py` script. Finetuned model can be found on the HuggingFace model hub [here](https://huggingface.co/manav/causal_qa).

Then, to use the various models to generate answers for a given csv of questions, use `QA/predict.py`. To prepare the ProphetNet questions for the QA input, use `format_ce_prophetnet.py`. In this step, you will produce 2 output csvs beginning with `qa_` for each csv of questions generated in the question-generation step.

You can then use the `ce_q_eval.py` scripts found in `CSVs/` to get an analysis of QA performance broken down by typology.

### 2) Cause/Effect in Answer Recall

We also hypothesize that a good causal question will include the cause/effect in its text when asking about the other i.e. a question asking about the cause will mention the effect and a question asking about effect will mention the cause. These calculations are done by `ce_q_eval.py`. Move into the `CSVs` directory and run `python ce_q_eval.py --input <path_to_input_file> --ce_recall` to calculate the recall scores. This will also print out an analysis of these scores based on typology.

### 3) Human Evaluation

We have included the HTML files for both human evaluation tasks.  `TurkTasks/causal_mturk_task.html` is the interface for the task where crowdworkers determine if an extracted cause/effect pair is correct.  `TurkTasks/qg_mturk_task.html` is the interface for the task where crowdworkers evaluate generated questions.  They are asked to determine (1) whether the answer is correct for the generated question and (2) whether the question is causal in nature.

## How to Cite

If you extend or use this work, please cite our paper:
```
@inproceedings{stasaski-etal-2021-automatically,
    title = "Automatically Generating Cause-and-Effect Questions from Passages",
    author = "Stasaski, Katherine  and
      Rathod, Manav  and
      Tu, Tony  and
      Xiao, Yunfang  and
      Hearst, Marti A.",
    booktitle = "Proceedings of the 16th Workshop on Innovative Use of NLP for Building Educational Applications",
    month = apr,
    year = "2021",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/2021.bea-1.17",
    pages = "158--170",
    abstract = "Automated question generation has the potential to greatly aid in education applications, such as online study aids to check understanding of readings. The state-of-the-art in neural question generation has advanced greatly, due in part to the availability of large datasets of question-answer pairs. However, the questions generated are often surface-level and not challenging for a human to answer. To develop more challenging questions, we propose the novel task of cause-and-effect question generation. We build a pipeline that extracts causal relations from passages of input text, and feeds these as input to a state-of-the-art neural question generator. The extractor is based on prior work that classifies causal relations by linguistic category (Cao et al., 2016; Altenberg, 1984). This work results in a new, publicly available collection of cause-and-effect questions. We evaluate via both automatic and manual metrics and find performance improves for both question generation and question answering when we utilize a small auxiliary data source of cause-and-effect questions for fine-tuning. Our approach can be easily applied to generate cause-and-effect questions from other text collections and educational material, allowing for adaptable large-scale generation of cause-and-effect questions.",
}
```
Let us know if you have any questions!

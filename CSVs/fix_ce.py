import pandas as pd


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


df = pd.read_csv("Textbook/textbook_ce.csv")

contexts, causes, effects = [], [], []
for i, row in df.iterrows():
    contexts.append(fix(row["Text"]))
    causes.append(fix(row["Cause"]).strip(".,!?\'\"-'` "))
    effects.append(fix(row["Effect"]).strip(".,!?\'\"-'` "))

df["Text"], df["Cause"], df["Effect"] = contexts, causes, effects
df.to_csv("Textbook/fixed_textbook_ce.csv")

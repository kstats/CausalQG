import csv
import json
import re

from pattern_match import TXT2Patterns

sentences = []
patterns = TXT2Patterns()
with open("tqa/tqa_train_val_test/train/tqa_v1_train.json", "r") as f:
    data = json.loads(f.read())
    for d in data:
        topics = d['topics']
        for t in topics:
            text = d['topics'][t]['content']['text']
            for p in patterns:
                ptr = re.compile(p[0])
                sentences.extend(ptr.findall(text))

with open('textbook.csv', 'w', newline='', encoding='utf8') as csvfile:
    writer = csv.writer(csvfile, delimiter=',',
                            quoting=csv.QUOTE_MINIMAL)
    writer.writerows([[s] for s in sentences])

import os
from nltk.tokenize import word_tokenize
import json


lemmas = set()
path = ""

with open('italian_borrowings.jsonl','r') as f:
    for line in f:
        line = json.loads(line)
        italian_words = line['italian_words']
        for word in italian_words:
            lemmas.add(word)


for fname in sorted(os.listdir(path)):
    year = int(fname.split('.')[0].split('_')[1])
    print(year,flush=True)
    with open(f'{path}/{fname}') as f:
        for line in f:
            line = line.replace('\n','')
            line_temp = line.replace("'", " ' ")
            tokens = set(word_tokenize(line_temp))
            intersection = tokens.intersection(lemmas)
            for word in intersection:
                with open(f'lastampa_words/{word}.txt','a+') as g:
                    g.write(f'{year}\t{line}\n')
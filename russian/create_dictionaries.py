import os
from nltk.tokenize import word_tokenize
from tqdm import tqdm
import json

print('Dictionary creation', flush=True)
D = {}

for fname in tqdm(sorted(os.listdir('json')), 'Processing lemmas..'):
    with open(f'json/{fname}') as f:
        for line in f:
            line = json.loads(line)
            text = line['text']
            year = line['year']
            tokens = [w.lower() for w in word_tokenize(text,language='russian')]
            if not year in D:
                D[year] = {}
            for token in tokens:
                if not token in D[year]:
                    D[year][token] = 1
                else:
                    D[year][token] = D[year][token] + 1

for year in D:
    with open(f'dictionaries/{year}.txt','w+') as f:
        for token in D[year]:
            f.write(f'{token}\t{D[year][token]}\n')

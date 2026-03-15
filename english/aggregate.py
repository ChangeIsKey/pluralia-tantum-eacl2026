import os
import re
from tqdm import tqdm
import json

lemma2forms = {}

with open('sing2plur.jsonl','r') as f:
    for line in f:
        line = json.loads(line)
        lemma = line['lemma_id'].split('_')[0]
        singulars = line['singular_forms']
        plurals = line['plural_forms']
        lemma2forms[lemma] = {'singular':singulars, 'plural':plurals}

def process_form(form, g, form_type):
    pattern = rf'\b{re.escape(form)}\b'
    if os.path.exists(f'times_words/{form}.txt'):
        with open(f'times_words/{form}.txt') as f:
            for line in f:
                line = line.replace('\n','').split('\t')
                year = int(line[0])
                line = '\t'.join(line[1:])
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    start, end = match.start(), match.end()
                    D = {"word": form, "year": year, "text": line, "start": start, "end": end, "form": form_type}
                    g.write(json.dumps(D)+'\n')
                
for lemma in tqdm(lemma2forms, 'Processing lemmas..'):
    with open(f'json/{lemma}.jsonl','w+') as g:
        for singular in lemma2forms[lemma]['singular']:
            process_form(singular, g, 'singular')
        for plural in lemma2forms[lemma]['plural']:
            process_form(plural, g, 'plural')

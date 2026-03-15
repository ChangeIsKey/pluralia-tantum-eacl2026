import os
import sys
from WordTransformer import WordTransformer, InputExample
import numpy as np
import pickle
from tqdm import tqdm
import re
import random
import json

# Initialize the model globally
global_model = WordTransformer('pierluigic/xl-lexeme')

def encode_and_save(lemma, sampled_examples, language):
    examples = [InputExample(texts=ex['text'], positions=[ex['start'], ex['end']]) for ex in sampled_examples]
    vecs = global_model.encode(examples, batch_size=3000)
    vector_dir = f'{language}/vectors'
    with open(os.path.join(vector_dir, f'{lemma}.pkl'), 'wb+') as f:
        pickle.dump([vecs,sampled_examples], f)

def process_lemma(fname, language, start_year, end_year, n_years, max_total_samples):
    lemma = fname.split('.')[0]
    json_dir = f'{language}/json'
    with open(os.path.join(json_dir, fname)) as f:
        filling_list = [[] for _ in range(n_years)]
        form2examples = {'singular': filling_list.copy(), 'plural': filling_list.copy()}

        for line in f:
            line = json.loads(line)
            number = line['spacy_number'] if language == 'italian' else line['form']
            if number == '':
                continue
            year = line['year']
            if year < start_year or year > end_year:
                continue
            form2examples[number][year - start_year].append(line)

    form2available = {
        form: sum(len(examples_in_year) for examples_in_year in form2examples[form])
        for form in ['singular', 'plural']
    }

    form2target = {}
    if sum(form2available.values()) <= max_total_samples:
        form2target = form2available
    else:
        total_available = sum(form2available.values())
        for form in ['singular', 'plural']:
            form2target[form] = int((form2available[form] / total_available) * max_total_samples)

    sampled_examples = []
    for form in ['singular', 'plural']:
        available = form2available[form]
        target = form2target[form]
        if available <= target:
            for year_examples in form2examples[form]:
                sampled_examples.extend(year_examples)
        else:
            year_sizes = [len(year) for year in form2examples[form]]
            total = sum(year_sizes)
            year_targets = [int((size / total) * target) if total > 0 else 0 for size in year_sizes]
            while sum(year_targets) < target:
                for i in range(n_years):
                    if sum(year_targets) < target and len(form2examples[form][i]) > year_targets[i]:
                        year_targets[i] += 1
            for i, year_examples in enumerate(form2examples[form]):
                count = min(len(year_examples), year_targets[i])
                sampled_examples.extend(random.sample(year_examples, count))

    if len(sampled_examples) > max_total_samples:
        sampled_examples = random.sample(sampled_examples, max_total_samples)

    encode_and_save(lemma, sampled_examples, language)

if __name__ == '__main__':
    language = sys.argv[1]
    print(language, flush=True)

    if not os.path.exists(f'{language}/vectors'):
        os.mkdir(f'{language}/vectors')

    language2span = {'italian': (1910, 2005), 'english': (1785, 2013), 'russian': (1750, 2022)}
    start_year, end_year = language2span[language]
    n_years = end_year - start_year + 1
    max_total_samples = 3000

    json_dir = f'{language}/json'
    files = os.listdir(json_dir)
    vector_dir = f'{language}/vectors'
    vector_files = os.listdir(vector_dir)
    files = [w+'.jsonl' for w in set([w.split('.')[0] for w in files]).difference(set([w.split('.')[0] for w in vector_files]))]

    for fname in tqdm(files, desc='Processing lemmas'):
        process_lemma(fname, language, start_year, end_year, n_years, max_total_samples)

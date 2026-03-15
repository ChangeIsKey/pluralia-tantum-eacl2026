import os
import random
import sys
import numpy as np
import gzip
import argparse
import json
import pickle
from corpora import load_corpus
import re
from nltk.tokenize import word_tokenize
from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Corpora statistics',
        description="Computation of corpus statistics")

    conf = 'times.config'
    corpus = load_corpus(conf)

    target_words = set()
    lemma_ids = set()
    with open(f'sing2plur.jsonl') as f:
        for line in f:
            line = json.loads(line)
            for form in line['singular_forms']:
                target_words.add(form.lower()+'_NOUN')
            for form in line['plural_forms']:
                target_words.add(form.lower()+'_NOUN')


    for time_point in tqdm(corpus.time_points, 'Processing time points...'):
        for tokens, line in corpus.line_iterator(time_point):
            line = re.sub(r"\s+", " ", line)
            if line[0] == '>':
                line = line[1:]
            tokens = set(tokens)
            intersection = tokens.intersection(target_words)
            for word in intersection:
                word_name = '_'.join(word.split('_')[:-1])
                with open(f'times_words/{word_name}.txt','a+') as g:
                    g.write(f'{time_point}\t{line}\n')




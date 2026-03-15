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
    path = ""

    target_words = set()
    lemma_ids = set()
    for fname in os.listdir('words'):
        with open(f'words/{fname}') as f:
            for line in f:
                line = json.loads(line)
                lemma = line['lemma']
                sense_id = line['sense_id']
                lemma_id = sense_id.split('-')[0]
                lemma_ids.add(lemma_id)
                target_words.add(lemma.lower()+'_NOUN')

    with open('sing2plur.jsonl','w+') as g:
        for fname in os.listdir(path):
            with open(f'{path}/{fname}') as f:
                D = json.load(f)
                for elem in D:
                    lemma_id = elem['id']
                    if lemma_id in lemma_ids:
                        british_inflections = [j for i in elem['inflections'] for j in i['inflections'] if i['region']=='British']
                        plural_inflections = [i['form'] for i in british_inflections if i['part_of_speech'] == 'NNS']
                        for p in plural_inflections:
                            target_words.add(p.lower()+'_NOUN')
                        singular_inflections = [i['form'] for i in british_inflections if i['part_of_speech'] == 'NN']
                        for s in singular_inflections:
                            target_words.add(s.lower()+'_NOUN')
                        g.write(json.dumps({'lemma_id':lemma_id, 'singular_forms':singular_inflections, 'plural_forms':plural_inflections})+'\n')

 
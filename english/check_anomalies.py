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
    lemmas = set()

    with open('words/ending_s_formal_plt.jsonl') as f:
        for line in f:
            line = json.loads(line)
            lemmas.add(line['lemma'])

    with open('anomalies.txt','w+') as g:
        with open('sing2plur.jsonl') as f:
            for line in f:
                line = json.loads(line)
                singulars = line['singular_forms']
                for lemma in lemmas:
                    if lemma in singulars:
                        g.write(line['lemma_id']+'\n')


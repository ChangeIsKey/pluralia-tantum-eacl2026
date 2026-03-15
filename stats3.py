import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from joypy import joyplot
from scipy.stats import spearmanr

language = 'english'

# Step 1: Build the mappings
lemma2category = {}
category2lemma = {}
if language == 'english':
    for fname in os.listdir(f'{language}/new_words'):
        category = fname.split('.')[0]
        with open(f'{language}/new_words/{fname}') as f:
            for line in f:
                line = json.loads(line)
                lemma = line['sense_id'].split('_')[0]
                lemma2category[lemma] = category
                category2lemma.setdefault(category, set()).add(lemma)
elif language == 'italian':
    plur2sing = {}
    with open(f'{language}/lemmas.csv') as f:
        for line in f:
            line = line.replace('\n','').split(';')
            plur2sing[line[0]] = line[1]
    with open(f'{language}/dataset.csv') as f:
        categoryid = {}
        for j,line in enumerate(f):
            line = line.replace('\n','').split('\t')
            if j == 0:
                categoryid = {i:c for i,c in enumerate(line)}
                for c in line:
                    category2lemma[c] = set()
            else:
                for i,w in enumerate(line):
                    w = ''.join(filter(lambda x: not x.isdigit(), w))
                    if w in plur2sing:
                        w = plur2sing[w]
                    if i == 0 and w in lemma2category:
                        continue
                    lemma2category[w] = categoryid[i]
                    category2lemma[categoryid[i]].add(w)
elif language == 'russian':
    with open(f'{language}/dataset.csv') as f:
        categoryid = {}
        for j,line in enumerate(f):
            line = line.replace('\n','').split(';')
            if j == 0:
                categoryid = {i:c for i,c in enumerate(line)}
                for c in categoryid:
                    category2lemma[c] = set()
            else:
                for i,w in enumerate(line):
                    w = ''.join(filter(lambda x: not x.isdigit(), w))
                    if i == 1 and w in lemma2category:
                        continue
                    lemma2category[w] = categoryid[i]
                    category2lemma[c].add(w)


word2segments = {}
plural_words = set()
with open(f'{language}/change_points.jsonl') as f:
    for line in f:
        line = json.loads(line)
        lemma = line['lemma']
        segment_means = line['segment_means']
        if len(segment_means)==2:
            word2segments[lemma] = segment_means

word2change_scores = {}
with open(f'{language}/change_scores_cluster.jsonl') as f:
    for line in f:
        line = json.loads(line)
        lemma = line['lemma']
        if lemma in word2segments:
            change_scores = line['introduced_sense']
            word2change_scores[lemma] = change_scores

word2freq_changes = {}

for word in word2segments:
    freq_changes = []
    for j in range(1,len(word2segments[word])):
        if word2segments[word][j]<0:
            freq_changes.append(word2segments[word][j])
        else:
            freq_changes.append(None)
    word2freq_changes[word] = freq_changes

c1 = []
c2 = []
words = []
categories = []
category2c1 = {}
category2c2 = {}
word2c2 = {}


for word in word2freq_changes:
    for j in range(len(word2freq_changes[word])):
        if not word2change_scores[word][j] == None and not word2freq_changes[word][j]==None:
            if word in lemma2category:
                c1.append(word2freq_changes[word][j])
                c2.append(word2change_scores[word][j])
                words.append(word)
                categories.append(lemma2category[word])
                if not categories[-1] in category2c1:
                    category2c1[categories[-1]] = []
                    category2c2[categories[-1]] = []
                category2c1[categories[-1]].append(c1[-1])
                category2c2[categories[-1]].append(c2[-1])
                if not word in word2c2:
                    word2c2[word] = []
                word2c2[word].append(c2[-1])
            else:
                print(word)




for category in category2c1:
    print(category, len(category2c1[category]))
    print(np.mean(category2c1[category]), np.std(category2c1[category]))
    print(len(np.where(np.array(category2c2[category])==True)[0]))
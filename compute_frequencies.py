import os
import json
from tqdm import tqdm
import numpy as np

language2span = {'italian':(1910,2005), 'english':(1785,2013), 'russian':(1750,2022)}


for language in language2span:
    print(language)
    V = []
    N = []
    with open(f'{language}/years.txt') as f:
        for line in f:
            year, counts, words = [int(w) for w in line.replace('\n','').split('\t')]
            if year >= language2span[language][0] and year <= language2span[language][1]:
                V.append(words)
                N.append(counts)
    V = np.array(V)
    N = np.array(N)
    vocabulary_sum = V+N
    with open(f'{language}/frequencies.jsonl','w+') as g:
        for fname in tqdm(os.listdir(f'{language}/json'), 'Processing lemmas..'):
            lemma = fname.split('.')[0]
            zero_list = [0]*(language2span[language][1]-language2span[language][0]+1)
            with open(f'{language}/json/{fname}') as f:
                counts = {'singular': zero_list.copy(), 'plural': zero_list.copy()}
                for line in f:
                    line = json.loads(line)
                    year = line['year']
                    if year >= language2span[language][0] and year <= language2span[language][1]:
                        if not language == 'italian':
                            number = line['form'] 
                        else:
                            number = line['spacy_number']
                        if number == None or number == '':
                            continue
                        counts[number][year-language2span[language][0]] = counts[number][year-language2span[language][0]] + 1

                counts['singular'] = np.array(counts['singular'])
                counts['plural'] = np.array(counts['plural'])
                relative_singular = counts['singular']/N
                relative_plural = counts['plural']/N
                prob_singular = (1 + counts['singular'])/vocabulary_sum
                prob_plural = (1 + counts['plural'])/vocabulary_sum
                ratios = (np.log(prob_singular/prob_plural)).tolist()
                D = {
                'lemma':lemma,
                'absolute_frequencies': [counts['singular'].tolist(), counts['plural'].tolist()],
                'relative_frequencies': [relative_singular.tolist(), relative_plural.tolist()],
                'probs': [prob_singular.tolist(), prob_plural.tolist()],
                'ratios':ratios,
                }
                g.write(json.dumps(D)+'\n')

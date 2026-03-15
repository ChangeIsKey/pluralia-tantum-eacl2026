import os
import json
import pickle
import numpy as np
from scipy.spatial.distance import cdist

language2span = {'italian':(1910,2005), 'english':(1785,2013), 'russian':(1750,2022)}


for language in language2span:
    empty_set = set()
    lemmas = []
    scores = []
    with open(f'{language}/all_change_scores.jsonl','w+') as g:
        for fname in os.listdir(f'{language}/vectors'):
            lemma = fname.split('.')[0]
            with open(f'{language}/vectors/{fname}','rb') as f:
                vecs, examples = pickle.load(f)
                years = [e['year'] for e in examples]
                forms = [e['form'] if not language=='italian' else e['spacy_number'] for e in examples]
                forms = np.array(forms)
                years = np.array(years)
                singular_idxs = np.where(forms=='singular')
                plural_idxs = np.where(forms=='plural')
                singular_vecs = vecs[singular_idxs]
                plural_vecs = vecs[plural_idxs] 
                plural_years = years[plural_idxs]

                start_year, end_year = language2span[language]
                year_range = end_year - start_year + 1
                set_plural_years = set(plural_years)
                plural_timeseries = [[] for y in range(end_year+1) if y in set_plural_years]
                year2index = {y:i for i,y in enumerate(sorted(set_plural_years))}
                ts = [int(y) for y in sorted(year2index)]

                for j, year in enumerate(plural_years):
                    if start_year <= year <= end_year:
                        plural_timeseries[year2index[year]].append(plural_vecs[j])

                scores = []

                for i in range(1, len(plural_timeseries)):

                    # Collect vectors before and after the current change point
                    before_vecs = [vec for vec in plural_timeseries[i-1]]
                    after_vecs = [vec for vec in plural_timeseries[i]]

                    if before_vecs and after_vecs:
                        before_mat = np.vstack(before_vecs)
                        after_mat = np.vstack(after_vecs)
                        dist_matrix = cdist(before_mat, after_mat, metric='cosine')
                        avg_score = np.mean(dist_matrix)
                        scores.append(avg_score)
                    else:
                        scores.append(None)

                g.write(json.dumps({'lemma':lemma, 'ts':ts, 'change_scores':scores})+'\n')


"""
if len(singular_vecs) == 0 or len(plural_vecs) == 0:
    empty_set.add(lemma)
else:
    cosine_distances = cdist(singular_vecs, plural_vecs, metric='cosine') 
    lemmas.append(lemma)
    scores.append(np.mean(cosine_distances))
    #print(lemma, scores[-1])

ordered_pairs = [(x,y) for x,y in sorted(zip(scores,lemmas),reverse=True)]
with open(f'{language}_scores.txt','w+') as g:
    for x,y in ordered_pairs:
        g.write(f'{x}\t{y}\n')
    for x in empty_set:
        g.write(f'{x}\tMissing singular/plural\n')
"""
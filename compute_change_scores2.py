import os
import json
import pickle
import numpy as np
from scipy.spatial.distance import cdist
from sklearn.cluster import AgglomerativeClustering

language2span = {'italian':(1910,2005), 'english':(1785,2013), 'russian':(1750,2022)}


for language in language2span:
    word2change_points = {}
    with open(f'{language}/change_points.jsonl') as f:
        for line in f:
            line = json.loads(line)
            lemma = line['lemma']
            change_points = line['change_points']
            word2change_points[lemma] = change_points
    empty_set = set()
    lemmas = []
    scores = []
    with open(f'{language}/change_scores_cluster.jsonl','w+') as g:
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
                plural_timeseries = [[] for _ in range(year_range)]

                for j, year in enumerate(plural_years):
                    if start_year <= year <= end_year:
                        plural_timeseries[year - start_year].append(plural_vecs[j])

                # Compute change scores around change points
                change_points = [range(start_year,end_year)[c] for c in word2change_points[lemma]]
                all_points = [start_year] + change_points + [end_year + 1]  # Add boundaries
                scores = []

                for i in range(1, len(all_points) - 1):
                    prev = all_points[i - 1] - start_year
                    curr = all_points[i] - start_year
                    next_ = all_points[i + 1] - start_year

                    # Collect vectors before and after the current change point
                    before_vecs = [vec for year in range(prev, curr) for vec in plural_timeseries[year]]
                    after_vecs = [vec for year in range(curr, next_) for vec in plural_timeseries[year]]

                    cluster2instances = {}
                    if before_vecs and after_vecs:
                        before_mat = np.vstack(before_vecs)
                        after_mat = np.vstack(after_vecs)
                        all_vecs = np.vstack([before_vecs,after_vecs])
                        labels = AgglomerativeClustering(n_clusters=None, metric='cosine', linkage='average', distance_threshold=0.5).fit_predict(all_vecs)
                        for i,cluster in enumerate(labels):
                            if not cluster in cluster2instances:
                                cluster2instances[cluster] = {'before':0, 'after':0}
                            if i<len(before_mat):
                                cluster2instances[cluster]['before'] = cluster2instances[cluster]['before'] + 1
                            else:
                                cluster2instances[cluster]['after'] = cluster2instances[cluster]['after'] + 1
                        introduced_sense = False
                        for c in cluster2instances:
                            if cluster2instances[c]['before']+cluster2instances[c]['after']>=10:
                                if cluster2instances[c]['before'] == 0:
                                    introduced_sense = True
                                    break
                        scores.append(introduced_sense)
                    else:
                        scores.append(None)

                g.write(json.dumps({'lemma':lemma, 'introduced_sense':scores})+'\n')


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
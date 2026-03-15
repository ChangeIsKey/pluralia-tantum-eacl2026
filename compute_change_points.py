import os
import json
from tqdm import tqdm
import numpy as np
import ruptures as rpt

language2span = {'italian':(1910,2005), 'english':(1785,2013), 'russian':(1750,2022)}


for language in language2span:
    with open(f'{language}/frequencies.jsonl') as f:
        with open(f'{language}/change_points.jsonl','w+') as g:
            for line in tqdm(f,f'Processing {language}..'):
                line = json.loads(line)
                lemma = line['lemma']
                ratios = np.array(line['ratios'])
                #window_size = 5
                # Compute moving average
                #weights = np.ones(window_size) / window_size
                #ratios = np.convolve(ratios, weights, mode='valid')
                model = "rbf"  # good for nonlinear shifts
                algo = rpt.Pelt(model=model).fit(ratios)
                change_points = algo.predict(pen=10)[:-1]  
                # Compute average ratios before and after each change point
                segment_means = []
                start = 0
                for cp in change_points + [len(ratios)]:
                    segment = ratios[start:cp]
                    mean = float(np.mean(segment)) if len(segment) > 0 else None
                    segment_means.append(mean)
                    start = cp

                g.write(json.dumps({
                    'lemma': lemma,
                    'change_points': change_points,
                    'segment_means': segment_means
                }) + '\n')
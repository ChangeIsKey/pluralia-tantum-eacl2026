from collections import defaultdict
from scipy.stats import kendalltau
import json
import os
import numpy as np
from matplotlib import pyplot as plt
import csv

analysis_path = 'analysis_reasoner'

maplabels = {
    'Significati prevalentemente al plurale ':'Plural Dominant',
    'Significati esclusivamente alla forma plurale (pluralia tantum semantici)': 'Semantic PT',
    'Sostantivi esclusivamente al pluale (Pluralia tantum formali)': 'Morph. PT',
    'Pluralia tantum formali': 'Morph. PT',
    'plural dominant': 'Plural Dominant',
    'semantic plt':'Semantic PT',
    'morphologicalplt': 'Morph. PT',
    'semanticplt': 'Semantic PT',
    'pluraldominant': 'Plural Dominant'
}

def get_categories(language):
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
        plur2sing = {}
        with open(f'{language}/ru_lemmas.txt') as f:
            for line in f:
                sing, plur = line.replace('\n','').split('\t')
                plur2sing[plur] = sing
        with open(f'{language}/dataset2.csv') as f:
            categoryid = {}
            for j,line in enumerate(f):
                line = line.replace('\n','').split(';')
                if j == 0:
                    categoryid = {i:c for i,c in enumerate(line)}
                    for c in line:
                        category2lemma[c] = set()
                else:
                    for i,w in enumerate(line):
                        w = ''.join(filter(lambda x: not x.isdigit(), w)).lower()
                        if not len(w.strip())==0:
                            if w in plur2sing:
                                w1 = plur2sing[w]
                            else:
                                w1 = None
                            if i == 1 and w in lemma2category:
                                continue
                            lemma2category[w] = categoryid[i]
                            if not w1 == None:
                                lemma2category[w1] = categoryid[i]
                                category2lemma[categoryid[i]].add(w1)
                            else:
                                lemma2category[w1] = categoryid[i]
                                category2lemma[categoryid[i]].add(w1)
    return lemma2category, category2lemma

language2span = {'italian':(1910,2005), 'english':(1785,2013), 'russian':(1750,2022)}

general_theme = set()
specialized_theme = set()

label2feature = {}

with open('mapping.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        label = row.get('Label', '')
        feature = row.get('Mapping', '')
        category = row.get('Category', '')
        if feature:
            label2feature[label] = feature
            if category == 'general text theme':
                general_theme.add(feature)
            elif category == 'specialized text theme':
                specialized_theme.add(feature)
        else:
            label2feature[label] = None

language_features = {}

for language in language2span:
    language_features[language] = set()
    for fname in os.listdir(f'{analysis_path}/{language}'):
        lemma = fname.split('_')[-1].split('.')[0]
        if language == 'russian':
            stats = {'sense_inventory_predict':{}, 'sense_categories_predict':{}, 'semantic_categories_predict':{}, 'colligation_L1_predict':{}, 'colligation_R1_predict':{}, 'diaphasic_preference_predict':{}, 'text_theme_predict':{}, 'morphological_categories_predict':{}}
        else:
            stats = {'sense_inventory_predict':{}, 'sense_categories_predict':{}, 'semantic_categories_predict':{}, 'colligation_L1_predict':{}, 'colligation_R1_predict':{}, 'diaphasic_preference_predict':{}, 'text_theme_predict':{}}

        with open(f'{analysis_path}/{language}/{fname}') as f:
            for line in f:
                line = json.loads(line)
                number = line['spacy_number'] if language == 'italian' else line['form']
                for k in stats:
                    if not k == 'sense_inventory_predict':
                        if type(line[k]) == list:
                            keys = []
                            for v in line[k]:
                                if not v == None and len(v)>0:
                                    if not type(v) == list:
                                        v = v.replace('"','').replace('[','').replace("'",'').replace(']','').strip()
                                        if len(v)>0:
                                            if not label2feature[v] == None:
                                                keys.append(label2feature[v])
                                    else:
                                        for v2 in v:
                                            v2 = v2.replace('"','').replace('[','').replace("'",'').replace(']','').strip()
                                            if not label2feature[v2] == None:
                                                keys.append(label2feature[v2])
                        else:
                            if not line[k] == None:
                                keys = []
                                for v in line[k].replace('[','').replace(']','').replace('"','').replace("'",'').split(','):
                                    v = v.strip()
                                    if len(v)>0:
                                        if not label2feature[v] == None:
                                            keys.append(label2feature[v])
                            else:
                                keys = []
                        for k2 in keys:
                            if k == 'text_theme_predict':
                                if k2 in general_theme:
                                    feature = k+f'_general_theme'
                                else:
                                    feature = k+f'_specialized_theme'
                            else:
                                feature = k+f'_{k2}'
                            language_features[language].add(feature)

    # --- Build correlations per word per year ---
    lemma2category, category2lemma = get_categories(language)
    feature_names = list(language_features[language])
    words = []
    word_categories = []
    word_year_correlations = defaultdict(lambda: defaultdict(dict))
    all_years = set()

    for fname in os.listdir(f'{analysis_path}/{language}'):
        lemma = fname.split('_')[-1].split('.')[0]
        if not lemma in lemma2category or lemma2category[lemma] == 'syntacticplt':
            continue
        if lemma2category[lemma] == 'syntacticplt':
            print(lemma2category[lemma], lemma)
        word_categories.append(lemma2category[lemma])
        words.append(lemma)

        # Initialize feature data per year
        yearly_feature_counts = defaultdict(lambda: {f: [[], []] for f in feature_names})

        with open(f'{analysis_path}/{language}/{fname}') as f:
            for line in f:
                line = json.loads(line)
                number = line['spacy_number'] if language == 'italian' else line['form']
                year = int(line['year'])
                all_years.add(year)
                number_id = 1 if number == 'singular' else 0

                example_features = set()
                for k in stats:
                    if not k == 'sense_inventory_predict':
                        if type(line[k]) == list:
                            keys = []
                            for v in line[k]:
                                if not v == None and len(v)>0:
                                    if not type(v) == list:
                                        v = v.replace('"','').replace('[','').replace("'",'').replace(']','').strip()
                                        if len(v)>0:
                                            if not label2feature[v] == None:
                                                keys.append(label2feature[v])
                                    else:
                                        for v2 in v:
                                            v2 = v2.replace('"','').replace('[','').replace("'",'').replace(']','').strip()
                                            if not label2feature[v2] == None:
                                                keys.append(label2feature[v2])
                        else:
                            if not line[k] == None:
                                keys = []
                                for v in line[k].replace('[','').replace(']','').replace('"','').replace("'",'').split(','):
                                    v = v.strip()
                                    if len(v)>0:
                                        if not label2feature[v] == None:
                                            keys.append(label2feature[v])
                            else:
                                keys = []

                    for k2 in keys:
                        if k == 'text_theme_predict':
                            feature = k + '_general_theme' if k2 in general_theme else k + '_specialized_theme'
                        else:
                            feature = k + '_' + k2
                        example_features.add(feature)

                for feature in feature_names:
                    present = 1 if feature in example_features else 0
                    yearly_feature_counts[year][feature][0].append(present)
                    yearly_feature_counts[year][feature][1].append(number_id)

        # Compute Kendall correlations per year per feature
        for year, fcounts in yearly_feature_counts.items():
            for feature in feature_names:
                x, y = fcounts[feature]
                if len(set(x)) > 1 and len(set(y)) > 1:
                    corr = kendalltau(x, y).statistic
                else:
                    corr = np.nan
                word_year_correlations[lemma][year][feature] = corr

    # --- Group years into decades ---
    decade_bins = defaultdict(list)
    for year in all_years:
        decade = (year // 10) * 10
        decade_bins[decade].append(year)
    decades_sorted = sorted(decade_bins.keys())

    # --- Group and sort features ---
    all_features = set()
    for lemma in word_year_correlations:
        for year in word_year_correlations[lemma]:
            for f, v in word_year_correlations[lemma][year].items():
                if v is not None and abs(v) > 0.3:
                    all_features.add(f)

    # Group feature names
    grouped_data = {}
    for name in all_features:
        group, feature_name = name.split('_predict_', 1)
        group = group.replace('_', ' ')
        grouped_data.setdefault(group, []).append(feature_name)

    # Sort and flatten
    sorted_feature_names = []
    group_labels = []
    current_index = 0

    for group in sorted(grouped_data):
        features = sorted(grouped_data[group])
        group_labels.append((group, current_index))
        for fname in features:
            full_name = f"{group.replace(' ', '_')}_predict_{fname}"
            sorted_feature_names.append(full_name)
        current_index += len(features)
        if group != list(sorted(grouped_data.keys()))[-1]:
            sorted_feature_names.append('')
            current_index += 1

    # --- Plot per word ---
    for lemma in words:
        matrix = []

        for fname in sorted_feature_names:
            if fname == '':
                matrix.append([np.nan]*len(decades_sorted))
            else:
                row = []
                for decade in decades_sorted:
                    # Get all years in the decade for this word
                    decade_vals = [word_year_correlations[lemma].get(y, {}).get(fname, np.nan) for y in decade_bins[decade]]
                    # Filter out NaNs
                    valid_vals = [v for v in decade_vals if not np.isnan(v)]
                    if valid_vals:
                        avg_corr = np.mean(valid_vals)
                    else:
                        avg_corr = np.nan
                    row.append(avg_corr)
                matrix.append(row)

        matrix = np.array(matrix)

        fig, ax = plt.subplots(figsize=(10, 6))
        im = ax.imshow(matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)

        # X-axis: decades
        ax.set_xticks(range(len(decades_sorted)))
        ax.set_xticklabels(decades_sorted, rotation=90, fontsize=8)

        # Y-axis: features
        non_blank_y_indices = [i for i, name in enumerate(sorted_feature_names) if name != '']
        non_blank_y_labels = [name.split('_predict_', 1)[1] for name in sorted_feature_names if name != '']
        ax.set_yticks(non_blank_y_indices)
        ax.set_yticklabels(non_blank_y_labels, fontsize=8)

        # Row group labels
        for group, y_pos in group_labels:
            ax.text(-1, y_pos - 1, group, va='center', ha='right',
                    fontsize=9, fontweight='bold', transform=ax.transData)

        # Title
        ax.set_title(f'Feature Correlation by Decade for "{lemma}"', fontsize=12)

        # Colorbar
        plt.colorbar(im, ax=ax)

        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)

        plt.tight_layout()
        plt.savefig(f'heatmap_time/{language}/{lemma}.png')
        plt.close()

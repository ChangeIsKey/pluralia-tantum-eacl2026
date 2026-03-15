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

for language in language2span:
    lemma2category, category2lemma = get_categories(language)
    words = []
    word_categories = []
    feature_names = list(language_features[language])
    correlations = []
    for fname in os.listdir(f'{analysis_path}/{language}'):
        lemma = fname.split('_')[-1].split('.')[0]
        all_features = set()

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
                            all_features.add(feature)

        feature_counts = {k:[[],[]] for k in all_features}
        line_count = 0
        with open(f'{analysis_path}/{language}/{fname}') as f:
            for line in f:
                line = json.loads(line)
                number = line['spacy_number'] if language == 'italian' else line['form']
                number_id = 0
                line_count = line_count + 1
                if number == 'singular':
                    number_id = 1
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
                                if k2 in general_theme:
                                    feature = k+f'_general_theme'
                                else:
                                    feature = k+f'_specialized_theme'
                            else:
                                feature = k+f'_{k2}'
                            example_features.add(feature)

                for f in feature_counts:
                    if not f in example_features:
                        feature_counts[f][0].append(0)
                    else:
                        feature_counts[f][0].append(1)
                    feature_counts[f][1].append(number_id)


        cs = []
        for f in feature_names:
            if f in feature_counts:
                stat = kendalltau(feature_counts[f][0],feature_counts[f][1]).statistic
                cs.append(stat)
            else:
                cs.append(None)
        if not lemma in lemma2category or lemma2category[lemma] == 'syntacticplt':
            continue
            
        word_categories.append(lemma2category[lemma])
        words.append(lemma)
        correlations.append(cs)

    # Convert to NumPy array if not already
    """
    print(len(words))
    print(len(correlations))
    print(len(feature_names))
    print(len(word_categories))
    print(correlations.shape)
    """
    correlations = np.array(correlations, dtype=float).T

    # Filter: Keep only rows with at least one absolute correlation > 0.3
    mask = np.any(np.abs(correlations) > 0.3, axis=1)
    filtered_correlations = correlations[mask]
    filtered_feature_names = np.array(feature_names)[mask]

    # --- Group rows by feature prefix ---
    grouped_data = {}
    for name, row in zip(filtered_feature_names, filtered_correlations):
        group, feature_name = name.split('_predict_', 1)
        group = group.replace('_', ' ')
        if group not in grouped_data:
            grouped_data[group] = []
        grouped_data[group].append((feature_name, row))

    # Flatten grouped row data with white space between groups
    sorted_feature_names = []
    sorted_correlations = []
    group_labels = []
    current_index = 0

    for group in sorted(grouped_data.keys()):
        features = sorted(grouped_data[group], key=lambda x: x[0])
        group_labels.append((group, current_index))
        for feature_name, row in features:
            sorted_feature_names.append(f"{feature_name}")
            sorted_correlations.append(row)
        current_index += len(features)
        if group != list(sorted(grouped_data.keys()))[-1]:
            sorted_correlations.append(np.full(len(words), np.nan))  # white space row
            sorted_feature_names.append('')
            current_index += 1

    sorted_correlations = np.array(sorted_correlations)  # <-- Now this is defined

    # --- Group columns by word category ---
    grouped_columns = {}
    for word, category in zip(words, word_categories):
        if category not in grouped_columns:
            grouped_columns[category] = []
        grouped_columns[category].append(word)

    # Build new column order
    sorted_words = []
    sorted_indices = []
    column_group_labels = []
    current_col_index = 0

    for category in sorted(grouped_columns.keys()):
        word_list = sorted(grouped_columns[category])
        column_group_labels.append((category, current_col_index + len(word_list)//2))
        for word in word_list:
            idx = words.index(word)
            sorted_words.append(word)
            sorted_indices.append(idx)
        if category != list(sorted(grouped_columns.keys()))[-1]:
            sorted_indices.append(None)
            sorted_words.append('')
            current_col_index += len(word_list) + 1
        else:
            current_col_index += len(word_list)

    # Rearrange correlation columns
    reordered_correlations = []
    for row in sorted_correlations:
        new_row = []
        for idx in sorted_indices:
            if idx is None:
                new_row.append(np.nan)
            else:
                new_row.append(row[idx])
        reordered_correlations.append(new_row)

    reordered_correlations = np.array(reordered_correlations)

    # --- Plot ---
    if language == 'italian' or language == 'russian':
        fig, ax = plt.subplots(figsize=(12, 7))
    else:
        fig, ax = plt.subplots(figsize=(20, 6))
    im = ax.imshow(reordered_correlations, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)

    # X-axis labels
    non_blank_x_indices = [i for i, word in enumerate(sorted_words) if word != '']
    non_blank_x_labels = [word for word in sorted_words if word != '']
    ax.set_xticks(non_blank_x_indices)
    ax.set_xticklabels(non_blank_x_labels, rotation=270, ha='center')

    # Y-axis labels
    non_blank_y_indices = [i for i, name in enumerate(sorted_feature_names) if name != '']
    non_blank_y_labels = [name for name in sorted_feature_names if name != '']
    ax.set_yticks(non_blank_y_indices)
    ax.set_yticklabels(non_blank_y_labels)

    # Group labels for rows
    for group, y_pos in group_labels:
        ax.text(-1, y_pos - 1, group, va='center', ha='right',
                fontsize=10, fontweight='bold', transform=ax.transData)

    # Group labels for columns
    for category, x_pos in column_group_labels:
        ax.text(x_pos, -1.5, maplabels[category], va='bottom', ha='center',
                fontsize=10, fontweight='bold', transform=ax.transData)

    # Remove heatmap boundaries
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Colorbar
    plt.colorbar(im, ax=ax)

    plt.tight_layout()
    plt.savefig(f'heatmap_{language}.svg')
    plt.show()
    plt.close()

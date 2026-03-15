from scipy.stats import kendalltau
import json
import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import transforms
import csv

analysis_path = 'analysis_reasoner'

# Mapping for nicer category labels (Italian)
maplabels = {
    'Significati prevalentemente al plurale ': 'Plural Dominant',
    'Significati esclusivamente alla forma plurale (pluralia tantum semantici)': 'Semantic PT',
    'Sostantivi esclusivamente al pluale (Pluralia tantum formali)': 'Morph. PT',
    'Pluralia tantum formali': 'Morph. PT',
    'plural dominant': 'Plural Dominant',
    'semantic plt': 'Semantic PT',
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

# Languages to process
languages = ['italian', 'english', 'russian']

# Themes for text
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

# First pass: build a dict of per‐language heat‐data arrays
all_heatmaps = {}
global_vals = []
# Collect features per language
language_features = {}
for lang in languages:
    feats = set()
    stats_keys = [
        'sense_categories_predict', 'semantic_categories_predict',
        'colligation_L1_predict', 'colligation_R1_predict',
        'diaphasic_preference_predict', 'text_theme_predict'
    ] + (['morphological_categories_predict'] if lang == 'russian' else [])
    for fname in os.listdir(f'{analysis_path}/{lang}'):
        with open(f'{analysis_path}/{lang}/{fname}') as f:
            for line in f:
                line = json.loads(line)
                for k in stats_keys:
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
                        feats.add(feature)
    language_features[lang] = list(feats)

# Generate and plot heatmaps
for lang in languages:
    lemma2cat, category2lemmas = get_categories(lang)
    feats = language_features[lang]
    words, cats_by_word, corr_rows = [], [], []
    stats_keys = [
        'sense_categories_predict', 'semantic_categories_predict',
        'colligation_L1_predict', 'colligation_R1_predict',
        'diaphasic_preference_predict', 'text_theme_predict'
    ] + (['morphological_categories_predict'] if lang == 'russian' else [])

    # Compute per-word correlations
    for fname in os.listdir(f'{analysis_path}/{lang}'):
        lemma = fname.split('_')[-1].split('.')[0]
        if lemma not in lemma2cat:
            continue
        counts = {f: [[], []] for f in feats}
        with open(f'{analysis_path}/{lang}/{fname}') as f:
            for line in f:
                line = json.loads(line)
                num = line.get('spacy_number') if lang == 'italian' else line.get('form')
                num_id = 1 if num == 'singular' else 0
                active = set()
                for k in stats_keys:
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
                            active.add(feature)
                for f in feats:
                    counts[f][0].append(1 if f in active else 0)
                    counts[f][1].append(num_id)
        corr_vals = [kendalltau(counts[f][0], counts[f][1]).statistic for f in feats]
        if not lemma in lemma2cat or lemma2cat[lemma] == 'syntacticplt':
            continue
        words.append(lemma)
        cats_by_word.append(maplabels[lemma2cat[lemma]])
        corr_rows.append(corr_vals)

    # Prepare correlation matrix
    if not corr_rows:
        print(f"No data for {lang}, skipping.")
        continue
    mat = np.array(corr_rows, dtype=float).T  # [n_feats, n_words]

    # Determine categories based on words
    initial_cats = sorted(set(cats_by_word))
    cat_indices = {c: [i for i,wc in enumerate(cats_by_word) if wc == c] for c in initial_cats}

    # Fallback to all categories if missing
    if not initial_cats:
        initial_cats = list(category2lemmas.keys())
        cat_indices = {c: [i for i,w in enumerate(words) if lemma2cat[w] == c] for c in initial_cats}

    # Use only categories with data
    cats = [c for c, idxs in cat_indices.items() if idxs]
    idxs_list = [cat_indices[c] for c in cats]

    # Aggregate by category
    agg = np.vstack([np.nanmean(mat[:, idxs], axis=1) for idxs in idxs_list]).T

    # Prepare plotting mask (all features)
    mask = np.ones(agg.shape[0], dtype=bool)
    filtered_feats = np.array(feats)[mask]
    filtered_rows = agg[mask]

    # Group features and flatten for heatmap
    grouped = {}
    for name, row in zip(filtered_feats, filtered_rows):
        grp, nm = name.split('_predict_', 1)
        grouped.setdefault(grp.replace('_', ' '), []).append((nm, row))

    heat_data, y_labels = [], []
    for grp in sorted(grouped):
        for nm, row in sorted(grouped[grp], key=lambda x: x[0]):
            heat_data.append(row)
            y_labels.append(nm)
        # add a blank separator row (and label)
        heat_data.append(np.full(len(cats), np.nan))
        y_labels.append('')
    # drop the final separator
    heat_data = np.vstack(heat_data[:-1])
    
    # store and collect for global range
    all_heatmaps[lang] = (heat_data, y_labels, cats)
    global_vals.append(heat_data[~np.isnan(heat_data)])


# Compute global vmin/vmax
all_vals = np.concatenate(global_vals)
vmin, vmax = all_vals.min(), all_vals.max()
print(f"Global correlation range: {vmin:.3f} to {vmax:.3f}")

for lang, (heat_data, y_labels, cats) in all_heatmaps.items():
    fig, ax = plt.subplots(figsize=(10, 6))
    cax = ax.imshow(
        heat_data, 
        cmap='coolwarm',
        aspect='auto',
        vmin=vmin, 
        vmax=vmax
    )

    # X axis: the categories
    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels(
        [maplabels.get(c, c) for c in cats], fontweight='bold', ha='center'
    )

    # Y axis: only label the rows that have non‐empty names
    y_idx = [i for i, lab in enumerate(y_labels) if lab]
    ax.set_yticks(y_idx)
    ax.set_yticklabels([y_labels[i] for i in y_idx])

    # Find blank rows (these are where we’ll write group names)
    blank_idx = [i for i, lab in enumerate(y_labels) if not lab]

    # Use the same order you used to build the heatmap/groups
    group_order = [] # don't sort unless you intend to

    for g in sorted(grouped.keys()):
        if g == 'morphological categories':
            if lang == 'russian':
                group_order.append(g)
        else:
            group_order.append(g)

    # Write each group name on the corresponding blank row
    text_transform = transforms.blended_transform_factory(ax.transAxes, ax.transData)
    x_in_margin = -0.02  # a bit left of the y-axis, in axes coords

    ax.text(
            x_in_margin, -1, group_order[0],
            va='center', ha='right', fontweight='bold',
            transform=text_transform, clip_on=False
    )

    group_order = group_order[1:]

    for row_i, grp in zip(blank_idx, group_order):
        ax.text(
            x_in_margin, row_i, grp,
            va='center', ha='right', fontweight='bold',
            transform=text_transform, clip_on=False
        )
    

    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.colorbar(cax, ax=ax)
    plt.tight_layout()
    plt.savefig(f'heatmap_{lang}_by_category_global_with_labels.svg')
    plt.show()
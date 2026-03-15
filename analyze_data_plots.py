import json
import os
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import matplotlib

analysis_path = "analysis_reasoner"

matplotlib.rcParams.update({
    'font.size': 20,
    'lines.linewidth': 2.5   # <-- sets default line width for all plots
})

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

maplabels = {
    'Significati prevalentemente al plurale ':'Plural Dominant',
    'Significati esclusivamente alla forma plurale (pluralia tantum semantici)': 'Semantic PT',
    'Sostantivi esclusivamente al pluale (Pluralia tantum formali)': 'Formal PT',
    'Pluralia tantum formali': 'Formal PT',
    'plural dominant': 'Plural Dominant',
    'semantic plt':'Semantic PT',
    'morphologicalplt': 'Formal PT',
    'semanticplt': 'Semantic PT',
    'pluraldominant': 'Plural Dominant'
}

language2span = {'italian':(1910,2005), 'english':(1785,2013), 'russian':(1750,2022)}

for language in language2span:
    lemma2category, category2lemma = get_categories(language)
    change_points = {}
    start, end = language2span[language]
    with open(f'{language}/change_points.jsonl') as f:
        for line in f:
            line = json.loads(line)
            change_points[line['lemma']] = []
            for j in range(len(line['change_points'])):
                if line['segment_means'][j] > 0 and line['segment_means'][j+1]<0:
                    change_points[line['lemma']].append(list(range(start,end))[line['change_points'][j]])

    for fname in os.listdir(f'{analysis_path}/{language}'):
        lemma = fname.split('_')[-1].split('.')[0]
        if lemma in lemma2category:
            category = maplabels[lemma2category[lemma]]
            lemma_change_points = change_points[lemma]
            stats = {'sense_inventory_predict':{}, 'sense_categories_predict':{}, 'semantic_categories_predict':{}, 'colligation_L1_predict':{}, 'colligation_R1_predict':{}, 'diaphasic_preference_predict':{}, 'text_theme_predict':{}}
            
            sense_timeseries = {}

            with open(f'{analysis_path}/{language}/{fname}') as f:
                for line in f:
                    line = json.loads(line)
                    number = line['spacy_number'] if language == 'italian' else line['form']
                    year = line['year']
                    sense_id = str(line['sense_inventory_predict'])

                    if not number in sense_timeseries:
                        sense_timeseries[number] = {}

                    if not sense_id in sense_timeseries[number]:
                        sense_timeseries[number][sense_id] = [0]*(end-start+1)

                    sense_timeseries[number][sense_id][year-start] = sense_timeseries[number][sense_id][year-start] + 1



            # Create path
            plot_path = f"plots/{language}/{category}"
            os.makedirs(plot_path, exist_ok=True)

            # Plotting
            years = list(range(start, end + 1))
            fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

            # Collect all unique sense IDs from both singular and plural
            all_senses = set()
            for number in ['singular', 'plural']:
                all_senses.update(sense_timeseries.get(number, {}).keys())
            all_senses = sorted(all_senses)

            # Assign colors to sense_ids using a colormap
            cmap = cm.get_cmap('tab10', len(all_senses))
            color_map = {sense_id: cmap(i) for i, sense_id in enumerate(all_senses)}

            # Compute max y value across both subplots
            max_y = 0
            for number in ['singular', 'plural']:
                for frequencies in sense_timeseries.get(number, {}).values():
                    max_y = max(max_y, max(frequencies))

            for i, number in enumerate(['singular', 'plural']):
                ax = axs[i]
                for sense_id, frequencies in sense_timeseries.get(number, {}).items():
                    ax.plot(years, frequencies, label=f'Sense {sense_id}', color=color_map[sense_id])
                for cp in change_points[lemma]:
                    ax.axvline(x=cp, color='red', linestyle='--')
                ax.set_title(f'{number.capitalize()} Forms')
                ax.set_ylabel('Frequency')
                ax.set_ylim(0, max_y * 1.1)  # same scale + small margin
                ax.grid(True)

            # shared X‐label
            axs[1].set_xlabel('Year')

            # gather handles & labels from both axes
            handles, labels = [], []
            for ax in axs:
                h, l = ax.get_legend_handles_labels()
                handles.extend(h)
                labels.extend(l)

            # remove duplicate labels, keeping only the first handle for each label
            unique = {}
            for h, l in zip(handles, labels):
                if l not in unique:
                    unique[l] = h

            # sort labels alphabetically, and get their handles in the same order
            sorted_labels = sorted(unique.keys())
            sorted_handles = [unique[l] for l in sorted_labels]

            # place one legend at the bottom with alphabetically ordered labels
            fig.legend(
                sorted_handles, sorted_labels,
                loc='lower center',
                ncol=4,
                bbox_to_anchor=(0.5, -0.02),
                frameon=False
            )

            plot_file = f"{plot_path}/{lemma}.png"
            plt.tight_layout(rect=[0, 0.05, 1, 0.95])
            plt.savefig(plot_file, bbox_inches='tight')
            plt.close()
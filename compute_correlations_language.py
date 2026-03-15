from scipy.stats import kendalltau
import json
import os

language2span = {'italian':(1910,2005), 'english':(1785,2013), 'russian':(1750,2022)}

general_theme = set(['daily life', 'nature', 'travel'])
specialized_theme = set(['law', 'biology', 'medicine', 'war', 'philosophy', 'travel', 'geography', 'history', 'arts', 'technology', 'sports', 'philosophy', 'administration', 'religion', 'politics', 'economy', 'pedagogy', 'physics', 'biology', 'music', 'cuisine'])
language_features = {}

for language in language2span:
    language_features[language] = set()
    for fname in os.listdir(f'analysis/{language}'):
        lemma = fname.split('_')[-1].split('.')[0]
        stats = {'sense_inventory_predict':{}, 'sense_categories_predict':{}, 'semantic_categories_predict':{}, 'colligation_L1_predict':{}, 'colligation_R1_predict':{}, 'diaphasic_preference_predict':{}, 'text_theme_predict':{}}

        with open(f'analysis/{language}/{fname}') as f:
            for line in f:
                line = json.loads(line)
                number = line['spacy_number'] if language == 'italian' else line['form']
                for k in stats:
                    if not k == 'sense_inventory_predict':
                        if type(line[k]) == list:
                            keys = [v.replace('"','') for v in line[k] if not v==None and len(v)>0]
                        else:
                            if not line[k] == None:
                                keys = [v.replace('"','') for v in line[k].replace('[','').replace(']','').split(',') if len(v)>0]
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
                            if feature == 'diaphasic_preference_predict_neutral':
                                continue
                            if feature == 'semantic_categories_predict_concrete':
                                continue
                            if feature == 'semantic_categories_predict_inanimate':
                                continue
                            language_features[language].add(feature)



for language in language2span:
    all_features = language_features[language]
    feature_counts = {k:[[],[]] for k in all_features}
    for fname in os.listdir(f'analysis/{language}'):
        lemma = fname.split('_')[-1].split('.')[0]
        stats = {'sense_inventory_predict':{}, 'sense_categories_predict':{}, 'semantic_categories_predict':{}, 'colligation_L1_predict':{}, 'colligation_R1_predict':{}, 'diaphasic_preference_predict':{}, 'text_theme_predict':{}}
        
        with open(f'analysis/{language}/{fname}') as f:
            for line in f:
                line = json.loads(line)
                number = line['spacy_number'] if language == 'italian' else line['form']
                number_id = 0
                if number == 'singular':
                    number_id = 1
                example_features = set()
                for k in stats:
                    if not k == 'sense_inventory_predict':
                        if type(line[k]) == list:
                            keys = [v.replace('"','') for v in line[k] if not v==None and len(v)>0]
                        else:
                            if not line[k] == None:
                                keys = [v.replace('"','') for v in line[k].replace('[','').replace(']','').split(',') if len(v)>0]
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
                    if f == 'diaphasic_preference_predict_neutral':
                        continue
                    if f == 'semantic_categories_predict_concrete':
                        continue
                    if f == 'semantic_categories_predict_inanimate':
                        continue
                    if not f in example_features:
                        feature_counts[f][0].append(0)
                    else:
                        feature_counts[f][0].append(1)
                    feature_counts[f][1].append(number_id)


        #print(lemma)
    print(language)
    for f in feature_counts:
        stat = kendalltau(feature_counts[f][0],feature_counts[f][1]).statistic
        #if stat >= 0.4 or stat <= -0.4:
        print(f, stat)

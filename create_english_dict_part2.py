import json
import re

sense2definition = {}

with open('/mimer/NOBACKUP/groups/cik_data/cassotti/oed_data/sense_history.txt') as f:
    for line in f:
        line = json.loads(line)
        sense2definition[line['sense_id']] = line['definition']


plur_stat = [
    'With plural agreement'
    'frequently in plural',
    'usually in plural',
    'commonly in plural',
    'Almost always in plural',
    'also in plural',
    'chiefly in plural',
    'in plural',
    'with singular agreement',
    'with plural or singular agreement',
    'with singular or plural agreement'
]

# Compile a case-insensitive regex pattern that matches any of the phrases
pattern = re.compile(r'\b(?:' + '|'.join(re.escape(p) for p in plur_stat) + r')\b', flags=re.IGNORECASE)

def remove_plural_status(text):
    return pattern.sub('', text).strip()

with open('temp_en_dict.txt') as f:
    with open('en_dict.txt','w+') as g:
        lemmas = f.read().split('\n\n\n')
        for lemma_line in lemmas:
            new_lines = []
            for j,line in enumerate(lemma_line.split('\n')):
                if j == 0:
                    new_lines.append(line)
                else:
                    print(line)
                    entry, sid = line.split('\t')
                    definition = sense2definition[sid]
                    if not definition == None:
                        definition = remove_plural_status(definition)
                        new_lines.append(f'{entry}\t{definition}')
                    else:
                        print(lemma_line)

            new_lines = '\n'.join(new_lines)
            g.write(new_lines+'\n\n\n')

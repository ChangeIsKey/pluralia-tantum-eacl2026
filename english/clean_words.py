import json 
import os



for fname in os.listdir('old_words'):
    with open(f'old_words/{fname}') as f:
        with open(f'words/{fname}','w+') as g:
            for line in f:
                line = json.loads(line)
                if line['end'] == None and line['lemma'][0].islower():
                    g.write(json.dumps(line)+'\n')


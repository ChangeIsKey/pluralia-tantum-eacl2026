

sing2plur = {}
with open(f'ru_lemmas.txt') as f:
    for line in f:
        sing, plur = line.replace('\n','').split('\t')
        sing2plur[sing] = plur


with open(f'dataset2.csv','w+') as g:    
    with open(f'dataset.csv') as f:
        for j,line in enumerate(f):
            if j == 0:
                g.write(line)
            else:
                line = line.replace('\n','').split(';')
                new_line = []
                for w in line:
                    if ''.join(filter(lambda x: not x.isdigit(), w)).lower() in sing2plur:
                        new_line.append(sing2plur[''.join(filter(lambda x: not x.isdigit(), w)).lower()])
                    else:
                        new_line.append(w)
                g.write(';'.join(new_line)+'\n')

import os


with open('years.txt', 'w+') as g:
    for fname in sorted(os.listdir('dictionaries')):
        N = 0
        V = 0
        year = int(fname.split('.')[0])
        with open(f'dictionaries/{fname}') as f:
            for line in f:
                line_split = line.replace('\n','').split('\t')
                n = line_split[-1]
                n = int(n)
                N = N + n
                V = V + 1
        g.write(f'{year}\t{N}\t{V}\n')
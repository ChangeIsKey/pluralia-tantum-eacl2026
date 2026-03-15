import json
import os
import numpy as np 
from matplotlib import pyplot as plt

language2span = {'italian':(1910,2005), 'english':(1785,2013), 'russian':(1750,2022)}
print('Language\tCorpus\tTime span\tN. Tokens\tUnique Words')
for language in language2span:
    tot_C, tot_V = 0,0

    with open(f'{language}/years.txt') as f:
        for line in f:
            year, C, V = line.replace('\n','').split('\t')
            tot_C = int(C) + tot_C
            tot_V = int(V) + tot_V
    print(language+'\t '+'\t'+f'{language2span[language][0]}-{language2span[language][1]}\t'+str(tot_C)+f'\t{tot_V}')
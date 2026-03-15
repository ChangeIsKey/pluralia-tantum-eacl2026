import gzip
import argparse
import json
import pickle
from corpora import load_corpus
import re
from nltk.tokenize import word_tokenize
from tqdm import tqdm

print('Dictionary creation', flush=True)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Corpora statistics',
        description="Computation of corpus statistics")

    conf = 'times.config'
    corpus = load_corpus(conf)


    for time_point in tqdm(corpus.time_points, 'Processing time points...'):
        with open(f'dictionaries/{time_point}.txt','w+') as f:
            D = corpus.dictionary(time_point)
            for token in D:
                f.write(f'{token}\t{D[token]}\n')

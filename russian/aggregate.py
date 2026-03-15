import csv
import json
import os
from prereform2modern import Processor
import re
import pandas as pd
from tqdm import tqdm

import re

def extract_year_average(s):
    # First, extract and remove full dates (e.g., DD.MM.YYYY and YYYY.MM)
    full_date_matches = re.findall(r'\b\d{2}\.\d{2}\.\d{4}\b', s)
    short_date_matches = re.findall(r'\b\d{4}\.\d{2}\b', s)

    years = []

    # Extract year from full dates (DD.MM.YYYY)
    for date in full_date_matches:
        try:
            years.append(int(date.split('.')[-1]))
        except ValueError:
            continue

    # Extract year from short dates (YYYY.MM)
    for date in short_date_matches:
        try:
            years.append(int(date.split('.')[0]))
        except ValueError:
            continue

    # Remove matched dates from string to avoid double-counting
    cleaned = s
    for date in full_date_matches + short_date_matches:
        cleaned = cleaned.replace(date, '')

    # Now extract year or year ranges
    tokens = re.findall(r'\b\d{3,4}(?:-\d{3,4})?\b', cleaned)
    for token in tokens:
        if '-' in token:
            try:
                start, end = map(int, token.split('-'))
                years.append((start + end) / 2)
            except ValueError:
                continue
        else:
            try:
                years.append(int(token))
            except ValueError:
                continue

    if not years:
        print(years)
        return None

    return int(sum(years) / len(years)) 



for fname in tqdm(os.listdir('output-revised'),'Processing lemmas..'):
    # Open the CSV and JSONL files
    new_fname = fname.split('.')[0]+'.jsonl'
    examples = set()
    with open(f'json/{new_fname}','w+') as g:
        with open(f'output-revised/{fname}', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                json_line = json.dumps(row, ensure_ascii=False)
                example_source = row['Example source']
                left_context = row['Left context']
                center_word = row['Center']
                center_word_processed, _, _ = Processor.process_text(text=center_word, show=False, delimiters=False,check_brackets=False)
                right_context = row['Right context']
                time = row['Created']
                year = extract_year_average(time)
                if not len(str(year)) == 4:
                    print('Error', year, time)

                punct = row['Punct'].strip()
                left_context, changes, s_json = Processor.process_text(
                    text=left_context,
                    show=False,
                    delimiters=False,
                    check_brackets=False
                )
                left_context = re.sub(r"\s+", " ", left_context)
                if len(left_context)>0 and left_context[-1] == ' ':
                    left_context = left_context[:-1]

                center_word, changes, s_json = Processor.process_text(
                    text=center_word,
                    show=False,
                    delimiters=False,
                    check_brackets=False
                )
                center_word = re.sub(r"\s+", " ", center_word)

                right_context, changes, s_json = Processor.process_text(
                    text=right_context,
                    show=False,
                    delimiters=False,
                    check_brackets=False
                )
                right_context = re.sub(r"\s+", " ", right_context)

                punct = f' {punct}'

                sentence_parts = []
                if left_context:
                    sentence_parts.append(left_context)
                sentence_parts.append(center_word + punct)
                if right_context:
                    sentence_parts.append(right_context)
                sentence = " ".join(sentence_parts)
                start_offset = len(left_context) + 1 if left_context else 0
                end_offset = start_offset + len(center_word)
                if not punct == ' —':
                    if punct == ' ':
                        sentence = sentence[:end_offset] + sentence[end_offset+1:]
                else:
                    sentence = sentence[:end_offset] + sentence[end_offset+1:]

                start, end = start_offset, end_offset

                number = row['Number']

                example_source = example_source+f'_{start}_{end}'
                if not example_source in examples:
                    examples.add(example_source)
                    D = {'word':center_word_processed, 'year':year, 'text':sentence, 'start':start, 'end':end, 'form':number, 'id':example_source, 'created':row['Created']}
                    g.write(json.dumps(D)+'\n')

                if not sentence[start:end] == center_word_processed:
                    print(center_word_processed)
                    print('original start-end', row['Start'], row['End'])
                    print('new start-end', start, end)
                    print('sentence', sentence)
                    print('oriignal sentence', row['Processed sentence'])
                    print('original original sentence', left_context, center_word, right_context)
                    print(sentence[start:end])
                    print('------------')
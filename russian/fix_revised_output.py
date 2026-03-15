import pandas as pd
import spacy
import spacy_udpipe
import os
import re
import json

folder_name = "output-revised"
output_folder = "output-final"

for fname in os.listdir(output_folder):
    os.remove(f'{output_folder}/{fname}')

for fname in os.listdir(folder_name):
    # Read the CSV file
    df = pd.read_csv(f'{folder_name}/{fname}', delimiter=';', quoting=1, encoding='utf-8')  # quoting=1 is pd.io.common.csv_quoting.QUOTE_ALL

    # Function to safely strip text
    def safe_strip(text):
        if pd.isna(text):
            return ""
        return text.strip()


    # Function to extract lemma and number using reconstructed sentence
    def extract_lemma_number(row):
        left_context = safe_strip(row['Left context'])
        center_word = safe_strip(row['Center'])
        right_context = safe_strip(row['Right context'])
        punct = safe_strip(row['Punct'])

        left_context, changes, s_json = Processor.process_text(
            text=left_context,
            show=False,
            delimiters=False,
            check_brackets=False
        )
        left_context = re.sub(r"\s+", " ", left_context)

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

        return sentence, start_offset, end_offset, lemma, number, annotator_system


    # Apply the function and create new columns
    df[['Processed sentence','Start','End','Lemma', 'Number', 'AnnotatorSystem']] = df.apply(extract_lemma_number, axis=1, result_type='expand')

    if len(df['Lemma'].value_counts()) > 0:
        lemma = df['Lemma'].value_counts().idxmax()
        output_path = f'{output_folder}/{lemma}.csv'

        # Check if the file already exists
        if os.path.exists(output_path):
            # Append data without header
            df.to_csv(output_path, mode='a', index=False, sep=';', quoting=1, header=False)
        else:
            # Create new file with header
            df.to_csv(output_path, mode='w', index=False, sep=';', quoting=1, header=True)

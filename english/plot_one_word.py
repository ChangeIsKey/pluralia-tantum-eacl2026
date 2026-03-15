import json
from matplotlib import pyplot as plt

import matplotlib

matplotlib.rcParams.update({
    'font.size': 20,
    'lines.linewidth': 2.5   # <-- sets default line width for all plots
})

language2span = {'italian':(1910,2005), 'english':(1785,2013), 'russian':(1750,2022)}

with open('change_points.jsonl') as f:
    for line in f:
        line = json.loads(line)
        means = line['segment_means']
        for j, m in enumerate(means[1:-1]):
            if means[j-1] > 1 and means[j] < 0:
                print(line['lemma'])
                print(means[j-1],means[j])
                print(line['segment_means'])

word = "facility"
language = "english"
sing_t = []
plur_t = []
start,end = language2span[language]
years = list(range(start,end+1))

with open('frequencies.jsonl') as f:
    for line in f:
        line = json.loads(line)
        lemma = line['lemma']
        if lemma == word:
            sing_t, plur_t = line['relative_frequencies']
            break

from matplotlib.ticker import ScalarFormatter

# Plot the frequencies
plt.figure(figsize=(12, 6))
plt.plot(years, sing_t, label='Singular Form')
plt.plot(years, plur_t, label='Plural Form')
plt.xlabel("Year")
plt.ylabel("Relative Frequency")

# Use scientific notation for the y-axis
formatter = ScalarFormatter(useMathText=True)
formatter.set_scientific(True)
formatter.set_powerlimits((-2, 2))  # Controls when scientific notation kicks in
plt.gca().yaxis.set_major_formatter(formatter)

plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(word + '.png')
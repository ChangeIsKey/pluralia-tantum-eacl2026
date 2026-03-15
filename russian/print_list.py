import os


with open('files.txt','w+') as f:
    for fname in sorted(os.listdir('output')):
        fname = fname.split('.')[0]
        f.write(fname+'\n')

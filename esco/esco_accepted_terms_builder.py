'''
Converter from occupations csv into occupations tsv (code, acceptedTerm)
that will contain several accepted terms per each code.

Usage:
    python esco_accepted_terms_builder.py with_codes_occupations_es.csv

Author: https://github.com/mmaguero
Refactorer: https://github.com/aasensios
'''

import pandas as pd
import numpy as np
import sys

# primary_key = 'iscoGroup'
primary_key = 'code'

# args
input_file = sys.argv[1]
output_file = f'{input_file.split(".")[0]}.tsv'

# read data
data = pd.read_csv(input_file, encoding = 'utf8', sep=',')
data[primary_key] = data[primary_key].apply(str)

# write output
to_file = []
with open(output_file, "w+") as f:

    for index, row in data.iterrows():

        # desc columns: preferredLabel	altLabels	hiddenLabels
        desc = []
        if pd.notna(row['preferredLabel']): 
            for lbl in row['preferredLabel'].split('/'):
                desc.append(str(lbl).strip())
        if pd.notna(row['altLabels']): 
            for lbl in row['altLabels'].split('\n'):
                desc.append(str(lbl).strip())
        if pd.notna(row['hiddenLabels']): 
            for lbl in row['hiddenLabels'].split('\n'):
                desc.append(str(lbl).strip())

        for d in desc:
            if len(d.strip())>0:
                d = str(d).replace('/','') if d.strip().startswith('/') else d
                to_file.append([str(row[primary_key]),str(d).strip()])
    
    unique_rows = np.unique(to_file, axis=0)
    for k, v in unique_rows:
        f.write("{}\t{}\n".format(k,v))

import pandas as pd
import numpy as np
import sys

# args
fileIn = sys.argv[1]

# read data
data = pd.read_csv(fileIn, encoding = 'utf8', sep=',')
data['iscoGroup'] = data['iscoGroup'].apply(str)

# write output
to_file = []
with open(fileIn[:-4]+".tsv", "w+") as f:
    
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
                to_file.append([str(row['iscoGroup']),str(d).strip()])
    
    unique_rows = np.unique(to_file, axis=0)
    for k, v in unique_rows:
        f.write("{}\t{}\n".format(k,v))
        

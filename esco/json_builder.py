'''
Convert from occupations full csv into json, taking into account
the preferred, alternative and hidden labels each ESCO code might contain.

Usage: python json_builder.py occupations_es_extra_code.csv esco.json

Author: https://github.com/aasensios
'''

import csv
import json
import sys

input_filename = sys.argv[1]
output_filename = sys.argv[2]

with open(input_filename) as f:
    reader = csv.DictReader(f)
    rows = list(reader)

with open(output_filename, 'w') as f:
    terms = list()
    for row in rows:
        code = row.get('code').strip()
        name = row.get('preferredLabel').strip()
        alternatives = [alternative.strip() for alternative in row.get('altLabels').splitlines()]
        hiddens = [hidden.strip() for hidden in row.get('hiddenLabels').splitlines()]
        synonyms = list(set(alternatives + hiddens))
        term = dict(code=code, name=name, synonyms=synonyms)
        terms.append(term)

    json.dump(terms, f, ensure_ascii=False, indent=2)

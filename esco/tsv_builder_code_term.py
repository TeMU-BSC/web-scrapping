'''
Convert from occupations full csv into (code\tterm) tsv, taking into account
the preferred, alternative and hidden labels each ESCO code might contain.

Usage: python tsv_builder_code_term.py occupations_es_extra_code.csv esco_codes_occupations_es.tsv

Important: Once the tsv file is generated, it should be manually cleaned,
searching for slashes ('/') in masculine/femenine differentiated terms,
adding new lines as needed.

Author: https://github.com/aasensios
'''

import csv
import os
import sys

input_filename = sys.argv[1]
output_filename = sys.argv[2]

with open(input_filename) as f:
    reader = csv.DictReader(f)
    rows = list(reader)

with open(output_filename, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['code', 'term'], dialect=csv.excel_tab)
    writer.writeheader()

    rows_to_write = list()
    for row in rows:
        code = row.get('code')
        preferred = row.get('preferredLabel').split('/')
        alternative = row.get('altLabels').splitlines()
        hidden = row.get('hiddenLabels').splitlines()
        terms = set([term.strip() for term in preferred + alternative + hidden])
        rows_to_write.extend([dict(code=code, term=term) for term in terms])
    
    sorted_rows_to_write = sorted(rows_to_write, key=lambda row: (row.get('code'), row.get('term')))
    writer.writerows(sorted_rows_to_write)

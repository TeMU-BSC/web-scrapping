'''
Scrap the exact (granular) code for every occupation in
"European Skills/Competences, qualifications and Occupations" (ESCO) website:
https://ec.europa.eu/esco/portal/occupation

Previously, all occupations terms in Spanish have been downloaded from:
https://ec.europa.eu/esco/portal/download

For each row of the file occupations_es.csv, the script bypasses the ESCO's
website redirections with a nice ad-hoc hack and extracts the exact ESCO code
from the HTML (which is the first <p> element). Finally, a new csv file is
written with an extra 'code' column.

Usage: python scrapper.py occupations_es.csv occupations_es_extra_code.csv

Author: https://github.com/aasensios
'''

import csv
import sys
import urllib.parse

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://ec.europa.eu/esco/portal/occupation'
input_filename = sys.argv[1]
output_filename = sys.argv[2]


def scrap_esco_code(concept_uri: str) -> str:
    '''Get the exact ESCO code from HTML page.'''
    safe_url = urllib.parse.quote(concept_uri, safe='')

    # URL format after multiple redirections by ESCO website
    url = f'{BASE_URL}?uri={safe_url}&conceptLanguage=es&full=true#&uri={concept_uri}'

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    code = soup.p.text
    return code

with open(input_filename) as input_file:
    rows = list(csv.DictReader(input_file))
    fieldnames = list(rows[0].keys())
    fieldnames.append('code')

with open(output_filename, 'w') as output_file:
    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    writer.writeheader()

for row in rows:
    concept_uri = row.get('conceptUri')
    code = scrap_esco_code(concept_uri)
    row['code'] = code

    with open(output_filename, 'a') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writerow(row)

    # visual progress in terminal
    print(code, row.get('preferredLabel'))

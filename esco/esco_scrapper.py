'''
Script to scrap the exact codes of every occupation from
"European Skills/Competences, qualifications and Occupations" (ESCO) website.

Previously, we have downloaded all occupations terms in Spanish via the portal:
https://ec.europa.eu/esco/portal/download

File: ./occupations_es.csv

For each row of that csv file, the script visits the conceptUri (with a nice
hack to avoid internal website redirections) and extracts the exact ESCO code
from the webpage (that is the first <p> element).

Finally, it writes a new csv file with an extra column for the ESCO code.

Usage:
    python test_esco.py occupations_es.csv

Author: https://github.com/aasensios
'''

import csv
import sys
import urllib.parse

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://ec.europa.eu/esco/portal/occupation'
input_filename = sys.argv[1]
output_filename = f'with_codes_{input_filename}'


def scrap_esco_code(concept_uri):
    safe_url = urllib.parse.quote(concept_uri, safe='')
    url = f'{BASE_URL}?uri={safe_url}&conceptLanguage=es&full=true#&uri={concept_uri}'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    code = soup.p.text
    return code

with open(input_filename) as input_file:
    rows = list(csv.DictReader(input_file))
    fieldnames = rows[0].keys()

with open(output_filename, 'w') as output_file:
    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        concept_uri = row.get('conceptUri')
        code = scrap_esco_code(concept_uri)
        row['code'] = code
        writer.writerow(row)

        # for visual progress in terminal
        print(code, row.get('preferredLabel'))

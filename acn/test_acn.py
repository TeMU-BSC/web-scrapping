'''
Script to download news from Agència Calatana de Notícies (ACN) website
using Selenium IDE and Selenium Web Driver.

This scrapper is prepared to run without graphical interface, using the chrome
driver and faking a screen via a python wrapper for Xvfb.

For each article, the script checks if that article has been previously
downloaded, so it can be executed in different moments avoiding duplicates.

https://addons.mozilla.org/en-US/firefox/addon/selenium-ide/
https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-linux64.tar.gz

Usage:
    sudo apt install xvfb
    xvfb-run pytest -s test_acn.py

Notes:
    Xvfb has to be installed on the system.
    -s (--capture=no) option allows to see stdout like print statements inside test_* functions.

Author: https://github.com/aasensios
'''

import json
import os
import pathlib
import time

import pytest
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

BASE_URL = 'https://www.acn.cat'
USERNAME = 'TEXT'
PASSWORD = '1865GB'
DOWNLOADS_DIR = os.path.join(pathlib.Path().absolute(), 'downloaded')
METADATA_DIR = os.path.join(pathlib.Path().absolute(), 'articles_with_metadata')
SCRAPPED_URLS_FILE_PATH = pathlib.Path('scrapped_urls.txt')
LAST_VISITED_PAGE_FILE_PATH = pathlib.Path('last_visited_page.txt')

if not os.path.isfile(SCRAPPED_URLS_FILE_PATH):
    SCRAPPED_URLS_FILE_PATH.touch()
if not os.path.isdir(DOWNLOADS_DIR):
    os.mkdir(DOWNLOADS_DIR)
if not os.path.isdir(METADATA_DIR):
    os.mkdir(METADATA_DIR)

# Read what page start scrapping from.
if starting_page := input('\nStarting page for scrapping [press ENTER to start from last visited page]: '):
    page_url = f'{BASE_URL}/text/{starting_page}'
else:
    with open(LAST_VISITED_PAGE_FILE_PATH) as f:
        page_url = f.read()

# Store the visited URLs to avoid downloading and parsing the same articles more than once.
with open(SCRAPPED_URLS_FILE_PATH) as f:
    scrapped_urls = list(f.read().splitlines())
print(f'Total scrapped articles: {len(scrapped_urls)}')

class TestAcn():
    def setup_method(self, method):
        self.vars = {}

        # Start a virtual display before lanching Chrome.
        self.disp = Display().start()

        # https://blog.testproject.io/2018/02/20/chrome-headless-selenium-python-linux-servers/
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox') # Required when running as root user; otherwise you would get no sandbox errors. 
        prefs = {
            "download.default_directory": DOWNLOADS_DIR,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
        }
        chrome_options.add_experimental_option('prefs', prefs)
        self.driver = webdriver.Chrome(
            executable_path=os.path.join(pathlib.Path().absolute(), 'chromedriver_linux64_85.0.4183.87', 'chromedriver'),
            options=chrome_options,
            service_args=['--verbose', '--log-path=./chromedriver.log']
        )

    def teardown_method(self, method):
        self.driver.quit()
        self.disp.stop()

    def test_download_news_with_metadata(self):

        # Login
        self.driver.get(f"{BASE_URL}/subscriptors")
        self.driver.find_element_by_id("username").send_keys(USERNAME)
        self.driver.find_element_by_id("password").send_keys(PASSWORD)
        self.driver.find_element_by_xpath("//button[@type=\'submit\']").click()

        # Accept cookies in bottom banner to avoid 'selenium.common.exceptions.ElementClickInterceptedException'.
        self.driver.find_element_by_class_name('accept').click()

        # Go to section where news can be downloaded as plain text files.
        self.driver.get(page_url)
        while True:
            current_page_url = self.driver.current_url

            # Overwrite the last page visited.
            with open(LAST_VISITED_PAGE_FILE_PATH, 'w') as f:
                f.write(current_page_url)

            # Terminal feedback on currently precessed page.
            print('')
            print(current_page_url)

            article_elements = self.driver.find_elements_by_xpath("//a[starts-with(@href, '/text/item')]")
            articles_urls = [href for element in article_elements if (href := element.get_attribute("href")) not in scrapped_urls]
            for article_url in articles_urls:

                # Terminal feedback on currently processed article.
                print(article_url)

                # Load the article in emulated browser.
                self.driver.get(article_url)

                # Get article's id.
                id = self.driver.find_elements_by_class_name('element-staticcontent')[1].text.split(': ')[1]
                text_file = os.path.join(DOWNLOADS_DIR, f'noticia_{id}.txt')

                # Download the plain text file and wait until the file is downloaded.
                self.driver.find_element_by_xpath("//a[starts-with(@id, 'download')]").click()
                while not os.path.isfile(text_file):
                    time.sleep(0.5)

                # Get metadata.
                publication_datetime = self.driver.find_element_by_css_selector(".uk-text-left > .uk-margin-small").text
                categories = self.driver.find_element_by_class_name('element-itemcategory').text.split(': ')[1].split(', ')
                related_categories = self.driver.find_elements_by_class_name('element-relatedcategories')

                # Some articles may not have some metadata.
                try:
                    section_subsection = related_categories[0].text.split(': ')[1].split(', ')
                    section = section_subsection[0]
                    subsection = section_subsection[1] if len(section_subsection) > 1 else None
                except:
                    section = None
                    subsection = None
                
                try:
                    territorial_coding = related_categories[1].text.split(': ')[1].split(', ') if len(related_categories) > 1 else None
                except:
                    territorial_coding = None

                try:
                    # Fix missing colon ':' in HTML rendering.
                    tags = self.driver.find_element_by_class_name('element-itemtag').text.replace('Etiquetes', 'Etiquetes:').split(': ')[1].split(', ')
                except expected_conditions.NoSuchElementException:
                    tags = list()

                # Parse article's text content.
                with open(text_file) as f:
                    text = f.read()
                    title = text.splitlines()[0]
                    subtitle = text.splitlines()[1]
                    body = '\n'.join(line for line in text.splitlines()[2:] if line)

                metadata = dict(
                    url=article_url,
                    publication_datetime=publication_datetime,
                    text=text,
                    title=title,
                    subtitle=subtitle,
                    body=body,
                    section=section,
                    subsection=subsection,
                    territorial_coding=territorial_coding,
                    categories=categories,
                    id=id,
                    tags=tags,
                )

                # Write metadata and text in a json file.
                with open(os.path.join(METADATA_DIR, f'noticia_{id}.json'), 'w') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)

                # Write the scrapped URL in a file to avoid parsing the same article more than once in further executions.
                with open(SCRAPPED_URLS_FILE_PATH, 'a') as f:
                    f.write(f'{article_url}\n')

            # Go back to current page and look for next page button or finish if last page.
            self.driver.get(current_page_url)
            if not self.driver.find_elements_by_link_text("»"):
                break
            self.driver.find_element_by_link_text("»").click()

        # Logout
        self.driver.get(f'{BASE_URL}/surt')

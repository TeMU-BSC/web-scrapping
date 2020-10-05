'''
Script to download news from Agència Calatana de Notícies (ACN) website
using Selenium IDE and Selenium Web Driver for Firefox.

This scrapper is prepared to run without graphical interface, using the chrome
driver and faking a screen via a python wrapper for Xvfb.

For each article, the script checks if that article has been previously
downloaded, so it can be executed in different moments avoiding duplicates.

https://addons.mozilla.org/en-US/firefox/addon/selenium-ide/
https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-linux64.tar.gz

Usage: pytest -s acn/test_acn.py
Note: -s (--capture=no) option allows to see stdout like print statements inside test_* functions.

Author: https://github.com/aasensios
'''

import json
import os
import pathlib

import pytest
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException

CHROMEDRIVER_PATH = os.path.join(pathlib.Path().absolute(), 'chromedriver_linux64_85.0.4183.87', 'chromedriver')
PROJECT_DIR = 'acn'
DOWNLOADS_DIR = os.path.join(pathlib.Path().absolute(), PROJECT_DIR, 'downloaded')
METADATA_DIR = os.path.join(pathlib.Path().absolute(), PROJECT_DIR, 'articles_with_metadata')
BASE_URL = 'https://www.acn.cat'
USERNAME = 'TEXT'
PASSWORD = '1865GB'

if not os.path.isdir(DOWNLOADS_DIR):
    os.mkdir(DOWNLOADS_DIR)
if not os.path.isdir(METADATA_DIR):
    os.mkdir(METADATA_DIR)

visited_urls = list()
for dirpath, dirnames, filenames in os.walk(METADATA_DIR):
    for filename in filenames:
        with open(os.path.join(dirpath, filename)) as f:
            url = json.load(f).get('url')
            visited_urls.append(url)

print(f'already processed articles: {len(visited_urls)}')

class TestAcn():
    def setup_method(self, method):
        self.vars = {}

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

        # Start a virtual display before lanching Chrome.
        Display().start()

        self.driver = webdriver.Chrome(
            executable_path=CHROMEDRIVER_PATH,
            options=chrome_options,
            service_args=['--verbose', '--log-path=./chromedriver.log']
        )

    def teardown_method(self, method):
        self.driver.quit()

    def test_download_news_with_metadata(self):

        # Login
        self.driver.get(f"{BASE_URL}/subscriptors")
        self.driver.find_element_by_id("username").send_keys(USERNAME)
        self.driver.find_element_by_id("password").send_keys(PASSWORD)
        self.driver.find_element_by_xpath("//button[@type=\'submit\']").click()

        # Accept cookies in bottom banner to avoid 'selenium.common.exceptions.ElementClickInterceptedException'.
        self.driver.find_element_by_class_name('accept').click()

        # Read what page start scrapping from.
        with open(os.path.join(PROJECT_DIR, 'acn_last_visited_page.txt')) as f:
            page_url = f.read()
        if picked_page := input('Start scrapping from page [press RETURN to start from last visited page]: '):
            page_url = f'{BASE_URL}/text/{picked_page}'

        # Go to section where news can be downloaded as plain text files.
        self.driver.get(page_url)
        while True:
            current_page_url = self.driver.current_url

            # Override tha last page visited.
            with open(os.path.join(PROJECT_DIR, 'acn_last_visited_page.txt'), 'w') as f:
                f.write(current_page_url)

            # Terminal feedback on currently precessed page.
            print('')
            print(current_page_url)

            article_elements = self.driver.find_elements_by_xpath("//a[starts-with(@href, '/text/item')]")
            articles_urls = [element.get_attribute("href") for element in article_elements if element.get_attribute("href") not in visited_urls]
            for article_url in articles_urls:

                # Terminal feedback on currently processed article.
                print(article_url)

                # Load the article in emulated browser.
                self.driver.get(article_url)

                # Download the txt file.
                self.driver.find_element_by_xpath("//a[starts-with(@id, 'download')]").click()

                # Get metadata.
                publication_datetime = self.driver.find_element_by_css_selector(".uk-text-left > .uk-margin-small").text
                section_subsection = self.driver.find_elements_by_class_name('element-relatedcategories')[0].text.split(': ')[1].split(', ')
                section = section_subsection[0]
                subsection = section_subsection[1] if len(section_subsection) > 1 else None
                territorial_coding = self.driver.find_elements_by_class_name('element-relatedcategories')[1].text.split(': ')[1].split(', ')
                categories = self.driver.find_element_by_class_name('element-itemcategory').text.split(': ')[1].split(', ')
                id = self.driver.find_elements_by_class_name('element-staticcontent')[1].text.split(': ')[1]

                # Some articles may not have assigned tags.
                try:
                    # Fix missing colon ':'.
                    tags = self.driver.find_element_by_class_name('element-itemtag').text.replace('Etiquetes', 'Etiquetes:').split(': ')[1].split(', ')
                except NoSuchElementException:
                    tags = list()

                # Parse article's text content.
                with open(os.path.join(DOWNLOADS_DIR, f'noticia_{id}.txt')) as f:
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

            # Go back to current page and look for next page button or finish if last page.
            self.driver.get(current_page_url)
            if not self.driver.find_elements_by_link_text("»"):
                break
            self.driver.find_element_by_link_text("»").click()

        # Logout
        self.driver.find_element_by_link_text("Surt").click()

'''
Script to download news from Agència Calatana de Notícies (ACN) website
using Selenium IDE and Selenium Web Driver for Firefox.

https://addons.mozilla.org/en-US/firefox/addon/selenium-ide/
https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-linux64.tar.gz

Usage: pytest -s test_acn.py
Note: -s (--capture=no) option allows to see stdout like print statements inside test_* functions.

Author: https://github.com/aasensios
'''

# Generated by Selenium IDE
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from pathlib import Path
import os


class TestAcn():
    def setup_method(self, method):
        # Prevent download dialog
        # https://stackoverflow.com/a/62254004
        downloads_dir = os.path.join(Path().absolute(), 'downloaded_files')
        options = webdriver.FirefoxOptions()
        options.set_preference('browser.download.manager.showWhenStarting', False)
        options.set_preference('browser.download.dir', downloads_dir)
        options.set_preference('browser.download.folderList', 2)  # 0: Desktop, 1: Downloads, 2: custom directory
        options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/html')  # Checked 'content-type: text/html' in Browser: F12 > Network > Headers
        self.driver = webdriver.Firefox(
            executable_path=os.path.join(Path().absolute(), 'geckodriver-v0.27.0-linux64/geckodriver'),
            options=options,
        )
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_download_text_files(self):

        # Login
        self.driver.get("https://www.acn.cat/subscriptors")
        self.driver.find_element(By.ID, "username").send_keys("TEXT")
        self.driver.find_element(By.ID, "password").send_keys("1865GB")
        self.driver.find_element(By.XPATH, "//button[@type=\'submit\']").click()

        # Accept cookies disclaimer banner to avoid selenium.common.exceptions.ElementClickInterceptedException
        self.driver.find_element_by_class_name('accept').click()

        # Go to section where news can be downloaded as plain text files
        self.driver.get("https://www.acn.cat/text")
        TOTAL_PAGES = 14505
        for page in range(TOTAL_PAGES):
            for button in self.driver.find_elements_by_link_text('text'):
                button.click()
                print(button)

            # Next page
            self.driver.find_element(By.LINK_TEXT, "»").click()

        # Logout
        self.driver.find_element(By.LINK_TEXT, "Surt").click()

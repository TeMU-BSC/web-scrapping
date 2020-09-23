'''
Script to download news from Agència Calatana de Notícies (ACN) website
using Selenium IDE and Selenium Web Driver.

https://addons.mozilla.org/en-US/firefox/addon/selenium-ide/
https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-linux64.tar.gz

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
        self.driver = webdriver.Firefox(executable_path=os.path.join(Path().absolute(), 'geckodriver-v0.27.0-linux64/geckodriver'))
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_login(self):
        self.driver.get("https://www.acn.cat/")
        self.driver.find_element(By.LINK_TEXT, "Entra").click()
        self.driver.find_element(By.NAME, "username").send_keys("TEXT")
        self.driver.find_element(By.NAME, "password").send_keys("1865GB")
        self.driver.find_element(By.NAME, "Submit").click()

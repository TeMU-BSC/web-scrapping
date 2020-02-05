'''
Script to download all the projects at Portal Fondo de Investigación en Salud
(FIS) of the Instituto de Salud Carlos III (ISCIII) website:
https://portalfis.isciii.es/es/Paginas/inicio.aspx

Author: https://github.com/aasensios
'''

# https://addons.mozilla.org/en-US/firefox/addon/selenium-ide/

# Generated by Selenium IDE
import pytest
import time
import json
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

SEARCH_CRITERIA = 'de'  # Jerónimo recommended that 'de' generic search criteria, 2607 results as 2020-02-05
RESULTS_PER_PAGE = 10  # Observed in webpage
TOTAL_PAGES_STRING = '261'  # Observed in webpage

class TestPortalfis():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_desearchscrapping(self):
    self.driver.get("https://portalfis.isciii.es/es/Paginas/inicio.aspx")
    self.driver.find_element(By.ID, "ctl00_ctl34_g_778f81e9_9d69_4f23_85fa_4f0191adfa23_txtBuscar").send_keys(SEARCH_CRITERIA)
    self.driver.find_element(By.ID, "ctl00_ctl34_g_778f81e9_9d69_4f23_85fa_4f0191adfa23_imbBuscar").click()
    self.driver.find_element(By.ID, "ctl00_ctl34_g_b8905950_4e9a_4a7e_9d2d_d728f1b64287_chkCoincidenciaExacta").click()
    self.driver.find_element(By.ID, "ctl00_ctl34_g_b8905950_4e9a_4a7e_9d2d_d728f1b64287_btnBuscar").click()
    # Find the total number of pages
    self.vars["total_pages"] = self.driver.find_element(By.ID, "ctl00_ctl34_g_b8905950_4e9a_4a7e_9d2d_d728f1b64287_lblNumTotalPaginas").text
    total_pages_string = TOTAL_PAGES_STRING
    try:
      total_pages_number = int(total_pages_string)
    except:
      total_pages_number = 0
    # Create a list of two-digit formatted strings ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
    results_per_page = [f'{i:02d}' for i in range(1, RESULTS_PER_PAGE + 1)]
    # Init an incremental counter for filenames
    filenumber = 1
    # Loop through all pages
    for page in range(total_pages_number):
      # Get the desired fields from each result
      for result in results_per_page:
        # Enter into the result link
        self.driver.find_element(By.ID, f"ctl00_ctl34_g_b8905950_4e9a_4a7e_9d2d_d728f1b64287_rptResultados_ctl{result}_lnkProyecto").click()
        # Get the desired data from html page
        self.vars["project_id"] = self.driver.find_element(By.ID, "aspnetForm").get_attribute("action")
        self.vars["project_title"] = self.driver.find_element(By.CSS_SELECTOR, "h2").text
        self.vars["project_abstract"] = self.driver.find_element(By.CSS_SELECTOR, "p.resumenDelProyecto").text
        # Build mesinesp format
        clean_id = re.search(r'(?<=idProyecto=).*$', self.vars["project_id"]).group().replace('%2f', '/')
        data = {
          '_id': clean_id,
          'ti_es': self.vars["project_title"],
          'ab_es': self.vars["project_abstract"],
        }
        # Write to disk
        with open(os.path.join('scrapped_docs', f'{filenumber:04d}.json'), 'w', encoding='utf-8') as f:
          json.dump(data, f, ensure_ascii=False, indent=4)
        # Go back to results list
        self.driver.find_element(By.ID, "ctl00_ctl34_g_063b679b_01b6_4da9_8097_7aba78758e18_lnkMigaPanBusqueda").click()
        # Prepare the next filename
        filenumber += 1
      # Go to next page
      self.driver.find_element(By.ID, "ctl00_ctl34_g_b8905950_4e9a_4a7e_9d2d_d728f1b64287_ctl00_imgSiguiente").click()

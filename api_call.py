
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import codecs
import re
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def script(dep_code, arr_code):
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    
    #HEADLESS OPTIONS
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    chrome_options.add_argument(f'user-agent={user_agent}')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    url = 'https://jsx.com/home/search'
    driver.get(url)

    dep_box = driver.find_element(By.CSS_SELECTOR, ".station-select__icon.ng-tns-c287-5")
    dep_box.click()

    with open('page_content.html', 'w', encoding='utf-8') as file:
        file.write(driver.page_source)

    dep_in = driver.find_element(By.CSS_SELECTOR, ".gbunmask.ng-tns-c287-5.ng-untouched.ng-pristine.ng-valid")
    dep_in.send_keys(dep_code)
        
    dep_confirm = driver.find_element(By.CSS_SELECTOR, ".city-airport.ng-tns-c287-5")
    dep_confirm.click()

    arr_box = driver.find_element(By.CSS_SELECTOR, ".station-select__icon.ng-tns-c287-6")
    arr_box.click()
    
    driver.get_screenshot_as_file("screenshot.png")
    
    arr_in = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div[2]/div[2]/div/input")
    arr_in.send_keys(arr_code)

    driver.close()
    
script("EDC", "BCT")
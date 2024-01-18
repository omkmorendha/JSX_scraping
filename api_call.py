from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC

def script(dep_code, arr_code, date_dep, date_arr):
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    
    #HEADLESS OPTIONS
    #chrome_options.add_argument('--headless')
    #user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    #chrome_options.add_argument(f'user-agent={user_agent}')
    
    driver = uc.Chrome(options=chrome_options)

    url = 'https://www.jsx.com/home/search'
    driver.get(url)

    driver.get_screenshot_as_file("screenshot.png")
    with open('page_content.html', 'w', encoding='utf-8') as file:
        file.write(driver.page_source)

    dep_box = driver.find_element(By.CSS_SELECTOR, ".station-select__icon.ng-tns-c287-5")
    dep_box.click()

    dep_in = driver.find_element(By.CSS_SELECTOR, ".gbunmask.ng-tns-c287-5.ng-untouched.ng-pristine.ng-valid")
    dep_in.send_keys(dep_code)
    
    try:
        dep_confirm = driver.find_element(By.CSS_SELECTOR, ".city-airport.ng-tns-c287-5")
        dep_confirm.click()
    except:
        return "Invalid Departure Airport Code"

    arr_box = driver.find_element(By.CSS_SELECTOR, ".station-select__icon.ng-tns-c287-6")
    arr_box.click()
    
    arr_in = driver.find_element(By.CSS_SELECTOR, ".gbunmask.ng-tns-c287-6.ng-untouched.ng-pristine.ng-valid")
    arr_in.send_keys(arr_code)
    
    try:
        arr_confirm = driver.find_element(By.CSS_SELECTOR, ".city-airport.ng-tns-c287-6")
        arr_confirm.click()
    except:
        return "Invalid Arrival Airport Code"

    date_box = driver.find_element(By.CSS_SELECTOR, ".datepicker-departure-container.ng-tns-c294-7.round-trip.ng-star-inserted")
    date_box.click()

    try:
        date_object = datetime.strptime(date_dep, '%d-%m-%Y')
        formatted_date = date_object.strftime('%A, %B %d, %Y')
        date_1 = driver.find_element(By.CSS_SELECTOR, f"[aria-label=\"{formatted_date}\"]")
        date_1.click()
    except:
        return "Invalid Departure Date"

    try:
        date_object = datetime.strptime(date_arr, '%d-%m-%Y')
        formatted_date = date_object.strftime('%A, %B %d, %Y')
        date_2 = driver.find_element(By.CSS_SELECTOR, f"[aria-label=\"{formatted_date}\"]")
        date_2.click()
    except:
        return "Invalid Arrival Date"

    date_confirm = driver.find_element(By.CSS_SELECTOR, "[aria-label=\"Close dates picker\"]")
    date_confirm.click()
    
    find_flights = driver.find_element(By.ID, "label-find-flights")
    find_flights.click()

    time.sleep(5)
   
    if(driver.current_url == 'https://www.jsx.com/home/search'):
        return "Invalid Dates"
    
    driver.close()
    
print(script("EDC", "TSM", "18-01-2024", "19-01-2024"))
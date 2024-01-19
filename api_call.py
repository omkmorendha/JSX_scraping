from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
from datetime import datetime, timedelta
import undetected_chromedriver as uc

max_attempts = 10
code_to_city={
    "EDC" : "Austin, TX",
    "TSM" : "Taos, NM",
    "BCT" : "Boca Raton, FL",
    "MMU" : "Morristown, NJ",
}


def parse_page(page, dep_code, arr_code, change_date = 0):
    soup = BeautifulSoup(page, 'html.parser')
    time_spans = soup.find_all('span', class_='flight-details-time--hour-minute')
    ampm_spans = soup.find_all('span', class_='flight-details-time--am-pm')
    planeType = soup.find('div', class_='flight-numbers__identifier').text.strip()

    dep_date_element = soup.find('div', class_='flight-card__section selected-flight selected-not-connecting ng-star-inserted').h3
    dep_date = dep_date_element.get_text().strip()
    dep_date = datetime.strptime(dep_date, '%a, %B %d').replace(year=datetime.now().year + change_date).strftime('%d-%m-%Y')
    
    try:
        seats = int(soup.find('div', id='label-seats-left-plural').text.strip().split()[0])
    except:
        seats = 'INF'
    
    price = soup.find('div', class_='low-fare-ribbon-item-price ng-star-inserted').text.strip()
    
    results = {
        'dep_time' : time_spans[0].text.strip() + ' ' + ampm_spans[0].text.strip(),
        'dep_date' : dep_date,
        'mobile' : "19974812447",
        'userid' : 459,
        'from_city' : code_to_city[dep_code],
        'from_airport' : dep_code,
        'to_city' : code_to_city[arr_code],
        'to_airport' : arr_code,
        'planetype' : planeType,
        "availableseats": seats,
        "Totalprice": price,
        "is_flexible": 0,
        "is_private": 0,
        "flyxo_id": None,
        "bookingUrl": None,
        "flight_source": "jsx"
    }
    
    return results


def script(dep_code, arr_code, date_dep=datetime.now().strftime("%d-%m-%Y")):
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    
    #HEADLESS OPTIONS
    #chrome_options.add_argument('--headless')
    #user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    #chrome_options.add_argument(f'user-agent={user_agent}')
    
    driver = uc.Chrome(options=chrome_options)

    url = 'https://www.jsx.com/home/search'
    driver.get(url)

    trip_type = driver.find_element(By.XPATH, '//mat-icon[text()="flight_takeoff"]')
    trip_type.click()
    
    time.sleep(1)
    one_way_select = driver.find_element(By.ID, "mat-option-1")
    one_way_select.click()
    
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

    date_box = driver.find_element(By.CSS_SELECTOR, ".datepicker-departure-container.ng-tns-c294-7.ng-star-inserted.one-way")
    date_box.click()

    while True:
        date_object = datetime.strptime(date_dep, '%d-%m-%Y')
        formatted_date = date_object.strftime('%A, %B %d, %Y')
        date_element = driver.find_element(By.CSS_SELECTOR, f"[aria-label=\"{formatted_date}\"]")
            
        date_element.click()
        date_confirm = driver.find_element(By.CSS_SELECTOR, "[aria-label=\"Close dates picker\"]")
        date_confirm.click()

        find_flights = driver.find_element(By.ID, "label-find-flights")
        find_flights.click()
        
        time.sleep(2)    
        
        if(driver.current_url == 'https://www.jsx.com/home/search'):
            date_box = driver.find_element(By.CSS_SELECTOR, ".datepicker-departure-container.ng-tns-c294-7.ng-star-inserted.one-way")
            date_box.click()
            date_object += timedelta(days=1)
            date_dep = date_object.strftime('%d-%m-%Y')
        else:
            break
    
    # full_page = driver.find_element(By.CSS_SELECTOR, ".fare-price-wrapper.desktop.ng-star-inserted")
    # full_page.click()
    
    #time.sleep(50)
    
    out = parse_page(driver.page_source, arr_code, dep_code)
    driver.close()
    return out

#print(parse_page("page_content.html", "EDC", "TSM", "18-01-2024"))
print(script("CSL", "DAL"))#, "19-01-2024"))
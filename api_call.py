from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
from datetime import datetime, timedelta
import undetected_chromedriver as uc
import re
import random


code_to_city={
    "HPN": "NEW YORK",
    "BCT": "BOCA RATON",
    "OPF": "SOUTH FLORIDA",
    "DAL": "DALLAS",
    "MMU": "MORRISON TOWN",
    "PBI": "SOUTH FLORIDA",
    "BZN": "BOZEMAN"
}


def parse_page(page, dep_code, arr_code, dep_date, avail):
    soup = BeautifulSoup(page, 'html.parser')
    time_spans = soup.find_all('span', class_='flight-details-time--hour-minute')
    ampm_spans = soup.find_all('span', class_='flight-details-time--am-pm')
    planeType = soup.find('span', class_='flight-numbers__identifier').text.strip()

    price_text = soup.find('div', class_='total-cost ng-star-inserted').text.strip()
    price = re.search(r'\$([\d,]+(\.\d{1,2})?)', price_text).group(1)
    
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
        "availableseats": avail,
        "Totalprice": price,
        "is_flexible": 0,
        "is_private": 0,
        "flyxo_id": None,
        "bookingUrl": None,
        "flight_source": "jsx"
    }
    
    return results


def script(dep_code, arr_code, date_dep=datetime.now().strftime("%d-%m-%Y"), MAX_days = 7):
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

    days_add = 0
    while True:
        date_object = datetime.strptime(date_dep, '%d-%m-%Y')
        formatted_date = date_object.strftime('%A, %B %d, %Y')
        date_element = driver.find_element(By.CSS_SELECTOR, f"[aria-label=\"{formatted_date}\"]")
            
        date_element.click()
        date_confirm = driver.find_element(By.CSS_SELECTOR, "[aria-label=\"Close dates picker\"]")
        date_confirm.click()

        find_flights = driver.find_element(By.ID, "label-find-flights")
        find_flights.click()
        
        time.sleep(5)    
        
        if(driver.current_url == 'https://www.jsx.com/home/search'):
            date_box = driver.find_element(By.CSS_SELECTOR, ".datepicker-departure-container.ng-tns-c294-7.ng-star-inserted.one-way")
            date_box.click()
            date_object += timedelta(days=1)
            days_add += 1
            date_dep = date_object.strftime('%d-%m-%Y')
        else:
            break
    
    
    time.sleep(1)
    
    output = []

    date_object = datetime.strptime(date_dep, '%d-%m-%Y')
    date_object -= timedelta(days=days_add)
    date_dep = date_object.strftime('%d-%m-%Y')
    
    for i in range(MAX_days):
        tab = driver.find_element(By.XPATH, f"//li[@aria-labelledby='lowFareItem{i}']")
        button = tab.find_element(By.CSS_SELECTOR, ".low-fare-ribbon-item-date")
        button.click()
        time.sleep(2)
    
        top_date =  driver.find_elements(By.CSS_SELECTOR, '.item.item-presentation.ng-star-inserted')[2]

        date_obj = datetime.strptime(date_dep, "%d-%m-%Y")
        dep_date_format = date_obj.strftime("%b %d")
        
        if top_date.text == dep_date_format:
            flights = driver.find_elements(By.XPATH, "//div[@class='fare-card ng-star-inserted']")
            for i in range(0, len(flights), 2):
                flights = driver.find_elements(By.XPATH, "//div[@class='fare-card ng-star-inserted']")
                
                try:
                    avail = flights[i].find_element(By.ID, "label-seats-left-plural")
                    text_content = avail.text
                    avail_seats = re.search(r'\d+', text_content).group()
                except:
                    try:
                        avail = flights[i].find_element(By.ID, "label-seats-left-singular")
                        avail_seats = 1
                    except:
                        avail_seats = random.randint(10, 15)
                
                time.sleep(2)
                flights[i].click()
                time.sleep(2)
                
                out = parse_page(driver.page_source, arr_code, dep_code, date_dep, avail_seats)
                if out is not None and out not in output:
                    output.append(out)
                
                # driver.get_screenshot_as_file("screenshot.png")
                # with open('page_content.html', 'w', encoding='utf-8') as file:
                #     file.write(driver.page_source)
                
                time.sleep(2)
                edit_button = driver.find_element(By.ID, "label-selected-flight-edit")
                edit_button.click()
                time.sleep(2)

        date_object = datetime.strptime(date_dep, '%d-%m-%Y')
        date_object += timedelta(days=1)
        date_dep = date_object.strftime('%d-%m-%Y')
        
    driver.close()
    return output


if __name__ == "__main__":
    routes = [
        ("HPN", "BCT"), 
        ("HPN", "DAL"), 
        ("HPN", "OPF"), 
        ("OPF", "DAL"),
        ("OPF", "HPN"),
        ("MMU", "BCT"),
        ("BCT", "MMU"),
        ("BCT", "HPN"),
        ("PBI", "BZN")
    ]
    
    print(script("HPN", "BCT"))
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
from datetime import datetime, timedelta
import undetected_chromedriver as uc
import re
import random
import requests
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import os
from pyvirtualdisplay import Display

load_dotenv()
log_file_path = 'Logfile.log'  # Replace with your desired log file path
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


code_to_city={
    "HPN": "NEW YORK",
    "BCT": "SOUTH FLORIDA",
    "OPF": "SOUTH FLORIDA",
    "DAL": "DALLAS",
    "MMU": "NEW YORK",
    "BZN": "BOZEMAN"
}


def parse_page(page, dep_code, arr_code, dep_date, avail):
    soup = BeautifulSoup(page, 'html.parser')
    time_spans = soup.find_all('span', class_='flight-details-time--hour-minute')
    ampm_spans = soup.find_all('span', class_='flight-details-time--am-pm')
    time_12_hour = time_spans[0].text.strip() + ' ' + ampm_spans[0].text.strip()
    planeType = soup.find('span', class_='flight-numbers__identifier').text.strip()

    price_text = soup.find('div', class_='total-cost ng-star-inserted').text.strip()
    price = float(re.search(r'\$([\d,]+(\.\d{1,2})?)', price_text).group(1).replace(',', ''))
    
    dep_date_formatted = datetime.strptime(dep_date, "%d-%m-%Y").strftime("%Y-%m-%d")
    
    results = {
        'dep_time': datetime.strptime(time_12_hour, "%I:%M %p").strftime("%H:%M"),
        'dep_date': dep_date_formatted,
        'mobile': "19974812447",
        'userid': 659,
        'from_city': code_to_city[dep_code],
        'from_airport': dep_code,
        'to_city': code_to_city[arr_code],
        'to_airport': arr_code,
        'planetype': planeType,
        "availableseats": avail,
        "Totalprice": price,
        "is_flexible": 0,
        "is_private": 0,
        "flyxo_id": 0,
        "bookingUrl": "https://www.jsx.com/home/search",
        "flight_source": "jsx"
    }
    
    return results


def script(dep_code, arr_code, date_dep=datetime.now().strftime("%d-%m-%Y"), MAX_days = 30):
    with Display():
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--window-size=1920,1080")
            
        #HEADLESS OPTIONS
        #chrome_options.add_argument('--headless=new')
        #user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        #chrome_options.add_argument(f'user-agent={user_agent}')

        driver = uc.Chrome(options=chrome_options, use_subprocess=False)
        
        try:
            print(f"From {dep_code} to {arr_code}")
            url = 'https://www.jsx.com/home/search'
            driver.get(url)
            
            trip_type = driver.find_element(By.XPATH, '//mat-icon[text()="flight_takeoff"]')
            trip_type.click()
            
            time.sleep(1)
            one_way_select = driver.find_element(By.ID, "mat-option-1")
            one_way_select.click()

            dep_box = driver.find_element(By.CSS_SELECTOR, ".station-select__icon")
            dep_box.click()

            dep_in = driver.find_element(By.CSS_SELECTOR, ".gbunmask.ng-tns-c283-5.ng-untouched.ng-pristine.ng-valid")
            dep_in.send_keys(dep_code)
            
            try:
                dep_confirm = driver.find_element(By.CSS_SELECTOR, ".city-airport.ng-tns-c283-5")
                dep_confirm.click()
            except:
                driver.quit()
                print(f"Invalid Departure Airport Code {dep_code} to {arr_code}")
                return []
            
            arr_box = driver.find_element(By.CSS_SELECTOR, ".station-select__icon.ng-tns-c283-6")
            arr_box.click()
            
            arr_in = driver.find_element(By.CSS_SELECTOR, ".gbunmask.ng-tns-c283-6.ng-untouched.ng-pristine.ng-valid")
            arr_in.send_keys(arr_code)
            
            try:
                arr_confirm = driver.find_element(By.CSS_SELECTOR, ".city-airport.ng-tns-c283-6")
                arr_confirm.click()
            except:
                driver.quit()
                print(f"Invalid Arrival Airport Code {dep_code} to {arr_code}")
                return []
                        
            date_box = driver.find_element(By.CSS_SELECTOR, ".datepicker-departure-container.ng-tns-c290-7.ng-star-inserted.one-way")
            date_box.click()
            days_add = 0
            tries = MAX_days
            
            while True:
                date_object = datetime.strptime(date_dep, '%d-%m-%Y')
                formatted_date = date_object.strftime('%A, %B %-d, %Y')
                try:     
                    date_element = driver.find_element(By.CSS_SELECTOR, f"[aria-label=\"{formatted_date}\"]")
                    date_element.click()
                    
                    date_confirm = driver.find_element(By.CSS_SELECTOR, "[aria-label=\"Close dates picker\"]")
                    date_confirm.click()
                    find_flights = driver.find_element(By.ID, "label-find-flights")
                    find_flights.click()
                except:
                    pass
                
                # time.sleep(3)
                # driver.get_screenshot_as_file("screenshot.png")
                # with open('page_content.html', 'w', encoding='utf-8') as file:
                #     file.write(driver.page_source)
                # time.sleep(3)  
                
                time.sleep(3)    
                
                tries -= 1
                
                if(driver.current_url == 'https://www.jsx.com/home/search'):
                    date_box = driver.find_element(By.CSS_SELECTOR, ".input-container.ng-tns-c290-7")
                    #date_box.click()
                    driver.execute_script("arguments[0].click();", date_box)
                    date_object += timedelta(days=1)
                    days_add += 1
                    date_dep = date_object.strftime('%d-%m-%Y')
                    
                    if tries <= 0:
                        print(f"No Flights available from {dep_code} to {arr_code}")
                        driver.quit()
                        return []
                else:
                    break
        
            time.sleep(1)
            
            output = []
            for i in range(MAX_days - tries - 1, MAX_days):
                try:
                    tab = driver.find_element(By.XPATH, f"//li[@aria-labelledby='lowFareItem{i}']")
                    button = tab.find_element(By.CSS_SELECTOR, ".low-fare-ribbon-item-date")
                    
                    button.click()
                    time.sleep(2)
                except:
                    for _ in range(4):
                        try:
                            next_button = driver.find_element(By.CSS_SELECTOR, ".low-fare-ribbon-control.next")
                            next_button.click()
                            time.sleep(1)  # Adjust the sleep time as needed
                        except Exception as e:
                            print(f"Error clicking next button: {e}")

                    time.sleep(5)
                    try:
                        tab = driver.find_element(By.XPATH, f"//li[@aria-labelledby='lowFareItem{i}']")
                        button = tab.find_element(By.CSS_SELECTOR, ".low-fare-ribbon-item-date")
                        
                        button.click()
                        time.sleep(2)
                    except:
                        pass
            
                top_date =  driver.find_elements(By.CSS_SELECTOR, '.item.item-presentation.ng-star-inserted')[2]
                date_obj = datetime.strptime(date_dep, "%d-%m-%Y")
                dep_date_format = date_obj.strftime("%b %d")
                
                if top_date.text == dep_date_format:
                    flights = driver.find_elements(By.XPATH, "//div[@class='fare-card ng-star-inserted']")
                    
                    for i in range(0, len(flights), 2):
                        try:
                            avail = flights[i].find_element(By.ID, "label-seats-left-plural")
                            text_content = avail.text
                            avail_seats = re.search(r'\d+', text_content).group()
                        except:
                            try:
                                avail = flights[i].find_element(By.ID, "label-seats-left-singular")
                                avail_seats = 1
                            except:
                                avail_seats = random.randint(5, 15)
                        
                        time.sleep(2)
                        
                        flights = driver.find_elements(By.XPATH, "//div[@class='fare-card ng-star-inserted']")
                        flights[i].click()
                        time.sleep(2)
                        
                        out = parse_page(driver.page_source, dep_code, arr_code, date_dep, avail_seats)
                        if out is not None and out not in output:
                            output.append(out)
                        
                        time.sleep(2)
                        edit_button = driver.find_element(By.ID, "label-selected-flight-edit")
                        edit_button.click()
                        time.sleep(2)
                date_object = datetime.strptime(date_dep, '%d-%m-%Y')
                date_object += timedelta(days=1)
                date_dep = date_object.strftime('%d-%m-%Y')
                
            driver.quit()
            return output
        
        except Exception as e:
            print("error: ", e)
            driver.quit()
            return []


if __name__ == "__main__":
    routes = [
        ("HPN", "BCT"), 
        ("HPN", "OPF"), 
        ("OPF", "DAL"), 
        ("OPF", "HPN"), 
        ("MMU", "BCT"), 
        ("BCT", "MMU"),
        ("BCT", "HPN") 
    ]
    
    error_message = None
    output = []
    for i in range(len(routes)):
        try:
            out = script(routes[i][0], routes[i][1], MAX_days=30)

            # if (out == []):
            #     out = script(routes[i][0], routes[i][1], MAX_days=7)
                
        except Exception as e:
            print(e)
            logging.error(f"An unexpected error occurred: {e}")
            error_message = e
            out = []
        
        output.extend(out)
    
    # output = script("MMU", "BCT")
    api_endpoint = os.environ.get('API_ENDPOINT')
    post_data = {}
    
    if(output == []):
        post_data["flights"] = "Error in retrieving data"
        slack_token = os.environ.get("SLACK_API_TOKEN")
        channel_id = os.environ.get("CHANNEL_ID")
    
        try:
            client = WebClient(token=slack_token)
            
            if not error_message:
                error_message = "500 error on JSW"
                
            message = f"Error occurred in the script:\n\n{error_message}"
            response = client.chat_postMessage(
                channel=channel_id,
                text=message
            )
            if not response["ok"]:
                print(f"Failed to send message to Slack. Error: {response['error']}")
        except SlackApiError as e:
            print(f"Slack API error: {e.response['error']}")
      
    else:
        post_data["flights"] = output
    
        #logging.info(f"Data posted: {post_data}")
        response = requests.post(api_endpoint, json=post_data)
        
        if response.status_code == 200:
            logging.info(f"Data successfully posted to the API. Response: {response.text}")
        else:
            logging.error(f"Failed to post data to the API. Status code: {response.status_code}")
            logging.error(response.text)
            slack_token = os.environ.get("SLACK_API_TOKEN")
            channel_id = os.environ.get("CHANNEL_ID")
        
            try:
                client = WebClient(token=slack_token)
                message = f"Failed to post data to the API. Status code: {response.status_code}"
                response = client.chat_postMessage(
                    channel=channel_id,
                    text=message
                )
                if not response["ok"]:
                    print(f"Failed to send message to Slack. Error: {response['error']}")
            except SlackApiError as e:
                print(f"Slack API error: {e.response['error']}")
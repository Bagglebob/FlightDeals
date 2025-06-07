from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
from datetime import datetime
from dateutil import parser
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException,StaleElementReferenceException


def run_scraper(selected_date, return_date, origin="Toronto", destination="Dubai"):
    dt = datetime.strptime(selected_date, "%Y-%m-%d")
    
    
    # Format as "Month Year" (e.g., "December 2025")
    target_caption = dt.strftime("%B %Y")
   

    # Format as "1 July, 2025"
    formatted_date = dt.strftime("%#d %B, %Y")
    

    returnDate = datetime.strptime(return_date,"%Y-%m-%d").strftime("%#d %B, %Y")
    

    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    driver.set_window_size(1920, 1080)

    URL = "https://www.cheapflights.ca/"
    
    # Open the URL
    req = driver.get(URL)
       

    searchForm = findSearchForm(driver)
    

    # find elements for Flight origin input and Flight destination input
    # inputs = searchForm[0].find_elements(By.TAG_NAME, "input")
    # for i in inputs:
    #     print(i.get_attribute("name"), i.get_attribute("aria-label"))
    inputs = findInputElements(searchForm)


    origin_input = inputs[0]
    origin_input.click()
    # Clear any existing text    
    origin_input.send_keys(Keys.BACKSPACE)
    origin_input.send_keys(Keys.BACKSPACE)
    origin_input.send_keys(Keys.BACKSPACE)
    # Enter the origin and select from suggestions
    origin_input.send_keys(origin)
    time.sleep(2)  # Let the suggestions load
    origin_input.send_keys(Keys.DOWN)
    origin_input.send_keys(Keys.RETURN)

    dest_input = inputs[1]
    dest_input.click()
    dest_input.send_keys(destination)
    time.sleep(2)  # Let the suggestions load
    dest_input.send_keys(Keys.DOWN)
    dest_input.send_keys(Keys.RETURN)


    departureDate = findDepartureDateElement(driver)

    departureDate.click()  # Open calendar

    
    # Select Calendar Div
    calendar = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[aria-label='Select start date from calendar input']"))
    )

    for c in calendar:
        print(
            "Calendar class name:",        
            c.get_attribute("aria-label"),
            c.get_attribute("class")
        )

    
    selectDeptDate(driver, target_caption, formatted_date, returnDate)

    submitSearch(driver)

    time.sleep(5)  # Wait for results to load
    # Extract flight deals
    flightDeals = extractFlightDeals(driver)
    print("UNPARSED DEALS:",flightDeals,"UNPARSED DEALS DONE!!\n")
    parsedDeals = parseDealData(flightDeals)
    print("PARSED Deals:", parsedDeals,"PARSED DEALS DONE!!\n")
    # clean up and close the driver
    driver.quit()
    return parsedDeals
    
        

def findSearchForm(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "main-search-form"))
        )
        searchForm = driver.find_elements(By.ID, "main-search-form")
        return searchForm
    except Exception as e:
        print("Error finding search form:", e)
        return None

def findInputElements(searchForm):
    try:
        inputs = searchForm[0].find_elements(By.TAG_NAME, "input")
       
        return inputs
    except Exception as e:
        print("Error finding input elements:", e)
        return None

def findDepartureDateElement(driver):
    try:
        departureDate = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Departure date']"))
        )
        
        return departureDate
    except Exception as e:
        print("Error finding departure date element:", e)
        return None

def selectDeptDate(driver, target_date, formatted_date, returnDate):    
    # Select Calendar Div
    calendar = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[aria-label='Select start date from calendar input']"))
    )


    # Select Next and Previous month buttons
    prevButton = calendar[0].find_element(By.CSS_SELECTOR, '[aria-label="Previous month"]')
    nextButton = calendar[0].find_element(By.CSS_SELECTOR, '[aria-label="Next month"]')

    
    
    month_text = calendar[0].find_element(By.CSS_SELECTOR, "table caption").text.strip()
    
    # change month (next month until caption == month)
    while(calendar[0].find_element(By.CSS_SELECTOR, "table caption").text != target_date):
        nextButton.click()
        WebDriverWait(driver, 2).until(
            lambda d: d.find_element(By.CSS_SELECTOR, "[aria-label='Select start date from calendar input'] table caption").text.strip() != month_text
        )
    month_text = calendar[0].find_element(By.CSS_SELECTOR, "table caption").text.strip()
    
    dateButton = calendar[0].find_element(By.XPATH, f".//div[starts-with(@aria-label, '{formatted_date}')]")
    dateButton.click()
    
      
    returnDate = calendar[0].find_element(By.XPATH, f".//div[starts-with(@aria-label, '{returnDate}')]")
    # returnDate = WebDriverWait(driver, 10).until(
    #     EC.presence_of_all_elements_located((By.XPATH, f".//div[starts-with(@aria-label, '{returnDate}')]"))
    # )
    
    
    time.sleep(2)  # Wait for the date to be selected
    returnDate.click()    


def submitSearch(driver):
    try:
        searchButton = driver.find_element(By.CSS_SELECTOR, "[aria-label='Find Deals']")
        searchButton.click()
    except Exception as e:
        print("Error finding or clicking the search button:", e)


def extractFlightDeals(driver):
    flight_deals = [] # ← List to store all deals
    try:
        # Wait for the results to load
        deals = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class*="result-item-container"][role="group"]'))
        )                
        for i in range(len(deals)):
            try:
                # Refetch deal to avoid stale element
                deal = WebDriverWait(driver, 10).until(
                    lambda d: d.find_elements(By.CSS_SELECTOR, 'div[class*="result-item-container"][role="group"]')[i]
                )

                price_elem = WebDriverWait(driver, 3).until(
                    lambda d: deal.find_element(By.CSS_SELECTOR, "div[class*='price-text']")
                )
                # print("Price found:", price_elem.text)
                price = price_elem.text.strip()

                # Extract and print the deal link
                # Extract the <a> tag href inside the price section
                link_elem = deal.find_element(By.CSS_SELECTOR, "div[class*='price-section'] a")
                deal_link = link_elem.get_attribute("href")
               

                # scope to content-section inside this one deal, and extract the departure airport
                contentSection = WebDriverWait(driver, 10).until(
                    lambda d: deal.find_elements(By.CSS_SELECTOR, 'div[class*="content-section"]')
                )
               
                # Extract airport codes from within the content-section
                try:
                    
                    legs_data = []
                    try:
                        legs = contentSection[0].find_elements(By.CSS_SELECTOR, "ol > li")
                        for leg in legs:
                            segments = leg.text.strip().split('\n')
                            segments = [s for s in leg.text.strip().split('\n') if s.strip() != "-"]
                            legs_data.append(segments)
                    except Exception as e:
                        print("Error extracting legs:", e)

                    # Build and store deal object
                    deal_obj = {
                        "price": price,
                        "deal_link": deal_link,
                        "legs": legs_data
                    }
                    flight_deals.append(deal_obj)
                except Exception as e:
                    print("Error extracting airport info:", e)
            except TimeoutException:
                print("Price not found in this deal.")
            except StaleElementReferenceException:
                print("Deal became stale, skipping or retrying.")
    except Exception as e:
        print("Error extracting flight deals:", e)
    # driver.quit()
    return flight_deals


# {
#   "price": "C$ 1,325",
#   "deal_link": "https://www.cheapflights.ca/book/flight?code=kfHiO9Zlst.tYUOhBwwtNbTYwQ_VUUUMA.96956.9629bf90967b6638afcd0c4d3a856def&h=1656983adc02&sub=F-3276301010609040527E0d6192e0ae2&bucket=e&pageOrigin=F..RP.FE.M5",
#   "legs": {
#     "departure": {
#       "FlightTime": "11:00 pm – 7:45 pm",
#       "ArrivesNxtDay": "+1",
#       "DepartAirline": "JFKJohn F Kennedy Intl",
#       "ArriveAirline": "DXBDubai Intl",
#       "Layover": "direct",
#       "TotalTime": "12h 45m"
#     },
#     "arrival": {
#       "FlightTime": "8:30 am – 2:25 pm",
#       "DepartAirline": "DXBDubai Intl",
#       "ArriveAirline": "JFKJohn F Kennedy Intl",
#       "Layover": "direct",
#       "TotalTime": "13h 55m"
#     }
#   }
# }



def parseDealData(flight_deals):
    result = []

    for deal in flight_deals:
        if "legs" not in deal or not deal["legs"]:
            continue

        legs = deal["legs"]
        parsed = {
            "price": deal["price"],
            "deal_link": deal["deal_link"],
            "legs": {}
        }

        # Parse departure leg
        if len(legs) > 0:
            leg = legs[0]
            dep = {
                "FlightTime": leg[0],
                "ArrivesNxtDay": "+1" if "+1" in leg else "",
                "DepartAirline": leg[2] if len(leg) > 2 else "",
                "ArriveAirline": leg[3] if len(leg) > 3 else "",
                "Layover": leg[4] if len(leg) > 4 else "",
                "Stopover": leg[5] if len(leg) > 5 and "layover" not in leg[5] else "",
                "LayoverDuration": leg[6] if len(leg) > 6 and "layover" in leg[6] else "",
                "TotalTime": leg[-1]  # always at end
            }
            parsed["legs"]["departure"] = dep

        # Parse return leg
        if len(legs) > 1:
            leg = legs[1]
            arr = {
                "FlightTime": leg[0],
                "ArrivesNxtDay": "+1" if "+1" in leg else "",
                "DepartAirline": leg[2] if "+1" in leg else leg[1],
                "ArriveAirline": leg[3] if "+1" in leg else leg[2],
                "Layover": leg[4] if "+1" in leg else leg[3],
                "Stopover": leg[4] if len(leg) > 4 and "layover" not in leg[4] else "",
                "LayoverDuration": leg[5] if len(leg) > 5 and "layover" in leg[5] else "",
                "TotalTime": leg[-1]  # always at end
            }
            parsed["legs"]["arrival"] = arr

        result.append(parsed)

    return result

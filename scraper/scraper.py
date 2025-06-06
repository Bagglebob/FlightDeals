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
    print("Selected date:", dt.strftime("%Y-%m-%d"))
    
    # Format as "Month Year" (e.g., "December 2025")
    target_caption = dt.strftime("%B %Y")
    print("Target caption:", target_caption)

    # Format as "1 July, 2025"
    formatted_date = dt.strftime("%#d %B, %Y")
    print("Formatted date for selection:", formatted_date)

    returnDate = datetime.strptime(return_date,"%Y-%m-%d").strftime("%#d %B, %Y")
    print("Formatted Return date:", returnDate)

    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")

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
    print("Main Search Form elements:")
    for i in searchForm:
        print(i.tag_name, i.get_attribute("name"), i.get_attribute("aria-label"))



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

    # Select Next and Previous month buttons
    # prevButton = calendar[0].find_element(By.CSS_SELECTOR, '[aria-label="Previous month"]')
    # nextButton = calendar[0].find_element(By.CSS_SELECTOR, '[aria-label="Next month"]')

    # print(prevButton.get_attribute("aria-label"))
    # print(nextButton.get_attribute("aria-label"))

    # caption = calendar[0].find_element(By.CSS_SELECTOR, "table caption")
    # month_text = caption.text
    # print("Current Month Shown in Calendar:", month_text)

    # change month (next month until caption == month)
    # while(calendar[0].find_element(By.CSS_SELECTOR, "table caption").text != target_caption):
    #     nextButton.click()
    selectDeptDate(driver, target_caption, formatted_date, returnDate)

    submitSearch(driver)

    
    print(extractFlightDeals(driver))
    time.sleep(10)
    # clean up and close the driver
    driver.quit()


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
        for i in inputs:
            print(i.get_attribute("name"), i.get_attribute("aria-label"))
        return inputs
    except Exception as e:
        print("Error finding input elements:", e)
        return None

def findDepartureDateElement(driver):
    try:
        departureDate = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Departure date']"))
        )
        print(departureDate.get_attribute("aria-label"))
        return departureDate
    except Exception as e:
        print("Error finding departure date element:", e)
        return None

def selectDeptDate(driver, target_date, formatted_date, returnDate):    
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

    # Select Next and Previous month buttons
    prevButton = calendar[0].find_element(By.CSS_SELECTOR, '[aria-label="Previous month"]')
    nextButton = calendar[0].find_element(By.CSS_SELECTOR, '[aria-label="Next month"]')

    print(prevButton.get_attribute("aria-label"))
    print(nextButton.get_attribute("aria-label"))

    
    month_text = calendar[0].find_element(By.CSS_SELECTOR, "table caption").text.strip()
    
    print("Current Month Shown in Calendar:", month_text)
    while(calendar[0].find_element(By.CSS_SELECTOR, "table caption").text != target_date):
        nextButton.click()
        WebDriverWait(driver, 2).until(
            lambda d: d.find_element(By.CSS_SELECTOR, "[aria-label='Select start date from calendar input'] table caption").text.strip() != month_text
        )
    month_text = calendar[0].find_element(By.CSS_SELECTOR, "table caption").text.strip()
    
    dateButton = calendar[0].find_element(By.XPATH, f".//div[starts-with(@aria-label, '{formatted_date}')]")
    print("Date Button found:", dateButton.get_attribute("aria-label"), dateButton.get_attribute("role"))
    dateButton.click()
    
      
    returnDate = calendar[0].find_element(By.XPATH, f".//div[starts-with(@aria-label, '{returnDate}')]")
    # returnDate = WebDriverWait(driver, 10).until(
    #     EC.presence_of_all_elements_located((By.XPATH, f".//div[starts-with(@aria-label, '{returnDate}')]"))
    # )
    
    print("Return Date Button found:", returnDate.get_attribute("aria-label"), returnDate.get_attribute("role"))
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
                print("Price found:", price_elem.text)
                price = price_elem.text.strip()

                # Extract and print the deal link
                # Extract the <a> tag href inside the price section
                link_elem = deal.find_element(By.CSS_SELECTOR, "div[class*='price-section'] a")
                deal_link = link_elem.get_attribute("href")
                print("Deal link:", deal_link)

                # scope to content-section inside this one deal, and extract the departure airport
                contentSection = WebDriverWait(driver, 10).until(
                    lambda d: deal.find_elements(By.CSS_SELECTOR, 'div[class*="content-section"]')
                )
                print("Content section found:", len(contentSection), "elements")
                # Extract airport codes from within the content-section
                try:
                    airport_blocks = contentSection[0].find_elements(By.CSS_SELECTOR, 'div[class*="full-airport"]')
                    print("Airport blocks found:", len(airport_blocks))
                    

                    # OLD CODE: Uncomment to print legs details
                    # legs = contentSection[0].find_elements(By.CSS_SELECTOR, "ol > li")
                    # print("Legs found:", len(legs))
                    # for leg in legs:
                    #     print("Leg details:\"", leg.text.strip().split('\n'), "\"")

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
    
    return flight_deals

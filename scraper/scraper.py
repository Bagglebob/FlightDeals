from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
from datetime import datetime

def run_scraper(selected_date):
    dt = datetime.strptime(selected_date, "%Y-%m-%d")
    # Format as "Month Year" (e.g., "December 2025")
    target_caption = dt.strftime("%B %Y")
    print("Target caption:", target_caption)
    driver = webdriver.Chrome()
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
    req = driver.get(URL)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "main-search-form"))
    )
    # find main search form
    searchForm = driver.find_elements(By.ID, "main-search-form")
    print("Main Search Form elements:")
    for i in searchForm:
        print(i.tag_name, i.get_attribute("name"), i.get_attribute("aria-label"))


    # find elements for Flight origin input and Flight destination input
    inputs = searchForm[0].find_elements(By.TAG_NAME, "input")
    for i in inputs:
        print(i.get_attribute("name"), i.get_attribute("aria-label"))

    departureDate = None

    departureDate = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Departure date']")))

    if(departureDate):
        print("departureDate found!")
    print(departureDate.get_attribute("aria-label"))


    origin_input = inputs[0]
    origin_input.click()
    origin_input.send_keys("Toronto")
    time.sleep(2)  # Let the suggestions load
    origin_input.send_keys(Keys.DOWN)
    origin_input.send_keys(Keys.RETURN)

    dest_input = inputs[1]
    dest_input.click()
    dest_input.send_keys("Dubai")
    time.sleep(2)  # Let the suggestions load
    dest_input.send_keys(Keys.DOWN)
    dest_input.send_keys(Keys.RETURN)

    departureDate.click()  # Open calendar


    # # Select exact date
    # WebDriverWait(driver, 5).until(
    #     EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label=Select start date from calendar input]"))
    # )

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

    caption = calendar[0].find_element(By.CSS_SELECTOR, "table caption")
    month_text = caption.text
    print("Current Month Shown in Calendar:", month_text)

    # change month (next month until caption == month)
    while(calendar[0].find_element(By.CSS_SELECTOR, "table caption").text != target_caption):
        nextButton.click()
        WebDriverWait(driver, 2).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR,'[aria-label="Next month"]'))
    )

    time.sleep(5)

    # clean up and close the driver
    driver.quit()

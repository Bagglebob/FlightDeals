# Flight Deals Scraper

This Python script uses Selenium to scrape round-trip flight deals from [cheapflights.ca](https://www.cheapflights.ca/). It automates searching flights for a given starting point, destination, departure date, and return date, then extracts and parses flight deal information including price, flight times, airports, layovers, and provides you with a link to the deal.

---

## Overview

- Automates browser interaction using Selenium with stealth settings to avoid detection.
- Inputs origin, destination, departure date, and return date on the website.
- Navigates calendar widget on [cheapflights.ca](https://www.cheapflights.ca/) to select dates.
- Submits the search and waits for results.
- Extracts flight deal details from the search results page.
- Parses raw text data into structured dictionaries.
- Returns a list of parsed flight deals with info about Departure Trip and Return Trip.

---

## Functions

### `run_scraper(selected_date, return_date, origin="Toronto", destination="Dubai")`

Main function to execute the scraping process.

- **Parameters:**
  - `selected_date` (str): Departure date in `YYYY-MM-DD` format.
  - `return_date` (str): Return date in `YYYY-MM-DD` format.
  - `origin` (str): Departure airport/city (default "Toronto").
  - `destination` (str): Destination airport/city (default "Dubai").

- **Returns:** List of parsed flight deals (dictionaries).

- **Flow:**
  1. Formats dates for the website calendar.
  2. Initializes Chrome WebDriver with stealth options and headless mode.
  3. Loads the homepage.
  4. Finds and fills origin and destination inputs with auto-suggestions.
  5. Opens calendar and selects departure and return dates.
  6. Submits the search form.
  7. Waits for results and extracts raw deal data.
  8. Parses raw data into structured dictionaries.
  9. Closes browser and returns parsed deals.

---

### `findSearchForm(driver)`

- **Purpose:** Locate the main search form element on the homepage.

- **Parameters:** `driver` - Selenium WebDriver instance.

- **Returns:** List containing the search form element, or `None` if not found.

---

### `findInputElements(searchForm)`

- **Purpose:** Find all input fields inside the search form (expected origin and destination inputs).

- **Parameters:** `searchForm` - List containing the search form element.

- **Returns:** List of `<input>` elements, or `None` on failure.

---

### `findDepartureDateElement(driver)`

- **Purpose:** Locate the departure date input/button element to trigger the calendar popup.

- **Parameters:** `driver` - Selenium WebDriver instance.

- **Returns:** Departure date element, or `None` if not found.

---

### `selectDeptDate(driver, target_date, formatted_date, returnDate)`

- **Purpose:** Select the departure and return dates in the calendar widget.

- **Parameters:**
  - `driver` - Selenium WebDriver instance.
  - `target_date` - Target month and year string (e.g., "July 2025").
  - `formatted_date` - Departure date formatted as `"1 July, 2025"`.
  - `returnDate` - Return date formatted as `"10 July, 2025"`.

- **Process:**
  - Waits for calendar to load.
  - Navigates calendar months until the target month is displayed.
  - Clicks the correct departure date.
  - Clicks the correct return date.

---

### `submitSearch(driver)`

- **Purpose:** Click the search button to submit the flight search form.

- **Parameters:** `driver` - Selenium WebDriver instance.

- **Returns:** None. Prints an error message if button is not found or clickable.

---

### `extractFlightDeals(driver)`

- **Purpose:** Extract raw flight deal elements from the search results page.

- **Parameters:** `driver` - Selenium WebDriver instance.

- **Returns:** List of raw flight deal dictionaries containing:
  - `price`
  - `deal_link`
  - `legs` (list of leg details as raw text segments)

- **Details:**
  - Waits for flight result items to appear.
  - Extracts price, booking link, and leg segment text.
  - Handles stale elements and timeouts gracefully.

---

### `parseDealData(flight_deals)`

- **Purpose:** Convert raw deal text data into structured flight deal dictionaries.

- **Parameters:** `flight_deals` - List of raw flight deal dictionaries (output of `extractFlightDeals`).

- **Returns:** List of parsed deals with structure:

  
```python
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
```

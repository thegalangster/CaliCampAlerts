from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta
import crud, re
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

def check_availability(alert):

    campground_code = alert.campground.code
    date_start = alert.date_start
    date_stop = alert.date_stop
    end_month = alert.date_stop.month

    # Navigate to the campground page with that ID
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome('/Users/aimeehome/Documents/CaliCamp/chromedriver', options=options)
    driver.get('https://www.recreation.gov/camping/campgrounds/' + str(campground_code))

    # Closes welcome page
    try:
        welcome_close_button = driver.find_element(By.XPATH, '//button[@aria-label="Close modal"]')
        welcome_close_button.click()
    except NoSuchElementException:
        # Handle element not existing
        pass

    # Opens Select Dates
    try:
        select_dates_div = driver.find_element(By.XPATH, '//div[contains(text(), "Select Dates ...")]')
        select_dates_button = select_dates_div.find_element(By.XPATH, '..')
        select_dates_button.click()
    except NoSuchElementException:
        # Handle element not existing
        pass

    # Returns all buttons that have availability information
    availability_tds = driver.find_elements(By.XPATH, '//td[contains(@class, "CalendarDay")]')

    availability_set = set()  # Set of datetime objects
    if not availability_tds:
        availability_tds = driver.find_elements(By.XPATH, '//button[@class="rec-availability-date"]')
        end_reached = extract_dates(availability_set, availability_tds, date_start, date_stop)
        while not end_reached:
            # Go to next set of dates
            try:
                select_forward_button = driver.find_element(By.XPATH, '//button[@aria-label="Go Forward 5 Days"]')
                driver.execute_script("arguments[0].click();", select_forward_button)
                availability_tds = driver.find_elements(By.XPATH, '//button[@class="rec-availability-date"]')
                end_reached = extract_dates(availability_set, availability_tds, date_start, date_stop)
            except NoSuchElementException:
                # Handle element not existing
                pass
    else:
        extract_dates(availability_set, availability_tds, date_start, date_stop)

    return filter_on_requirements(availability_set=availability_set, alert=alert)

def extract_dates(availability_set, availability_tds, date_start, date_stop):
    # Parses through all availability dates and stores available dates in a set
    end_reached = False
    for availability_td in availability_tds:
        availability = availability_td.get_attribute('aria-label')
        if "It’s available" in availability or "is available" in availability:
            date_only = re.search("(January?|February?|March?|April?|May?|June?|July?|August?|September?|October?|November?|December?)\s+(\d{1,2}),\s+(\d{4})", availability)
            date_only_abbrev = re.search("(Jan?|Feb?|Mar?|Apr?|May?|Jun?|Jul?|Aug?|Sep?|Oct?|Nov?|Dec?)\s+(\d{1,2}),\s+(\d{4})", availability)
            if date_only is not None:
                date_ = datetime.strptime(date_only.group(0), "%B %d, %Y")
            else:
                date_ = datetime.strptime(date_only_abbrev.group(0), "%b %d, %Y")
            if date_ >= date_start and date_ <= date_stop:
                availability_set.add(date_)
            elif date_ > date_stop:
                end_reached = True

    return end_reached

def filter_on_requirements(availability_set, alert):
    date_start = alert.date_start
    date_stop = alert.date_stop
    day = alert.day
    min_length = alert.min_length

    ordered_dates = sorted(availability_set)  # Returns an ascending list of available dates

    date_windows = []
    date_window = []
    for date in ordered_dates:
        bitmap_index = date.weekday()
        if day[bitmap_index] == '1':
            if not date_window:
                date_window.append(date)
            elif date_window[-1] == date - timedelta(days=1):  # Check if the day after is available
                date_window.append(date)
            else:
                date_windows.append(date_window)
                date_window = [] 
    if date_window:
        date_windows.append(date_window)

    if date_windows:
        return True

    return False
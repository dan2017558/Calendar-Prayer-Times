from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

from messagebox import show_error

# Setup the Chrome WebDriver
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Use the driver manager to ensure the correct ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL of the website containing prayer times
url = ""
driver.get(url)

# Set a maximum timeout duration (in seconds)
max_wait_time = 30

# Start a timer to measure how long it takes
start_time = time.time()

try:
    # Wait for the table to load dynamically
    table = WebDriverWait(driver, max_wait_time).until(EC.visibility_of_element_located((By.CLASS_NAME, "monthlyTimetable")))

    # Get page source after JavaScript has rendered the content
    page_source = driver.page_source

except TimeoutException:
    # If table doesn't load within the max_wait_time
    show_error(f"Timed out waiting for the table to load after {max_wait_time} seconds.", quit=True)

finally:
    # Close the driver
    driver.quit()

# Parse the page
soup = BeautifulSoup(page_source, 'html.parser')

# Find prayer times table
table = soup.find('table', {'class': 'dptTimetable customStyles dptUserStyles'})

# Extract rows from the table
rows = table.find_all('tr')

# Process & Cleanup data
prayer_times = []
for row in rows:
    cols = row.find_all('td')
    cols = [ele.text.strip() for ele in cols]
    if len(cols) > 0:
        prayer_times.append(cols)

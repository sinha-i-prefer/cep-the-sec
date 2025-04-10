import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# ---------- MySQL DB Setup ----------
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='#HiMaNsHu123',
    database='job_lists'
)

cursor = conn.cursor()

print("Connected to DB. Creating table if not exists...")

cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    company VARCHAR(255),
    location VARCHAR(255),
    date_posted VARCHAR(100),
    job_type VARCHAR(100),
    link TEXT
)
""")
print("Table check/creation done.")

# ---------- Web Scraping Setup ----------
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Chrome(options=options)

url = "https://jobs.disabilitytalent.org/jobs/?l=India&p=1&s=400"
driver.get(url)
time.sleep(3)  # Initial page load

# ---------- Handle "Load More" Button ----------
max_clicks = 10  # Set a limit to prevent infinite clicking
click_count = 0

while click_count < max_clicks:
    try:
        # Wait for button to be clickable
        load_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "load-more"))
        )
        
        # Scroll to the button (helps in some cases)
        driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
        time.sleep(1)
        
        # Click the button
        load_more_button.click()
        click_count += 1
        print(f"Clicked 'Load More' button {click_count} time(s)")
        
        # Wait for new content to load
        time.sleep(3)
        
        # Check if button is still present
        if not driver.find_elements(By.CLASS_NAME, "load-more"):
            print("No more 'Load More' button found. Ending pagination.")
            break
            
    except Exception as e:
        print(f"Error clicking 'Load More': {str(e)}")
        break

# ---------- Scraping and DB Insertion ----------
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

jobs = []

for job in soup.find_all('article', class_='listing-item'):
    job_data = {}

    title_div = job.find('div', class_='listing-item__title')
    if title_div and title_div.a:
        job_data['title'] = title_div.a.text.strip()
        job_data['link'] = "https://jobs.disabilitytalent.org" + title_div.a['href']

    company = job.find('span', class_='listing-item__info--item-company')
    if company:
        job_data['company'] = company.text.strip()

    location = job.find('span', class_='listing-item__info--item-location')
    if location:
        job_data['location'] = location.text.strip()

    date = job.find('div', class_='listing-item__date')
    if date:
        job_data['date_posted'] = date.text.strip()

    job_type = job.find('span', class_='listing-item__employment-type')
    if job_type:
        job_data['job_type'] = job_type.text.strip()

    if job_data:
        jobs.append(job_data)
        cursor.execute('''
            INSERT INTO jobs (title, company, location, date_posted, job_type, link)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            job_data.get('title'),
            job_data.get('company'),
            job_data.get('location'),
            job_data.get('date_posted'),
            job_data.get('job_type'),
            job_data.get('link')
        ))

conn.commit()
conn.close()

print(f"\nInserted {len(jobs)} job(s) into the MySQL database successfully!")
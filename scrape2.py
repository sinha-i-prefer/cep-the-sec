import time
import mysql.connector
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------- Web Driver Setup ----------
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Chrome(options=options)

# ---------- MySQL DB Setup ----------
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='#HiMaNsHu123',
        database='job_lists'
    )
    cursor = conn.cursor()
    print("Connected to DB.")
except mysql.connector.Error as err:
    print(f"Failed to connect to database: {err}")
    driver.quit()
    exit(1)

# ---------- Scraping Logic ----------
all_jobs_data = []
max_pages = 5

for current_page in range(1, max_pages + 1):
    url = f"https://www.swarajability.org/?page={current_page}"
    print(f"\nAccessing page {current_page}: {url}")
    driver.get(url)
    time.sleep(5)
    
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "app-custom-job-card .card"))
        )
    except Exception as e:
        print(f"Timeout on page {current_page}: {e}")
        continue

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_cards = soup.select("app-custom-job-card")

    print(f"Found {len(job_cards)} job cards on page {current_page}")
    
    for job_card in job_cards:
        job_data = {}
        title_element = job_card.select_one("a.job-title")
        company_element = job_card.select_one(".Ename a")
        job_type_element = job_card.select_one("button.job-type")
        location_spans = job_card.select("span.location-background")

        if title_element:
            job_data['title'] = title_element.text.strip()
            job_data['link'] = "https://www.swarajability.org" + title_element.get('href', '')

        if company_element:
            job_data['company'] = company_element.text.strip()

        if job_type_element:
            job_data['job_type'] = job_type_element.text.strip()

        locations = []
        for span in location_spans:
            loc = span.text.replace("Location 1:", "").replace("Location 2:", "").replace("Location 3:", "")
            locations.append(" | ".join([x.strip() for x in loc.split("|") if x.strip()]))

        if locations:
            job_data['location'] = "; ".join(locations)
        else:
            location_p = job_card.select_one("p.top:has(i.icofont-location-pin)")
            if location_p:
                job_data['location'] = location_p.text.replace("Locations:", "").strip()

        if 'title' in job_data and 'company' in job_data:
            all_jobs_data.append(job_data)

# ---------- Insert into MySQL ----------
print(f"\nInserting {len(all_jobs_data)} jobs into the database...")

insert_query = '''
    INSERT INTO jobs (title, company, location, job_type, link)
    VALUES (%s, %s, %s, %s, %s)
'''

try:
    for job in all_jobs_data:
        cursor.execute(insert_query, (
            job.get('title', 'Not specified'),
            job.get('company', 'Not specified'),
            job.get('location', 'Not specified'),
            job.get('job_type', 'Not specified'),
            job.get('link', '#')
        ))
    conn.commit()
    print("All jobs inserted successfully.")
except mysql.connector.Error as err:
    print(f"Database error: {err}")

# ---------- Final Sample ----------
print("\nSample of scraped jobs:")
for i, job in enumerate(all_jobs_data[:5], 1):
    print(f"\nJob {i}:")
    print(f"Title: {job.get('title', 'N/A')}")
    print(f"Company: {job.get('company', 'N/A')}")
    print(f"Job Type: {job.get('job_type', 'N/A')}")
    print(f"Location: {job.get('location', 'N/A')}")
    print(f"Link: {job.get('link', 'N/A')}")

# ---------- Cleanup ----------
cursor.close()
conn.close()
driver.quit()
print("\nScraping complete. Database connection closed.")

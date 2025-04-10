import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
time.sleep(5)

soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

# ---------- Scraping and DB Insertion ----------
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

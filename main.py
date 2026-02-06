import pandas as pd
import os
import time
from datetime import datetime, timezone

from bs4 import BeautifulSoup
from pymongo import MongoClient

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)


url = "https://www.nba.com/players"
driver.get(url)

wait = WebDriverWait(driver, 20)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
time.sleep(2)  # buffer mic (React)


all_docs = []
page = 1

while True:
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")

    table = soup.find("table")
    if not table:
        print("Nu am gasit tabelul. Stop.")
        break

    thead = table.find("thead")
    if not thead:
        print("Nu am gasit thead. Stop.")
        break

    headers = [th.get_text(" ", strip=True) for th in thead.find_all("th")]

    tbody = table.find("tbody")
    if not tbody:
        print("Nu am gasit tbody. Stop.")
        break

    rows_this_page = 0
    for tr in tbody.find_all("tr"):
        tds = tr.find_all("td")
        values = [td.get_text(" ", strip=True) for td in tds]

        doc = dict(zip(headers, values))

        doc["scraped_at"] = datetime.now(timezone.utc).isoformat()
        doc["source"] = url
        doc["page"] = page

        if doc:  # siguranta
            all_docs.append(doc)
            rows_this_page += 1

    print(f"Pagina {page}: {rows_this_page} randuri extrase")
    page += 1

    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, "button[data-pos='next']")
        if next_btn.get_attribute("disabled"):
            print("Next disabled -> ultima pagina.")
            break

        next_btn.click()
        time.sleep(2)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr")))

    except Exception as e:
        print("Nu am gasit Next -> stop.")
        print("Eroare:", e)
        break


players = pd.DataFrame(all_docs)
players.to_csv("nba_players.csv", index=False, encoding="utf-8")


load_dotenv()
mongodb_uri = os.getenv("MONGODB_URI")
if not mongodb_uri:
    driver.quit()
    raise ValueError("MONGODB_URI nu este setat in environment variables.")

client = MongoClient(mongodb_uri)
db = client["nba_scraping"]
collection = db["nba_players"]

result = collection.insert_many(all_docs)
print("\nMongoDB: inserate =", len(result.inserted_ids))


driver.quit()
client.close()
print("Gata scrapingul!")
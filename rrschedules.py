import requests
import json
import os
import logging
from datetime import datetime, timedelta
import feedparser
import zipfile
import sqlite3
import pandas as pd
import asyncio
import aiohttp

rss_url = 'https://github.com/septadev/GTFS/releases.atom'
feed = feedparser.parse(rss_url)
latest_release_update = feed["entries"][0]["updated"]
current_time = datetime.utcnow()
update_datetime = datetime.strptime(latest_release_update, "%Y-%m-%dT%H:%M:%SZ")
one_day_before = current_time - timedelta(days=1)
day_of_week = datetime.now().strftime('%A').lower()
if one_day_before <= update_datetime <= current_time:
    download_zip_path = os.path.join("./data", "septa_gtfs.zip")
    target_rail_path = os.path.join("./data", "google_rail.zip")
    with requests.get("https://www3.septa.org/developer/gtfs_public.zip", stream=True) as response:
        response.raise_for_status()
        with open(download_zip_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    with zipfile.ZipFile(download_zip_path, "r") as zip_ref:
        zip_ref.extractall("./data")

    os.remove(download_zip_path)
    with zipfile.ZipFile(target_rail_path, "r") as zip_ref:
        zip_ref.extractall("./data")
    conn = sqlite3.connect("./data/septa.sqlite")
    cursor = conn.cursor()
    for file_name in os.listdir("./data"):
        if file_name.endswith('.txt'):
            file_path = os.path.join("./data", file_name)
            df = pd.read_csv(file_path)
            table_name = os.path.splitext(file_name)[0]
            df.to_sql(table_name, conn, if_exists='replace', index=False)
else:
    conn = sqlite3.connect("./data/septa.sqlite")
    cursor = conn.cursor()

query = f"""
    SELECT COUNT(DISTINCT block_id) FROM trips t INNER JOIN calendar c ON t.service_id = c.service_id
    WHERE c.{day_of_week} = 1;
    """

cursor.execute(query)
result = cursor.fetchall()
output = [str(row[0]) for row in result]
cursor.close()
conn.close()


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


today_date = datetime.now().strftime("%Y-%m-%d")

scraping_dir = f"scraping/rr-schedule/{today_date}"
log_dir = f"logs/rr-schedule/{today_date}"

os.makedirs(scraping_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

# Set up logging
log_filename = f"{log_dir}/{get_timestamp()}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

json_filename = f"{scraping_dir}/rr-schedule_{get_timestamp()}.json"

API_URL = "https://www3.septa.org/api/RRSchedules/index.php?req1="


async def fetch_url(session, query):
    url = f"{API_URL}{query}"
    async with session.get(url) as r:
        data = await r.json()
        return {query: data}


async def fetch_all_data(queries):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, q) for q in queries]
        return await asyncio.gather(*tasks)


def save_to_json(data, filename="output.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    data = asyncio.run(fetch_all_data(output))
    save_to_json(data, "septa_schedules.json")
    print("Data saved to septa_schedules.json")

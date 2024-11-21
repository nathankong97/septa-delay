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
    try:
        with requests.get("https://www3.septa.org/developer/gtfs_public.zip", stream=True) as response:
            response.raise_for_status()
            with open(download_zip_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        logging.info("GTFS ZIP file downloaded successfully.")
    except Exception as e:
        logging.error(f"Failed to download GTFS ZIP file: {e}")
        raise
    try:
        with zipfile.ZipFile(download_zip_path, "r") as zip_ref:
            zip_ref.extractall("./data")
        os.remove(download_zip_path)
        logging.info("GTFS ZIP file extracted and removed successfully.")
    except Exception as e:
        logging.error(f"Failed to extract GTFS ZIP file: {e}")
        raise

    try:
        with zipfile.ZipFile(target_rail_path, "r") as zip_ref:
            zip_ref.extractall("./data")
        logging.info("Google Rail ZIP file extracted successfully.")
    except Exception as e:
        logging.error(f"Failed to extract Google Rail ZIP file: {e}")
        raise
    conn = sqlite3.connect("./data/septa.sqlite")
    cursor = conn.cursor()
    for file_name in os.listdir("./data"):
        if file_name.endswith('.txt'):
            file_path = os.path.join("./data", file_name)
            df = pd.read_csv(file_path)
            table_name = os.path.splitext(file_name)[0]
            df.to_sql(table_name, conn, if_exists='replace', index=False)
else:
    logging.info("No new GTFS updates found within the last 24 hours.")
    conn = sqlite3.connect("./data/septa.sqlite")
    cursor = conn.cursor()
logging.info("SQLite connection established.")

query = f"""
    SELECT DISTINCT block_id FROM trips t INNER JOIN calendar c ON t.service_id = c.service_id
    WHERE c.{day_of_week} = 1;
    """
logging.info(f"Executing query: {query}")
cursor.execute(query)
result = cursor.fetchall()
output = [str(row[0]) for row in result]
logging.info(f"Query result: {output}")
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
    logging.info(f"Fetching URL: {url}")
    try:
        async with session.get(url) as response:
            data = await response.json()
            logging.info(f"Data fetched for query {query}")
            return {query: data}
    except Exception as e:
        logging.error(f"Error fetching query {query}: {e}")
        return {query: None}


async def fetch_all_data(queries):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, q) for q in queries]
        return await asyncio.gather(*tasks)


def save_to_json(data, filename):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        logging.info(f"Data saved to JSON file: {filename}")
    except Exception as e:
        logging.error(f"Failed to save data to JSON: {e}")
        raise


if __name__ == "__main__":
    logging.info("Starting main script execution...")
    try:
        data = asyncio.run(fetch_all_data(output))
        save_to_json(data, json_filename)
        logging.info("All tasks completed successfully.")
    except Exception as e:
        logging.critical(f"Critical error occurred: {e}", exc_info=True)
    logging.info("Script execution completed.")

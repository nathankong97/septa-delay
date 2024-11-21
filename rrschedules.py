import os
import logging
import requests
import json
import zipfile
import sqlite3
import pandas as pd
import asyncio
import aiohttp
from datetime import datetime, timedelta
import feedparser

# Constants
RSS_URL = 'https://github.com/septadev/GTFS/releases.atom'
GTFS_ZIP_URL = "https://www3.septa.org/developer/gtfs_public.zip"
DATA_DIR = "./data"
SCRAPING_DIR_BASE = "scraping/rr-schedule"
LOG_DIR_BASE = "logs/rr-schedule"
DB_PATH = os.path.join(DATA_DIR, "septa.sqlite")
API_URL = "https://www3.septa.org/api/RRSchedules/index.php?req1="


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


def create_directories(path):
    os.makedirs(path, exist_ok=True)


def setup_logging(log_dir):
    log_filename = f"{log_dir}/{get_timestamp()}.log"
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)
    logging.info("Logging initialized.")
    return log_filename


def download_and_extract_zip(url, zip_path, extract_path):
    logging.info(f"Downloading ZIP file from {url}...")
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(zip_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    logging.info(f"Download completed. Extracting ZIP file to {extract_path}...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)
    os.remove(zip_path)
    logging.info(f"ZIP extraction completed. {zip_path} removed.")


def update_database(data_dir, db_path):
    logging.info("Updating SQLite database with GTFS files...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for file_name in os.listdir(data_dir):
        if file_name.endswith('.txt'):
            file_path = os.path.join(data_dir, file_name)
            table_name = os.path.splitext(file_name)[0]
            try:
                logging.info(f"Inserting {file_name} into database table '{table_name}'...")
                df = pd.read_csv(file_path)
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                logging.info(f"Table '{table_name}' updated successfully.")
            except Exception as e:
                logging.error(f"Error processing {file_name}: {e}")

    cursor.close()
    conn.close()
    logging.info("Database update completed.")


def query_database(db_path, day_of_week):
    logging.info(f"Querying database for day_of_week: {day_of_week}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = f"""
        SELECT COUNT(DISTINCT block_id) 
        FROM trips t 
        INNER JOIN calendar c ON t.service_id = c.service_id
        WHERE c.{day_of_week} = 1;
    """

    cursor.execute(query)
    result = cursor.fetchall()
    output = [str(row[0]) for row in result]
    cursor.close()
    conn.close()
    logging.info(f"Query completed. Result: {output}")
    return output


async def fetch_url(session, query):
    url = f"{API_URL}{query}"
    try:
        async with session.get(url) as response:
            data = await response.json()
            logging.info(f"Fetched data for query: {query}")
            return {query: data}
    except Exception as e:
        logging.error(f"Error fetching query {query}: {e}")
        return {query: None}


async def fetch_all_data(queries):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, query) for query in queries]
        return await asyncio.gather(*tasks)


def save_to_json(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
    logging.info(f"Data saved to {filename}.")


def main():
    logging.info("Parsing RSS feed for GTFS updates...")
    feed = feedparser.parse(RSS_URL)
    latest_release_update = feed["entries"][0]["updated"]
    update_datetime = datetime.strptime(latest_release_update, "%Y-%m-%dT%H:%M:%SZ")

    current_time = datetime.utcnow()
    one_day_before = current_time - timedelta(days=1)
    day_of_week = datetime.now().strftime('%A').lower()

    if one_day_before <= update_datetime <= current_time:
        logging.info("GTFS update found within the last 24 hours. Downloading new data...")
        create_directories(DATA_DIR)
        download_zip_path = os.path.join(DATA_DIR, "septa_gtfs.zip")
        download_and_extract_zip(GTFS_ZIP_URL, download_zip_path, DATA_DIR)
        update_database(DATA_DIR, DB_PATH)
    else:
        logging.info("No GTFS updates found within the last 24 hours.")
    output = query_database(DB_PATH, day_of_week)[:15]

    today_date = datetime.now().strftime("%Y-%m-%d")
    scraping_dir = f"{SCRAPING_DIR_BASE}/{today_date}"
    log_dir = f"{LOG_DIR_BASE}/{today_date}"
    create_directories(scraping_dir)
    create_directories(log_dir)
    setup_logging(log_dir)

    json_filename = f"{scraping_dir}/rr-schedule_{get_timestamp()}.json"
    logging.info("Starting asynchronous API calls...")
    data = asyncio.run(fetch_all_data(output))
    save_to_json(data, json_filename)
    logging.info("All tasks completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"Critical error occurred: {e}", exc_info=True)

import requests
import json
import os
import logging
from datetime import datetime


# Function to get the current timestamp in the format yyyy-mm-dd-hh-mm-ss
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


# Get today's date to create directories
today_date = datetime.now().strftime("%Y-%m-%d")

# Directories for storing scraping data and logs
scraping_dir = f"scraping/train-view/{today_date}"
log_dir = f"logs/train-view/{today_date}"

# Create directories if they don't exist
os.makedirs(scraping_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

# Set up logging
log_filename = f"{log_dir}/{get_timestamp()}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Path to the JSON file with timestamped filename
json_filename = f"{scraping_dir}/train_view_{get_timestamp()}.json"

# API endpoint (replace with actual API URL)
API_URL = "https://www3.septa.org/api/TrainView/index.php"  # Replace with the real URL


# Function to fetch and store data in JSON file
def fetch_and_store_data():
    try:
        # Fetching data from the API
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        data = response.json()

        # Store data in JSON file
        with open(json_filename, "w") as file:
            json.dump(data, file, indent=4)

        logging.info(f"Data fetched and stored at {datetime.now()}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data: {e}")
    except Exception as e:
        logging.error(f"Error processing data: {e}")


# Run the function once for testing
fetch_and_store_data()

import os
from datetime import datetime

# Function to get the current timestamp in the format yyyy-mm-dd-hh-mm-ss
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

# Function to get today's date in yyyy-mm-dd format
def get_today_date():
    return datetime.now().strftime("%Y-%m-%d")

# Create directories if they don't exist
def create_dir(directory):
    os.makedirs(directory, exist_ok=True)

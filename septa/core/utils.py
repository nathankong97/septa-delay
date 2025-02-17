import os
from datetime import datetime


def get_timestamp():
    """Return current timestamp."""
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


def get_today_date() -> str:
    """Return today's date."""
    return datetime.now().strftime("%Y-%m-%d")


def create_dir(directory):
    """Create directories if they don't exist."""
    os.makedirs(directory, exist_ok=True)

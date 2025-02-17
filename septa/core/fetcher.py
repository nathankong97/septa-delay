import requests
import logging


def fetch_data(api_url):
    """Fetch data from an API and return JSON response."""
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {api_url}: {e}")
        return None

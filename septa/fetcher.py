import requests
try:
    from util import get_timestamp
except ImportError:
    from .util import get_timestamp


# Fetch data from the API
def fetch_data(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        # Log the error and return None
        logging.error(f"Error fetching data: {e}")
        return None
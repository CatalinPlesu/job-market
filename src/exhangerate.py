# exchangemld.py
import requests

API_URL = "https://open.er-api.com/v6/latest/{}"


class ExchangeAPIError(Exception):
    """Custom exception for ExchangeRate API errors."""
    pass


def get_exchange_rates(base_code="MDL"):
    """
    Fetch all exchange rates relative to a given base currency.
    Returns a dict like:
        { 'USD': 1.0, 'EUR': 0.92, 'MDL': 17.6, ... }

    Example:
        rates = get_exchange_rates("EUR")
        print(rates["USD"])  # 1.09
    """
    base_code = base_code.upper()
    response = requests.get(API_URL.format(base_code))

    if response.status_code == 429:
        raise ExchangeAPIError("Rate limit exceeded. Wait 20 minutes before retrying.")
    if response.status_code != 200:
        raise ExchangeAPIError(f"HTTP {response.status_code}: {response.text}")

    data = response.json()
    if data.get("result") != "success":
        raise ExchangeAPIError(f"API error: {data.get('error-type', 'unknown error')}")

    return data["rates"]

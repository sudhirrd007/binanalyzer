import requests
import logging
from pydantic import BaseModel, field_validator, ValidationError, validate_call


def get_response(method="get", endpoint_str="", params={}, headers={}):
    url = "http://binance_api:8000/"
    if endpoint_str != "":
        url += endpoint_str

    if not headers:
        headers = {"accept": "application/json"}

    if not params:
        params = {}

    if method == "get":
        response = requests.get(url, headers=headers, params=params)
    elif method == "post":
        response = requests.post(url, headers=headers, params=params)
    else:
        raise ValueError("Invalid method")

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError("Error in response")


class Stats(BaseModel):
    symbol: str
    buy_price_normal: float = None
    sell_price_normal: float = None
    precision: float = None
    # high_24h: float = None
    # low_24h: float = None

    def __init__(self, **data):
        super().__init__(**data)
        self.refresh_stats()

    def refresh_stats(self):
        self.buy_price_normal = self.get_coin_price()
        self.sell_price_normal = self.buy_price_normal * (1 - 0.015)
        self.precision = calculate_precision(self.buy_price_normal)

    def get_coin_price(self):
        logging.info(
            "Getting Coin Price for %s - %s",
            self.symbol,
            get_response(method="get", params={"coin_name": "btc"}),
        )
        return get_response(method="get", params={"coin_name": "btc"})


def calculate_precision(value):
    # Convert the value to a string to work with decimal places
    value_str = f"{value:.16f}"  # Convert value to string with enough precision
    value_str = value_str.rstrip("0")  # Strip unnecessary trailing zeros

    # Find the position of the decimal point
    if "." in value_str:
        decimal_position = value_str.find(".")
        # Count how many significant decimal places there are
        significant_decimals = len(value_str) - decimal_position - 1
    else:
        # If there is no decimal point, no rounding is necessary
        significant_decimals = 0

    return significant_decimals

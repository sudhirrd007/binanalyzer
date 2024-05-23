import requests
import logging
from pydantic import BaseModel, field_validator, ValidationError, validate_call


def get_response(method="get", endpoint_method="", params={}, headers={}):
    # url = "http://binance_api:8000/"
    url = "http://localhost:8000/"
    if endpoint_method != "":
        url += endpoint_method

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


class Wallet(BaseModel):
    symbol: str
    # coin_holdings_dict: dict = None
    total_available_coins: float = None

    def __init__(self, **data):
        super().__init__(**data)
        self.refresh_wallet()

    def refresh_wallet(self):
        # self.coin_holdings_dict = self.get_total_no_of_coins(self.symbol)
        # self.total_available_coins = self.coin_holdings_dict["total_coins"]
        self.total_available_coins = self.get_total_no_of_coins(self.symbol)

    def get_total_no_of_coins(self, symbol):
        symbol = symbol.upper().strip()
        spot_wallet_response = get_response(
            method="get",
            endpoint_method="coins_in_spot_wallet",
            params={"coin_name": symbol},
        )
        spot_coins = (
            spot_wallet_response["free_coins"]
            + spot_wallet_response["locked_coins"]
            + spot_wallet_response["freeze_coins"]
            + spot_wallet_response["ipoable_coins"]
            + spot_wallet_response["withdrawing_coins"]
        )
        funding_wallet_response = get_response(
            method="get",
            endpoint_method="coins_in_funding_wallet",
            params={"coin_name": symbol},
        )
        funding_coins = (
            funding_wallet_response["free_coins"]
            + funding_wallet_response["locked_coins"]
            + funding_wallet_response["freeze_coins"]
            + funding_wallet_response["withdrawing_coins"]
        )
        earn_wallet_response = get_response(
            method="get",
            endpoint_method="coins_in_earn_wallet",
            params={"coin_name": symbol},
        )
        earn_coins = earn_wallet_response["total_coins"]
        total_coins = spot_coins + funding_coins + earn_coins
        return total_coins

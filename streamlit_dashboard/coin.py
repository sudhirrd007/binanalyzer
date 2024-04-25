import logging

import requests
import json

logging.basicConfig(level=logging.INFO)

BASE_URL = "http://127.0.0.1:5000/"


class Coin:
    def __init__(self, symbol):
        self.symbol = symbol

    def get_coin_price(self):
        payload = json.dumps({"coin": self.symbol})
        headers = {"Content-Type": "application/json"}

        response = requests.request(
            "POST",
            BASE_URL + "/coinpair_price",
            headers=headers,
            data=payload,
            timeout=400000,
        )

        return response.json()

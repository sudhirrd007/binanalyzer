from coin import Coin

import logging

logging.basicConfig(level=logging.INFO)

BASE_URL = "http://127.0.0.1:5000"

class StreamlitFacade:
    def get_coin_price(self, coin):
        coin_obj = Coin(coin)
        return coin_obj.get_coin_price()

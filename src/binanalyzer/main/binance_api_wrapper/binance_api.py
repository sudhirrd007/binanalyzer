from binance.spot import Spot
# from binance.api import API
import hmac
import hashlib
import requests
from datetime import datetime, timedelta


class BinanceAPI:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def get_coinpair_price(self, coin_pair):
        """Fetch the current price of the coin_pair"""
        client = Spot()
        response = client.ticker_price(symbol=f"{coin_pair}")
        return float(response["price"])

    def get_convert_history(
        self, start_timestamp=None, end_timestamp=None, **params_dict
    ):
        """Fetch the convert trade history
        end_timestamp: int(end.timestamp()*1000-1000) send less 1 second to get the last trade
        start_timestamp: {1623824139000} should be have length 13
        """
        # Validating the parameters -------------------------
        if start_timestamp:
            if not isinstance(start_timestamp, int):
                if isinstance(start_timestamp, float):
                    start_timestamp = int(start_timestamp.timestamp())
                else:
                    raise ValueError("start_timestamp should be an int or float type")
        else:
            start_timestamp = datetime.now() - timedelta(days=45)
            start_timestamp = start_timestamp.timestamp() * 1000 - 1000
            start_timestamp = int(start_timestamp)

        if end_timestamp:
            if not isinstance(end_timestamp, int):
                if isinstance(end_timestamp, float):
                    end_timestamp = int(end_timestamp.timestamp())
                else:
                    raise ValueError("end_timestamp should be an int or float type")
        else:
            end_timestamp = datetime.now().timestamp()
            end_timestamp = int(end_timestamp * 1000)

        # Logic -------------------------
        client = Spot(api_key=self.api_key, api_secret=self.api_secret)

        response = client.get_convert_trade_history(
            startTime=start_timestamp,
            endTime=end_timestamp,
        )
        return response  # response['list']

    def fetch_no_of_coin_from_spot_wallet(self, coin):
        """Get your no of coins in Binance Spot Wallet
        coin: ex 'BTC', 'ETH', 'USDT', 'BNB'
        """
        timestamp = int(get_timestamp_offset())
        # timestamp = int(time.time() * 1000 + get_timestamp_offset())

        query_string = f"asset={coin}&timestamp={timestamp}"
        # query_string = f"timestamp={timestamp}"

        signature = self.generate_signature(query_string)

        url = f"https://api.binance.com/sapi/v3/asset/getUserAsset?{query_string}&signature={signature}"
        payload = {}
        headers = {
            "Content-Type": "application/json",
            "X-MBX-APIKEY": self.api_key,
        }
        result = requests.request(
            "POST", url, headers=headers, data=payload, timeout=10
        )
        response = result.json()
        if not response:
            return 0
        else:
            total_coins = 0
            for item in response:
                total_coins += float(item["free"]) + float(item["locked"])
            return total_coins

    def fetch_no_of_coin_from_funding_wallet(self, coin):
        """Get your no of coins in Binance Funding Wallet
        coin: ex 'BTC', 'ETH', 'USDT', 'BNB'
        """
        timestamp = int(get_timestamp_offset())
        # timestamp = int(time.time() * 1000 + get_timestamp_offset())

        query_string = f"asset={coin}&timestamp={timestamp}"
        # query_string = f"timestamp={timestamp}"

        signature = self.generate_signature(query_string)

        url = f"https://api.binance.com/sapi/v1/asset/get-funding-asset?{query_string}&signature={signature}"
        payload = {}
        headers = {
            "Content-Type": "application/json",
            "X-MBX-APIKEY": self.api_key,
        }
        result = requests.request(
            "POST", url, headers=headers, data=payload, timeout=10
        )
        response = result.json()
        if not response:
            return 0
        else:
            total_coins = 0
            for item in response:
                total_coins += float(item["free"]) + float(item["locked"])
            return total_coins

    def fetch_no_of_coin_from_flexible_earn_wallet(self, coin):
        """Get your no of coins in Binance Earn Wallet :: Flexible Savings
        coin: ex 'BTC', 'ETH', 'USDT', 'BNB'
        """
        timestamp = int(get_timestamp_offset())
        # timestamp = int(time.time() * 1000 + get_timestamp_offset())

        query_string = f"asset={coin}&timestamp={timestamp}"
        # query_string = f"timestamp={timestamp}"

        signature = self.generate_signature(query_string)

        url = f"https://api.binance.com/sapi/v1/simple-earn/flexible/position?{query_string}&signature={signature}"
        payload = {}
        headers = {
            "Content-Type": "application/json",
            "X-MBX-APIKEY": self.api_key,
        }
        result = requests.request("GET", url, headers=headers, data=payload, timeout=10)
        response = result.json()
        if not response:
            return 0
        else:
            total_coins = 0
            for item in response["rows"]:
                total_coins += float(item["totalAmount"])
            return total_coins


    def generate_signature(self, query_string):
        m = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        )
        return m.hexdigest()


def get_timestamp_offset():
    url = "https://api.binance.com/api/v3/time"
    payload = {}
    headers = {"Content-Type": "application/json"}
    response = requests.request("GET", url, headers=headers, data=payload, timeout=10)
    return response.json()["serverTime"]
    # return json.loads(response.text)["serverTime"] - int(time.time() * 1000)


# Useful methods
# https://binance-docs.github.io/apidocs/spot/en/#simple-earn-endpoints

# Spot Assets ==================================================
# client.get_asset_balance(asset='USDT') # Spot Account

import os
import hmac
import hashlib
import requests

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

print(API_KEY)

class BinanceAPIWrapper:
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
            "X-MBX-APIKEY": API_KEY,
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
            "X-MBX-APIKEY": API_KEY,
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
            "X-MBX-APIKEY": API_KEY,
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
            API_SECRET.encode("utf-8"),
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

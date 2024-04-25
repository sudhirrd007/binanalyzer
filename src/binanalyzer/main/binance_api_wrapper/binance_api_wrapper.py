import os
import hmac
import hashlib
import requests
from binance.spot import Spot
from datetime import datetime, timedelta

BASE_URL = "https://api.binance.com"


class BinanceAPIWrapper:
    def __init__(self):
        pass

    def get_coinpair_price(self, coin_pair) -> float:
        """Fetch the current price of the coin_pair"""
        client = Spot()
        response = client.ticker_price(symbol=f"{coin_pair}")
        return float(response["price"])

    def get_total_no_of_coins(self, coin):
        """Get your total no of coins in Binance Spot, Funding, Flexible Earn Wallet"""
        spot = self.get_no_of_coin_from_spot_wallet(coin)
        funding = self.get_no_of_coin_from_funding_wallet(coin)
        flexible_earn = self.get_no_of_coin_from_flexible_earn_wallet(coin)
        total_coins = spot + funding + flexible_earn
        return {
            "spot": spot,
            "funding": funding,
            "flexible_earn": flexible_earn,
            "total_coins": total_coins,
        }

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
        client = Spot(
            api_key=os.getenv("BINANCE_API_KEY"),
            api_secret=os.getenv("BINANCE_API_SECRET"),
        )

        response = client.get_convert_trade_history(
            startTime=start_timestamp,
            endTime=end_timestamp,
        )
        return response  # response['list']

    def get_no_of_coin_from_spot_wallet(self, coin_name):
        """Get your no of coins in Binance Spot Wallet
        coin: ex 'BTC', 'ETH', 'USDT', 'BNB'
        """
        query_string, signature, payload, headers = create_api_parameters(coin_name)
        url = f"{BASE_URL}/sapi/v3/asset/getUserAsset?{query_string}&signature={signature}"

        result = requests.request(
            "POST",
            url,
            headers=headers,
            data=payload,
            timeout=10,
        )
        response = result.json()
        if not response:
            return 0
        else:
            total_coins = 0
            for item in response:
                total_coins += float(item["free"]) + float(item["locked"])
            return total_coins

    def get_no_of_coin_from_funding_wallet(self, coin_name):
        """Get your no of coins in Binance Funding Wallet
        coin: ex 'BTC', 'ETH', 'USDT', 'BNB'
        """
        query_string, signature, payload, headers = create_api_parameters(coin_name)
        url = f"{BASE_URL}/sapi/v1/asset/get-funding-asset?{query_string}&signature={signature}"
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

    def get_no_of_coin_from_flexible_earn_wallet(self, coin_name):
        """Get your no of coins in Binance Earn Wallet :: Flexible Savings
        coin: ex 'BTC', 'ETH', 'USDT', 'BNB'
        """
        query_string, signature, payload, headers = create_api_parameters(coin_name)
        url = f"{BASE_URL}/sapi/v1/simple-earn/flexible/position?{query_string}&signature={signature}"
        result = requests.request("GET", url, headers=headers, data=payload, timeout=10)
        response = result.json()
        if not response:
            return 0
        else:
            total_coins = 0
            for item in response["rows"]:
                total_coins += float(item["totalAmount"])
            return total_coins


def get_timestamp_offset():
    url = f"{BASE_URL}/api/v3/time"
    payload = {}
    headers = {"Content-Type": "application/json"}
    response = requests.request("GET", url, headers=headers, data=payload, timeout=10)
    return response.json()["serverTime"]
    # return json.loads(response.text)["serverTime"] - int(time.time() * 1000)


def generate_signature(query_string):
    m = hmac.new(
        os.getenv("BINANCE_API_SECRET").encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256,
    )
    return m.hexdigest()


def create_api_parameters(coin_name):
    """Create Metadata for Binance API calling"""
    timestamp = int(get_timestamp_offset())
    # timestamp = int(time.time() * 1000 + get_timestamp_offset())

    query_string = f"asset={coin_name}&timestamp={timestamp}"
    # query_string = f"timestamp={timestamp}"

    signature = generate_signature(query_string)

    payload = {}
    headers = {
        "Content-Type": "application/json",
        "X-MBX-APIKEY": os.getenv("BINANCE_API_KEY"),
    }

    return query_string, signature, payload, headers

import os
import hmac
import hashlib
import requests
from binance.spot import Spot
from datetime import datetime, timedelta

BASE_URL = "https://api.binance.com"


class BinanceWrapper:
    def __init__(self):
        pass

    def get_coinpair_price(self, coin_pair) -> float:
        """Fetch the current price of the coin_pair"""
        # make coin pair in upper case
        coin_pair = coin_pair.upper().strip()
        client = Spot()
        response = client.ticker_price(symbol=coin_pair)
        return float(response["price"])

    def get_total_no_of_coins(self, coin):
        """Get your total no of coins in Binance Spot, Funding, Flexible Earn Wallet"""
        spot = self.get_no_of_coin_from_spot_wallet(coin)
        funding = self.get_no_of_coin_from_funding_wallet(coin)
        flexible_earn = self.get_no_of_coin_from_flexible_earn_wallet(coin)
        total_coins = spot + funding + flexible_earn
        return total_coins

    def get_convert_history(
        self, start_timestamp=None, end_timestamp=None, **params_dict
    ):
        """Fetch the convert trade history
        end_timestamp: int(end.timestamp()*1000-1000) send less 1 second to get the last trade
        start_timestamp: {1623824139000} should be have length 13

        sample response from binance api:
            response['list'] = [
                {
                    "quoteId": "9950f21b3f4b43329da49c2532c64719",
                    "orderId": 1670059876560505617,
                    "orderStatus": "SUCCESS",
                    "fromAsset": "LTC",
                    "fromAmount": "0.32771067",
                    "toAsset": "USDT",
                    "toAmount": "24.09672353",
                    "ratio": "73.5305000000000000",
                    "inverseRatio": "0.0135997987229789",
                    "createTime": 1709156558791,
                    "orderType": "MARKET",
                    "side": "SELL",
                },
                {
                    "quoteId": "9950f21b3f4b43329da49c2532c64719",
                    "orderId": 1670059876560505617,
                    "orderStatus": "SUCCESS",
                    "fromAsset": "USDT",
                    "fromAmount": "24.09672353",
                    "toAsset": "LTC",
                    "toAmount": "0.32771067",
                    "ratio": "73.5305000000000000",
                    "inverseRatio": "0.0135997987229789",
                    "createTime": 1709156558791,
                    "orderType": "MARKET",
                    "side": "BUY",
            ]
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
            return None
        else:
            response_dict = {
                "free_coins": 0.0,
                "locked_coins": 0.0,
                "freeze_coins": 0.0,
                "withdrawing_coins": 0.0,
                "ipoable_coins": 0.0,
            }
            for item in response:
                response_dict["free_coins"] += float(item["free"])
                response_dict["locked_coins"] += float(item["locked"])
                response_dict["freeze_coins"] += float(item["freeze"])
                response_dict["withdrawing_coins"] += float(item["withdrawing"])
                response_dict["ipoable_coins"] += float(item["ipoable"])

            return response_dict

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
            return None
        else:
            response_dict = {
                "free_coins": 0.0,
                "locked_coins": 0.0,
                "freeze_coins": 0.0,
                "withdrawing_coins": 0.0,
            }
            for item in response:
                response_dict["free_coins"] += float(item["free"])
                response_dict["locked_coins"] += float(item["locked"])
                response_dict["freeze_coins"] += float(item["freeze"])
                response_dict["withdrawing_coins"] += float(item["withdrawing"])

            return response_dict

    def get_no_of_coin_from_earn_wallet(self, coin_name):
        """Get your no of coins in Binance Earn Wallet :: Flexible Savings
        coin: ex 'BTC', 'ETH', 'USDT', 'BNB'

        sample response from binance api:
            {
                "total": 1,
                "rows": [
                    {
                        "totalAmount": "0.02353327",
                        "tierAnnualPercentageRate": {"0-0.01BTC": "0.00250000"},
                        "latestAnnualPercentageRate": "0.0005999",
                        "asset": "BTC",
                        "canRedeem": True,
                        "collateralAmount": "0",
                        "productId": "BTC001",
                        "yesterdayRealTimeRewards": "0.00000004",
                        "cumulativeBonusRewards": "0.00001799",
                        "cumulativeRealTimeRewards": "0.00001614",
                        "cumulativeTotalRewards": "0.00019682",
                        "autoSubscribe": True,
                    }
                ],
            }
        """
        query_string, signature, payload, headers = create_api_parameters(coin_name)
        url = f"{BASE_URL}/sapi/v1/simple-earn/flexible/position?{query_string}&signature={signature}"
        result = requests.request("GET", url, headers=headers, data=payload, timeout=10)
        response = result.json()

        if not response:
            return False
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

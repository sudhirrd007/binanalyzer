import logging
import json
import requests
from .transaction.transaction import Transaction
from .transaction.binance_transaction import BinanceTransaction
from .binance_api import BinanceAPI

logging.basicConfig(level=logging.INFO)


class DatabaseSync:
    def sync_database(self):
        logging.info(green_message("Syncing database from Binance (Binanalyzer)"))
        binance_transaction_list = fetch_binance_transactions_list()
        # A sample binance_transaction_list from binance
        # [{
        #     "quoteId": "9950f21b3f4b43329da49c2532c64719",
        #     "orderId": 1670059876560505617,
        #     "orderStatus": "SUCCESS",
        #     "fromAsset": "LTC",
        #     "fromAmount": "0.32771067",
        #     "toAsset": "USDT",
        #     "toAmount": "24.09672353",
        #     "ratio": "73.5305000000000000",
        #     "inverseRatio": "0.0135997987229789",
        #     "createTime": 1709156558791,
        #     "orderType": "MARKET",
        #     "side": "SELL",
        # },]

        transaction_list = []
        for trans_dict in binance_transaction_list:
            binance_trans_obj = BinanceTransaction(**trans_dict)
            binance_trans_dict = binance_trans_obj.convert_to_transaction()
            binance_trans_dict["automatically_added"] = False
            transaction_obj = Transaction(**binance_trans_dict)
            transaction_list.append(transaction_obj.model_dump())

        payload = json.dumps({"transaction_list": transaction_list})
        headers = {"Content-Type": "application/json"}

        response = requests.request(
            "POST",
            "http://binanalyzer_database:8080/binance_transactions/sync_binance_transactions",
            headers=headers,
            data=payload,
            timeout=400000,
        )
        if response.status_code == 200:
            logging.info(green_message("Database synced successfully"))
        else:
            raise Exception(red_message(f"Failed to sync database. {response.text}"))


def fetch_binance_transactions_list():
    response = BinanceAPI().get_convert_history()
    if not response or "list" not in response:
        logging.warning("No transactions found in Binance convert history response")
        return []
    return response["list"]


def red_message(message):
    red_code = "\033[91m"  # Red
    end_code = "\033[0m"
    return f"""{red_code} {message} {end_code}"""


def green_message(message):
    green_code = "\033[92m"  # Green
    end_code = "\033[0m"
    return f"""{green_code} {message} {end_code}"""

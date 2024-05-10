import logging
from pathlib import Path
from omegaconf import OmegaConf
import json

from binance_wrapper.binance_wrapper import BinanceWrapper
from sqlite_wrapper import SQLiteWrapper
from transaction.transaction import Transaction

current_dir = Path(__file__).resolve().parent
credentials_yml_path = current_dir.joinpath("data").joinpath("initial_transactions.yml")
CONF = OmegaConf.load(credentials_yml_path)
UNTRACKED_TRANSACTIONS_JSON_FILE = current_dir.joinpath("data").joinpath(
    "untracked_transactions.json"
)

logging.basicConfig(level=logging.INFO)


class DBSync:
    def __init__(self):
        self.binance_wrapper = BinanceWrapper()
        self.sqlite_wrapper_obj = SQLiteWrapper()

    def sync_database(self):
        row_count = self.sqlite_wrapper_obj.database_manager_obj.fetch_row_count()
        if row_count == 0:
            self.sync_initial_transactions()
            self.sync_untracked_transactions()

        logging.info(green_message("Syncing database from Binance"))
        response = self.binance_wrapper.binance_api.get_convert_history()
        transaction_list = response["list"]

        # A sample transaction_dict from transaction_list
        # {
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
        # }
        success, duplicated, failed = 0, 0, 0
        for trans_dict in transaction_list:
            timezone = "US/Eastern"
            timestamp = trans_dict["createTime"]
            order_status = trans_dict["orderStatus"]
            quote_id = trans_dict["quoteId"]
            order_id = trans_dict["orderId"]
            automatically_added = 0
            conversion_ratio = float(trans_dict["ratio"])
            trade_type = trans_dict["orderType"]

            # values relies on if transaction is BUY or SELL
            coin = None
            coin_amount = None
            usdt_equivalent = None
            buy_sell = None
            miscellaneous = ""

            if trans_dict["toAsset"] == "USDT":
                coin = trans_dict["fromAsset"]
                coin_amount = float(trans_dict["fromAmount"])
                usdt_equivalent = float(trans_dict["toAmount"])
                buy_sell = "SELL"
            elif trans_dict["fromAsset"] == "USDT":
                coin = trans_dict["toAsset"]
                coin_amount = float(trans_dict["toAmount"])
                usdt_equivalent = float(trans_dict["fromAmount"])
                buy_sell = "BUY"
            else:
                print("Error: USDT not found in trans_dict")
                continue

            transaction_obj = Transaction(
                coin=coin,
                timezone=timezone,
                timestamp=timestamp,
                order_status=order_status,
                quote_id=quote_id,
                order_id=order_id,
                automatically_added=automatically_added,
                coin_amount=coin_amount,
                conversion_ratio=conversion_ratio,
                trade_type=trade_type,
                usdt_equivalent=usdt_equivalent,
                buy_sell=buy_sell,  # BUY is True, SELL is False
                miscellaneous=miscellaneous,
            )
            response = (
                self.sqlite_wrapper_obj.database_manager_obj.insert_single_transaction(
                    transaction_obj
                )
            )
            if response == "success":
                logging.info(
                    green_message(f'Successful: OrderId: {trans_dict["orderId"]}')
                )
                success += 1
            elif response == "duplicated":
                duplicated += 1
            else:
                logging.info(red_message(f'Failed: OrderId: {trans_dict["orderId"]}'))
                failed += 1

        logging.info(
            "Total: %s, Success: %s, Duplicated: %s, Failed: %s",
            len(transaction_list),
            success,
            duplicated,
            failed,
        )

    def sync_initial_transactions(self):
        logging.info(green_message("Syncing initial transactions"))
        success, duplicated, failed = 0, 0, 0

        for _, coin_trans_list in CONF.items():
            for coin_dict in coin_trans_list:
                transaction_obj = Transaction(
                    coin=coin_dict["coin"],
                    timezone=coin_dict["timezone"],
                    timestamp=coin_dict["timestamp"],
                    order_status=coin_dict["order_status"],
                    quote_id=coin_dict["quote_id"],
                    order_id=coin_dict["order_id"],
                    automatically_added=coin_dict["automatically_added"],
                    coin_amount=coin_dict["coin_amount"],
                    conversion_ratio=coin_dict["conversion_ratio"],
                    trade_type=coin_dict["trade_type"],
                    usdt_equivalent=coin_dict["usdt_equivalent"],
                    buy_sell=coin_dict["buy_sell"],  # BUY is True, SELL is False
                    miscellaneous=coin_dict["miscellaneous"],
                )
                response = self.sqlite_wrapper_obj.database_manager_obj.insert_single_transaction(
                    transaction_obj
                )
                if response == "success":
                    logging.info(
                        green_message(
                            f'Successful: order_id: {transaction_obj["order_id"]}'
                        )
                    )
                    success += 1
                elif response == "duplicated":
                    duplicated += 1
                else:
                    logging.info(
                        red_message(f'Failed: order_id: {transaction_obj["order_id"]}')
                    )
                    failed += 1

        logging.info(
            "Success: %s, Duplicated: %s, Failed: %s",
            success,
            duplicated,
            failed,
        )

    def sync_untracked_transactions(self):
        logging.info(green_message("Syncing untracked transactions"))
        success, duplicated, failed = 0, 0, 0

        # Loading the JSON data
        with open(UNTRACKED_TRANSACTIONS_JSON_FILE, "r", encoding="utf-8") as json_file:
            transaction_list = json.load(json_file)

        for trans_dict in transaction_list:
            timezone = "US/Eastern"
            timestamp = trans_dict["createTime"]
            order_status = trans_dict["orderStatus"]
            quote_id = trans_dict["quoteId"]
            order_id = trans_dict["orderId"]
            automatically_added = 0
            conversion_ratio = float(trans_dict["ratio"])
            trade_type = trans_dict["orderType"]

            # values relies on if transaction is BUY or SELL
            coin = None
            coin_amount = None
            usdt_equivalent = None
            buy_sell = None
            miscellaneous = ""

            if trans_dict["toAsset"] == "USDT":
                coin = trans_dict["fromAsset"]
                coin_amount = float(trans_dict["fromAmount"])
                usdt_equivalent = float(trans_dict["toAmount"])
                buy_sell = "SELL"
            elif trans_dict["fromAsset"] == "USDT":
                coin = trans_dict["toAsset"]
                coin_amount = float(trans_dict["toAmount"])
                usdt_equivalent = float(trans_dict["fromAmount"])
                buy_sell = "BUY"
            else:
                print("Error: USDT not found in trans_dict")
                continue

            transaction_obj = Transaction(
                coin=coin,
                timezone=timezone,
                timestamp=timestamp,
                order_status=order_status,
                quote_id=quote_id,
                order_id=order_id,
                automatically_added=automatically_added,
                coin_amount=coin_amount,
                conversion_ratio=conversion_ratio,
                trade_type=trade_type,
                usdt_equivalent=usdt_equivalent,
                buy_sell=buy_sell,  # BUY is True, SELL is False
                miscellaneous=miscellaneous,
            )
            response = (
                self.sqlite_wrapper_obj.database_manager_obj.insert_single_transaction(
                    transaction_obj
                )
            )
            if response == "success":
                logging.info(
                    green_message(f'Successful: OrderId: {trans_dict["orderId"]}')
                )
                success += 1
            elif response == "duplicated":
                duplicated += 1
            else:
                logging.info(red_message(f'Failed: OrderId: {trans_dict["orderId"]}'))
                failed += 1

        logging.info(
            "Total: %s, Success: %s, Duplicated: %s, Failed: %s",
            len(transaction_list),
            success,
            duplicated,
            failed,
        )


def red_message(message):
    red_code = "\033[91m"  # Red
    end_code = "\033[0m"
    return f"""{red_code} {message} {end_code}"""


def green_message(message):
    green_code = "\033[92m"  # Green
    end_code = "\033[0m"
    return f"""{green_code} {message} {end_code}"""

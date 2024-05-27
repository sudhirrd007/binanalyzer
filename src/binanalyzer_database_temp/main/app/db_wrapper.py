"""Do not expose this class to outside"""

import sqlite3
from sqlite3 import Error
import pandas as pd
from pathlib import Path
import logging
import json

logging.basicConfig(level=logging.INFO)

current_dir = Path(__file__).resolve().parent
BINANCE_DB_PATH = current_dir.parent.joinpath("data").joinpath("binance3.db")
DATA_DIR = current_dir.parent.joinpath("data")
UNTRACKED_TRANSACTIONS_JSON_FILE = DATA_DIR.joinpath("untracked_transactions.json")
INITIAL_TRANSACTIONS_JSON_FILE = DATA_DIR.joinpath("initial_transactions.json")

TABLE_NAME = "binance_transactions"

INSERT_QUERY = f"""
INSERT INTO {TABLE_NAME} (
    order_id, quote_id, coin, timezone, timestamp, year, month, day, time,
    order_status, automatically_added, coin_amount, conversion_ratio,
    usdt_equivalent, trade_type, buy_sell, miscellaneous
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


class DBWrapper:
    def __init__(self):
        self.create_and_load_tables_if_not_exists()

    # Endpoint
    def db_sync(self, transaction_list: list):
        logging.info(green_message("Syncing latest transactions"))
        self.insert_transcation_from_list(transaction_list)

    def create_and_load_tables_if_not_exists(self):
        with sqlite3.connect(BINANCE_DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            with open(DATA_DIR.joinpath("init.sql"), "r", encoding="utf-8") as file:
                sql_script = file.read()
            cursor.executescript(sql_script)

            cursor.execute("SELECT COUNT(*) FROM binance_transactions")
            count = cursor.fetchone()[0]
            if not count:
                logging.info(green_message("Syncing initial transactions"))
                with open(
                    INITIAL_TRANSACTIONS_JSON_FILE, "r", encoding="utf-8"
                ) as json_file:
                    transaction_list_temp = json.load(json_file)
                self.insert_transcation_from_list(transaction_list_temp)

                logging.info(green_message("Syncing untraced transactions"))
                with open(
                    UNTRACKED_TRANSACTIONS_JSON_FILE, "r", encoding="utf-8"
                ) as json_file:
                    transaction_list_temp = json.load(json_file)
                self.insert_transcation_from_list(transaction_list_temp)

    def insert_single_transaction(self, transaction_dict: dict):
        insert_data = (
            transaction_dict["order_id"],
            transaction_dict["quote_id"],
            transaction_dict["coin"],
            transaction_dict["timezone"],
            transaction_dict["timestamp"],
            transaction_dict["year"],
            transaction_dict["month"],
            transaction_dict["day"],
            transaction_dict["time"],
            transaction_dict["order_status"],
            transaction_dict["automatically_added"],
            transaction_dict["coin_amount"],
            transaction_dict["conversion_ratio"],
            transaction_dict["usdt_equivalent"],
            transaction_dict["trade_type"],
            transaction_dict["buy_sell"],
            transaction_dict["miscellaneous"],
        )

        with sqlite3.connect(BINANCE_DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            try:
                cursor.execute(INSERT_QUERY, insert_data)
                connection.commit()
                logging.info("Record Inserted in %s successfully", TABLE_NAME)
                return "success"
            except sqlite3.IntegrityError as e:
                if "unique" in str(e).lower().strip():
                    return "duplicated"
                else:
                    logging.error("Error: %s", str(e))
                    return "failed"
            except Error as e:
                logging.error("Error: %s", e)
                logging.error("Transaction dict %s", transaction_dict)
                return "failed"

    # Endpoint
    def fetch_all_transactions(self):
        with sqlite3.connect(BINANCE_DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(f"""SELECT * FROM {TABLE_NAME} ORDER BY timestamp ASC""")
            rows = cursor.fetchall()
            rows = [dict(row) for row in rows]
        return rows

    # Endpoint
    def filter_transactions(self, filter_dict: dict):
        if not filter_dict:
            return self.fetch_all_transactions()

        select_query = (
            "SELECT * FROM "
            + TABLE_NAME
            + " WHERE "
            + " AND ".join([f"{key} = '{value}'" for key, value in filter_dict.items()])
            + " COLLATE NOCASE ORDER BY timestamp ASC"
        )

        with sqlite3.connect(BINANCE_DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(select_query)
            rows = cursor.fetchall()
            rows = [dict(row) for row in rows]
        return rows

    # Endpoint
    def fetch_row_count(self):
        with sqlite3.connect(BINANCE_DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(f"""SELECT COUNT(*) FROM {TABLE_NAME}""")
            count = cursor.fetchone()[0]
        return count

    def insert_transcation_from_list(self, transaction_list: str):
        success, duplicated, failed = 0, 0, 0
        for trans_dict in transaction_list:
            response = self.insert_single_transaction(trans_dict)
            if response == "success":
                logging.info(
                    green_message("Successful: ")
                    + f'order_id: {trans_dict["order_id"]}'
                )
                success += 1
            elif response == "duplicated":
                duplicated += 1
            else:
                logging.info(
                    red_message("Failed: ") + f'order_id: {trans_dict["order_id"]}'
                )
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


if __name__ == "__main__":
    obj = DBWrapper()

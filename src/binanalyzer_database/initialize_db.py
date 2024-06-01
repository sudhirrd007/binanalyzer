import json
import mysql.connector
import time
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

current_dir = Path(__file__).resolve().parent
DATA_DIR = current_dir.joinpath("main").joinpath("data")
SQL_FILE = DATA_DIR.joinpath("mysql_init.sql")
UNTRACKED_TRANSACTIONS_JSON_FILE = DATA_DIR.joinpath("untracked_transactions.json")
INITIAL_TRANSACTIONS_JSON_FILE = DATA_DIR.joinpath("initial_transactions.json")

TABLE_NAME = "binance_transactions"

INSERT_QUERY = f"""
INSERT INTO {TABLE_NAME} (
    order_id, quote_id, coin, timezone, timestamp, year, month, day, time,
    order_status, automatically_added, coin_amount, conversion_ratio,
    usdt_equivalent, trade_type, buy_sell, miscellaneous
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

logging.info("Waiting for MySQL service to be ready for 20 seconds")
# Wait for the MySQL service to be ready
time.sleep(20)  # Adjust the sleep time as needed

# Establish the database connection
with mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", "123000"),
    database=os.getenv("MYSQL_DATABASE", "binanalyzer_database"),
    port=os.getenv("MYSQL_PORT", "3306"),
) as connection:
    # Create a cursor object using the cursor() method
    with connection.cursor() as cursor:
        # Read the SQL file
        with open(SQL_FILE, "r", encoding="utf-8") as file:
            sql_script = file.read()

        logging.info(">>> Executing SQL script")
        for result in cursor.execute(sql_script, multi=True):
            if result.with_rows:
                logging.info("Executed: %s", result.statement)
                logging.info("Result: %s", result.fetchall())
            else:
                logging.info("Executed: %s", result.statement)
        connection.commit()

        # cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        cursor.execute("SELECT COUNT(*) FROM binance_transactions", multi=False)
        # Fetch all rows from the executed query
        row_count = cursor.fetchone()[0]
        logging.info(">>>>> Row count: %s", row_count)
        connection.commit()

        if row_count < 1:
            logging.info("Syncing initial transactions")
            with open(INITIAL_TRANSACTIONS_JSON_FILE, "r", encoding="utf-8") as file:
                transactions = json.load(file)
            for transaction_dict in transactions:
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
                cursor.execute(INSERT_QUERY, insert_data)
                connection.commit()

            logging.info("Syncing untracked transactions")
            with open(UNTRACKED_TRANSACTIONS_JSON_FILE, "r", encoding="utf-8") as file:
                transactions = json.load(file)
            for transaction_dict in transactions:
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
                cursor.execute(INSERT_QUERY, insert_data)
                connection.commit()

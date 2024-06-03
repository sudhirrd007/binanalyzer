import os
from pathlib import Path
import logging
import mysql.connector
from mysql.connector import Error
from .transaction import Transaction

logging.basicConfig(level=logging.INFO)

current_dir = Path(__file__).resolve().parent
DATA_DIR = current_dir.parent.parent.joinpath("data")

TABLE_NAME = "binance_transactions"


def get_connection_obj():
    try:
        # Establish the database connection
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "123000"),
            database=os.getenv("MYSQL_DATABASE", "binanalyzer_database"),
            port=os.getenv("MYSQL_PORT", "3306"),
        )
        # Check if the connection is successful
        if connection.is_connected():
            return connection
        else:
            raise Exception(f"Connection failed. {str(e)}")
    except Exception as e:
        raise Exception(f"Connection failed. {str(e)}")


CONNECTION = get_connection_obj()
logging.info("CONNECTION object created")


class BinanceTransactionsTable:
    def sync_table_with_remote(self, transaction_dict_list: list):
        if not transaction_dict_list:
            logging.warning("Empty transaction list")
        for transaction_dict in transaction_dict_list:
            transaction_obj = Transaction(**transaction_dict)
            try:
                self.insert_single_transaction(transaction_dict)
            except Exception as e:
                if "duplicate" in str(e).lower().strip():
                    logging.warning("Duplicate record: %s", transaction_obj.order_id)
                else:
                    raise Exception(f"Failed- {str(e)}")

    # Endpoint
    def row_count(self):
        with CONNECTION.cursor() as cursor:
            # Execute the SELECT * query
            cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
            # Fetch all rows from the executed query
            row_count = cursor.fetchone()[0]
            logging.info(">>>>> Row count: %s", row_count)
            return row_count

    # Endpoint
    def select_all(self):
        with CONNECTION.cursor(dictionary=True) as cursor:
            # Execute the SELECT * query
            cursor.execute(f"SELECT * FROM {TABLE_NAME}")
            # Fetch all rows from the executed query
            records = cursor.fetchall()
            return records

    # Endpoint
    def insert_single_transaction(self, transaction_dict: dict):
        with CONNECTION.cursor() as cursor:
            transaction_obj = Transaction(**transaction_dict)
            try:
                insert_query = transaction_obj.create_insert_query()
                cursor.execute(insert_query)
                CONNECTION.commit()
                logging.info(
                    "Record Inserted successfully: %s", transaction_obj.order_id
                )
            except mysql.connector.IntegrityError as e:
                if "duplicate" in str(e).lower().strip():
                    logging.warning("Duplicate record: %s", transaction_obj.order_id)
                    raise Exception("Duplicate")
                else:
                    logging.error("Error: %s", str(e))
                    raise Exception(f"Failed - {str(e)}")
            except Error as e:
                logging.error("Error: %s", e)
                logging.error("Error Transaction dict %s", transaction_dict)
                raise Exception(f"Failed - {str(e)}")

    # Endpoint
    def filter_transactions(self, filter_dict: dict):
        if not filter_dict:
            return self.select_all()
        select_query = (
            "SELECT * FROM "
            + TABLE_NAME
            + " WHERE "
            + " AND ".join(
                [f"{key} = LOWER('{value}')" for key, value in filter_dict.items()]
            )
            + " ORDER BY timestamp ASC"
        )
        try:
            with CONNECTION.cursor(dictionary=True) as cursor:
                cursor.execute(select_query)
                records = cursor.fetchall()
                return records
        except Error as e:
            logging.error("Error: %s", e)
            raise Exception(f"Failed - {str(e)}")
        finally:
            if "cursor" in locals():
                cursor.close()


def red_message(message):
    red_code = "\033[91m"  # Red
    end_code = "\033[0m"
    return f"""{red_code} {message} {end_code}"""


def green_message(message):
    green_code = "\033[92m"  # Green
    end_code = "\033[0m"
    return f"""{green_code} {message} {end_code}"""

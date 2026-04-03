import os
from pathlib import Path
import logging
import mysql.connector
from mysql.connector import Error
from .transaction import Transaction
from sqlmodel import Field, SQLModel, create_engine, Session, select
from sqlalchemy import text, and_
from sqlalchemy.exc import IntegrityError
import pymysql

logging.basicConfig(level=logging.INFO)

current_dir = Path(__file__).resolve().parent
DATA_DIR = current_dir.parent.parent.joinpath("data")

# Set up the MySQL database connection
host = os.getenv("MYSQL_HOST", "localhost")
user = os.getenv("MYSQL_USER", "root")
password = os.getenv("MYSQL_PASSWORD", "123000")
database = os.getenv("MYSQL_DATABASE", "binanalyzer_database")
port = os.getenv("MYSQL_PORT", "3306")
DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}/{database}"

ENGINE = create_engine(DATABASE_URL, echo=False)


# Create the tables
SQLModel.metadata.create_all(ENGINE)


class BinanceTransactionsTable:
    def sync_table_with_remote(self, transaction_dict_list: list):
        if not transaction_dict_list:
            logging.warning("Empty transaction list")
        for transaction_dict in transaction_dict_list:
            transaction_obj = Transaction(**transaction_dict)
            try:
                self.insert_single_transaction(transaction_obj)
            except IntegrityError:
                logging.warning(
                    ">>> Duplicate record - order_id: %s", transaction_obj.order_id
                )

    # # Endpoint
    def row_count(self):
        with Session(ENGINE) as session:
            result = session.execute(
                text(f"SELECT COUNT(*) FROM {Transaction.__tablename__}")
            )
            row_count = result.scalar()
            return int(row_count)

    # Endpoint
    def select_all(self):
        with Session(ENGINE) as session:
            statement = select(Transaction)
            result = session.exec(statement)
            # Convert the results to a list of dictionaries
            return [transaction.model_dump() for transaction in result.all()]

    # Endpoint
    def insert_single_transaction(self, transaction_obj: Transaction):
        with Session(ENGINE) as session:
            session.add(transaction_obj)
            session.commit()

    # # Endpoint
    def filter_transactions(self, filter_dict: dict):
        if not filter_dict:
            return self.select_all()

        with Session(ENGINE) as session:
            # Construct the dynamic where clause
            filter_conditions = [
                getattr(Transaction, key) == value for key, value in filter_dict.items()
            ]
            statement = select(Transaction).where(and_(*filter_conditions))
            result = session.exec(statement)
            # Convert the results to a list of dictionaries
            return [transaction.model_dump() for transaction in result.all()]


def red_message(message):
    red_code = "\033[91m"  # Red
    end_code = "\033[0m"
    return f"""{red_code} {message} {end_code}"""


def green_message(message):
    green_code = "\033[92m"  # Green
    end_code = "\033[0m"
    return f"""{green_code} {message} {end_code}"""

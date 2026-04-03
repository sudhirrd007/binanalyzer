import json
import time
import os
import logging
from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text
from main.app.binance_transactions_table.transaction import Transaction

logging.basicConfig(level=logging.INFO)

current_dir = Path(__file__).resolve().parent
DATA_DIR = current_dir.joinpath("main").joinpath("data")
UNTRACKED_TRANSACTIONS_JSON_FILE = DATA_DIR.joinpath("untracked_transactions.json")
INITIAL_TRANSACTIONS_JSON_FILE = DATA_DIR.joinpath("initial_transactions.json")


# Set up the MySQL database connection
host = os.getenv("MYSQL_HOST", "localhost")
user = os.getenv("MYSQL_USER", "root")
password = os.getenv("MYSQL_PASSWORD", "123000")
database = os.getenv("MYSQL_DATABASE", "binanalyzer_database")
port = os.getenv("MYSQL_PORT", "3306")
DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}/{database}"

logging.info("Waiting for MySQL service to be ready for 20 seconds")
# Wait for the MySQL service to be ready
# time.sleep(20)  # Adjust the sleep time as needed

ENGINE = create_engine(DATABASE_URL, echo=False)

# Create the tables
SQLModel.metadata.create_all(ENGINE)


with Session(ENGINE) as session:
    for field_name, field_info_obj in Transaction.model_fields.items():
        if field_info_obj.description:
            session.exec(text(field_info_obj.description))

    result = session.execute(text(f"SELECT COUNT(*) FROM {Transaction.__tablename__}"))
    current_row_count = int(result.scalar())
    logging.info(">>>>> Row count: %s", current_row_count)

    if current_row_count < 80:
        logging.info("Syncing initial transactions")
        with open(INITIAL_TRANSACTIONS_JSON_FILE, "r", encoding="utf-8") as file:
            transactions = json.load(file)
        for transaction_dict in transactions:
            transaction_obj = Transaction(**transaction_dict)
            session.add(transaction_obj)
            session.commit()
        logging.info("%s transactions saved", len(transactions))

        logging.info("Syncing untracked transactions")
        with open(UNTRACKED_TRANSACTIONS_JSON_FILE, "r", encoding="utf-8") as file:
            transactions = json.load(file)
        for transaction_dict in transactions:
            transaction_obj = Transaction(**transaction_dict)
            session.add(transaction_obj)
            session.commit()
        logging.info("%s transactions saved", len(transactions))

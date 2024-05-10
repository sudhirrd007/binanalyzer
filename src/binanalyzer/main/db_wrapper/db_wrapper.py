from .sqlite_wrapper import SQLiteWrapper
from pathlib import Path

current_dir = Path(__file__).resolve().parent
BINANCE_DB_PATH = current_dir.parent.joinpath("data").joinpath("binance.db")

TABLE_NAME = "binance_transactions"

CREATE_TABLE_QUERY = """CREATE TABLE IF NOT EXISTS {table_name} (
    order_id TEXT PRIMARY KEY,
    quote_id TEXT NOT NULL,
    coin TEXT NOT NULL,
    timezone TEXT,
    timestamp INTEGER,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    time TEXT,
    order_status TEXT NOT NULL,
    automatically_added INTEGER CHECK (automatically_added IN (0, 1)),
    coin_amount REAL NOT NULL,
    conversion_ratio REAL NOT NULL,
    usdt_equivalent REAL NOT NULL,
    trade_type TEXT NOT NULL,
    buy_sell TEXT INTEGER CHECK (automatically_added IN (0, 1)),
    miscellaneous TEXT
);"""


class DBWrapper:
    def __init__(self):
        self.database_manager_obj = SQLiteWrapper(
            database_path=BINANCE_DB_PATH, table_name=TABLE_NAME
        )

    def sync_db(self):
        self.initialize_db()
        self.sync_initial_transactions()
        self.sync_untracked_transactions()

    def sync_initial_transactions(self):
        pass

    def sync_untracked_transactions(self):
        pass

    def initialize_db(self):
        self.database_manager_obj.create_table_if_not_exists(
            CREATE_TABLE_QUERY.format(table_name=TABLE_NAME)
        )


def red_message(message):
    red_code = "\033[91m"  # Red
    end_code = "\033[0m"
    return f"""{red_code} {message} {end_code}"""


def green_message(message):
    green_code = "\033[92m"  # Green
    end_code = "\033[0m"
    return f"""{green_code} {message} {end_code}"""

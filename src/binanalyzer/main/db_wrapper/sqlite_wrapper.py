"""Do not expose this class to outside"""

import sqlite3
from sqlite3 import Error
import pandas as pd

import logging

logging.basicConfig(level=logging.INFO)


class SQLiteWrapper:
    def __init__(self, database_path: str, table_name: str):
        self.database_path = database_path
        self.table_name = table_name

    def create_table_if_not_exists(self, create_table_query: str):
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (self.table_name,),
            )
            result = cursor.fetchone()
        if not result:
            with sqlite3.connect(self.database_path) as connection:
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                cursor.execute(create_table_query)
                connection.commit()
                logging.info("Table %s created successfully", self.table_name)

    def insert_single_transaction(self, transaction_obj: dict):
        keys = transaction_obj.__dict__.keys()
        values = transaction_obj.__dict__.values()

        keys_str = ", ".join(keys)
        values_str = ""
        for value in values:
            if isinstance(value, str):
                values_str += f"'{value}', "
            else:
                values_str += f"{value}, "

        if values_str.endswith(", "):
            values_str = values_str[:-2]

        insert_query = (
            f"""INSERT INTO {self.table_name} ({keys_str}) VALUES ({values_str})"""
        )

        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            try:
                cursor.execute(insert_query)
                connection.commit()
                logging.info("Record Inserted in %s successfully", self.table_name)
                return "success"
            except sqlite3.IntegrityError as e:
                if "unique" in str(e).lower().strip():
                    return "duplicated"
                else:
                    logging.error("Error: %s", str(e))
                    return "failed"
            except Error as e:
                logging.error("Error: %s", e)
                logging.error("Transaction dict %s", transaction_obj.__dict__)
                return "failed"

    def fetch_all_transactions(self):
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(
                f"""SELECT * FROM {self.table_name} ORDER BY timestamp ASC"""
            )
            rows = cursor.fetchall()
            rows = [dict(row) for row in rows]
        return rows

    def fetch_all_transactions_df(self):
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            df = pd.read_sql_query(
                f"""SELECT * FROM {self.table_name} ORDER BY timestamp ASC""",
                connection,
            )
            # trans_list = df.to_dict('records')
            # return trans_list
        return df

    def filter_transactions(self, filter_dict: dict):
        if not filter_dict:
            return self.fetch_all_transactions()

        select_query = (
            "SELECT * FROM "
            + self.table_name
            + " WHERE "
            + " AND ".join([f"{key} = '{value}'" for key, value in filter_dict.items()])
            + " ORDER BY timestamp ASC"
        )

        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(select_query)
            rows = cursor.fetchall()
            rows = [dict(row) for row in rows]
        return rows

    def filter_transactions_df(self, filter_dict: dict):
        if not filter_dict:
            return self.fetch_all_transactions()

        select_query = (
            "SELECT * FROM "
            + self.table_name
            + " WHERE "
            + " AND ".join([f"{key} = '{value}'" for key, value in filter_dict.items()])
            + " ORDER BY timestamp ASC"
        )

        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            df = pd.read_sql_query(select_query, connection)
        return df

    def fetch_row_count(self):
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(f"""SELECT COUNT(*) FROM {self.table_name}""")
            count = cursor.fetchone()[0]
        return count

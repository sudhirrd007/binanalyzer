import mysql.connector
from mysql.connector import Error
import os

import pymysql


def check_table_exists(connection, table_name):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                AND table_name = %s
            """,
                (table_name,),
            )
            if cursor.fetchone()[0] == 1:
                return True
            else:
                return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    # Connect to MySQL
    connection = pymysql.connect(
        host="mysql",
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        port=int(os.getenv("MYSQL_PORT")),
    )

    table_name = "earn_wallet"

    if check_table_exists(connection, table_name):
        print(f"Table '{table_name}' exists.")
    else:
        print(f"Table '{table_name}' does not exist.")
        # Here you can create the table if it does not exist
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE earn_wallet (
                    coin VARCHAR(255) PRIMARY KEY,
                    total_coins DOUBLE NOT NULL
                )
            """)
            print(f"Table '{table_name}' has been created.")

    connection.close()


if __name__ == "__main__":
    main()

from flask import Flask, request, jsonify, make_response
import logging
import os
import logging
import http.client
import mysql.connector
from mysql.connector import Error

from main.api_routes.binance_transactions_table import binance_transactions_router

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.register_blueprint(binance_transactions_router)

# Define your MySQL database credentials
host = os.getenv("MYSQL_HOST", "localhost")
user = os.getenv("MYSQL_USER", "root")
password = os.getenv("MYSQL_PASSWORD", "123000")
database = os.getenv("MYSQL_DATABASE", "binanalyzer_database")
port = os.getenv("MYSQL_PORT", "3306")


@app.route("/")
def hello_world():
    return "<h1>Hello from, Binanalyzer database index endpoint</h1>"


@app.route("/hello")
def hello():
    return "<h1>Hello from, Binanalyzer database Home Page!</h1>"


@app.route("/test_db_connection", methods=["GET"])
def test_db_connection():
    try:
        # Establish the database connection
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
        )
        if connection.is_connected():
            logging.info("Connected to the MySQL database")
            return make_response(jsonify({"isSuccess": True}, 200))
    except Error as e:
        logging.error("Error: %s", {e})
        return make_response(jsonify({"isSuccess": False, "description": str(e)}, 500))
    finally:
        if "connection" in locals() and connection.is_connected():
            connection.close()
            logging.info("MySQL connection is closed")


def main():
    """Main method to start the app"""
    app.run(debug=True, port=8081)


if (__name__) == "__main__":
    main()

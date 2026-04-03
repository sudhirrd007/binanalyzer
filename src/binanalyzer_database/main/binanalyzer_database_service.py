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


@app.route("/")
def hello_world():
    return "<h1>Hello from, Binanalyzer database index endpoint</h1>"


@app.route("/hello")
def hello():
    return "<h1>Hello from, Binanalyzer database Home Page!</h1>"


def main():
    """Main method to start the app"""
    app.run(debug=True)


if (__name__) == "__main__":
    main()

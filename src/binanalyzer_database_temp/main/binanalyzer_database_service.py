from flask import Flask, request, jsonify
import logging
import os
import logging
import http.client
import mysql.connector
from mysql.connector import Error

from main.api_routes.db_wrapper import db_blueprint as db_router  # Adjust the import path as needed

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Setup debugging session
is_debug_session = os.getenv('DEBUG', 'False')
if is_debug_session == 'True':
    import debugpy
    debugpy.listen(("0.0.0.0", 80))

app.register_blueprint(db_router)

# @app.route('/test_connection', methods=['GET'])
# def test_connection():
#     logging.info(">>>>>>>>>>>>>>>>>>>>>>> Testing connection to backend service")
#     conn = http.client.HTTPConnection("backend", 9090)
#     conn.request("GET", "/hello")
#     response = conn.getresponse()
#     print(response.status, response.reason)
#     data = response.read()
#     print(data)
#     conn.close()
#     return data

def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        logging.info("Connection to MySQL DB successful")
    except Error as e:
        logging.info(f"The error '{e}' occurred")
    return connection

# Define your MySQL database credentials
host_name = "mysql"  # or the IP address of your MySQL server
user_name = "my_user"
user_password = "user-password"
db_name = "my_database"

@app.route('/hello')
def get_hello():
    """""Method to test app running"""
    # Connect to the database
    connection = create_connection(host_name, user_name, user_password, db_name)
    logging.info(">>>>>>>>>>>>>>>>>>>>>>> Testing connection to backend service")
    logging.info(f"Connection: {connection}")
    return "Hello from BinAnalyzer Database Service Temp!"


def main():
    """Main method to start the app"""
    app.run(debug=True)

if(__name__) == "__main__":
    main()

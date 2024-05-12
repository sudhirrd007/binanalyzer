from flask import Flask, request, jsonify
import logging
import os
import logging
import http.client

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


@app.route('/hello')
def get_hello():
    """""Method to test app running"""
    return "Hello from BinAnalyzer Database Service!"


def main():
    """Main method to start the app"""
    app.run(debug=True)

if(__name__) == "__main__":
    main()

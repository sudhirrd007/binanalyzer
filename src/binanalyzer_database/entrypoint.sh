#!/bin/sh

# Run the initialization script
python initialize_db.py

# Start Gunicorn
exec gunicorn main.binanalyzer_database_service:app -c config/gunicorn_config.py

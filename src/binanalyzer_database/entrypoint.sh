#!/bin/sh

echo "Initializing the database..."

# Run the initialization script
python initialize_db.py

echo "Database initialized successfully!"

# Start Gunicorn
exec gunicorn main.binanalyzer_database_service:app -c config/gunicorn_config.py

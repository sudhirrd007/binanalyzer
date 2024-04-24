"""Gunicorn configuration parameters"""
import os

# Define workers depending on the environment
# Debugpy library, used to debug locally in a container, can only handle 1 worker
environment = os.getenv('ENVIRONMENT', 'prod')
NUM_WORKERS = 1 if environment == 'local' else 4
# Allow automatic reloading when debugging locally so changes are automatically picked up
is_reload = environment == 'local'
# Timeout period is unlimited for local
TIMEOUT_EXPIRATION = 0 if environment == 'local' else 600

# Configure the Gunicorn parameters
bind = '0.0.0.0:8080'
workers = NUM_WORKERS
timeout = TIMEOUT_EXPIRATION
reload = is_reload

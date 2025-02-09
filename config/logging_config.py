import os
import sys
import logging
import logging.config

def setup_logging():
    # Define the absolute path to the logs directory
    log_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'logs')

    # Create the logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    # Specify the path to the logging configuration file
    log_config_path = os.path.join(os.path.dirname(__file__), 'logging.conf')

    # Check if the configuration file exists
    if not os.path.isfile(log_config_path):
        raise FileNotFoundError(f"{log_config_path} doesn't exist")

    # Load the logging configuration
    logging.config.fileConfig(log_config_path,
            defaults={'log_dir': log_dir},
            disable_existing_loggers=False
    )

    # Dynamically set the log path
    log_file_path = os.path.join(log_dir, 'app.log')

    # Access the file handler and update its filename dynamically
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.FileHandler):
            handler.baseFilename = log_file_path 
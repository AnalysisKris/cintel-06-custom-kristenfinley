import logging
import os

def setup_logger(script_name, log_level=logging.INFO):
    """Set up a logger with both file and console handlers."""
    
    # Ensure the logs directory exists
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_filename = os.path.join(log_dir, f"{script_name}.log")
    
    # Create a logger
    logger = logging.getLogger(script_name)
    logger.setLevel(log_level)  # Set the log level from the parameter
    
    # Create file and console handlers
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(log_level)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Define a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Return the logger and the log file name
    return logger, log_filename

import os  # For handling file paths and environment operations
import logging  # For logging messages to a file and optionally the console
from pathlib import Path  # For ensuring the existence of directories and paths
import signal  # For handling termination signals gracefully
import sys  # For exiting the program upon encountering errors
from dotenv import load_dotenv  # For loading environment variables from .env files
from pprint import pformat  # For pretty printing complex data structures

# Load environment variables from the .env file located in the src directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

def setup_logging(verbosity: str, log_filename: str) -> None:
    """
    Set up logging for the application, directing output to both a file and optionally the console.

    Args:
        verbosity (str): The logging level; 'debug' enables console output, 'prod' only logs to file.
        log_filename (str): The name of the log file to write to.

    Raises:
        Exception: If any error occurs while setting up the logging.
    """
    try:
        # Get the log directory from the environment variables, default to "logs" if not found
        log_dir = os.getenv("LOG_DIR", "logs")
        # Ensure the log directory exists; create it if necessary
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        # Define the full path to the log file
        log_file = os.path.join(log_dir, log_filename)

        # Set the format for log messages
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        logging.basicConfig(
            filename=log_file,  # Set the log file path
            level=logging.DEBUG if verbosity == "debug" else logging.INFO,  # Set log level based on verbosity
            format=log_format  # Apply the log format
        )

        # If verbosity is set to debug, output logs to the console as well
        if verbosity == "debug":
            console_handler = logging.StreamHandler()  # Create a console handler for output
            console_handler.setFormatter(logging.Formatter(log_format))  # Apply the log format to console output
            logging.getLogger().addHandler(console_handler)  # Add the console handler to the logger

    except Exception as e:
        # Log any error that occurs during logging setup and exit
        logging.error(f"Failed to set up logging: {pformat(e)}")
        sys.exit(1)  # Exit the program with status code 1 if logging setup fails

def signal_handler(sig: int, frame: object) -> None:
    """
    Handle termination signals to shut down the service gracefully.

    Args:
        sig: Signal number.
        frame: Current stack frame (unused).
    """
    logging.info('Shutting down gracefully...')  # Log the shutdown event
    sys.exit(0)  # Exit the program with a status of 0, indicating a successful shutdown

def register_signal_handlers() -> None:
    """
    Register signal handlers for graceful shutdown on termination signals.
    """
    # Register the handler for SIGTERM signals (e.g., system termination)
    signal.signal(signal.SIGTERM, signal_handler)
    # Register the handler for SIGINT signals (e.g., Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)


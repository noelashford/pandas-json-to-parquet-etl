#!/usr/bin/python3

import os  # For handling file paths and environment operations
import logging  # For logging messages to a file and optionally the console
import shutil  # For copying and removing files
from pathlib import Path  # For ensuring the existence of directories and paths
import signal  # For handling termination signals gracefully
import sys  # For exiting the program upon encountering errors
import argparse  # For parsing command-line arguments
from dotenv import load_dotenv  # For loading environment variables from .env files
from pprint import pformat  # For pretty printing complex data structures
from watchdog.observers import Observer  # For monitoring file system events
from watchdog.events import FileSystemEventHandler  # For handling file system events
from common_utils import setup_logging, register_signal_handlers  # Import custom utility functions

# Load environment variables from the .env file located in the src directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Construct the full paths using BASE_DIR environment variable and other paths
base_dir = os.getenv("BASE_DIR", "/root/interviews/cohere")  # Retrieve the base directory
source_folder = os.path.join(base_dir, os.getenv("PARQUET_RAW_DIR", "parquet_raw"))  # Define the source folder path
destination_folder = os.path.join(base_dir, os.getenv("PARQUET_FINAL_DIR", "parquet_final"))  # Define the destination folder path

def debug_print_paths():
    """Print paths and environment variables when in debug mode."""
    print("BASE_DIR:", base_dir)  # Print the base directory
    print("PARQUET_RAW_DIR:", source_folder)  # Print the source folder path
    print("PARQUET_FINAL_DIR:", destination_folder)  # Print the destination folder path
    print("LOG_DIR:", os.path.join(base_dir, os.getenv("LOG_DIR", "logs").lstrip('/')))  # Print the log directory path

class ParquetSyncHandler(FileSystemEventHandler):
    """
    Handles file system events and synchronizes files between the source and destination folders.
    """
    def __init__(self, source_folder: str, destination_folder: str) -> None:
        """
        Initialize the handler with source and destination folders.

        Args:
            source_folder (str): The folder to watch for changes.
            destination_folder (str): The folder to sync changes to.
        """
        self.source_folder = source_folder  # Store the source folder path
        self.destination_folder = destination_folder  # Store the destination folder path

    def on_modified(self, event) -> None:
        """Called when a file or directory is modified in the source folder."""
        logging.debug(f"Modified event detected: {event}")  # Log the modified event
        self.sync_folders()  # Synchronize the source and destination folders

    def on_created(self, event) -> None:
        """Called when a file or directory is created in the source folder."""
        logging.debug(f"Created event detected: {event}")  # Log the created event
        self.sync_folders()  # Synchronize the source and destination folders

    def on_deleted(self, event) -> None:
        """Called when a file or directory is deleted in the source folder."""
        logging.debug(f"Deleted event detected: {event}")  # Log the deleted event
        self.sync_folders()  # Synchronize the source and destination folders

    def sync_folders(self) -> None:
        """
        Synchronize files from the source folder to the destination folder.
        """
        try:
            # Copy new or modified files from the source to the destination
            for filename in os.listdir(self.source_folder):
                src_file = os.path.join(self.source_folder, filename)  # Define the path to the source file
                dest_file = os.path.join(self.destination_folder, filename)  # Define the path to the destination file
                shutil.copy2(src_file, dest_file)  # Copy the file to the destination

            # Remove files from the destination that no longer exist in the source
            for filename in os.listdir(self.destination_folder):
                dest_file = os.path.join(self.destination_folder, filename)  # Define the path to the destination file
                src_file = os.path.join(self.source_folder, filename)  # Define the path to the source file
                if not os.path.exists(src_file):  # Check if the source file no longer exists
                    os.remove(dest_file)  # Remove the file from the destination

            # Log a message indicating successful synchronization
            logging.info(f"Synchronized {self.source_folder} with {self.destination_folder}")

        except FileNotFoundError as e:
            # Log an error if the source or destination folder is not found and exit
            logging.error(f"Error: Source or destination folder not found. Exception: {pformat(e)}")
            sys.exit(1)  # Exit the program with a status code of 1
        except PermissionError as e:
            # Log an error if there is a permission issue during synchronization and exit
            logging.error(f"Error: Permission denied during synchronization. Exception: {pformat(e)}")
            sys.exit(1)  # Exit the program with a status code of 1
        except Exception as e:
            # Log any unexpected error that occurs during synchronization and exit
            logging.error(f"Error: Unexpected error during synchronization. Exception: {pformat(e)}")
            sys.exit(1)  # Exit the program with a status code of 1

if __name__ == "__main__":
    # Set up argument parsing for verbosity level
    parser = argparse.ArgumentParser(description="Parquet Synchronization Service")
    parser.add_argument('--verbosity', choices=['debug', 'prod'], default='prod', help='Set the verbosity level (default: prod)')
    args = parser.parse_args()  # Parse the command-line arguments

    # Set up logging based on the verbosity level
    setup_logging(args.verbosity, "parquet_sync.log")
    # Register signal handlers for graceful shutdown
    register_signal_handlers()

    # Print debug information if verbosity is set to debug
    if args.verbosity == 'debug':
        debug_print_paths()

    # Check if the source folder exists; log an error and exit if not
    if not os.path.exists(source_folder):
        logging.error(f"Error: Source folder '{source_folder}' does not exist.")
        sys.exit(1)  # Exit the program with a status code of 1

    # Check if the destination folder exists; log an error and exit if not
    if not os.path.exists(destination_folder):
        logging.error(f"Error: Destination folder '{destination_folder}' does not exist.")
        sys.exit(1)  # Exit the program with a status code of 1

    # Create an event handler for synchronizing folders
    event_handler = ParquetSyncHandler(source_folder, destination_folder)
    # Create an observer to watch for changes in the source folder
    observer = Observer()
    observer.schedule(event_handler, path=source_folder, recursive=False)
    observer.start()  # Start the observer

    try:
        while True:
            pass  # Keep the script running to monitor file system events
    except KeyboardInterrupt:
        observer.stop()  # Stop the observer if the script is interrupted (e.g., Ctrl+C)
    observer.join()  # Wait for the observer thread to finish


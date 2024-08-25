#!/usr/bin/python3

import os  # For handling file paths and environment operations
import pandas as pd  # For creating DataFrames and saving them as Parquet files
import json  # For loading JSON data from files
import sys  # For exiting the program upon encountering errors
import argparse  # For parsing command-line arguments
import logging  # For logging messages to a file and optionally the console
from pathlib import Path  # For ensuring the output directory exists
from dotenv import load_dotenv  # For loading environment variables from .env files
from pprint import pformat  # For pretty printing complex data structures
from common_utils import setup_logging, register_signal_handlers  # Import custom utility functions

# Load environment variables from the .env file located in the src directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Construct the full paths using BASE_DIR environment variable and other paths
base_dir = os.getenv("BASE_DIR", "/root/interviews/cohere")  # Retrieve the base directory
input_file = os.path.join(base_dir, "json_input", "iris.json")  # Define the input file path
output_folder = os.path.join(base_dir, os.getenv("PARQUET_RAW_DIR", "parquet_raw"))  # Define the output folder path

def debug_print_paths():
    """Print paths and environment variables when in debug mode."""
    print("BASE_DIR:", base_dir)
    print("PARQUET_RAW_DIR:", output_folder)
    print("LOG_DIR:", os.path.join(base_dir, os.getenv("LOG_DIR", "logs")))

def json_to_parquet(input_file: str, output_folder: str) -> None:
    """
    Convert JSON data from an input file to a Parquet file and save it to the specified output folder.

    Args:
        input_file (str): Path to the input JSON file.
        output_folder (str): Directory where the Parquet file should be saved.

    Raises:
        SystemExit: Exits the program if any error occurs during the process.
    """
    # Log the start of the JSON file reading process
    logging.info(f"Attempting to read JSON file from: {input_file}")

    # Ensure the output directory exists; create it if necessary
    try:
        Path(output_folder).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        # Log any error that occurs while creating the output directory and exit
        logging.error(f"Error: Could not create output directory '{output_folder}'. Exception: {pformat(e)}")
        sys.exit(1)

    # Attempt to read the JSON file
    try:
        with open(input_file, 'r') as json_file:
            data = json.load(json_file)  # Load the JSON data from the file
        logging.info(f"Successfully read JSON file: {input_file}")  # Log successful file reading
        logging.debug(f"Contents of the file:\n{pformat(data)}")  # Pretty print the contents of the file
    except FileNotFoundError:
        # Log an error if the input file is not found and exit
        logging.error(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        # Log any error that occurs while decoding JSON data and exit
        logging.error(f"Error: Failed to decode JSON from file '{input_file}'. Exception: {pformat(e)}")
        sys.exit(1)
    except Exception as e:
        # Log any unexpected error that occurs while reading the file and exit
        logging.error(f"Error: Unexpected error reading input file '{input_file}'. Exception: {pformat(e)}")
        sys.exit(1)

    # Attempt to convert the JSON data to a pandas DataFrame
    try:
        df = pd.DataFrame(data)  # Convert JSON data to a pandas DataFrame
    except ValueError as e:
        # Log any error that occurs while converting JSON data to a DataFrame and exit
        logging.error(f"Error: Failed to convert JSON data to DataFrame. Exception: {pformat(e)}")
        sys.exit(1)
    except Exception as e:
        # Log any unexpected error that occurs while converting JSON data to a DataFrame and exit
        logging.error(f"Error: Unexpected error converting JSON data to DataFrame. Exception: {pformat(e)}")
        sys.exit(1)

    # Define the output file path
    output_file = os.path.join(output_folder, 'iris.parquet')

    # Attempt to save the DataFrame as a Parquet file
    try:
        df.to_parquet(output_file, index=False)  # Save the DataFrame as a Parquet file
        logging.info(f"Converted {input_file} to {output_file}")  # Log the successful conversion
    except Exception as e:
        # Log any error that occurs while saving the DataFrame to a Parquet file and exit
        logging.error(f"Error: Failed to write DataFrame to Parquet file '{output_file}'. Exception: {pformat(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Set up argument parsing for verbosity level
    parser = argparse.ArgumentParser(description="Convert JSON to Parquet")
    parser.add_argument('--verbosity', choices=['debug', 'prod'], default='prod', help='Set the verbosity level (default: prod)')
    args = parser.parse_args()  # Parse the command-line arguments

    # Set up logging based on the verbosity level
    setup_logging(args.verbosity, "json_to_parquet.log")

    # Register signal handlers for graceful shutdown
    register_signal_handlers()

    # Print debug information if verbosity is set to debug
    if args.verbosity == 'debug':
        debug_print_paths()

    # Perform the JSON to Parquet conversion
    json_to_parquet(input_file, output_folder)


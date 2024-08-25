#!/bin/bash

# Cleanup script to remove output and log files, but not the virtual environment

# Load the .env file from the src directory
source ./src/.env

# Remove all files in the parquet_raw directory, but not the directory itself
echo "Cleaning up parquet_raw directory..."
rm -f "${PARQUET_RAW_DIR}"/*

# Remove all files in the parquet_final directory, but not the directory itself
echo "Cleaning up parquet_final directory..."
rm -f "${PARQUET_FINAL_DIR}"/*

# Remove all log files in the logs directory, but not the directory itself
echo "Cleaning up log files..."
rm -f "${LOG_DIR}"/*

# Confirmation message
echo "Cleanup completed. All output and log files have been removed."


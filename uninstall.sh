#!/bin/bash

# Uninstallation script for JSON to Parquet Conversion and Parquet Synchronization services

# Load the .env file from the src directory
source ./src/.env

# Function to check if the command succeeded
check_command() {
    if [ $? -ne 0 ]; then
        echo "Error: $1 failed. Continuing with uninstallation..."
    fi
}

echo "Starting uninstallation of services..."

# Execute the cleanup script to remove all output and log files
./cleanup.sh
check_command "Running cleanup script"

# Stop and disable the JSON to Parquet service
sudo systemctl stop json_to_parquet.service
check_command "Stopping json_to_parquet.service"
sudo systemctl disable json_to_parquet.service
check_command "Disabling json_to_parquet.service"

# Stop and disable the Parquet Synchronization service
sudo systemctl stop parquet_sync.service
check_command "Stopping parquet_sync.service"
sudo systemctl disable parquet_sync.service
check_command "Disabling parquet_sync.service"

# Remove the service files
sudo rm -f "${SYSTEMD_DIR}/json_to_parquet.service"
check_command "Removing json_to_parquet.service file"
sudo rm -f "${SYSTEMD_DIR}/parquet_sync.service"
check_command "Removing parquet_sync.service file"

# Reload systemd to apply the changes
sudo systemctl daemon-reload
check_command "Reloading systemd daemon"

# Ensure the BASE_DIR and VENV_DIR are correctly set
BASE_DIR="${BASE_DIR:-/root/interviews/cohere}"
VENV_DIR="${VENV_DIR:-$BASE_DIR/services}"

# Directly check the expansion
echo "Removing virtual environment directory: $VENV_DIR"

# Remove the virtual environment directory
rm -rf "$VENV_DIR"
check_command "Removing virtual environment directory"

# Remove the __pycache__ directories
find "$BASE_DIR/src" -name "__pycache__" -type d -exec rm -rf {} +
check_command "Removing __pycache__ directories"

# Confirmation message
echo "Uninstallation completed successfully."


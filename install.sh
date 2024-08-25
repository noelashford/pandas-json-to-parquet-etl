#!/bin/bash

# Load the .env file from the src directory
source ./src/.env

# Expand the BASE_DIR, SRC_DIR, VENV_DIR, and SYSTEMD_DIR environment variables
BASE_DIR=$(eval echo "$BASE_DIR")
SRC_DIR=$(eval echo "$SRC_DIR")
VENV_DIR=$(eval echo "$VENV_DIR")
SYSTEMD_DIR=$(eval echo "$SYSTEMD_DIR")

# Function to check if a command succeeded
check_command() {
    if [ $? -ne 0 ]; then
        echo "Error: $1 failed. Exiting."
        exit 1
    fi
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 could not be found. Please install Python 3 and try again."
    exit 1
fi

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 could not be found. Please install pip3 and try again."
    exit 1
fi

# Check if venv is installed
if ! python3 -m venv --help &> /dev/null; then
    echo "Error: venv is not installed. Please install venv and try again."
    exit 1
fi

# Create a virtual environment in the services directory
python3 -m venv "$VENV_DIR"
check_command "Creating virtual environment"

# Activate the virtual environment
source "$VENV_DIR/bin/activate"
check_command "Activating virtual environment"

# Install dependencies from requirements.txt
pip3 install -r "$SRC_DIR/requirements.txt"
check_command "Installing Python dependencies"

# Deactivate the virtual environment
deactivate

# Create the Parquet Synchronization service file (continuous)
sudo bash -c "cat > ${SYSTEMD_DIR}/parquet_sync.service <<EOL
[Unit]
Description=Parquet Synchronization Service
After=network.target

[Service]
ExecStart=${VENV_DIR}/bin/python3 ${SRC_DIR}/parquet_sync.py --verbosity prod
WorkingDirectory=${SRC_DIR}
Restart=always
User=$(whoami)
Group=$(whoami)

[Install]
WantedBy=multi-user.target
EOL"
check_command "Creating parquet_sync.service"

# Create the JSON to Parquet service file (one-time)
sudo bash -c "cat > ${SYSTEMD_DIR}/json_to_parquet.service <<EOL
[Unit]
Description=JSON to Parquet Conversion Service
After=network.target

[Service]
ExecStart=${VENV_DIR}/bin/python3 ${SRC_DIR}/json_to_parquet.py --verbosity prod
WorkingDirectory=${SRC_DIR}
Type=oneshot
RemainAfterExit=yes
User=$(whoami)
Group=$(whoami)

[Install]
WantedBy=multi-user.target
EOL"
check_command "Creating json_to_parquet.service"

# Reload systemd to acknowledge the new service files
sudo systemctl daemon-reload
check_command "Reloading systemd daemon"

# Enable and start the Parquet Synchronization service
sudo systemctl enable parquet_sync.service
check_command "Enabling parquet_sync.service"
sudo systemctl start parquet_sync.service
check_command "Starting parquet_sync.service"

# Start the JSON to Parquet service (run once)
sudo systemctl start json_to_parquet.service
check_command "Starting json_to_parquet.service"

# Confirm the status of the services
echo "Checking the status of the services..."
sudo systemctl status parquet_sync.service
sudo systemctl status json_to_parquet.service


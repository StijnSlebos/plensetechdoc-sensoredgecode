#!/bin/bash
# This scripts configures all settings so the Raspberry Pi
# can read out the Plensors

# Function to enable UART and disable Bluetooth
enable_uart_disable_bt() {
  echo "Enabling UART and disabling serial console and Bluetooth..."

  # Disable serial console in /boot/cmdline.txt
  sudo sed -i 's/console=serial0,[0-9]\+ //g' /boot/cmdline.txt

  # Disable serial console and enable serial port in /boot/config.txt
  sudo sed -i 's/^dtoverlay=pi3-miniuart-bt/#dtoverlay=pi3-miniuart-bt/' /boot/firmware/config.txt
  sudo bash -c "echo 'enable_uart=1' >> /boot/firmware/config.txt"
  sudo bash -c "echo 'dtoverlay=disable-bt' >> /boot/firmware/config.txt"
}

# Function to enable Serial Port
configure_serial() {
  echo "Enabling Serial Port..."
  sudo raspi-config nonint do_serial 2
}

# Function to install the required system packages
install_system_packages() {
    echo "Installing system package libsndfile1..."
    sudo apt-get install -y \
    libsndfile1
    sudo rm -rf /var/lib/apt/lists/*
}

# Function to configure the folders for the MeasurePlensor, InternalTemp and ProcessData
# scripts or Greengrass components
configure_folders() {
  echo "Configuring folders..."

  # Define the base directory and folder paths
  BASE_DIR="/home/plense/plensor_data"
  FOLDERS=(
      "$BASE_DIR/audio_data/time_domain_not_processed"
      "$BASE_DIR/audio_data/time_domain_processed"
      "$BASE_DIR/audio_data/frequency_domain/magnitude_spectrum"
      "$BASE_DIR/audio_data/frequency_domain/phase_spectrum"
      "$BASE_DIR/environment_data"
      "$BASE_DIR/audio_data/tof"
  )

  # Log file
  LOG_FILE="/var/log/create_folders.log"

  # Create log file if it doesn't exist
  if [ ! -f "$LOG_FILE" ]; then
      sudo touch "$LOG_FILE"
  fi

  # Function to create a folder
  create_folder() {
      local FOLDER=$1
      if [ ! -d "$FOLDER" ]; then
          sudo mkdir -p "$FOLDER"
          if [ $? -eq 0 ]; then
              echo "Successfully created folder: $FOLDER"
          else
              echo "Error creating folder: $FOLDER"
          fi
      else
          echo "Folder already exists: $FOLDER"
      fi
  }

  # Create each folder
  for FOLDER in "${FOLDERS[@]}"; do
      create_folder "$FOLDER"
  done

  echo "Folder creation script completed."
}

# Function to create a .venv in the correct folder and install the dependencies
# of the measure-plensor and the process-data folders
install_dependencies() {
    echo "Creating virtual environment..."
    cd /home/plense/edge-code
    python -m venv .venv
    source .venv/bin/activate
    pip install -r /home/plense/edge-code/measure-plensor/artifact/requirements.txt
    pip install -r /home/plense/edge-code/process-data/artifact/requirements.txt
}

# Function to ensure permissions for the log folder are set PERMANENTLY
set_permissions_log_folder() {
    echo "Setting permissions for the logs folder..."
    sudo chmod -R 777 /greengrass/v2/logs
}

# Function to create an example metadata file
# needed for the edge-code/measure-plensor/artifact/app.py to
# measure a Plensor
setup_metadata_file() {
    echo "Setting up metadata file to be able to measure a Plensor..."

    # Define the file path
    METADATA_FILE="/home/plense/metadata/Plensor#99999_metadata.json"

    # Create the JSON content
    cat <<EOF | sudo tee "$METADATA_FILE" > /dev/null
{
    "sensor_id": "#99999",
    "pi_id": "plensepi00018",
    "customer_id": "#EXAMPLE_CUSTOMER_ID",
    "pilot_id": "#EXAMPLE_PILOT_ID",
    "test_id": "#BELLPEPPER",
    "sensor_type": "PLENSOR",
    "sensor_version": "V9.9",
    "amp_factor": "EXAMPLE_AMP_FACTOR"
}
EOF

    # Set permissions to make the file writable by the user
    sudo chmod 666 "$METADATA_FILE"

    # Confirm creation
    if [ -f "$METADATA_FILE" ]; then
        echo "Metadata file created successfully: $METADATA_FILE"
    else
        echo "Failed to create metadata file."
    fi
}

# Function to create an example message.json file needed
# for the edge computer to measure a Plensor
setup_message_file() {
    echo "Setting up message.json to be able to measure a Plensor..."

    # Define the file path
    MESSAGE_FILE="/home/plense/metadata/message.json"

    # Create the JSON content
    cat <<EOF | sudo tee "$MESSAGE_FILE" > /dev/null
{
	"measurement_interval": 60,
	"damping": 0,
	"log_level": "INFO",
	"commands": ["SINE", "BLOCK", "TEMP", "TOF_BLOCK"],
	"duration": 50000,
	"start_frequency": 20000,
	"stop_frequency": 100000,
	"repetitions": 10,
	"tof_timeout": 450,
	"tof_half_periods": 20
}
EOF

    # Set permissions to make the file writable by the user
    sudo chmod 666 "$MESSAGE_FILE"

    # Confirm creation
    if [ -f "$MESSAGE_FILE" ]; then
        echo "message.json file created successfully: $MESSAGE_FILE"
    else
        echo "Failed to create message.json"
    fi
}

# Function to ensure permissions for the plensor_data folder
# are set PERMANENTLY
set_permissions_plensor_data_folder() {
    echo "Setting permissions for the plensor_data folder..."
    sudo chmod -R 777 /home/plense/plensor_data
}

# Reboot if user prompt is yes
reboot_now() {
    echo "Rebooting now for changes to take effect..."
    sudo reboot
}

##########################################################################

# Main script
echo "Welcome to the Raspberry Pi setup script to read out the Plensors."
echo "Please enter 'y' or 'no' to each of the following steps."

read -p "Enable Serial Port? " do_configure_serial
read -p "Enable UART and disable Bluetooth? " do_enable_uart_disable_bt
read -p "Install Linux system package needed for Plensor communication? " do_install_system_packages
read -p "Configure the folders to save Plensor data and internal temperature to?" do_configure_folders
read -p "Install dependencies measure-plensor and process-data? " do_install_dependencies
read -p "Set permissions for the logs folder? " do_set_log_folder_permissions
read -p "Create example metadata file? " do_setup_metadata_file
read -p "Create example message.json? " do_setup_message_file
read -p "Set permissions plensor_data folder? " do_set_permissions_plensor_data_folder
read -p "Rebooting after this installer script? " do_reboot

# And execute the functions chosen by the user
if [ "$do_enable_uart_disable_bt" = "y" ]; then enable_uart_disable_bt; fi
if [ "$do_configure_serial" = "y" ]; then configure_serial; fi
if [ "$do_install_system_pack
ages" = "y" ]; then install_system_packages; fi
if [ "$do_configure_folders" = "y" ]; then configure_folders; fi
if [ "$do_install_dependencies" = "y" ]; then install_dependencies; fi
if [ "$do_set_log_folder_permissions" = "y" ]; then set_permissions_log_folder; fi
if [ "$do_setup_metadata_file" = "y" ]; then setup_metadata_file; fi
if [ "$do_setup_message_file" = "y" ]; then setup_message_file; fi
if [ "$do_set_permissions_plensor_data_folder" = "y" ]; then set_permissions_plensor_data_folder; fi
if [ "$do_reboot" = "y" ]; then reboot_now; fi

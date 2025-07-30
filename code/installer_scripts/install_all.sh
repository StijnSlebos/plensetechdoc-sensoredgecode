#!/bin/bash

# Function to prompt and execute an installer script
run_script() {
  local script_name=$1
  local description=$2
  local prompt="Would you like to run the ${description}? (y/n): "
  read -p "$prompt" response
  if [ "$response" = "y" ]; then
    if [ -f "$script_name" ]; then
      echo "Running ${description}..."
      bash "$script_name"
    else
      echo "Error: ${description} not found at $script_name."
    fi
  else
    echo "Skipping ${description}."
  fi
}

# Main script
echo "Welcome to the combined installer script."
echo "This script allows you to run individual installer scripts based on your preference."

# Define paths and descriptions of the installer scripts
SCRIPT1="/home/plense/edge-code/installer_scripts/install_basic.sh"
SCRIPT2="/home/plense/edge-code/installer_scripts/install_gg.sh"
SCRIPT3="/home/plense/edge-code/installer_scripts/install_plensor.sh"

# Prompt the user for each installer script
run_script "$SCRIPT1" "Install basic script"
run_script "$SCRIPT2" "Install Greengrass script"
run_script "$SCRIPT3" "Install Plensor script"

echo "All selected scripts have been executed."


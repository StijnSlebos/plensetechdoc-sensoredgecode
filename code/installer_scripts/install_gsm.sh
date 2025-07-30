#!/bin/bash

# Function to install ModemManager Linux system service
install_mmcli() {
  sudo apt update
  sudo apt install modemmanager
}

# Function to setup GSM connection
setup_gsm() {
  echo "Setting up GSM connection..."
  APN=$1
  USERNAME=$2
  PASSWORD=$3
  sudo systemctl status NetworkManager
  sudo nmcli con add type gsm ifname 'cdc-wdm0' con-name 'gsm-connection' apn "$APN"
  sudo nmcli con modify 'gsm-connection' gsm.username "$USERNAME" gsm.password "$PASSWORD"
  sudo nmcli con modify 'gsm-connection' connection.autoconnect yes
  sudo nmcli con up 'gsm-connection'
}

##########################################################################

# Main script
echo "Welcome to the Raspberry Pi setup script."
echo "Please enter 'y' or 'no' to each of the following steps."

read -p "Setup GSM connection (you will be prompted for APN, username, and password)? " do_setup_gsm

# Odido settings:
# APN: smartsites.t-mobile
# gsm.username: 
# gsm.password:

if [ "$do_setup_gsm" = "y" ]; then
  read -p "Enter GSM APN: " gsm_apn
  read -p "Enter GSM username: " gsm_username
  read -p "Enter GSM password: " gsm_password
  install_mmcli
  setup_gsm $gsm_apn $gsm_username $gsm_password
fi

echo "Rebooting now to let the changes take effect..."

reboot
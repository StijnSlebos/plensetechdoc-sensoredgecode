#!/bin/bash

# Function to enable I2C and configure static IP
enable_i2c() {
  echo "Enabling I2C and configuring static IP..."
  sudo raspi-config nonint do_i2c 0
  sudo ip addr add 169.254.182.240/16 dev eth0
  echo "Please ping the connected camera to ensure packets are returned."
  sudo bash -c "echo 'interface eth0' >> /etc/dhcpcd.conf"
  sudo bash -c "echo 'static ip_address=169.254.182.240/16' >> /etc/dhcpcd.conf"
  sudo systemctl restart dhcpcd
  sudo reboot
}

# Function to configure static ethernet port using NetworkManager
configure_networkmanager() {
  echo "Configuring static ethernet port using NetworkManager..."
  sudo nmcli con add type ethernet con-name flir-static
  sudo nmcli con modify flir-static ipv4.addresses 169.254.182.242/16
  sudo nmcli con modify flir-static ipv4.method manual
  sudo nmcli con up flir-static
  sudo nmcli con modify flir-static connection.autoconnect yes
}

##########################################################################

# Main script
echo "Welcome to the setup script to configure the Raspberry Pi for the FLIR."
echo "Please enter 'yes' or 'no' to each of the following steps."

read -p "Enable I2C and configure static IP? " do_enable_i2c
read -p "Configure static ethernet port using NetworkManager? " do_configure_networkmanager

if [ "$do_enable_i2c" = "yes" ]; then enable_i2c; fi
if [ "$do_configure_networkmanager" = "yes" ]; then configure_networkmanager; fi

echo "Setup script for the FLIR completed."
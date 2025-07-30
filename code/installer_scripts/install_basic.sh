#!/bin/bash

# Function to update and upgrade the OS
update_os() {
  echo "Updating and upgrading the OS..."
  sudo apt-get update
  sudo apt-get upgrade -y
}

# Function to enable auto login for user 'plense'
enable_auto_login() {
  echo "Enabling auto login..."
  sudo raspi-config nonint do_boot_behaviour B4
}

# Function to set keyboard layout to US
set_keyboard_us() {
  echo "Setting keyboard layout to US..."
  sudo raspi-config nonint do_configure_keyboard us
}

# Function to set local timezone to Amsterdam
set_timezone_ams() {
  echo "Setting timezone to Amsterdam..."
  sudo timedatectl set-timezone Europe/Amsterdam
}

# Function to grant the plense user administrator permissions
ensure_plense_admin() {
  echo "Ensuring the 'plense' user has administrator permissions..."
  sudo bash -c "echo 'plense ALL=(ALL:ALL) ALL' >> /etc/sudoers"
}

# Function to disable password prompt for plense user, to let the other
# installer scripts run in one go without intermediate prompt
# which is annoying
disable_plense_password() {
  echo "Disabling the password prompt for Plense..."

  # Add the disable password line in the sudoers file
  sudo bash -c "echo 'plense ALL=(ALL) NOPASSWD: /usr/bin/apt-get, /usr/bin/unzip, /usr/bin/curl, /usr/bin/java, /usr/sbin/usermod, /bin/chmod, /bin/chgrp, /usr/bin/docker' >> /etc/sudoers"

  echo "Password prompt for plense user disabled."
}

# Function to grant read, write and execute permissions for all users
# for the home folder
grant_permissions_home() {
  echo "Granting permissions for the home folder..."

  sudo chmod -R 777 /home/plense
}

# Function to install VSCode
install_vscode() {
  echo "Installing VSCode..."
  sudo apt install -y code
}

# Function to configure Git
configure_git() {
  echo "Configuring Git..."
  if [ "$#" -ne 2 ]; then
    echo "Usage: configure_git user_email user_name"
    exit 1
  fi
  USER_EMAIL=$1
  USER_NAME=$2
  git config --global user.email "$USER_EMAIL"
  git config --global user.name "$USER_NAME"
  git config --global pull.rebase false
  code --install-extension ms-python.python
}

# Function to setup pi_id
setup_pi_id() {
  echo "Setting up pi_id..."
  PI_ID=$(hostname)
  sudo bash -c "echo '$PI_ID' > /etc/hostname"
  sudo mkdir -p /home/plense/metadata
  sudo bash -c "echo '$PI_ID' > /home/plense/metadata/container_hostname"
}

# Function to change permissions metadata folder
set_permissions_metadata_folder() {
    echo "Setting permissions for the logs folder..."
    sudo chmod -R 777 /home/plense/metadata
}

# Function to create error logs folder
create_error_logs_folder() {
    echo "Setting permissions for the logs folder..."
    sudo mkdir /home/plense/error_logs
    sudo chmod -R 777 /home/plense/error_logs
}

# Reboot if user prompt is yes
reboot_now() {
    echo "Rebooting now for changes to take effect..."
    sudo reboot
}

##########################################################################

# Main script
echo "Welcome to the Raspberry Pi setup script to install all basic tools."
echo "Please enter 'y' or 'no' to each of the following steps."

read -p "Update and upgrade the OS? " do_update_os
read -p "Enable auto login? " do_enable_auto_login
read -p "Set keyboard layout to US? " do_set_keyboard_us
read -p "Set timezone to Amsterdam? " do_set_timezone_ams
read -p "Ensure plense admin? " do_ensure_plense_admin
read -p "Grant permissions for home folder? " do_grant_permissions_home
read -p "Disable password prompt for plense user? " do_disable_plense_password
read -p "Install VSCode? " do_install_vscode
read -p "Setup pi_id (pi_id is hostname)? " do_setup_pi_id
read -p "Change permissions metadata folder? " do_set_permissions_metadata_folder
read -p "Create error_logs folder? " do_create_error_logs_folder

# Prompt the user for the Git installation and configuration
read -p "Configure Git (you will be prompted for user email and user name)? " do_configure_git
if [ "$do_configure_git" = "y" ]; then
  read -p "Enter Git user email: " git_user_email
  read -p "Enter Git user name: " git_user_name
fi

# Prompt the user for a reboot
read -p "Rebooting after this installer script? " do_reboot

# And execute the functions chosen by the user
if [ "$do_update_os" = "y" ]; then update_os; fi
if [ "$do_enable_auto_login" = "y" ]; then enable_auto_login; fi
if [ "$do_ensure_plense_admin" = "y" ]; then ensure_plense_admin; fi
if [ "$do_disable_plense_password" = "y" ]; then disable_plense_password; fi
if [ "$do_grant_permissions_home" = "y" ]; then grant_permissions_home; fi
if [ "$do_set_keyboard_us" = "y" ]; then set_keyboard_us; fi
if [ "$do_set_timezone_ams" = "y" ]; then set_timezone_ams; fi
if [ "$do_install_vscode" = "y" ]; then install_vscode; fi
if [ "$do_setup_pi_id" = "y" ]; then setup_pi_id; fi
if [ "$do_set_permissions_metadata_folder" = "y" ]; then set_permissions_metadata_folder; fi
if [ "$do_create_error_logs_folder" = "y" ]; then create_error_logs_folder; fi
if [ "$do_configure_git" = "y" ]; then configure_git $git_user_email $git_user_name; fi
if [ "$do_reboot" = "y" ]; then reboot_now; fi

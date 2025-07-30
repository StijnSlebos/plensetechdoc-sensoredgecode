#!/bin/bash

# Function to install AWS CLI
install_aws_cli() {
  echo "Downloading and installing AWS CLI..."

  # Download the AWS CLI for Linux ARM
  curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip"

  # Unzip the downloaded file
  unzip awscliv2.zip

  # Navigate to the AWS CLI installer directory
  cd aws

  # Install the AWS CLI
  sudo ./install

  # Verify the installation
  AWS_CLI_VERSION=$(aws --version 2>&1)
  if [[ $AWS_CLI_VERSION == aws-cli* ]]; then
    echo "AWS CLI installed successfully: $AWS_CLI_VERSION"
  else
    echo "AWS CLI installation failed."
  fi

  # Cleanup
  cd ..
  rm -rf awscliv2.zip aws
}

# Function to configure AWS CLI
configure_aws_cli() {
  echo "Configuring AWS CLI..."
  if [ "$#" -ne 3 ]; then
    echo "Usage: configure_aws_cli aws_access_key_id aws_secret_access_key aws_region"
    exit 1
  fi

  AWS_ACCESS_KEY_ID=$1
  AWS_SECRET_ACCESS_KEY=$2
  AWS_REGION=$3

  # Configure AWS CLI
  aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
  aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
  aws configure set region $AWS_REGION
  aws configure set output ""

  # Verify the configuration
  echo "AWS CLI configuration:"
  aws configure list
}

# Function to install Docker
install_docker() {
  echo "Installing Docker..."
  sudo apt-get update
  sudo apt-get upgrade -y
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  sudo usermod -aG docker plense
}

# Function to install AWS IoT Greengrass
install_greengrass() {
  cd ~
  echo "Installing JDK, needed for AWS IoT Greengrass..."
  sudo apt install -y default-jdk
  echo "Installing AWS IoT Greengrass..."
  curl -s https://d2s8p88vqu9w66.cloudfront.net/releases/greengrass-nucleus-latest.zip -o greengrass-nucleus-latest.zip
  unzip greengrass-nucleus-latest.zip -d GreengrassInstaller && rm greengrass-nucleus-latest.zip
  PI_HOSTNAME=$(hostname)
  sudo -E java -Droot="/greengrass/v2" -Dlog.store=FILE \
    -jar ./GreengrassInstaller/lib/Greengrass.jar \
    --aws-region eu-central-1 \
    --thing-name $PI_HOSTNAME \
    --thing-group-name MyGreengrassCoreGroup \
    --thing-policy-name GreengrassV2IoTThingPolicy \
    --tes-role-name GreengrassV2TokenExchangeRole \
    --tes-role-alias-name GreengrassCoreTokenExchangeRoleAlias \
    --component-default-user ggc_user:ggc_group \
    --provision true \
    --setup-system-service true \
    --deploy-dev-tools true
  sudo usermod -aG docker ggc_user
  sudo usermod -aG dialout ggc_user
  sudo chmod 666 /var/run/docker.sock
  sudo chgrp $USER /lib/systemd/system/docker.socket
  sudo chmod g+w /lib/systemd/system/docker.socket
  sudo /greengrass/v2/alts/current/distro/bin/loader
}

# Reboot if user prompt is yes
reboot_now() {
    echo "Rebooting now for changes to take effect..."
    sudo reboot
}

##########################################################################

# Main script
echo "Welcome to the Raspberry Pi setup script to install Greengrass."
echo "Please enter 'y' or 'no' to each of the following steps."

# Prompt the user for the AWS installation and configuration
read -p "Install AWS CLI? " do_install_aws_cli
read -p "Configure AWS CLI? " do_configure_aws_cli
if [ "$do_configure_aws_cli" = "y" ]; then
  read -p "Enter AWS Access Key ID: " AWS_ACCESS_KEY_ID
  read -p "Enter AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
  read -p "Enter AWS Region: " AWS_REGION
fi
read -p "Install Docker? " do_install_docker
read -p "Install AWS IoT Greengrass? " do_install_greengrass
read -p "Rebooting after this installer script? " do_reboot

# And execute the functions chosen by the user
if [ "$do_setup_pi_id" = "y" ]; then setup_pi_id $pi_id; fi
if [ "$do_install_aws_cli" = "y" ]; then install_aws_cli; fi
if [ "$do_configure_aws_cli" = "y" ]; then
  configure_aws_cli $AWS_ACCESS_KEY_ID $AWS_SECRET_ACCESS_KEY $AWS_REGION
fi
if [ "$do_install_docker" = "y" ]; then install_docker; fi
if [ "$do_install_greengrass" = "y" ]; then install_greengrass; fi
if [ "$do_reboot" = "y" ]; then reboot_now; fi
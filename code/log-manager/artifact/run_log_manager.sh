#!/bin/bash

# Set environment variables
export BUCKET_NAME='prd-signal-bucket'
export AWS_REGION='eu-central-1'

cd /home/plense/edge-code/log-manager/artifact
source /home/plense/edge-code/.venv/bin/activate
python app.py

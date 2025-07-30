#!/bin/bash

# Set environment variables for local operation
export AS_LOCAL='true'

cd /home/plense/edge-code/log-manager/artifact
source /home/plense/edge-code/.venv/bin/activate
python app.py

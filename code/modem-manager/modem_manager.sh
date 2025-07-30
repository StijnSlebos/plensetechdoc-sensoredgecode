#!/bin/bash

LOG_FILE="/home/plense/error_logs/ModemManagerPlense.log"
MODEM_STATUS=$(/usr/bin/mmcli -m 0)
MODEM_STATE=$(echo "$MODEM_STATUS" | awk -F "state: " '/state:/ {print $2}' | awk '{print $1}')

# Check if the modem state is connected -> this is the state in which
# it has a successful connection to a network (as you would expect)
if echo "$MODEM_STATE" | grep "connected"; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Modem is connected." >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Modem not connected. Attempting to restart ModemManager..." >> "$LOG_FILE"
    # sudo systemctl restart ModemManager
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ModemManager service restarted." >> "$LOG_FILE"
fi

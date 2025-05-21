#!/bin/bash

cd /home/superuser/mesh
TODAY=$(date +%F)  # format: YYYY-MM-DD
TARGET="meshtastic_paxcounter_log_${TODAY}.csv"
LINK="meshtastic_paxcounter_log_latest.csv"

if [ -f "$TARGET" ]; then
    ln -sf "$TARGET" "$LINK"
fi

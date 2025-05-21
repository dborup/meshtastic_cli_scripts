import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from datetime import datetime
import logging
import csv
import os

# 🔇 Suppress Meshtastic protobuf decode errors
logging.getLogger("meshtastic.mesh_interface").setLevel(logging.CRITICAL)
logging.getLogger("meshtastic.stream_interface").setLevel(logging.CRITICAL)

# Friendly names for nodes
NODE_NAMES = {
    '!b03da': 'node1',
    '!a0cc18': 'Node2',
    # Add more mappings here
}

# Logging options
LOG_TO_FILE = True

def get_log_file():
    return f"meshtastic_paxcounter_log_{datetime.now().strftime('%Y-%m-%d')}.csv"

def ensure_log_file_has_header():
    log_file = get_log_file()
    if not os.path.exists(log_file):
        with open(log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Time', 'NodeID', 'Name',
                'WiFi Count', 'BLE Count', 'Total Count',
                'Uptime (s)', 'Uptime (formatted)'
            ])

def format_uptime(seconds):
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    return f"{days}d {hours}h {minutes}m"

def on_receive(packet, interface):
    try:
        decoded = packet.get('decoded', {})
        if decoded.get('portnum') != 'PAXCOUNTER_APP':
            return

        data = decoded.get('paxcounter', {})
        from_id = packet.get('fromId', 'unknown')
        name = NODE_NAMES.get(from_id, from_id)

        wifi = data.get('wifi', 0)
        ble = data.get('ble', 0)
        total_count = wifi + ble
        uptime = data.get('uptime', 0)
        uptime_fmt = format_uptime(uptime)
        now = datetime.now().isoformat(timespec='seconds')

        print(f"📦 {name} | WiFi: {wifi} | BLE: {ble} | Total: {total_count} | Uptime: {uptime_fmt}")

        if LOG_TO_FILE:
            log_file = get_log_file()
            ensure_log_file_has_header()
            with open(log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    now, from_id, name,
                    wifi, ble, total_count,
                    uptime, uptime_fmt
                ])

    except Exception as e:
        print(f"⚠️ Error: {e}")

# Start listening
interface = meshtastic.serial_interface.SerialInterface()
pub.subscribe(on_receive, "meshtastic.receive")

print("🔍 Listening for PAXCOUNTER packets... Ctrl+C to stop.")
if LOG_TO_FILE:
    ensure_log_file_has_header()

try:
    while True:
        pass
except KeyboardInterrupt:
    print("\n🛑 Stopped.")

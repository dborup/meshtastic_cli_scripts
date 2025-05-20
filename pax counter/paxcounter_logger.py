import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from datetime import datetime
import logging
import csv

# 🔇 Suppress Meshtastic internal error spam
logging.getLogger("meshtastic.mesh_interface").setLevel(logging.CRITICAL)
logging.getLogger("meshtastic.stream_interface").setLevel(logging.CRITICAL)

# Optional CSV log file
LOG_TO_FILE = True
LOG_FILE = "meshtastic_paxcounter_log.csv"

if LOG_TO_FILE:
    try:
        with open(LOG_FILE, 'x', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time', 'NodeID', 'WiFi Count', 'BLE Count', 'Uptime (s)'])
    except FileExistsError:
        pass

def on_receive(packet, interface):
    try:
        decoded = packet.get('decoded', {})
        if decoded.get('portnum') != 'PAXCOUNTER_APP':
            return

        data = decoded.get('paxcounter', {})
        from_id = packet.get('fromId', 'unknown')
        wifi = data.get('wifi', 0)
        ble = data.get('ble', 0)
        uptime = data.get('uptime', 0)
        now = datetime.now().isoformat(timespec='seconds')

        print(f"📦 {from_id} | WiFi: {wifi} | BLE: {ble} | Uptime: {uptime}s")

        if LOG_TO_FILE:
            with open(LOG_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([now, from_id, wifi, ble, uptime])

    except Exception as e:
        print(f"⚠️ Error: {e}")

# Connect and subscribe
interface = meshtastic.serial_interface.SerialInterface()
pub.subscribe(on_receive, "meshtastic.receive")

print("🔍 Listening for PAXCOUNTER packets... Ctrl+C to stop.")
try:
    while True:
        pass
except KeyboardInterrupt:
    print("\n🛑 Stopped.")

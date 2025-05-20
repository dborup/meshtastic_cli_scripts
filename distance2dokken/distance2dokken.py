import math
import csv
import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from datetime import datetime

# Fixed Dokk1 coordinates
DOKK1_LAT = 56.1629
DOKK1_LON = 10.2039

LOG_FILE = "meshtastic_dokk1_log.csv"

# Memory of last positions
last_positions = {}

# Write CSV header if file doesn't exist
try:
    with open(LOG_FILE, 'x', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Time', 'NodeID', 'Latitude', 'Longitude', 'Altitude (m)', 'Distance (km)', 'HopCount', 'RSSI (dBm)', 'SNR (dB)'])
except FileExistsError:
    pass  # Already exists

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def on_receive(packet, interface):
    try:
        decoded = packet.get('decoded', {})
        if decoded.get('portnum') != 'POSITION_APP':
            return

        pos = decoded.get('position', {})
        from_id = packet.get('fromId', 'unknown')
        lat = pos.get('latitude')
        lon = pos.get('longitude')
        alt = pos.get('altitude', 0)

        if lat is None or lon is None:
            return

        # Round to 5 decimals to avoid micro changes
        lat_r = round(lat, 5)
        lon_r = round(lon, 5)

        # Check for duplicates
        last = last_positions.get(from_id)
        if last == (lat_r, lon_r):
            return  # No position change, skip logging

        # Update stored position
        last_positions[from_id] = (lat_r, lon_r)

        distance = haversine(DOKK1_LAT, DOKK1_LON, lat, lon)

        hop = packet.get('hopLimit', '?')
        rssi = packet.get('rxRssi', '?')
        snr = packet.get('rxSnr', '?')
        now = datetime.now().isoformat(timespec='seconds')

        print(f"📡 {from_id} → {distance:.2f} km from Dokk1 | Hop: {hop} | RSSI: {rssi} dBm | SNR: {snr} dB")

        with open(LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([now, from_id, lat, lon, alt, round(distance, 2), hop, rssi, snr])

    except Exception as e:
        print(f"⚠️ Error: {e}")

# Start Meshtastic serial interface
interface = meshtastic.serial_interface.SerialInterface()
pub.subscribe(on_receive, "meshtastic.receive")

print(f"📋 Logging to {LOG_FILE} — Ctrl+C to stop.")
try:
    while True:
        pass
except KeyboardInterrupt:
    print("\n🛑 Logging stopped.")

import meshtastic.serial_interface
from pubsub import pub
import time
import os
import json

# Configuration
reply_message = "pong"
trigger_keyword = "ping"
target_channel = 0
cooldown_seconds = 10
log_file = "pingpong_log.txt"
known_nodes_file = "known_nodes.txt"
stats_file = "ping_stats.json"

last_response_time = 0
known_nodes = {}
ping_stats = {}

# Load known nodes from file
if os.path.exists(known_nodes_file):
    with open(known_nodes_file, "r") as f:
        for line in f:
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                known_nodes[parts[0]] = parts[1]
            else:
                known_nodes[parts[0]] = parts[0]

# Load ping statistics from file
if os.path.exists(stats_file):
    with open(stats_file, "r") as f:
        ping_stats = json.load(f)

# Connect to Meshtastic device and get our own node ID
interface = meshtastic.serial_interface.SerialInterface()
my_node_id = interface.myInfo.my_node_num
print(f"✅ My node ID: {my_node_id}")

def send_message(message, channel=target_channel, hop_limit=1):
    interface.sendData(
        message.encode("utf-8"),
        destinationId=None,
        portNum="TEXT_MESSAGE_APP",
        wantAck=True,
        channelIndex=channel,
        hopLimit=hop_limit
    )
    print(f"📤 Sent on channel {channel} with hop limit {hop_limit}: {message}")

def greet_new_node(node_id, display_name):
    welcome = f"👋 Welcome to Aarhus mesh, {display_name}!"
    send_message(welcome, hop_limit=1)
    print(f"🎉 Welcomed new node: {node_id} ({display_name})")
    known_nodes[node_id] = display_name
    with open(known_nodes_file, "a") as f:
        f.write(f"{node_id} {display_name}\n")

def update_ping_stats(node_id, name, hop_limit):
    if node_id not in ping_stats:
        ping_stats[node_id] = {
            "name": name,
            "ping_count": 0,
            "hops": []
        }
    ping_stats[node_id]["ping_count"] += 1
    if hop_limit is not None:
        ping_stats[node_id]["hops"].append(hop_limit)

    with open(stats_file, "w") as f:
        json.dump(ping_stats, f, indent=2)

def onReceive(packet, interface):
    global last_response_time
    try:
        decoded = packet.get("decoded", {})
        portnum = decoded.get("portnum")
        channel_index = decoded.get("channelIndex", 0)
        payload = decoded.get("payload")
        sender = packet.get("fromId")

        if not sender or sender == my_node_id:
            return

        user_info = decoded.get("user", {})
        long_name = user_info.get("longName") or sender

        rssi = packet.get("rxRssi")
        snr = packet.get("rxSnr")
        hop_limit = packet.get("hopLimit")

        if portnum == 'TEXT_MESSAGE_APP' and payload:
            try:
                message = payload.decode('utf-8')
            except UnicodeDecodeError:
                print(f"⚠️ Ignored non-UTF8 payload from {sender}")
                return

            print(f"📩 Message from {long_name} ({sender}) on channel {channel_index}: {message}")
            if rssi is not None or snr is not None or hop_limit is not None:
                print(f"📶 Signal: RSSI={rssi} dBm, SNR={snr} dB, HopLimit={hop_limit}")

            with open(log_file, "a") as log:
                log.write(f"{time.ctime()}: from {long_name} ({sender}) (ch {channel_index}) - RSSI={rssi} SNR={snr} HopLimit={hop_limit} - {message}\n")

            if trigger_keyword.lower() in message.lower():
                update_ping_stats(sender, long_name, hop_limit)
                now = time.time()
                if now - last_response_time > cooldown_seconds:
                    send_message(reply_message, hop_limit=5)
                    last_response_time = now
                else:
                    print("⏱ Cooldown active. No reply.")

        # Welcome new node if it's not already known and not ourself
        if sender not in known_nodes and sender != my_node_id:
            if long_name != sender:
                greet_new_node(sender, long_name)
            else:
                print(f"⏳ Waiting to welcome {sender} – name not yet received.")

    except Exception as e:
        print(f"❌ Error: {e}")

pub.subscribe(onReceive, 'meshtastic.receive')

print("🔍 PingPong + Welcome + Stats service active.")
while True:
    time.sleep(1)

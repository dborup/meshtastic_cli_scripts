# Meshtastic PingPong + Welcome + Stats Bot

This Python script connects to a Meshtastic device via serial interface and runs a smart bot that:

- Replies with `"pong"` to any `"ping"` message  
- Welcomes new nodes by name (only once)  
- Logs all incoming messages with RSSI, SNR, and hop distance  
- Tracks per-node ping counts and hop stats  
- Prevents reply spam with a cooldown system  
- Ignores its own messages to avoid loops

---

## 🚀 Features

| Feature          | Description                                                 |
|------------------|-------------------------------------------------------------|
| `ping` listener  | Replies `"pong"` with `hopLimit=5`                          |
| Node welcome     | Sends greeting when a node appears for the first time       |
| Stats tracking   | Logs ping count + hop history per node to `ping_stats.json` |
| Signal logging   | Records RSSI and SNR with each message                      |
| Cooldown         | Prevents repeated replies too quickly (default: 10s)        |
| Self-ignore      | Automatically ignores messages from its own node            |

---

## 📁 Files Used / Created

| File               | Purpose                                                 |
|--------------------|---------------------------------------------------------|
| `pingpong_log.txt` | Log of all messages with timestamp and signal data      |
| `known_nodes.txt`  | Records which nodes have already received a welcome     |
| `ping_stats.json`  | Stores ping count and hop distances per node            |

---

## 🔧 Configuration (in-code)

| Variable            | Purpose                              | Default     |
|---------------------|--------------------------------------|-------------|
| `reply_message`     | Response to "ping"                   | `"pong"`    |
| `trigger_keyword`   | Word to trigger a reply              | `"ping"`    |
| `target_channel`    | Mesh channel index                   | `0`         |
| `cooldown_seconds`  | Time to wait before next reply       | `10`        |

---

## 🧪 Requirements

- Python 3.7+
- Meshtastic Python API
- PubSub

Install dependencies:

```bash
pip install meshtastic pypubsub

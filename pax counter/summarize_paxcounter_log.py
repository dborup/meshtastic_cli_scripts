import pandas as pd

# Load CSV
df = pd.read_csv("meshtastic_paxcounter_log.csv")

# Convert Time column to datetime
df["Time"] = pd.to_datetime(df["Time"])

# Group by Node
grouped = df.groupby("Name")

print("\n📊 Paxcounter Daily Summary\n")

for name, group in grouped:
    print(f"🔹 {name}")
    print(f"  First seen: {group['Time'].min()}")
    print(f"  Last seen : {group['Time'].max()}")
    print(f"  Max Total : {group['Total Count'].max()}")
    print(f"  Max WiFi  : {group['WiFi Count'].max()}")
    print(f"  Max BLE   : {group['BLE Count'].max()}")
    print(f"  Avg Total : {group['Total Count'].mean():.2f}")
    print(f"  Avg WiFi  : {group['WiFi Count'].mean():.2f}")
    print(f"  Avg BLE   : {group['BLE Count'].mean():.2f}")
    
    # Peak hour detection
    group['Hour'] = group['Time'].dt.hour
    peak = group.groupby("Hour")["Total Count"].mean().idxmax()
    print(f"  📈 Peak Hour: {peak}:00\n")


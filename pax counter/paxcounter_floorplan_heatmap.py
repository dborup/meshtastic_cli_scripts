import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Configuration: map node name to (x, y) pixel position
NODE_POSITIONS = {
    'Node1': (400, 250),
    'Node2': (150, 300),
    # Add more node mappings here
}

# Load latest CSV
df = pd.read_csv("meshtastic_paxcounter_log_latest.csv")
df["Time"] = pd.to_datetime(df["Time"])

# Get most recent record for each node
latest_df = df.sort_values("Time").groupby("Name").tail(1)

# Load floorplan image
floorplan = mpimg.imread("floorplan.png")  # <-- your image file
fig, ax = plt.subplots(figsize=(12, 8))
ax.imshow(floorplan)
ax.set_title("📍 PaxCounter Heatmap on Floorplan")

# Normalize for color scaling
max_count = latest_df["Total Count"].max()

# Plot each node
for _, row in latest_df.iterrows():
    name = row["Name"]
    count = row["Total Count"]
    if name in NODE_POSITIONS:
        x, y = NODE_POSITIONS[name]
        ax.scatter(x, y, s=200, c=[[1, 0, 0, count / max_count]], edgecolors='black')
        ax.text(x, y - 10, f"{name}\n{int(count)}", ha='center', va='bottom', fontsize=9)

plt.axis('off')
plt.tight_layout()
plt.savefig("paxcounter_floorplan_heatmap.png", dpi=300)
plt.show()

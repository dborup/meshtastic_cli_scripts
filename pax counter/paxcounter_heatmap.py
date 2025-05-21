import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the log
df = pd.read_csv("meshtastic_paxcounter_log_latest.csv")

# Parse time
df["Time"] = pd.to_datetime(df["Time"])

# Round timestamps to 15-minute intervals
df["TimeBin"] = df["Time"].dt.floor("15min")

# Pivot table: rows = Node, cols = TimeBin, values = Avg Total Count
heatmap_data = df.pivot_table(
    index="Name",
    columns="TimeBin",
    values="Total Count",
    aggfunc="mean"
)

# Plot
plt.figure(figsize=(15, 4 + len(heatmap_data)))
sns.heatmap(
    heatmap_data,
    cmap="YlOrRd",
    linewidths=0.5,
    linecolor="gray",
    cbar_kws={'label': 'Total Count'},
    annot=False  # change to True to show numbers
)

plt.title("📊 PaxCounter Heatmap (15-min bins)")
plt.xlabel("Time")
plt.ylabel("Node")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig("paxcounter_heatmap.png", dpi=300)
plt.show()

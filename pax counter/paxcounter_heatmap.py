import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Parse bin size from command-line, default to 15 minutes
bin_size = sys.argv[1] if len(sys.argv) > 1 else "15min"

# Load CSV log
df = pd.read_csv("meshtastic_paxcounter_log_latest.csv")
df["Time"] = pd.to_datetime(df["Time"])
df["TimeBin"] = df["Time"].dt.floor(bin_size)

# Get date range subtitle
start_date = df["Time"].min().strftime("%Y-%m-%d")
end_date = df["Time"].max().strftime("%Y-%m-%d")
subtitle = f"Date range: {start_date} to {end_date}"

# Pivot table for heatmap
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
    annot=False
)

# Main title and subtitle
plt.title(f"📊 PaxCounter Heatmap ({bin_size} bins)\n{subtitle}", fontsize=14)
plt.xlabel("Time")
plt.ylabel("Node")

# Format time axis to show HH:MM only
ax = plt.gca()
ax.set_xticklabels([t.strftime('%H:%M') for t in heatmap_data.columns])
plt.xticks(rotation=45, ha='right')

plt.tight_layout()

# Save with bin label
output_file = f"paxcounter_heatmap_{bin_size.replace(':', '')}.png"
plt.savefig(output_file, dpi=300)
plt.show()

print(f"✅ Saved heatmap: {output_file}")

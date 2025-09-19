import pandas as pd
import ast
import matplotlib.pyplot as plt


INPUT_FILE = "data/2_pkt/mirrors_packets.csv"

df = pd.read_csv(INPUT_FILE)


# Plot all mirrors in the same figure
plt.figure(figsize=(8, 4))
grouped = df.groupby("Mirror")
for mirror, group in grouped:
    for idx, row in group.iterrows():
        packet_times = ast.literal_eval(row["Packet Times"])
        cumulative_bytes = ast.literal_eval(row["Cumulative Bytes"])
        plt.plot(packet_times, cumulative_bytes, marker="o", label=mirror)
plt.xlabel("Packet Times (ms)")
plt.ylabel("Cumulative Bytes")
plt.legend()
plt.tight_layout()
plt.savefig("data/2_pkt/all_mirrors_packet_plot.png")
plt.close()

# Generate LaTeX table for domain statistics
latex_table = df[
    [
        "Mirror",
        "Total Bytes",
        "Packet Min",
        "Packet Max",
        "Packet Mode",
        "Packet Median",
    ]
]
latex_str = latex_table.to_latex(
    index=False, caption="Packet Statistics per Mirror", label="tab:packet_stats"
)
with open("data/2_pkt/mirrors_packet_stats.tex", "w") as f:
    f.write(latex_str)

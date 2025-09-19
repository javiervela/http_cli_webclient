import pandas as pd
import matplotlib.pyplot as plt

INPUT_CSV = "data/3_tcp_info/universities_with_tcp_info_rtt.csv"

df = pd.read_csv(INPUT_CSV)
latex_table = df[["Domain", "RTT_mean", "TCP_INFO_RTT", "TCP_INFO_RTT_var"]].to_latex(
    index=False
)
with open("data/3_tcp_info/universities_tcp_info_table.tex", "w") as f:
    f.write(latex_table)


plt.figure(figsize=(4, 3))
plt.scatter(df["RTT_mean"], df["TCP_INFO_RTT"], alpha=0.7)
plt.xlabel("RTT_mean")
plt.ylabel("TCP_INFO_RTT")
plt.grid(True)

# Highlight the diagonal where RTT_mean == TCP_INFO_RTT
min_val = min(df["RTT_mean"].min(), df["TCP_INFO_RTT"].min())
max_val = max(df["RTT_mean"].max(), df["TCP_INFO_RTT"].max())
plt.plot(
    [min_val, max_val],
    [min_val, max_val],
    color="red",
    linewidth=2,
    label="RTT = TCP_INFO_RTT",
)

plt.legend()
plt.tight_layout()
plt.savefig("data/3_tcp_info/rtt_mean_vs_tcp_info_rtt.png")

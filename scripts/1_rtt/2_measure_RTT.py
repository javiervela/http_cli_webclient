import pandas as pd
import subprocess
import statistics

INPUT_CSV = "data/1_rtt/universities.csv"
OUTPUT_CSV = "data/1_rtt/universities_with_rtt.csv"

df = pd.read_csv(INPUT_CSV)

ips = []
rtts = []
for domain in df["Domain"]:
    print(f"Pinging {domain}...")
    ip = None
    rtt_values = []
    for _ in range(20):
        try:
            result = subprocess.run(
                ["webclient", domain, "-ping"],
                capture_output=True,
                text=True,
                check=True,
            )
            output = result.stdout.strip()
            parts = output.split()
            if len(parts) >= 4 and parts[1] == "RTT":
                if ip is None:
                    ip = parts[0]
                rtt = float(parts[2])
                rtt_values.append(rtt)
        except Exception as e:
            print(f"Error with {domain}: {e}")
    if rtt_values:
        min_rtt = min(rtt_values)
        max_rtt = max(rtt_values)
        median_rtt = statistics.median(rtt_values)
        mean_rtt = statistics.mean(rtt_values)
    else:
        min_rtt = max_rtt = median_rtt = mean_rtt = None
    ips.append(ip)
    rtts.append(
        {"min": min_rtt, "max": max_rtt, "median": median_rtt, "mean": mean_rtt}
    )

# Add results to dataframe
df["IP"] = ips
df["RTT_min"] = [rtt["min"] for rtt in rtts]
df["RTT_max"] = [rtt["max"] for rtt in rtts]
df["RTT_median"] = [rtt["median"] for rtt in rtts]
df["RTT_mean"] = [rtt["mean"] for rtt in rtts]

# Save to new CSV
df.to_csv(OUTPUT_CSV, index=False)
print(f"Results saved to {OUTPUT_CSV}")

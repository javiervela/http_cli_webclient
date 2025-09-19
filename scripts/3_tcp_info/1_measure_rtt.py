import pandas as pd
import subprocess

INPUT_CSV = "data/1_rtt/universities_with_rtt.csv"
OUTPUT_CSV = "data/3_tcp_info/universities_with_tcp_info_rtt.csv"

df = pd.read_csv(INPUT_CSV)

rtts = []
for domain in df["Domain"]:
    print(f"Pinging {domain}...")
    rtt = None
    var = None
    try:
        result = subprocess.run(
            ["webclient", domain, "-info"],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout.strip().splitlines()
        for line in output:
            if line.startswith("TCP_INFO: RTT "):
                rtt = float(line.split()[2])
            elif line.startswith("TCP_INFO: RTT_var "):
                var = float(line.split()[2])
    except Exception as e:
        print(f"Error with {domain}: {e}")
    rtts.append({"rtt": rtt, "var": var})

# Add results to dataframe
df["TCP_INFO_RTT"] = [rtt["rtt"] for rtt in rtts]
df["TCP_INFO_RTT_var"] = [rtt["var"] for rtt in rtts]

# Save to new CSV
df.to_csv(OUTPUT_CSV, index=False)
print(f"Results saved to {OUTPUT_CSV}")

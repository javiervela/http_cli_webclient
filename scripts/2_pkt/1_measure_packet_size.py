import pandas as pd
import subprocess
import re
import ast
import matplotlib.pyplot as plt


INPUT_FILE = "data/2_pkt/mirrors.csv"
OUTPUT_FILE = "data/2_pkt/mirrors_packets.csv"

df = pd.read_csv(INPUT_FILE)


def measure_packet_info(row):
    mirror = row["Mirror"].strip()
    file_path = row["File"].strip()
    command = ["webclient", mirror, "80", file_path, "-pkt"]
    result = subprocess.run(command, capture_output=True, text=True)
    # Extract all "<number> bytes <number> ms" from output
    matches = re.findall(r"(\d+) bytes (\d+) ms", result.stdout)
    bytes_list = [int(m[0]) for m in matches]
    cumulative_bytes = [sum(bytes_list[: i + 1]) for i in range(len(bytes_list))]
    time_list = [int(m[1]) for m in matches]
    total_size = sum(bytes_list)
    total_time = sum(time_list)

    # Calculate statistics
    packet_min = min(bytes_list[1:])
    packet_max = max(bytes_list[1:])
    packet_mode = pd.Series(bytes_list[1:]).mode()[0]
    packet_median = pd.Series(bytes_list[1:]).median()

    # Store lists as strings for CSV
    return pd.Series(
        {
            "Packet Bytes": str(bytes_list),
            "Cumulative Bytes": str(cumulative_bytes),
            "Packet Times": str(time_list),
            "Total Bytes": total_size,
            "Total Time": total_time,
            "Packet Min": packet_min,
            "Packet Max": packet_max,
            "Packet Mode": packet_mode,
            "Packet Median": packet_median,
        }
    )


# Combine Mirror and File columns for input
df[
    [
        "Packet Bytes",
        "Cumulative Bytes",
        "Packet Times",
        "Total Bytes",
        "Total Time",
        "Packet Min",
        "Packet Max",
        "Packet Mode",
        "Packet Median",
    ]
] = df.apply(measure_packet_info, axis=1)
df.to_csv(OUTPUT_FILE, index=False)

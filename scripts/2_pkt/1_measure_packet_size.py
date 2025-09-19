import pandas as pd
import subprocess
import re


INPUT_FILE = "data/2_pkt/mirrors.csv"
INPUT_FILE_2 = "data/1_rtt/universities.csv"
OUTPUT_FILE = "data/2_pkt/mirrors_packets.csv"
OUTPUT_FILE_2 = "data/2_pkt/universities_packets.csv"

df = pd.read_csv(INPUT_FILE)
df_2 = pd.read_csv(INPUT_FILE_2)


def measure_packet_info(row, domain_col="Domain", file_col=None):
    mirror = row[domain_col].strip()
    file_path = row[file_col].strip() if file_col else "/"
    command = ["webclient", mirror, "80", file_path, "-pkt"]
    result = subprocess.run(command, capture_output=True, text=True)
    matches = re.findall(r"(\d+) bytes (\d+) ms", result.stdout)
    bytes_list = [int(m[0]) for m in matches]
    cumulative_bytes = [sum(bytes_list[: i + 1]) for i in range(len(bytes_list))]
    time_list = [int(m[1]) for m in matches]
    total_size = sum(bytes_list)
    total_time = sum(time_list)

    packet_min = min(bytes_list[1:])
    packet_max = max(bytes_list[1:])
    packet_mode = pd.Series(bytes_list[1:]).mode()[0]
    packet_median = pd.Series(bytes_list[1:]).median()

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
] = df.apply(
    lambda row: measure_packet_info(row, domain_col="Mirror", file_col="File"), axis=1
)
df.to_csv(OUTPUT_FILE, index=False)

df_2[
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
] = df_2.apply(lambda row: measure_packet_info(row, domain_col="Domain"), axis=1)
df_2.to_csv(OUTPUT_FILE_2, index=False)

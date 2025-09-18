import pandas as pd
from haversine import haversine, Unit
import adjustText
import matplotlib.pyplot as plt


INPUT_CSV = "data/1_rtt/universities_merged.csv"
OUTPUT_CSV = "data/1_rtt/universities_with_distance.csv"

WPI_COORDINATES = (42.2741, -71.8080)

df = pd.read_csv(INPUT_CSV)


def distance_wpi_to_latlong(row):
    coord = (row["Latitude"], row["Longitude"])
    return haversine(WPI_COORDINATES, coord, unit=Unit.KILOMETERS)


def distance_wpi_to_ip_latlong(row):
    coord = (row["IP_Latitude"], row["IP_Longitude"])
    return haversine(WPI_COORDINATES, coord, unit=Unit.KILOMETERS)


def distance_latlong_to_ip_latlong(row):
    coord1 = (row["Latitude"], row["Longitude"])
    coord2 = (row["IP_Latitude"], row["IP_Longitude"])
    return haversine(coord1, coord2, unit=Unit.KILOMETERS)


df["Distance_WPI_to_LatLong"] = df.apply(distance_wpi_to_latlong, axis=1)
df["Distance_WPI_to_IP_LatLong"] = df.apply(distance_wpi_to_ip_latlong, axis=1)
df["Distance_LatLong_to_IP_LatLong"] = df.apply(distance_latlong_to_ip_latlong, axis=1)

df = df[
    [
        "Domain",
        "Country",
        "IP_Country",
        "IP",
        "RTT_median",
        "Distance_WPI_to_LatLong",
        "Distance_WPI_to_IP_LatLong",
        "Distance_LatLong_to_IP_LatLong",
    ]
]

df.to_csv(OUTPUT_CSV, index=False)

latex_df = df.fillna("---")
latex_df["WPI_to_Uni"] = latex_df["Distance_WPI_to_LatLong"].apply(
    lambda x: f"{int(round(float(x)))}" if pd.notnull(x) and x != "---" else "---"
)
latex_df["WPI_to_IP"] = latex_df["Distance_WPI_to_IP_LatLong"].apply(
    lambda x: f"{int(round(float(x)))}" if pd.notnull(x) and x != "---" else "---"
)
latex_df["Uni_to_IP"] = latex_df["Distance_LatLong_to_IP_LatLong"].apply(
    lambda x: f"{int(round(float(x)))}" if pd.notnull(x) and x != "---" else "---"
)
latex_df = latex_df.drop(
    [
        "Distance_WPI_to_LatLong",
        "Distance_WPI_to_IP_LatLong",
        "Distance_LatLong_to_IP_LatLong",
    ],
    axis=1,
)
column_format = "p{3cm}" + "p{3cm}" + "p{3cm}" + "p{3cm}" + "rrrr"
latex_table = latex_df.to_latex(
    index=False,
    escape=True,
    column_format=column_format,
    longtable=False,
    caption=None,
)
rowcolors = "\\rowcolors{2}{gray!15}{white}\n"
latex_table = latex_table.replace("\\begin{tabular}", rowcolors + "\\begin{tabular}")
with open(OUTPUT_CSV.replace(".csv", "_table.tex"), "w") as f:
    f.write(latex_table)
print(f"Saved enriched file to {OUTPUT_CSV}")


plt.figure(figsize=(8, 6))
x = df["Distance_WPI_to_LatLong"]
y = df["RTT_median"]
labels = df["Domain"]

plt.scatter(x, y, color="blue")

texts = [
    plt.text(x.iloc[i], y.iloc[i], label, fontsize=12, alpha=0.8)
    for i, label in enumerate(labels)
]
adjustText.adjust_text(texts, arrowprops=dict(arrowstyle="->", color="gray", lw=0.5))

plt.xlabel("Distance from WPI to University (km)", fontsize=12)
plt.ylabel("Median RTT (ms)", fontsize=12)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig(OUTPUT_CSV.replace(".csv", "_scatter.png"))

plt.figure(figsize=(8, 6))
x_ip = df["Distance_WPI_to_IP_LatLong"]
y_ip = df["RTT_median"]
labels_ip = df["Domain"]

plt.scatter(x_ip, y_ip, color="green")

texts_ip = [
    plt.text(x_ip.iloc[i], y_ip.iloc[i], label, fontsize=12, alpha=0.8)
    for i, label in enumerate(labels_ip)
]
adjustText.adjust_text(texts_ip, arrowprops=dict(arrowstyle="->", color="gray", lw=0.5))

plt.xlabel("Distance from WPI to Server IP Location (km)", fontsize=12)
plt.ylabel("Median RTT (ms)", fontsize=12)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig(OUTPUT_CSV.replace(".csv", "_scatter_ip.png"))

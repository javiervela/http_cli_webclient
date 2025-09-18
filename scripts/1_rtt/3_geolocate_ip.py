import pandas as pd
import requests
import time

INPUT_CSV = "data/1_rtt/universities_with_rtt.csv"
OUTPUT_CSV = "data/1_rtt/universities_with_geoip.csv"
BASE_URL = "https://ipinfo.io"

df = pd.read_csv(INPUT_CSV)

cities, regions, countries, lats, lons = [], [], [], [], []

for ip in df["IP"]:
    print(f"Geolocating {ip}...")
    url = f"{BASE_URL}/{ip}/json"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    data = response.json()

    loc = data.get("loc", None)
    lat, lon = loc.split(",") if loc else (None, None)

    cities.append(data.get("city", None))
    regions.append(data.get("region", None))
    countries.append(data.get("country", None))
    lats.append(lat)
    lons.append(lon)
    time.sleep(0.5)

df["IP_City"] = cities
df["IP_Region"] = regions
df["IP_Country"] = countries
df["IP_Latitude"] = lats
df["IP_Longitude"] = lons

df.drop(
    columns=["IP", "RTT_min", "RTT_max", "RTT_median", "RTT_mean"],
    inplace=True,
    errors="ignore",
)

df.to_csv(OUTPUT_CSV, index=False)
print(f"Saved enriched file to {OUTPUT_CSV}")

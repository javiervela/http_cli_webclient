import pandas as pd
import requests
import time

INPUT_CSV = "data/1_rtt/universities.csv"
OUTPUT_CSV = "data/1_rtt/universities_with_coordinates.csv"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

df = pd.read_csv(INPUT_CSV)

latitudes = []
longitudes = []
cities = []
regions = []
countries = []

for uni in df["University"]:
    print(f"Fetching coordinates for: {uni}")
    params = {"q": uni, "format": "json", "limit": 1, "addressdetails": 1}
    response = requests.get(
        NOMINATIM_URL, params=params, headers={"User-Agent": "uni-locator"}
    )
    response.raise_for_status()
    data = response.json()
    latitudes.append(data[0].get("lat", ""))
    longitudes.append(data[0].get("lon", ""))
    address = data[0].get("address", {})
    cities.append(address.get("city", address.get("town", address.get("village", ""))))
    regions.append(address.get("state", address.get("region", "")))
    countries.append(address.get("country", ""))
    time.sleep(1)

df["Latitude"] = latitudes
df["Longitude"] = longitudes
df["City"] = cities
df["Region"] = regions
df["Country"] = countries

df.to_csv(OUTPUT_CSV, index=False)

import re
import requests

url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb?f=pjson"

try:
    response = requests.get(url)
    response.raise_for_status()
    map_servers = [
        item["name"]
        for item in response.json()["services"]
        if re.search(r"ACS|Census|Current", item["name"])
    ]
    print(f"✅ Successfully fetched map servers.")

except requests.exceptions.RequestException as e:
    print(f"❌ HTTP Request failed: {e}")

print(map_servers)

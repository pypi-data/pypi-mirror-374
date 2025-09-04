import requests
import geopandas as gpd


def get_tiger_polygons(
    layer_id: int,
    where_clause: str,
    fields: str,  # Added a parameter to specify fields
    service: str = "TIGERweb/tigerWMS_Current",
) -> gpd.GeoDataFrame:
    """
    Fetches geographic polygons from the US Census TIGERweb REST API.

    Args:
        layer_id (int): The numeric ID for the desired geography layer.
        where_clause (str): An SQL-like clause to filter the geographies.
        fields (str): A comma-separated string of field names to return.
        service (str): The name of the TIGERweb map service to query.
    """
    API_URL = f"https://tigerweb.geo.census.gov/arcgis/rest/services/{service}/MapServer/{layer_id}/query"

    params = {
        "where": where_clause,
        "outFields": fields,
        "outSR": "4326",
        "f": "geojson",
        "returnGeometry": "true",
        "returnCountOnly": "false",
        "resultOffset": 0,
        "resultRecordCount": 1_000,
        "timeout": 60,
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        gdf = gpd.GeoDataFrame.from_features(response.json()["features"])
        raw = response.json()["features"]
        print(f"✅ Successfully fetched {len(gdf)} polygons.")
        return raw

    except requests.exceptions.RequestException as e:
        print(f"❌ HTTP Request failed: {e}")
    except (KeyError, ValueError) as e:
        print(f"❌ Failed to parse response JSON: {e}")
        print(f"   Server Response: {response.text[:200]}...")

    return gpd.GeoDataFrame()


# --- Example Usage ---
# Fetching counties in Colorado (layer 82) with only specific fields

colorado_gdf = get_tiger_polygons(
    layer_id=8,
    where_clause="STATE IN ('08') AND COUNTY IN ('069')",
    fields="GEOID,NAME",  # Only request these three attribute fields
    service="TIGERweb/tigerWMS_Census2020",
)

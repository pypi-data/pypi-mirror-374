import os
from cendat import CenDatHelper
import polars as pl
import geopandas as gpd

cdh = CenDatHelper(key=os.getenv("CENSUS_API_KEY"))

cdh.list_products(years=[2023], patterns=r"acs/acs5\)")
cdh.set_products()
# cdh.list_groups(patterns=r"^race")
cdh.set_groups(["B17001"])
# cdh.describe_groups()
# cdh.set_variables("B01001_001E")
cdh.set_geos(["040"])
response = cdh.get_data(
    include_names=True,
    include_geometry=True,
    # within={"state": ["08", "56"]},
)
# df = response.to_polars(destring=True, concat=True)
df = response.to_gpd(destring=True, join_strategy="inner")
print(df.head())

response.tabulate(
    "NAME",
    "B17001_002E",
    "B17001_001E",
    where=[
        "B17001_001E > 1_000",
        "B17001_002E / B17001_001E < 0.01",
        "'CDP' not in NAME",
    ],
    weight_var="B17001_001E",
    strat_by="vintage",
)

# ------------------

cdh = CenDatHelper(key=os.getenv("CENSUS_API_KEY"))
cdh.list_products(years=[2023], patterns=r"/acs/acs5\)")
cdh.set_products()
cdh.set_variables("B01001_001E")  # total population
cdh.set_geos("150")
response = cdh.get_data(
    include_geometry=True,
    within={"state": ["08", "56"]},
)

# how many counties
response.tabulate("state", where="B01001_001E > 10_000")

# how many people in those counties
response.tabulate("state", weight_var="B01001_001E", where="B01001_001E > 10_000")

# ------------------

cdh.list_products(years=[2022, 2023], patterns="/cps/tobacco")
cdh.set_products()
cdh.list_groups()
cdh.set_variables(["PEA1", "PEA3", "PWNRWGT"])
cdh.set_geos("state", "desc")
response = cdh.get_data(
    within={"state": ["06", "48"]},
    include_attributes=True,
    include_names=True,
    include_geoids=True,
)
response.tabulate(
    "PEA1",
    "PEA3",
    strat_by="state",
    weight_var="PWNRWGT",
    weight_div=3,
)

# ------------------

cdh = CenDatHelper(key=os.getenv("CENSUS_API_KEY"))

cdh.list_products(patterns=r"2010/dec/sf1\)")
cdh.set_products()
cdh.list_groups(patterns=r"^race")
cdh.describe_groups("PCT23")
cdh.set_groups(["PCT23"])
cdh.set_geos("160")
response = cdh.get_data(
    within={"state": "08"},
)

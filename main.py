from fastapi import FastAPI, Query
from typing import List, Union
import xarray as xr

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/data/{lat}/{lon}")
async def get_data(
    lat: float,
    lon: float,
    parameters: Union[List[str], str] = Query(...)
):
    # Open the Netcdf file
    ds = xr.open_dataset("GEOS-CF.v01.rpl.aqc_tavg_1hr_g1440x721_v1.20250203_0030z.nc4", engine="netcdf4")

    # Subset the dataset
    subset = ds.sel(lat=lat, lon=lon, method='nearest')[parameters]

    # Convert to dictionary and return as JSON
    result = subset.to_dict()

    return result
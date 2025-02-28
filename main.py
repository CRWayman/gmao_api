from fastapi import FastAPI, Query, HTTPException, Depends, Path
from typing import List, Union, Annotated, Optional
import xarray as xr
from enum import Enum
import glob
import os
from datetime import date
import requests
import io
from fastapi.security import HTTPBasic, HTTPBasicCredentials


app = FastAPI()
DATASET_DIR = "./dataset_files"

security = HTTPBasic()


@app.get("/login")
def read_current_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    return {"username": credentials.username, "password": credentials.password}


@app.get("/")
async def root():
    return {"message": "Hello World"}


DATASET_ALLOWED_OPTIONS = {
    "fcst": {
        "chm": {
            "v1": ["NO2", "O3", "PM25", "Hcho", "CO", "SO2"]
        },
        "met": {
            "x1": ["MET"],
            "p23": ["MET"]
        }
    },
    "rpl": {
        "aqc": {
            "v1": ["NO2", "O3", "PM25"]
        },
        "chm": {
            "v1": ["NO2", "O3", "PM25"],
        }
    }
    
    
}

# Dependency to validate all parameters
def validate_params(mode, group, level, start_date, end_date):
    if mode and mode not in DATASET_ALLOWED_OPTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode '{mode}''. Allowed: {list(DATASET_ALLOWED_OPTIONS.keys())}"
        )

    if group and group not in DATASET_ALLOWED_OPTIONS[mode]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid group '{group}' for mode '{mode}'. Allowed: {list(DATASET_ALLOWED_OPTIONS[mode].keys())}"
        )
    
    if level and level not in DATASET_ALLOWED_OPTIONS[mode][group]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid level '{level}' for group '{group}'. Allowed: {list(DATASET_ALLOWED_OPTIONS[mode][group].keys())}"
        )

    if start_date or end_date and mode != "rpl":
        raise HTTPException(
            status_code=400,
            detail="Start and end dates are only allowed for mode 'rpl'."
        )
    
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before end date."
        )


@app.get("/cfapi/{mode}/")
@app.get("/cfapi/{mode}/{grp}/")
@app.get("/cfapi/{mode}/{grp}/{level}/")
async def get_dataset(
    mode = "fcst",
    grp = None,
    level = None,
    lat: Annotated[list[float], Query(max_length=2)] = [38],
    lon: Annotated[list[float], Query(max_length=2)] = [-77],
    products: Annotated[list, "Provide a list of products to subset a particular dataset.", Query(...)] = [],
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    # Validate parameters
    validate_params(mode, grp, level, start_date, end_date)

    # Resolve case sensitivity
    products = [param.upper() for param in products]

    # Get filenames that match the parameters
    filenames = get_file_paths(mode, grp, level)

    # Handle exception when filename not found
    if not filenames:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    file0 = filenames[0]

    # Open the NetCDF file
    # url = "https://portal.nccs.nasa.gov/datashare/gmao/geos-cf/v1/das/Y2025/M02/D27/GEOS-CF.v01.rpl.aqc_tavg_1hr_g1440x721_v1.20250227_0030z.nc4"
    # response = requests.get(url)
    # response.raise_for_status()  # Ensure the request was successful
    # file_like_object = io.BytesIO(response.content)
    
    with xr.open_dataset(file0, engine="h5netcdf") as ds:
        # Subset the dataset
        try:
            subset = ds.sel(lat=slice(lat[0], lat[-1]), lon=slice(lon[0], lon[-1]))[products]
            result = subset.to_dict()
        except KeyError:
            raise HTTPException(status_code=404, detail="Invalid product(s).")

    return result


def get_file_paths(mode, grp, level):
    if not grp:
        grp = list(DATASET_ALLOWED_OPTIONS[mode].keys())[0]
    
    if not level:
        level = list(DATASET_ALLOWED_OPTIONS[mode][grp].keys())[0]

    dataset_name_wildcard = f'GEOS-CF.v01.{mode}.{grp}*{level}*'
    file_list = glob.glob(os.path.join(DATASET_DIR, dataset_name_wildcard))
    file_list.sort()

    return file_list

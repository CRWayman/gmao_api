from fastapi import FastAPI, Query, HTTPException, Depends, Path
from typing import List, Union, Annotated, Optional
import xarray as xr
from enum import Enum
import glob
import os


app = FastAPI()
DATASET_DIR = "./dataset_files"


@app.get("/")
async def root():
    return {"message": "Hello World"}

class Collection(str, Enum):
    fcst = "fcst"
    rpl = "rpl"

class Dataset(str, Enum):
    chm = "chm"
    ems = "ems"
    htf = "htf"
    met = "met"
    xgc = "xgc"
    aqc = "aqc"

class Level(str, Enum):
    v1 = "v1"
    v72 = "v72"
    p23 = "p23"
    x1 = "x1"

class Product(str, Enum):
    NO2 = "NO2"
    CO = "CO"
    O3 = "O3"
    PM25 = "PM2.5"
    Hcho = "Hcho"
    SO2 = "SO2"


# DATASET_ALLOWED_OPTIONS = {
#     Collection.fcst: [{Dataset.chm:
#                        [{Level.v1: [Product.NO2, Product.O3, Product.PM25, Product.Hcho, Product.CO, Product.SO2]},
#                        ]},
#                       {Dataset.met: Level.x1, Dataset.met: Level.p23}]
    
# }

allowed_levels = {
    "met": {"x1", "p23"},
}

# Dependency to validate level
def validate_level(dataset: Optional[Dataset] = None, level: Optional[Level] = None):
    if dataset is None or level is None:
        return Level.v1
    
    if level not in allowed_levels.get(dataset, set()):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid level '{level}' for dataset '{dataset}'. Allowed: {allowed_levels.get(dataset, set())}"
        )
    return level


@app.get("/cfapi/{collection}/")
@app.get("/cfapi/{collection}/{dataset}/")
@app.get("/cfapi/{collection}/{dataset}/{level}/")
@app.get("/cfapi/{collection}/{dataset}/{level}/{lat}/{lon}")
async def get_dataset(
    collection: Collection = Collection.fcst,
    dataset: Optional[Dataset] = Dataset.chm,
    level: Optional[Level] = Depends(validate_level),
    lat: float = 38,
    lon: float = -77,
    products: Annotated[list, "Provide a list of products to subset a particular dataset.", Query(...)] = []
):
    # Resolve case sensitivity
    products = [param.upper() for param in products]

    # TODO: Perform parameter checks with database to verify validity

    # Get filenames that match the parameters
    filenames = get_file_paths(collection, dataset, level)

    # Handle exception when filename not found
    if not filenames:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    file0 = filenames[0]

    # Open the NetCDF file
    ds = xr.open_dataset(file0, engine="netcdf4")

    # Subset the dataset
    try:
        subset = ds.sel(lat=lat, lon=lon, method='nearest')[products]
        result = subset.to_dict()
    except KeyError:
        raise HTTPException(status_code=404, detail="Invalid product(s).")

    return result


def get_file_paths(collection, dataset, level):
    dataset_name_wildcard = f'GEOS-CF.v01.{collection}.{dataset}*{level}*'
    file_list = glob.glob(os.path.join(DATASET_DIR, dataset_name_wildcard))
    file_list.sort()

    return file_list

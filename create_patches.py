import numpy as np
import dask.array as da
import xarray as xr
import rasterio


class PatchCreator:
    def __init__(self, filename):
        self.filename = filename

    def print_filename(self):
        print("Filename: ", self.filename)


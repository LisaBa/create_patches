import numpy as np
import dask.array as da
import xarray as xr
import rasterio


class PatchCreator:
    def __init__(self, filename, n_bands=3, chunks_x=256, chunks_y=256):
        self.filename = filename
        self.n_bands = n_bands
        self.chunks_x = chunks_x
        self.chunks_y = chunks_y

        self.data = self.load_data()

    def print_info(self):
        print("Filename: ", self.filename)
        print("Dimensions: ", self.data.dims)
        print("Number of Bands: ", self.data.sizes["band"])
        print("Width: ", self.data.sizes["x"])
        print("Height: ", self.data.sizes["y"])
        print("Total Number of Pixels: ", self.data.sizes["x"] * self.data.sizes["y"])
        print("Number of resulting patches: ", int((self.data.sizes["x"] * self.data.sizes["y"])/(256*256)))

    def load_data(self):
        data = xr.open_rasterio(
            self.filename,
            chunks={"band": self.n_bands, "x": self.chunks_x, "y": self.chunks_y},
        )
        return data


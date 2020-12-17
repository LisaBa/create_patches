import numpy as np
import dask.array as da
import xarray as xr
import rasterio
from rasterio.windows import Window
import rioxarray as riox
import matplotlib.pyplot as plt
import os


class PatchCreator:
    def __init__(
        self,
        filename,
        output_folder,
        index_start=0,
        n_bands=3,
        chunks_x=256,
        chunks_y=256,
    ):
        self.filename = filename
        self.output_folder = output_folder
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
        print(
            "Number of resulting patches: ",
            int((self.data.sizes["x"] * self.data.sizes["y"]) / (256 * 256)),
        )

    def load_data(self):
        data = xr.open_rasterio(
            self.filename,
            chunks={"band": self.n_bands, "x": self.chunks_x, "y": self.chunks_y},
        )
        return data

    def create_subset(self):
        # subset = self.data[:, 20000:22000, 10000:12000]
        # print(subset)
        # return subset
        win = Window(0, 0, 256, 256)
        with rasterio.open(self.filename) as src:
            w = src.read(window=win)
        print(w.shape)

        # write meta data
        xform = rasterio.windows.transform(win, src.meta["transform"])
        meta_d = src.meta.copy()
        meta_d.update(
            {"driver": "GTiff", "height": 256, "width": 256, "transform": xform}
        )
        # write output
        with rasterio.open(
            os.path.join(self.output_folder, "images", "patch.tif"), "w", **meta_d
        ) as dest:
            dest.write(w)

    def plot_data(self, x):
        x = x.transpose("x", "y", "band")
        plt.imshow(x[:, :, :])
        plt.show()

    def create_patches(self, patch_size=256):
        # Create output folders for images and labels
        # os.mkdir(os.path.join(self.output_folder, "images"))
        # os.mkdir(os.path.join(self.output_folder, "labels"))

        # If its not dividable it need padding!
        # I need to export the patches because I need to upload them to the google drive
        patch = self.data[:, :256, :256]
        print(patch)
        self.plot_data(patch)
        with rasterio.open(
            os.path.join(self.output_folder, "images", "patch.tif"),
            "w",
            driver="GTiff",
            height=256,
            width=256,
            count=3,
            dtype=patch.dtype,
            crs="+init=epsg:32632",
        ) as dst:
            dst.write(patch)
        # patch.rio.to_raster(os.path.join(self.output_folder, "images", "patch.tif"))
        print("Patch created: ", patch)
        return patch


import numpy as np
import dask.array as da
import xarray as xr
import rasterio
from rasterio.windows import Window
import rioxarray as riox
import matplotlib.pyplot as plt
import os
import math
from PIL import Image
from sklearn.model_selection import train_test_split


class PatchCreator:
    def __init__(
        self,
        image_filename,
        mask_filename,
        output_folder,
        n_bands=3,
        patchsize_x=256,
        patchsize_y=256,
        stride=128,
        start_index=0,
    ):
        self.image_filename = image_filename
        self.mask_filename = mask_filename
        self.output_folder = output_folder
        self.n_bands = n_bands
        self.patchsize_x = patchsize_x
        self.patchsize_y = patchsize_y
        self.stride = stride
        self.start_index = start_index
        self.num_patches_x = None
        self.num_patches_y = None
        self.total_num_patches = None

        self.image, self.mask = self.load_data()
        self.mask_total_width = self.mask.sizes["x"]
        self.mask_total_height = self.mask.sizes["y"]

        self.print_info()

    def _calculate_num_patches(self):
        width = self.mask_total_width
        height = self.mask_total_height
        patchsize_x = self.patchsize_x
        patchsize_y = self.patchsize_y
        stride = self.stride

        self.num_patches_x = math.floor((width - patchsize_x) / stride) + 1
        self.num_patches_y = math.floor((height - patchsize_y) / stride) + 1

        self.total_num_patches = self.num_patches_x * self.num_patches_y
        return self.total_num_patches

    def print_info(self):
        print("Image filename: ", self.image_filename)
        print("Mask filename: ", self.mask_filename)
        print("Dimensions: ", self.image.dims)
        print("Number of Bands: ", self.image.sizes["band"])
        print(
            "Width and Height of image ",
            self.image.sizes["x"],
            "x",
            self.image.sizes["y"],
        )
        print(
            "Width and Height of mask ",
            self.mask.sizes["x"],
            "x",
            self.mask.sizes["y"],
        )
        print(
            "Max. number of resulting patches: ", self._calculate_num_patches(),
        )

    def load_data(self):
        img = xr.open_rasterio(
            self.image_filename,
            chunks={"band": self.n_bands, "x": self.patchsize_x, "y": self.patchsize_y},
        )
        mask = xr.open_rasterio(
            self.mask_filename,
            chunks={"band": 1, "x": self.patchsize_x, "y": self.patchsize_y},
        )

        return img, mask

    def _create_tif_output(
        self, filename, out_type, col_off, row_off, width, height, idx
    ):
        # Create image patch
        win = Window(col_off, row_off, width, height)
        with rasterio.open(filename) as src:
            w = src.read(window=win)

        # write meta data
        xform = rasterio.windows.transform(win, src.meta["transform"])
        meta_d = src.meta.copy()
        meta_d.update(
            {"driver": "GTiff", "height": height, "width": width, "transform": xform}
        )
        # write output
        with rasterio.open(
            os.path.join(self.output_folder, out_type, f"{idx}.tif"), "w", **meta_d,
        ) as dest:
            dest.write(w)

    def _create_single_patch(self, col_off, row_off, index):
        width = self.patchsize_x
        height = self.patchsize_y

        # Create name of output file, starting with index_start
        idx = index
        idx_zeros = str(idx).zfill(9)

        # Create image
        self._create_tif_output(
            self.image_filename, "images", col_off, row_off, width, height, idx_zeros
        )

        # Create mask
        self._create_tif_output(
            self.mask_filename, "labels", col_off, row_off, width, height, idx_zeros
        )

    def create_patches(self):
        # Create output folders for images and labels or check if they already exist
        if not os.path.isdir(os.path.join(self.output_folder, "images")):
            os.mkdir(os.path.join(self.output_folder, "images"))
        if not os.path.isdir(os.path.join(self.output_folder, "labels")):
            os.mkdir(os.path.join(self.output_folder, "labels"))

        idx = self.start_index

        for col in range(self.num_patches_x):
            for row in range(self.num_patches_y):
                min_x = col * self.stride
                min_y = row * self.stride

                # Check if mask has at least 200 pixels with pv on it
                win = Window(min_x, min_y, self.patchsize_x, self.patchsize_y)
                with rasterio.open(self.mask_filename) as src:
                    w = src.read(window=win)
                pv_pixel_sum = np.sum(w == 1)
                # print(np.unique(w))

                # I used an offset of 1 as there seems to be an extra line of pixels at the top of the mask
                # so with min_y + 1 theres no NA value
                # The sum of panel pixels need to be at least 200
                if pv_pixel_sum >= 200:
                    self._create_single_patch(col_off=min_x, row_off=min_y, index=idx)
                    # print(f"Created patch {idx}")
                    idx += 1
            perc = (col / self.num_patches_x) * 100
            print("{:.2f} %% of patches done".format(perc))

        print(f"{idx - self.start_index} patches created!")

    def create_patches_classification(
        self, test_set=False, test_split=0.25, eval_set=False
    ):
        index_list = list(range(self.total_num_patches))
        train_idxs, test_idxs = train_test_split(
            index_list, test_size=test_split, random_state=42
        )
        test_idxs, eval_idxs = train_test_split(
            test_idxs, test_size=test_split, random_state=42
        )

        pos_idx_train = self.start_index
        pos_idx_test = self.start_index
        pos_idx_eval = self.start_index
        neg_idx_train = self.start_index
        neg_idx_test = self.start_index
        neg_idx_eval = self.start_index
        total_idx = self.start_index

        for col in range(self.num_patches_x):
            for row in range(self.num_patches_y):
                min_x = col * self.stride
                min_y = row * self.stride

                win = Window(min_x, min_y, self.patchsize_x, self.patchsize_y)
                with rasterio.open(self.mask_filename) as src:
                    w = src.read(window=win)
                pv_pixel_sum = np.sum(w == 1)

                # Positive examples with at least 100 pixels of PV in them
                if pv_pixel_sum >= 100:
                    # Create image patch
                    win = Window(min_x, min_y, self.patchsize_x, self.patchsize_y)
                    with rasterio.open(self.image_filename) as src:
                        w = src.read(window=win)
                    w = w.transpose(1, 2, 0)
                    im = Image.fromarray(w.astype("uint8"), "RGB")
                    if total_idx in train_idxs:
                        f = "SPI_train"
                        i = pos_idx_train
                        pos_idx_train += 1
                    elif total_idx in test_idxs:
                        f = "SPI_val"
                        i = pos_idx_test
                        pos_idx_test += 1
                    elif total_idx in eval_idxs:
                        f = "SPI_eval"
                        i = pos_idx_eval
                        pos_idx_eval += 1

                    im.save(os.path.join(self.output_folder, f, "1", str(i) + ".png",))

                    # pos_idx += 1

                # Negative sample with less than 100 pixels of PV in them
                else:
                    # Create image patch
                    win = Window(min_x, min_y, self.patchsize_x, self.patchsize_y)
                    with rasterio.open(self.image_filename) as src:
                        w = src.read(window=win)
                    w = w.transpose(1, 2, 0)
                    im = Image.fromarray(w.astype("uint8"), "RGB")

                    if total_idx in train_idxs:
                        f = "SPI_train"
                        i = neg_idx_train
                        neg_idx_train += 1
                    elif total_idx in test_idxs:
                        f = "SPI_val"
                        i = neg_idx_test
                        neg_idx_test += 1
                    elif total_idx in eval_idxs:
                        f = "SPI_eval"
                        i = neg_idx_eval
                        neg_idx_eval += 1

                    im.save(os.path.join(self.output_folder, f, "0", str(i) + ".png",))

                    # neg_idx += 1

                total_idx += 1
            perc = (col / self.num_patches_x) * 100
            print("{:.2f} %% of patches done".format(perc))

        print(f"{self.total_num_patches} patches created!")

    def plot_data(self, x):
        x = x.transpose("x", "y", "band")
        plt.imshow(x[:, :, :])
        plt.show()


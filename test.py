from create_patches import PatchCreator
import xarray as xr
import rasterio
import matplotlib.pyplot as plt
import numpy as np

# Read file as xarray in chunks of 3x256x256
# image_filename = "C:/Users/Lisapisa/Documents/Master/Masterthesis/01-Raster/Other_Solar_Data/Bradbury2020/Modesto/Modesto_clipped.tif"
# mask_filename = "C:/Users/Lisapisa/Documents/Master/Masterthesis/01-Raster/Other_Solar_Data/Bradbury2020/Modesto/Modesto_panels.tif"
# output_folder = (
#     "C:/Users/Lisapisa/Documents/Master/Masterthesis/01-Raster/samples_Modesto"
# )
# output_folder = "C:/Users/Lisapisa/Documents/Master/Masterthesis/01-Raster/Other_Solar_Data/DeepSolar"

image_filename = "C:/Users/Lisapisa/Documents/Master/Masterthesis/01-Raster/Landsberg/annotated_area.tif"
mask_filename = "C:/Users/Lisapisa/Documents/Master/Masterthesis/01-Raster/Landsberg/Landsberg_panels_negative_ex.tif"
output_folder = (
    "C:/Users/Lisapisa/Documents/Master/Masterthesis/01-Raster/samples_negative"
)

new = PatchCreator(
    image_filename,
    mask_filename,
    output_folder,
    start_index=591,
    patchsize_x=256,
    patchsize_y=256,
    stride=128,
)

new.create_patches(panels=False)

# new.create_patches_classification()


# Load examples
# img = "C:/Users/Lisapisa/Documents/Master/Masterthesis/01-Raster/samples_auto/images/000000000.tif"
# msk = "C:/Users/Lisapisa/Documents/Master/Masterthesis/01-Raster/samples_auto/labels/000000000.tif"
# with rasterio.open(img) as src:
#     image = src.read()
# with rasterio.open(msk) as src:
#     mask = src.read()
# mask = np.where(mask <= 1, mask, 0)

# plt.imshow(image.transpose(1, 2, 0))
# plt.imshow(mask.squeeze(), alpha=0.5)
# plt.show()

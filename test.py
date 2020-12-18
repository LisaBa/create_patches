from create_patches import PatchCreator
import xarray as xr
import rasterio

# Read file as xarray in chunks of 3x256x256
filename = (
    "C:/Users/Lisapisa/Documents/Master/Masterthesis/01-Raster/annotated_area.tif"
)
mask_filename = ()
output_folder = "C:/Users/Lisapisa/Documents/Master/Masterthesis/01-Raster/samples_auto"

new = PatchCreator(filename, output_folder)
# new.print_info()

new.create_single_patch(9472, 0, 256, 256, 999)

# new.create_patches(start_index=0)

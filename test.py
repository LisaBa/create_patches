from create_patches import PatchCreator
import xarray as xr
import rasterio

# Read file as xarray in chunks of 3x256x256
filename = (
    "C:/Users/Lisapisa/Documents/Master/Masterthesis/01-Raster/annotated_area.tif"
)
output_folder = "C:/Users/Lisapisa/Documents/Master/Masterthesis/01-Raster/samples_auto"

new = PatchCreator(filename, output_folder)
new.print_info()
new.create_subset()

# Create patches and write into new files
# new.create_patches()
# sub = new.create_subset()
# new.plot_data(x=sub)
# new.create_patches()

# test = "C:/Users/Lisapisa/Documents/Master/Masterthesis/01-Raster/samples/images/000000000.tif"
# t = xr.open_rasterio(test)
# print(t)

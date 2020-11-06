from create_patches import PatchCreator

# Read file as xarray in chunks of 3x256x256
filename = r"C:\Users\Lisapisa\Documents\Master\Masterthesis\original_data\Landsberg\BaseImage.tif"

new = PatchCreator(filename)
new.print_filename()


# data = xr.open_rasterio(filename, chunks={"band": 3, "x": 256, "y": 256})
# print(data)

# Create patches and write into new files

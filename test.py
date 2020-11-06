from create_patches import PatchCreator

# Read file as xarray in chunks of 3x256x256
filename = r"C:\Users\Lisapisa\Documents\Master\Masterthesis\original_data\Landsberg\BaseImage.tif"

new = PatchCreator(filename)
new.print_info()

# Create patches and write into new files
new.create_patches()

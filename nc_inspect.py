import xarray as xr

# Example file path for an ensemble member
example_file = "/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/GEFS/Temp/20240816_00/01/Daily/2024230.nc"

# Open the dataset
data = xr.open_dataset(example_file)

# Print all variable names in the dataset
print(data.variables)
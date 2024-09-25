import xarray as xr

# Example file path for an ensemble member
example_file = "mnt\datawaha\hyex\beckhe\DATA_PROCESSED\ECMWF_IFS_open_ensemble_forecasts\LWd\20240816_00\002\Daily\2024236.nc"

# Open the dataset
data = xr.open_dataset(example_file)

# Print all variable names in the dataset
print(data.variables)
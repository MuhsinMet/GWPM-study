import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy as np

# Path to your NetCDF file
file_path = "/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ECMWF_AIFS_open_ensemble_forecasts/Temp/20240909_00/001/6hourly/2024260.00.nc"

# Open the NetCDF file
dataset = nc.Dataset(file_path)

# Extract latitude, longitude, and temperature data
lats = dataset.variables['lat'][:]
lons = dataset.variables['lon'][:]
temperature = dataset.variables['air_temperature'][:]  # Assuming temperature is in Kelvin

# Convert temperature to Celsius
temperature_data = temperature[0, :, :] - 273.15

# Basic plot without cartopy
plt.contourf(lons, lats, temperature_data, cmap='coolwarm')
plt.colorbar(label='Temperature in Celsius')
plt.title('Temperature')
plt.show()

import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs

# File path
file_path = file_path = "/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/GEFS/Temp/20240920_00/01/3hourly/2024266.00.nc"

# Open the NetCDF file
dataset = nc.Dataset(file_path)

# Extract variables (you may need to adjust variable names based on your dataset)
lats = dataset.variables['lat'][:]  # Assuming 'latitude' as the variable name
lons = dataset.variables['lon'][:]  # Assuming 'longitude' as the variable name
temperature = dataset.variables['air_temperature'][0, :, :]  # Adjust based on actual variable name and dimensions

# Create a meshgrid for latitude and longitude
lon_grid, lat_grid = np.meshgrid(lons, lats)

# Plotting
plt.figure(figsize=(12, 6))
ax = plt.axes(projection=ccrs.PlateCarree())

# Plot the temperature data
plt.contourf(lon_grid, lat_grid, temperature, 60, transform=ccrs.PlateCarree(), cmap='coolwarm')
plt.colorbar(label='Temperature (Degree Celcius)')

# Adding coastlines and title
ax.coastlines()
plt.title('Global Temperature Visualization')

# Show the plot
plt.show()

# Close the dataset
dataset.close()
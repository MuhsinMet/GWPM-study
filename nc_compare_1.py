import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# File paths templates for GEFS, ICON, and ERA5
gefs_path_template = '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/GEFS/Temp/20240612_00/01/3hourly/2024{day_of_year:03d}.{hour:02d}.nc'
icon_path_template = '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ICON/Temp/20240612_00/3hourly/2024{day_of_year:03d}.{hour:02d}.nc'
era5_path_template = '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ERA5_HRES/Temp/3hourly/2024{day_of_year:03d}.{hour:02d}.nc'

# Mecca coordinates
lat_mecca, lon_mecca = 21.4225, 39.8262

# Start and end time: 03 UTC on June 12 to 12 UTC on June 18 (6 days)
start_time = datetime(2024, 6, 12, 3)
end_time = datetime(2024, 6, 18, 12)
time_step = timedelta(hours=3)

current_time = start_time

gefs_temps = []
icon_temps = []
era5_temps = []
times = []

# Loop through each 3-hour step from June 12 03 UTC to June 18 12 UTC
while current_time <= end_time:
    day_of_year = current_time.timetuple().tm_yday  # Get day of the year
    hour = current_time.hour  # Get hour in UTC
    
    # Generate file names dynamically for GEFS, ICON, and ERA5
    gefs_file = gefs_path_template.format(day_of_year=day_of_year, hour=hour)
    icon_file = icon_path_template.format(day_of_year=day_of_year, hour=hour)
    era5_file = era5_path_template.format(day_of_year=day_of_year, hour=hour)
    
    try:
        # Load the GEFS and ICON data
        gefs_data = xr.open_dataset(gefs_file)
        icon_data = xr.open_dataset(icon_file)
        
        # Extract temperature data for Mecca (GEFS and ICON)
        gefs_temp = gefs_data['air_temperature'].sel(lat=lat_mecca, lon=lon_mecca, method='nearest').values
        icon_temp = icon_data['air_temperature'].sel(lat=lat_mecca, lon=lon_mecca, method='nearest').values
        
        # Load the ERA5 data and extract temperature
        era5_data = xr.open_dataset(era5_file)
        era5_temp = era5_data['air_temperature'].sel(lat=lat_mecca, lon=lon_mecca, method='nearest').values
        
        # Append temperatures to the lists
        gefs_temps.append(gefs_temp)
        icon_temps.append(icon_temp)
        era5_temps.append(era5_temp)
        
        # Append time label
        times.append(current_time.strftime('%Y-%m-%d %H:%M UTC'))
        
    except FileNotFoundError:
        print(f"File not found for {current_time.strftime('%Y-%m-%d %H:%M UTC')}. Skipping...")
    
    # Increment the current time by 3 hours
    current_time += time_step

# Plot the temperature time series
plt.figure(figsize=(10, 6))
plt.plot(times, gefs_temps, label='GEFS', marker='o', color='blue')
plt.plot(times, icon_temps, label='ICON', marker='o', color='green')
plt.plot(times, era5_temps, label='ERA5', marker='o', color='red')
plt.xticks(rotation=45)
plt.title('Temperature Time Series for Mecca (June 12-18, 2024)')
plt.xlabel('Time (UTC)')
plt.ylabel('Temperature (Celsius)')
plt.legend()
plt.tight_layout()
plt.show()

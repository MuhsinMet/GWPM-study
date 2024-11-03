import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# File path templates for different models
ecmwf_aifs_template = "/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ECMWF_AIFS_open_ensemble_forecasts/Temp/{date_str}_00/001/Daily/{day_of_year}.nc"
ecmwf_ifs_template = "/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ECMWF_IFS_open_ensemble_forecasts/Temp/{date_str}_00/001/Daily/{day_of_year}.nc"
gefs_template = "/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/GEFS/Temp/{date_str}_00/01/Daily/{day_of_year}.nc"
icon_template = "/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ICON/Temp/{date_str}_00/Daily/{day_of_year}.nc"
era5_template = "/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ERA5_HRES/Temp/Daily/{day_of_year}.nc"

# Coordinates for Mecca
lat_center, lon_center = 21.4225, 39.8262  
lat_range = np.arange(lat_center - 0.25, lat_center + 0.25, 0.05)
lon_range = np.arange(lon_center - 0.25, lon_center + 0.25, 0.05)

# Date range for the forecast
start_date = datetime(2024, 8, 16)
end_date = datetime(2024, 9, 16)
forecast_horizon = 5  # 5-day forecast

# Initialize lists to store data
dates = []
ecmwf_aifs_forecast = []
ecmwf_ifs_forecast = []
gefs_forecast = []
icon_forecast = []
era5_actual = []

# Helper function to extract and average data over a specified grid area
def get_area_average(data, lat_range, lon_range):
    subset = data.sel(lat=lat_range, lon=lon_range, method='nearest')
    return np.nanmean(subset.values)

# Loop through each day in the specified date range
current_date = start_date
while current_date <= end_date:
    forecast_start_str = current_date.strftime('%Y%m%d')
    forecast_day_of_year = (current_date + timedelta(days=forecast_horizon)).timetuple().tm_yday
    
    # Access the file paths for each model
    ecmwf_aifs_file = ecmwf_aifs_template.format(date_str=forecast_start_str, day_of_year=f"2024{forecast_day_of_year:03d}")
    ecmwf_ifs_file = ecmwf_ifs_template.format(date_str=forecast_start_str, day_of_year=f"2024{forecast_day_of_year:03d}")
    gefs_file = gefs_template.format(date_str=forecast_start_str, day_of_year=f"2024{forecast_day_of_year:03d}")
    icon_file = icon_template.format(date_str=forecast_start_str, day_of_year=f"2024{forecast_day_of_year:03d}")
    era5_file = era5_template.format(day_of_year=f"2024{forecast_day_of_year:03d}")
    
    try:
        # ECMWF AIFS
        aifs_data = xr.open_dataset(ecmwf_aifs_file)
        temp_aifs = get_area_average(aifs_data['air_temperature'], lat_range, lon_range)
        ecmwf_aifs_forecast.append(temp_aifs if not np.isnan(temp_aifs) else np.nan)

        # ECMWF IFS
        ifs_data = xr.open_dataset(ecmwf_ifs_file)
        temp_ifs = get_area_average(ifs_data['air_temperature'], lat_range, lon_range)
        ecmwf_ifs_forecast.append(temp_ifs if not np.isnan(temp_ifs) else np.nan)

        # GEFS
        gefs_data = xr.open_dataset(gefs_file)
        temp_gefs = get_area_average(gefs_data['air_temperature'], lat_range, lon_range)
        gefs_forecast.append(temp_gefs if not np.isnan(temp_gefs) else np.nan)

        # ICON
        icon_data = xr.open_dataset(icon_file)
        temp_icon = get_area_average(icon_data['air_temperature'], lat_range, lon_range)
        icon_forecast.append(temp_icon if not np.isnan(temp_icon) else np.nan)
        
        # ERA5
        era5_data = xr.open_dataset(era5_file)
        temp_era5 = get_area_average(era5_data['air_temperature'], lat_range, lon_range)
        era5_actual.append(temp_era5 if not np.isnan(temp_era5) else np.nan)

        # Append the current date to the list
        dates.append(current_date + timedelta(days=forecast_horizon))

    except (FileNotFoundError, KeyError, ValueError):
        print(f"Data issue for {current_date.strftime('%Y-%m-%d')} at 5-day forecast horizon")
        # Append NaN for missing data to maintain list consistency
        ecmwf_aifs_forecast.append(np.nan)
        ecmwf_ifs_forecast.append(np.nan)
        gefs_forecast.append(np.nan)
        icon_forecast.append(np.nan)
        era5_actual.append(np.nan)
        dates.append(current_date + timedelta(days=forecast_horizon))
    
    # Move to the next day
    current_date += timedelta(days=1)

# Ensure all lists are of the same length as 'dates'
min_length = len(dates)
ecmwf_aifs_forecast = ecmwf_aifs_forecast[:min_length]
ecmwf_ifs_forecast = ecmwf_ifs_forecast[:min_length]
gefs_forecast = gefs_forecast[:min_length]
icon_forecast = icon_forecast[:min_length]
era5_actual = era5_actual[:min_length]

# Plot the forecasts
plt.figure(figsize=(14, 7))

# Plot each model's forecast
plt.plot(dates, ecmwf_aifs_forecast, label='ECMWF AIFS', linestyle='-', color='blue')
plt.plot(dates, ecmwf_ifs_forecast, label='ECMWF IFS', linestyle='-', color='green')
plt.plot(dates, gefs_forecast, label='GEFS', linestyle='-', color='orange')
plt.plot(dates, icon_forecast, label='ICON', linestyle='-', color='purple')

# Plot ERA5 with a thicker, bolder line
plt.plot(dates, era5_actual, label='ERA5', linestyle='-', color='red', linewidth=2.5)

# Add labels, title, and legend
plt.title('5-Day Forecast Comparison Across Different Models (Mecca, Averaged Area)')
plt.xlabel('Date')
plt.ylabel('Temperature (Celsius)')
plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='medium')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

# File path template for ECMWF IFS ensemble members' daily temperature forecasts
ensemble_temp_path_template = '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ECMWF_IFS_open_ensemble_forecasts/Temp/20240917_00/{ensemble:03d}/Daily/2024{day_of_year:03d}.nc'

# Mumbai coordinates (change if necessary)
lat_mumbai, lon_mumbai = 19.0760, 72.8777

# Forecast days (1st day to 15th day)
forecast_days = range(1, 16)

# Initialize lists to store the forecast data for each ensemble member
ensemble_temp_forecasts = []
times = [f'Day {day}' for day in forecast_days]

# Loop through each ensemble member (1 to 10)
for ensemble in range(1, 11):
    member_forecasts = []
    
    # Loop through each forecast day (day 1 to day 15)
    for day in forecast_days:
        day_of_year = 261 + day - 1  # Assuming the forecast starts on 2024-09-17 (Julian day 261)
        
        # Generate the file path for the current ensemble member and day
        forecast_file = ensemble_temp_path_template.format(ensemble=ensemble, day_of_year=day_of_year)
        
        try:
            # Load the forecast data
            forecast_data = xr.open_dataset(forecast_file)
            
            # Extract temperature data for Mumbai, ensuring we get a scalar value
            temp_mumbai = forecast_data['air_temperature'].sel(lat=lat_mumbai, lon=lon_mumbai, method='nearest').values
            
            # Handle the case where temp_mumbai might be an array
            if np.isscalar(temp_mumbai):
                member_forecasts.append(temp_mumbai)
            else:
                member_forecasts.append(temp_mumbai.item())  # Convert to a single value if it's a one-element array
        
        except (FileNotFoundError, IndexError, KeyError):
            print(f"File not found or data issue for Ensemble {ensemble}, Day {day}. Skipping...")
            member_forecasts.append(np.nan)  # Use NaN if the file is missing or there's an issue
    
    # Ensure all forecasts have 15 days of data by appending NaNs if needed
    if len(member_forecasts) < 15:
        member_forecasts.extend([np.nan] * (15 - len(member_forecasts)))
        
    # Append the forecasts for this ensemble member
    ensemble_temp_forecasts.append(member_forecasts)

# Convert to a numpy array to handle any potential inconsistencies
ensemble_temp_forecasts = np.array(ensemble_temp_forecasts, dtype=np.float64)

# Plot the temperature forecasts for each ensemble member
plt.figure(figsize=(10, 6))

# Plot each ensemble member's forecast
for i, member_forecasts in enumerate(ensemble_temp_forecasts):
    plt.plot(times, member_forecasts, label=f'Ensemble {i+1}', marker='o', linestyle='--', alpha=0.7)

plt.title('ECMWF IFS Ensemble Temperature Forecasts (15-Day Forecast Horizon)')
plt.xlabel('Forecast Horizon (Days)')
plt.ylabel('Temperature (Celsius)')
plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fontsize='small', ncol=1)  # Set the legend to a single column
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

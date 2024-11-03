import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from config import config, models, reference_data, variables
from datetime import datetime, timedelta
from scipy.stats import pearsonr
import random

# User inputs
start_date_str = '20240816'  # Start date
end_date_str = '20240830'    # End date
param = 'Temp'  # Parameter to analyze ('Temp', 'P', 'RelHum', 'Wind')
reference_choice = 'ERA5'  # Choose between 'ERA5' and 'GDAS'
forecast_horizon = 15  # Set forecast horizon to 15 days
use_random_grid = True  # Set to True if you want to select a random grid point

# Convert start and end dates to datetime objects
start_date = datetime.strptime(start_date_str, "%Y%m%d")
end_date = datetime.strptime(end_date_str, "%Y%m%d")

# Initialize lists to store forecast and actual data over time
forecast_series = {model_name: [] for model_name in models if param in models[model_name]['predictors']}
actual_series = []

# Select a random grid point (if enabled) or define specific lat/lon
lat_index = None
lon_index = None

# Loop over the date range
current_date = start_date
while current_date <= end_date:
    forecast_date_str = current_date.strftime("%Y%m%d")
    print(f"\nAnalyzing forecasts starting from: {forecast_date_str}")
    
    forecast_target_date = current_date + timedelta(days=forecast_horizon)
    target_date_str = forecast_target_date.strftime("%Y%m%d")
    julian_day = forecast_target_date.timetuple().tm_yday
    year_julian_format = forecast_target_date.strftime("%Y") + f"{julian_day:03d}"
    print(f"  Forecast horizon: {forecast_horizon} days ahead (target Julian day: {year_julian_format})")

    # Access paths to forecast data for models for this specific date
    model_paths = {
        model_name: details['file_path'].replace("20240816", forecast_date_str).format(parameter=param).replace("2024230", year_julian_format)
        for model_name, details in models.items() if param in details['predictors']
    }

    # Access path for reference data (ERA5 or GDAS depending on the choice)
    reference_path = reference_data[reference_choice]['file_path'].replace("20240816", target_date_str).format(parameter=param).replace("2024230", year_julian_format)
    reference_variable_name = reference_data[reference_choice]['variable_names'][param]
    
    # Load reference data
    try:
        actual_ds = xr.open_dataset(reference_path)
        actual_temp = actual_ds[reference_variable_name].squeeze()
    except FileNotFoundError:
        print(f"Reference data not found at path: {reference_path}. Skipping this date.")
        current_date += timedelta(days=1)
        continue

    # Select a random grid point for analysis (or specific indices)
    if use_random_grid and lat_index is None and lon_index is None:
        lat_index = random.randint(0, actual_temp.shape[-2] - 1)  # Random lat index
        lon_index = random.randint(0, actual_temp.shape[-1] - 1)  # Random lon index
        print(f"Selected grid point (lat_index, lon_index): ({lat_index}, {lon_index})")

    # Store actual time series data for the chosen grid point
    actual_value = actual_temp.isel(lat=lat_index, lon=lon_index).values
    actual_series.append(actual_value)

    # Process each model's forecast for the current horizon
    for model_name, model_path in model_paths.items():
        print(f"    Processing model: {model_name}")
        
        try:
            model_ds = xr.open_dataset(model_path)
            variable_name = models[model_name]['variable_names'][param]
            forecast_temp = model_ds[variable_name].squeeze()

            if forecast_temp.dims != actual_temp.dims or forecast_temp.shape != actual_temp.shape:
                forecast_temp = forecast_temp.interp_like(actual_temp, method="linear")

            # Store forecast time series data for the chosen grid point
            forecast_value = forecast_temp.isel(lat=lat_index, lon=lon_index).values
            forecast_series[model_name].append(forecast_value)

        except FileNotFoundError:
            print(f"File not found: {model_path} for model '{model_name}' on date {forecast_date_str}.")
            continue
        except KeyError as e:
            print(e)
            continue

    current_date += timedelta(days=1)

# Convert lists to numpy arrays for easier correlation calculation
actual_series_np = np.array(actual_series)

# Calculate temporal correlation over time for each model
correlation_results = {}
for model_name, forecast_values in forecast_series.items():
    if len(forecast_values) > 0:
        forecast_series_np = np.array(forecast_values)
        # Calculate Pearson correlation between forecast and actual values
        corr, _ = pearsonr(forecast_series_np, actual_series_np)
        correlation_results[model_name] = corr

# Plot temporal correlation for each model
plt.figure(figsize=(10, 6))
models_to_plot = list(correlation_results.keys())
correlation_values = [correlation_results[model] for model in models_to_plot]

plt.bar(models_to_plot, correlation_values, color=['red', 'green', 'blue', 'orange'])
plt.title(f"Temporal Correlation Over 15 Days for a Single Grid Point\nParameter: **{param}** | Date Range: {start_date_str} to {end_date_str}", fontsize=14)
plt.xlabel('Models', fontsize=12)
plt.ylabel('Temporal Correlation', fontsize=12)

# Add correlation values on top of the bars
for i, corr in enumerate(correlation_values):
    plt.text(i, corr, f'{corr:.3f}', ha='center', va='bottom', fontsize=12)

plt.tight_layout()
plt.savefig(f'Temporal_Correlation_Single_Grid_{param}_{start_date_str}_to_{end_date_str}.png')
plt.show()

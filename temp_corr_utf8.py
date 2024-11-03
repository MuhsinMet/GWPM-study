# -*- coding: utf-8 -*-
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from config import models, reference_data, variables
from datetime import datetime, timedelta

# User inputs
start_date_str = '20240816'  # Start date
end_date_str = '20240818'    # End date (You can adjust this date range)
param = 'Temp'  # Parameter to analyze ('Temp', 'P', 'RelHum', 'Wind')

# Set the grid point (central latitude and longitude) and range for area averaging
latitude = 40.0  # Example central latitude (adjust as needed)
longitude = -100.0  # Example central longitude (adjust as needed)
lat_range = 1.0  # Range around the central latitude
lon_range = 1.0  # Range around the central longitude

# Convert start and end dates to datetime objects
start_date = datetime.strptime(start_date_str, "%Y%m%d")
end_date = datetime.strptime(end_date_str, "%Y%m%d")
forecast_horizons = list(range(1, 16))  # Forecast horizons from 1 to 15 days

# Prepare dictionary to store temporal correlations for each model
temporal_correlation = {model_name: [] for model_name in models.keys() if param in models[model_name]['predictors']}

# Loop over forecast horizons
for horizon in forecast_horizons:
    forecast_target_date = start_date + timedelta(days=horizon)
    julian_day = forecast_target_date.timetuple().tm_yday
    year_julian_format = forecast_target_date.strftime("%Y") + f"{julian_day:03d}"

    # Load reference data (ERA5 or GDAS)
    reference_dataset_name = variables[param]['reference_dataset']
    reference_path = reference_data[reference_dataset_name]['file_path'].replace("20240816", start_date_str).format(parameter=param).replace("2024230", year_julian_format)
    reference_variable_name = reference_data[reference_dataset_name]['variable_names'][param]
    
    print(f"\nProcessing horizon {horizon} (Julian day: {year_julian_format})")

    try:
        # Select data over a lat/lon range (average over the area)
        actual_ds = xr.open_dataset(reference_path)
        actual_temp = actual_ds[reference_variable_name].sel(
            lat=slice(latitude - lat_range, latitude + lat_range),
            lon=slice(longitude - lon_range, longitude + lon_range)
        ).mean(dim=['lat', 'lon']).squeeze()
        print(f"Reference data loaded for horizon {horizon}.")
    except FileNotFoundError:
        print(f"Reference data not found for horizon {horizon}.")
        continue

    # Process each model's forecast
    for model_name, details in models.items():
        if param not in details['predictors']:
            continue

        model_path = details['file_path'].replace("20240816", start_date_str).format(parameter=param).replace("2024230", year_julian_format)
        try:
            # Select data over a lat/lon range (average over the area)
            model_ds = xr.open_dataset(model_path)
            variable_name = models[model_name]['variable_names'][param]
            forecast_temp = model_ds[variable_name].sel(
                lat=slice(latitude - lat_range, latitude + lat_range),
                lon=slice(longitude - lon_range, longitude + lon_range)
            ).mean(dim=['lat', 'lon']).squeeze()

            if forecast_temp.shape != actual_temp.shape:
                forecast_temp = forecast_temp.interp_like(actual_temp, method='linear')

            # Check for valid data points
            valid_mask = np.isfinite(forecast_temp.values) & np.isfinite(actual_temp.values)
            if np.sum(valid_mask) >= 2:  # Ensure there are at least 2 valid data points
                corr, _ = pearsonr(forecast_temp.values[valid_mask], actual_temp.values[valid_mask])
                temporal_correlation[model_name].append(corr)
                print(f"Correlation calculated for {model_name}: {corr:.3f}")
            else:
                print(f"Not enough valid data points for {model_name} on horizon {horizon}.")
                temporal_correlation[model_name].append(np.nan)  # Not enough valid data points, set as NaN

        except FileNotFoundError:
            print(f"File not found: {model_path} for model '{model_name}' on horizon {horizon}.")
            temporal_correlation[model_name].append(np.nan)
            continue

# Check if any model has valid data
has_valid_data = any(np.sum(np.isfinite(temporal_correlation[model])) > 0 for model in temporal_correlation)

if has_valid_data:
    # Plot the temporal correlation for the specified grid
    plt.figure(figsize=(10, 6))
    for model_name, correlations in temporal_correlation.items():
        if len(correlations) > 0 and not np.all(np.isnan(correlations)):  # Plot only if there are valid correlations
            plt.plot(forecast_horizons, correlations, marker='o', label=model_name)

    plt.title(f"Temporal Correlation for {param} at Grid Point (Lat: {latitude}, Lon: {longitude}, Range: ±{lat_range}°)\nOver 15 Days of Forecast Horizon")
    plt.xlabel('Forecast Horizon (Days)')
    plt.ylabel('Temporal Correlation')
    plt.ylim(0, 1.1)  # Correlation ranges from 0 to 1
    plt.legend(title="Models")
    plt.grid(True)

    # Save the plot as a PNG file
    plt.savefig(f'Temporal_Correlation_{param}_{latitude}_{longitude}_Range_{lat_range}.png', dpi=300)
    plt.show()
else:
    print("No valid data for any model to plot temporal correlations.")

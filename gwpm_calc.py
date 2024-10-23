# gwpm_calc.py

import xarray as xr
import numpy as np
from config import models, reference_data, variables  # Import variables from config file
from datetime import datetime, timedelta
from scipy.stats import pearsonr 
import os

# User inputs
start_date_str = '20240816'  # Start date
end_date_str = '20240819'    # End date
param = 'Temp'  # Set this to the parameter you want to analyze ('Temp', 'P', 'RelHum', 'Wind')

# Convert start and end dates to datetime objects
start_date = datetime.strptime(start_date_str, "%Y%m%d")
end_date = datetime.strptime(end_date_str, "%Y%m%d")

forecast_horizons = list(range(1, 15))  # Forecast horizons from 1 to 15 days

# Initialize dictionaries to store aggregated RMSE and correlation values for each model and horizon
rmse_aggregated = {horizon: {model_name: 0 for model_name in models.keys() if param in models[model_name]['predictors']} for horizon in forecast_horizons}
correlation_aggregated = {horizon: {model_name: 0 for model_name in models.keys() if param in models[model_name]['predictors']} for horizon in forecast_horizons}
forecasts_count = {horizon: 0 for horizon in forecast_horizons}  # Track the number of forecasts processed for each horizon

# Loop over the date range
current_date = start_date
while current_date <= end_date:
    forecast_date_str = current_date.strftime("%Y%m%d")
    print(f"\nAnalyzing forecasts starting from: {forecast_date_str}")
    
    for horizon in forecast_horizons:
        forecast_target_date = current_date + timedelta(days=horizon)
        target_date_str = forecast_target_date.strftime("%Y%m%d")
        julian_day = forecast_target_date.timetuple().tm_yday  # Get the Julian day
        year_julian_format = forecast_target_date.strftime("%Y") + f"{julian_day:03d}"  # Format as YYYYJJJ
        print(f"  Forecast horizon: {horizon} days ahead (target Julian day: {year_julian_format})")

        # Access paths to forecast data for models for this specific date
        model_paths = {
            model_name: details['file_path'].replace("20240816", forecast_date_str).format(parameter=param).replace("2024230", year_julian_format)
            for model_name, details in models.items() if param in details['predictors']
        }

        # Access path for reference data (ERA5 or MSWEP depending on the parameter) for the target date
        reference_dataset_name = variables[param]['reference_dataset']
        if reference_dataset_name == 'MSWEP':
            # MSWEP path for precipitation
            reference_path = reference_data[reference_dataset_name]['file_path'].replace("{file_name}", year_julian_format)
        else:
            reference_path = reference_data[reference_dataset_name]['file_path'].replace("20240816", target_date_str).format(parameter=param).replace("2024230", year_julian_format)
        
        reference_variable_name = reference_data[reference_dataset_name]['variable_names'][param]
        
        # Load reference data
        try:
            actual_ds = xr.open_dataset(reference_path)
            actual_temp = actual_ds[reference_variable_name].squeeze()  # Use the correct variable name
        except FileNotFoundError:
            print(f"Reference data not found at path: {reference_path}. Skipping this date.")
            continue
        
        # Process each model's forecast for the current horizon
        for model_name, model_path in model_paths.items():
            print(f"    Processing model: {model_name}")
            
            try:
                model_ds = xr.open_dataset(model_path)
                variable_name = models[model_name]['variable_names'][param]
                forecast_temp = model_ds[variable_name].squeeze()

                if forecast_temp.dims != actual_temp.dims or forecast_temp.shape != actual_temp.shape:
                    forecast_temp = forecast_temp.interp_like(actual_temp, method="linear")

                # Calculate RMSE
                rmse = np.sqrt(((forecast_temp - actual_temp) ** 2).mean())
                rmse_aggregated[horizon][model_name] += rmse

                # Flatten the arrays for correlation calculation
                forecast_temp_flat = forecast_temp.values.flatten()
                actual_temp_flat = actual_temp.values.flatten()

                # Remove NaN and inf values
                valid_indices = np.isfinite(forecast_temp_flat) & np.isfinite(actual_temp_flat)
                forecast_temp_flat = forecast_temp_flat[valid_indices]
                actual_temp_flat = actual_temp_flat[valid_indices]

                if len(forecast_temp_flat) > 0 and len(actual_temp_flat) > 0:  # Ensure there's valid data
                    # Calculate Temporal Correlation
                    corr, _ = pearsonr(forecast_temp_flat, actual_temp_flat)
                    correlation_aggregated[horizon][model_name] += corr
                
            except FileNotFoundError:
                print(f"File not found: {model_path} for model '{model_name}' on date {forecast_date_str}.")
                continue
            except KeyError as e:
                print(e)
                continue
        
        forecasts_count[horizon] += 1
    
    # Move to the next forecast date
    current_date += timedelta(days=1)

# Save results to a .npz file
output_file = f'forecast_analysis_{param}_{start_date_str}_to_{end_date_str}.npz'
np.savez(output_file, rmse_aggregated=rmse_aggregated, correlation_aggregated=correlation_aggregated, forecasts_count=forecasts_count)

print(f"\nCalculation complete. Results saved to {output_file}")

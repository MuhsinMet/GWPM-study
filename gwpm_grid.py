import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from config import models, reference_data, variables  # Import necessary config data
from datetime import datetime, timedelta

# User inputs
lat_range = (35, 36)  # Example: latitude range (35 to 36)
lon_range = (140, 141)  # Example: longitude range (140 to 141)
param = 'Temp'  # Parameter to analyze
start_date_str = '20240815'  # Start date
end_date_str = '20240820'    # End date
reference_dataset = 'ERA5'  # Reference dataset: 'ERA5' or 'GDAS'

# Convert start and end dates to datetime objects
start_date = datetime.strptime(start_date_str, "%Y%m%d")
end_date = datetime.strptime(end_date_str, "%Y%m%d")

forecast_horizons = list(range(1, 16))  # Forecast horizons from 1 to 15 days

# Initialize dictionaries for RMSE and correlation calculations for the grid
rmse_grid = {horizon: {model_name: [] for model_name in models.keys() if param in models[model_name]['predictors']} for horizon in forecast_horizons}
correlation_grid = {horizon: {model_name: [] for model_name in models.keys() if param in models[model_name]['predictors']} for horizon in forecast_horizons}

# Loop over date range for analysis
current_date = start_date
while current_date <= end_date:
    forecast_date_str = current_date.strftime("%Y%m%d")
    print(f"\nAnalyzing forecasts starting from: {forecast_date_str}")
    
    for horizon in forecast_horizons:
        forecast_target_date = current_date + timedelta(days=horizon)
        target_date_str = forecast_target_date.strftime("%Y%m%d")
        julian_day = forecast_target_date.timetuple().tm_yday  # Julian day
        year_julian_format = forecast_target_date.strftime("%Y") + f"{julian_day:03d}"
        
        print(f"  Forecast horizon: {horizon} days ahead (target Julian day: {year_julian_format})")

        # Access model paths for the current horizon and date
        model_paths = {
            model_name: details['file_path'].replace("20240816", forecast_date_str).format(parameter=param).replace("2024230", year_julian_format)
            for model_name, details in models.items() if param in details['predictors']
        }

        # Load reference data
        reference_path = reference_data[reference_dataset]['file_path'].replace("20240816", target_date_str).format(parameter=param).replace("2024230", year_julian_format)
        reference_variable_name = reference_data[reference_dataset]['variable_names'][param]
        
        try:
            actual_ds = xr.open_dataset(reference_path)
            actual_temp = actual_ds[reference_variable_name].sel(lat=slice(*lat_range), lon=slice(*lon_range)).mean(dim=['lat', 'lon']).squeeze()
        except FileNotFoundError:
            print(f"Reference data not found at path: {reference_path}. Skipping this date.")
            continue

        # Process each model for the current horizon
        for model_name, model_path in model_paths.items():
            print(f"    Processing model: {model_name}")
            try:
                model_ds = xr.open_dataset(model_path)
                variable_name = models[model_name]['variable_names'][param]
                forecast_temp = model_ds[variable_name].sel(lat=slice(*lat_range), lon=slice(*lon_range)).mean(dim=['lat', 'lon']).squeeze()

                if forecast_temp.dims != actual_temp.dims or forecast_temp.shape != actual_temp.shape:
                    forecast_temp = forecast_temp.interp_like(actual_temp, method="linear")

                # Calculate RMSE
                rmse = np.sqrt(((forecast_temp - actual_temp) ** 2).mean().item())
                rmse_grid[horizon][model_name].append(rmse)

                # Calculate correlation
                forecast_temp_flat = forecast_temp.values.flatten()
                actual_temp_flat = actual_temp.values.flatten()
                valid_indices = np.isfinite(forecast_temp_flat) & np.isfinite(actual_temp_flat)
                forecast_temp_flat = forecast_temp_flat[valid_indices]
                actual_temp_flat = actual_temp_flat[valid_indices]
                
                if len(forecast_temp_flat) > 0 and len(actual_temp_flat) > 0:
                    corr = np.corrcoef(forecast_temp_flat, actual_temp_flat)[0, 1]
                    correlation_grid[horizon][model_name].append(corr)

            except FileNotFoundError:
                print(f"File not found: {model_path} for model '{model_name}' on date {forecast_date_str}.")
                continue

        forecasts_count = len(rmse_grid[horizon][model_name])  # Track how many forecasts were processed

    current_date += timedelta(days=1)

# Average the RMSE and Correlation over the time range for each horizon
average_rmse = {horizon: {model: np.mean(rmses) for model, rmses in models.items()} for horizon, models in rmse_grid.items()}
average_correlation = {horizon: {model: np.mean(corrs) for model, corrs in models.items()} for horizon, models in correlation_grid.items()}

# Plotting
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

# Set positions and width for the bars
x_labels = [f'{h}-Day' for h in forecast_horizons]
x = np.arange(len(x_labels))
width = 0.2  # Width of each bar

# Plot RMSE
for idx, model_name in enumerate([m for m in models.keys() if param in models[m]['predictors']]):
    rmse_values = [average_rmse[horizon][model_name] for horizon in forecast_horizons]
    rmse_values = [rmse if rmse is not None and np.isfinite(rmse) else 0 for rmse in rmse_values]
    ax1.bar(x + idx * width, rmse_values, width, label=model_name)
    for i, rmse in enumerate(rmse_values):
        if rmse > 0:  # Skip if RMSE is 0 (indicative of no data or issue)
            ax1.text(x[i] + idx * width, rmse, f'{rmse:.3f}', ha='center', va='bottom')

# Plot Temporal Correlation
for idx, model_name in enumerate([m for m in models.keys() if param in models[m]['predictors']]):
    corr_values = [average_correlation[horizon][model_name] for horizon in forecast_horizons]
    corr_values = [corr if corr is not None and np.isfinite(corr) else 0 for corr in corr_values]
    ax2.bar(x + idx * width, corr_values, width, label=model_name)
    for i, corr in enumerate(corr_values):
        if corr > 0:
            ax2.text(x[i] + idx * width, corr, f'{corr:.3f}', ha='center', va='bottom')


# Customize RMSE plot
ax1.set_title(f"RMSE for {param} at ({lat_range}, {lon_range})\n{start_date_str} to {end_date_str}")
ax1.set_xlabel('Forecast Horizon')
ax1.set_ylabel('RMSE')
ax1.set_xticks(x + width * 1.5)
ax1.set_xticklabels(x_labels)
ax1.legend(title='Models')

# Customize Correlation plot
ax2.set_title(f"Temporal Correlation for {param} at ({lat_range}, {lon_range})\n{start_date_str} to {end_date_str}")
ax2.set_xlabel('Forecast Horizon')
ax2.set_ylabel('Correlation')
ax2.set_xticks(x + width * 1.5)
ax2.set_xticklabels(x_labels)
ax2.legend(title='Models')

plt.tight_layout()

# Save and show plot
plt.savefig(f'Grid_Analysis_{param}_{start_date_str}_to_{end_date_str}.png')
plt.show()

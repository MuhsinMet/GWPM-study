import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from config import config, models, reference_data, variables  # Import variables from config file
from datetime import datetime, timedelta

# User inputs
start_date_str = '20240816'  # Start date
end_date_str = '20240819'    # End date
param = 'P'  # Set this to the parameter you want to analyze ('Temp', 'P', 'RelHum', 'Wind')

# Convert start and end dates to datetime objects
start_date = datetime.strptime(start_date_str, "%Y%m%d")
end_date = datetime.strptime(end_date_str, "%Y%m%d")

forecast_horizons = [3, 5, 7]  # Forecast horizons in days

# Initialize a dictionary to store aggregated RMSE values for each model and horizon
rmse_aggregated = {horizon: {model_name: 0 for model_name in models.keys()} for horizon in forecast_horizons}
forecasts_count = {horizon: 0 for horizon in forecast_horizons}  # Track the number of forecasts processed for each horizon

# Loop over the date range
current_date = start_date
while current_date <= end_date:
    forecast_date_str = current_date.strftime("%Y%m%d")
    print(f"\nAnalyzing forecasts starting from: {forecast_date_str}")
    
    for horizon in forecast_horizons:
        # Adjust the target date to correctly reflect the forecast horizon relative to the forecast start date
        forecast_target_date = current_date + timedelta(days=horizon)
        target_date_str = forecast_target_date.strftime("%Y%m%d")
        julian_day = forecast_target_date.timetuple().tm_yday  # Get the Julian day
        year_julian_format = forecast_target_date.strftime("%Y") + f"{julian_day:03d}"  # Format as YYYYJJJ
        print(f"  Forecast horizon: {horizon} days ahead (target Julian day: {year_julian_format})")
        
        # Access paths to forecast data for different models for this specific date
        model_paths = {
            model_name: details['file_path'].replace("20240816", forecast_date_str).format(parameter=param).replace("2024230", year_julian_format)
            for model_name, details in models.items()
        }

        # Access path for reference data (ERA5 or MSWEP depending on the parameter) for the target date
        reference_dataset_name = variables[param]['reference_dataset']
        
        # If the reference dataset is MSWEP, construct the file name accordingly
        if reference_dataset_name == 'MSWEP':
            reference_path = reference_data[reference_dataset_name]['file_path'].replace("{file_name}", year_julian_format)
        else:
            reference_path = reference_data[reference_dataset_name]['file_path'].replace("20240816", target_date_str).format(parameter=param).replace("2024230", year_julian_format)
        
        reference_variable_name = reference_data[reference_dataset_name]['variable_names'][param]

        
        # Load reference data
        try:
            actual_ds = xr.open_dataset(reference_path)
            actual_temp = actual_ds[reference_variable_name].squeeze()  # Use the correct temperature variable name
        except FileNotFoundError:
            print(f"Reference data not found at path: {reference_path}. Skipping this date.")
            continue
        
        # Process each model's forecast for the current horizon
        for model_name, model_path in model_paths.items():
            print(f"    Processing model: {model_name}")
            
            try:
                # Load model forecast data
                model_ds = xr.open_dataset(model_path)
                
                # Access the specific variable name from config
                variable_name = models[model_name]['variable_names'][param]
                if variable_name in model_ds:
                    forecast_temp = model_ds[variable_name].squeeze()
                else:
                    raise KeyError(f"Variable '{variable_name}' not found in the dataset for model '{model_name}'.")

                # Ensure dimensions match by regridding
                if forecast_temp.dims != actual_temp.dims or forecast_temp.shape != actual_temp.shape:
                    forecast_temp = forecast_temp.interp_like(actual_temp, method="linear")

                # Calculate RMSE for this forecast
                rmse = np.sqrt(((forecast_temp - actual_temp) ** 2).mean())
                rmse_aggregated[horizon][model_name] += rmse
                
            except FileNotFoundError:
                print(f"File not found: {model_path} for model '{model_name}' on date {forecast_date_str}.")
                continue
            except KeyError as e:
                print(e)
                continue
        
        forecasts_count[horizon] += 1  # Increment the count of forecasts processed for this horizon
    
    # Move to the next forecast date
    current_date += timedelta(days=1)

# Calculate the average RMSE for each model and horizon
average_rmse = {
    horizon: {model_name: (rmse_aggregated[horizon][model_name] / forecasts_count[horizon]) if forecasts_count[horizon] > 0 else None 
              for model_name in rmse_aggregated[horizon]}
    for horizon in forecast_horizons
}

# Create a bar plot for RMSE values for each model across all forecast horizons
fig, ax = plt.subplots(figsize=(14, 8))

# Set positions and width for the bars
x_labels = ['3-Day', '5-Day', '7-Day']
x = np.arange(len(x_labels))
width = 0.2  # Width of each bar

# Plot bars for each model
for idx, model_name in enumerate(models.keys()):
    rmse_values = [average_rmse[horizon][model_name] for horizon in forecast_horizons]
    ax.bar(x + idx * width, rmse_values, width, label=model_name)

    # Add RMSE values on top of each bar
    for i, rmse in enumerate(rmse_values):
        if rmse is not None:  # Only add text if rmse is not None
            ax.text(x[i] + idx * width, rmse + 0.005, f'{rmse:.3f}', ha='center', va='bottom')

# Customize plot
ax.set_title(f"Average RMSE Across Forecast Horizons (Parameter: {param})\nDate Range: {start_date_str} to {end_date_str}")
ax.set_xlabel('Forecast Horizon')
ax.set_ylabel('Average RMSE')
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(x_labels)
ax.legend(title='Models')
plt.tight_layout()

# Save the plot as a PNG file
plt.savefig(f'Combined_RMSE_Bar_Chart_{param}_{start_date_str}_to_{end_date_str}.png')
plt.show()

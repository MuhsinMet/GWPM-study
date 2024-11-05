import xarray as xr
import numpy as np
from config import models, reference_data, variables, start_date_str, end_date_str, param, reference_choice
from datetime import datetime, timedelta
from scipy.stats import pearsonr

# User inputs
start_date = datetime.strptime(start_date_str, "%Y%m%d")
end_date = datetime.strptime(end_date_str, "%Y%m%d")

forecast_horizons = list(range(1, 15))

# Initialize dictionaries for RMSE and correlation
rmse_aggregated = {horizon: {model_name: 0 for model_name in models.keys() if param in models[model_name]['predictors']} for horizon in forecast_horizons}
correlation_aggregated = {horizon: {model_name: [] for model_name in models.keys() if param in models[model_name]['predictors']} for horizon in forecast_horizons}
forecasts_count = {horizon: 0 for horizon in forecast_horizons}

# Loop over the date range
current_date = start_date
while current_date <= end_date:
    forecast_date_str = current_date.strftime("%Y%m%d")
    print(f"\nAnalyzing forecasts starting from: {forecast_date_str}")
    
    for horizon in forecast_horizons:
        forecast_target_date = current_date + timedelta(days=horizon)
        target_date_str = forecast_target_date.strftime("%Y%m%d")
        julian_day = forecast_target_date.timetuple().tm_yday
        year_julian_format = forecast_target_date.strftime("%Y") + f"{julian_day:03d}"
        
        model_paths = {
            model_name: details['file_path'].replace("20240816", forecast_date_str).format(parameter=param).replace("2024230", year_julian_format)
            for model_name, details in models.items() if param in details['predictors']
        }

        reference_dataset_name = reference_choice
        reference_path = reference_data[reference_dataset_name]['file_path'].replace("20240816", target_date_str).format(parameter=param).replace("2024230", year_julian_format)
        reference_variable_name = reference_data[reference_dataset_name]['variable_names'][param]
        
        if reference_dataset_name == 'MSWEP':
            reference_path = reference_data[reference_dataset_name]['file_path'].replace("{file_name}", year_julian_format)
        else:
            reference_path = reference_data[reference_dataset_name]['file_path'].replace("20240816", target_date_str).format(parameter=param).replace("2024230", year_julian_format)
        
        reference_variable_name = reference_data[reference_dataset_name]['variable_names'][param]
        
        try:
            actual_ds = xr.open_dataset(reference_path)
            actual_temp = actual_ds[reference_variable_name].squeeze()
        except FileNotFoundError:
            print(f"Reference data not found at path: {reference_path}. Skipping this date.")
            continue
        
        for model_name, model_path in model_paths.items():
            print(f"    Processing model: {model_name}")
            try:
                model_ds = xr.open_dataset(model_path)
                variable_name = models[model_name]['variable_names'][param]
                forecast_temp = model_ds[variable_name].squeeze()

                if forecast_temp.dims != actual_temp.dims or forecast_temp.shape != actual_temp.shape:
                    forecast_temp = forecast_temp.interp_like(actual_temp, method="linear")

                rmse = np.sqrt(((forecast_temp - actual_temp) ** 2).mean())
                rmse_aggregated[horizon][model_name] += rmse

                forecast_temp_flat = forecast_temp.values.flatten()
                actual_temp_flat = actual_temp.values.flatten()
                valid_indices = np.isfinite(forecast_temp_flat) & np.isfinite(actual_temp_flat)
                forecast_temp_flat = forecast_temp_flat[valid_indices]
                actual_temp_flat = actual_temp_flat[valid_indices]

                if len(forecast_temp_flat) > 0 and len(actual_temp_flat) > 0:
                    corr, _ = pearsonr(forecast_temp_flat, actual_temp_flat)
                    correlation_aggregated[horizon][model_name].append(corr)

            except FileNotFoundError:
                print(f"File not found: {model_path} for model '{model_name}' on date {forecast_date_str}.")
                continue

        forecasts_count[horizon] += 1
    current_date += timedelta(days=1)

# Average correlation values after the loop
for horizon in forecast_horizons:
    for model_name in correlation_aggregated[horizon]:
        if correlation_aggregated[horizon][model_name]:
            correlation_aggregated[horizon][model_name] = np.mean(correlation_aggregated[horizon][model_name])
        else:
            correlation_aggregated[horizon][model_name] = None

output_file = f"forecast_analysis_{param}_{start_date_str}_to_{end_date_str}.npz"
np.savez(output_file, rmse_aggregated=rmse_aggregated, 
                      correlation_aggregated=correlation_aggregated, 
                      forecasts_count=forecasts_count)
print(f"Calculation complete. Results saved to {output_file}")

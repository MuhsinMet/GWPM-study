# gwpm_plot.py
import subprocess
import os
import numpy as np
import matplotlib.pyplot as plt
from config import models  # Import model configurations

# User inputs
param = 'Temp'
start_date_str = '20240816'
end_date_str = '20240915'

# Check if the data file exists
data_file = f'forecast_analysis_{param}_{start_date_str}_to_{end_date_str}.npz'
if not os.path.exists(data_file):
    print(f"Data file {data_file} not found. Running calculation script...")
    subprocess.run(["python3", "gwpm_calc.py"])  # Run the calculation script automatically

# Load the saved data
data = np.load(data_file, allow_pickle=True)
rmse_aggregated = data['rmse_aggregated'].item()
correlation_aggregated = data['correlation_aggregated'].item()
forecasts_count = data['forecasts_count'].item()

# Continue with plotting as before...


data = np.load(data_file, allow_pickle=True)
rmse_aggregated = data['rmse_aggregated'].item()
correlation_aggregated = data['correlation_aggregated'].item()
forecasts_count = data['forecasts_count'].item()

forecast_horizons = list(range(1, 15))  # Forecast horizons from 1 to 15 days

# Create side-by-side plots for RMSE and Temporal Correlation
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

# Set positions and width for the bars
x_labels = [f'{h}-Day' for h in forecast_horizons]
x = np.arange(len(x_labels))
width = 0.2  # Width of each bar

# Plot RMSE
for idx, model_name in enumerate([m for m in models.keys() if param in models[m]['predictors']]):
    rmse_values = [rmse_aggregated[horizon][model_name] for horizon in forecast_horizons]
    rmse_values = [rmse for rmse in rmse_values if rmse is not None]  # Filter out None values
    if rmse_values:  # Only plot if there are valid RMSE values
        ax1.bar(x[:len(rmse_values)] + idx * width, rmse_values, width, label=model_name)

        # Add RMSE values on top of each bar
        for i, rmse in enumerate(rmse_values):
            ax1.text(x[i] + idx * width, rmse, f'{rmse:.3f}', ha='center', va='bottom', rotation=90)

# Plot Temporal Correlation
for idx, model_name in enumerate([m for m in models.keys() if param in models[m]['predictors']]):
    corr_values = [correlation_aggregated[horizon][model_name] for horizon in forecast_horizons]
    corr_values = [corr for corr in corr_values if corr is not None and corr > 0]  # Filter out None or zero values
    if corr_values:  # Only plot if there are valid correlation values
        ax2.bar(x[:len(corr_values)] + idx * width, corr_values, width, label=model_name)

        # Add correlation values on top of each bar
        for i, corr in enumerate(corr_values):
            ax2.text(x[i] + idx * width, corr, f'{corr:.3f}', ha='center', va='bottom', rotation=90)

# Customize RMSE plot
ax1.set_title(f"Average RMSE Across Forecast Horizons (Parameter: {param})\nDate Range: {start_date_str} to {end_date_str}")
ax1.set_xlabel('Forecast Horizon')

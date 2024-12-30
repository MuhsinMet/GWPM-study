import os
import numpy as np
import matplotlib.pyplot as plt
from config import models, start_date_str, end_date_str, param, reference_choice, variables  # Import variables explicitly
import subprocess

# Define plot directory
plot_dir = '/mnt/datawaha/hyex/msn/GWPM/plots'
os.makedirs(plot_dir, exist_ok=True)  # Ensure the directory exists

# Load the saved data
data_file = f"forecast_analysis_{param}_{reference_choice}_{start_date_str}_{end_date_str}.npz"

if not os.path.exists(data_file):
    print(f"Data file {data_file} not found. Running calculation script...")
    # Run the calculation script
    result = subprocess.run(['python3', 'gwpm_calc.py'], capture_output=True, text=True)
    print(result.stdout)  # Print the output of the calc script
    
    if not os.path.exists(data_file):
        print("Calculation script failed or data file was not generated.")
        exit(1)

# Load the saved data
data = np.load(data_file, allow_pickle=True)

# Extract the data
rmse_aggregated = data['rmse_aggregated'].item()
correlation_aggregated = data['correlation_aggregated'].item()
forecasts_count = data['forecasts_count'].item()

# Plotting RMSE and Temporal Correlation
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

# Set positions and width for the bars
forecast_horizons = list(rmse_aggregated.keys())
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

# Determine the min and max correlation values for y-axis limits
y_min, y_max = 0, 1
if corr_values:
    min_corr = min(corr_values)
    max_corr = max(corr_values)
    y_min = max(0, min_corr - 0.01)
    y_max = min(1, max_corr + 0.02)

# Customize RMSE plot
units = variables[param]['units']  # Retrieve units for the parameter
ax1.set_title(f"Average RMSE Across Forecast Horizons (Parameter: {param})\nDate Range: {start_date_str} to {end_date_str} in comparison with {reference_choice}")
ax1.set_xlabel('Forecast Horizon')
ax1.set_ylabel(f'Average RMSE ({units})')
ax1.set_xticks(x + width * 1.5)
ax1.set_xticklabels(x_labels)
ax1.legend(title='Models')

# Customize Temporal Correlation plot
ax2.set_title(f"Average Temporal Correlation Across Forecast Horizons (Parameter: {param})\nDate Range: {start_date_str} to {end_date_str} in comparison with {reference_choice}")
ax2.set_ylim([y_min, y_max])
ax2.set_xlabel('Forecast Horizon')
ax2.set_ylabel('Average Temporal Correlation')
ax2.set_xticks(x + width * 1.5)
ax2.set_xticklabels(x_labels)
ax2.legend(title='Models')

plt.tight_layout()

# Save the plot as a PNG file
plot_file = os.path.join(plot_dir, f'{param}_{reference_choice}_{start_date_str}_{end_date_str}_RMSE_Corr.png')
plt.savefig(plot_file)
plt.show()

# Delete the calculation results file
try:
    os.remove(data_file)
    print(f"Deleted calculation results file: {data_file}")
except OSError as e:
    print(f"Error deleting file {data_file}: {e}")

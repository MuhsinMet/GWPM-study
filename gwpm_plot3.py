import numpy as np
import matplotlib.pyplot as plt
from config import models  # Import the models dictionary

# User inputs
param = 'Temp'  # Set this to the parameter you want to analyze (e.g., 'Temp', 'P', 'RelHum', 'Wind')
start_date_str = '20240915'
end_date_str = '20240917'

# Load the saved data
data_file = f"forecast_analysis_{param}_{start_date_str}_to_{end_date_str}.npz"
data = np.load(data_file, allow_pickle=True)

# Extract the data
rmse_aggregated = data['rmse_aggregated'].item()
correlation_aggregated = data['correlation_aggregated'].item()
forecasts_count = data['forecasts_count'].item()

# Now proceed with plotting the RMSE and Temporal Correlation
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

# Customize RMSE plot
ax1.set_title(f"Average RMSE Across Forecast Horizons (Parameter: {param})\nDate Range: {start_date_str} to {end_date_str}")
ax1.set_xlabel('Forecast Horizon')
ax1.set_ylabel('Average RMSE')
ax1.set_xticks(x + width * 1.5)
ax1.set_xticklabels(x_labels)
ax1.legend(title='Models')

# Customize Temporal Correlation plot
ax2.set_title(f"Average Temporal Correlation Across Forecast Horizons (Parameter: {param})\nDate Range: {start_date_str} to {end_date_str}")
ax2.set_xlabel('Forecast Horizon')
ax2.set_ylabel('Average Temporal Correlation')

plt.tight_layout()

# Save the plot as a PNG file
plt.savefig(f'RMSE_and_Correlation_Comparison_{param}_{start_date_str}_to_{end_date_str}.png')
plt.show()

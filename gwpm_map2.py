import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from config import config, models, reference_data  # Import models and reference data from config file

# Extract information from the config file
forecast_dates = config['forecast_dates']
parameters = config['parameters']

# Choose parameter and date to analyze
param = 'Temp'  # This can be looped over to analyze other parameters as needed
forecast_date = forecast_dates[0]  # This can be looped over to analyze other dates

# Access paths to forecast data for different models
model_paths = {model_name: details['file_path'] for model_name, details in models.items()}

# Access path for reference data (ERA5)
reference_path = reference_data['ERA5']['file_path']
reference_variable_name = reference_data['ERA5']['variable_name']

# Load ERA5 data
actual_ds = xr.open_dataset(reference_path)
actual_temp = actual_ds[reference_variable_name].squeeze()  # Use the correct temperature variable name

# Initialize a dictionary to store the absolute error for each model and the actual temperature maps
absolute_errors = {}
temperature_maps = {'ERA5': actual_temp}  # Include ERA5 as the reference

# Process each model
for model_name, model_path in model_paths.items():
    print(f"Processing model: {model_name}")
    
    try:
        # Load model forecast data
        model_ds = xr.open_dataset(model_path)
        
        # Access the specific variable name from config
        variable_name = models[model_name]['variable_name']
        if variable_name in model_ds:
            forecast_temp = model_ds[variable_name].squeeze()
        else:
            raise KeyError(f"Variable '{variable_name}' not found in the dataset for model '{model_name}'.")

        # Check for missing data and fill if necessary
        forecast_temp = forecast_temp.fillna(0)
        actual_temp = actual_temp.fillna(0)

        # Ensure dimensions match by regridding
        if forecast_temp.dims != actual_temp.dims or forecast_temp.shape != actual_temp.shape:
            forecast_temp = forecast_temp.interp_like(actual_temp, method="linear")

        # Store the forecast temperature map
        temperature_maps[model_name] = forecast_temp
        
        # Calculate the absolute error compared to ERA5
        abs_error = np.abs(forecast_temp - actual_temp)
        absolute_errors[model_name] = abs_error
    except FileNotFoundError:
        print(f"File not found: {model_path}")
        continue
    except KeyError as e:
        print(e)
        continue

# Combine the absolute errors into a single xarray Dataset
abs_error_ds = xr.Dataset(absolute_errors)

# Identify the model with the minimum absolute error for each grid point
best_model = abs_error_ds.to_array(dim='model').argmin(dim='model')

# Map model index back to model names
model_indices = list(model_paths.keys())
best_model_names = xr.DataArray(
    np.array(model_indices)[best_model.values],
    dims=best_model.dims,
    coords=best_model.coords
)

# Ensure the data is numeric and handle NaN values
best_model_names = best_model_names.astype(str).fillna("Unknown")

# Encode model names as integers for plotting
model_encoding = {name: idx for idx, name in enumerate(model_indices)}
encoded_best_model = best_model_names.to_series().map(model_encoding).fillna(-1).to_xarray()

# Plot the best model map with a legend
plt.figure(figsize=(14, 7))
cax = encoded_best_model.plot(cmap='tab20', add_colorbar=False)
plt.title(f"Best Performing Model Compared to ERA5 (Temperature, Date: {forecast_date})")
plt.xlabel('Longitude')
plt.ylabel('Latitude')

# Create a legend for the plot
legend_handles = [mpatches.Patch(color=cax.cmap(cax.norm(model_encoding[model])), label=model) for model in model_indices]
plt.legend(handles=legend_handles, loc='lower left', bbox_to_anchor=(1.05, 0), title="Models")

plt.tight_layout()
plt.show()

# Visualize the global temperature maps for all models and ERA5
fig, axes = plt.subplots(nrows=1, ncols=len(models) + 1, figsize=(25, 5), subplot_kw={'projection': None})
fig.suptitle(f'Global Temperature Maps (Parameter: {param}, Date: {forecast_date})')

for ax, (model_name, temp_data) in zip(axes.flatten(), temperature_maps.items()):
    temp_data.plot(ax=ax, cmap='coolwarm', add_colorbar=True, cbar_kwargs={'label': 'Temperature (K)'})
    ax.set_title(model_name)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

plt.tight_layout()
plt.show()
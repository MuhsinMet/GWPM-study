import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from mpl_toolkits.basemap import Basemap
from config import config, models, reference_data, variables
from datetime import datetime, timedelta
from scipy.stats import pearsonr
import matplotlib.patches as mpatches

# User inputs
start_date_str = '20240816'
end_date_str = '20240930'
param = 'Temp'
method = 'RMSE'  # Change to 'Correlation' if using temporal correlation instead

# Convert start and end dates to datetime objects
start_date = datetime.strptime(start_date_str, "%Y%m%d")
end_date = datetime.strptime(end_date_str, "%Y%m%d")

forecast_horizons = list(range(1, 16))  # Forecast horizons from 1 to 15 days

# Prepare a dictionary to store RMSE values per model and per grid cell
grid_rmse = {model_name: None for model_name in models.keys() if param in models[model_name]['predictors']}

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
        print(f"  Forecast horizon: {horizon} days ahead (target Julian day: {year_julian_format})")

        # Access paths to forecast data for models for this specific date
        model_paths = {
            model_name: details['file_path'].replace("20240816", forecast_date_str).format(parameter=param).replace("2024230", year_julian_format)
            for model_name, details in models.items() if param in details['predictors']
        }

        # Access path for reference data for the target date
        reference_dataset_name = variables[param]['reference_dataset']
        if reference_dataset_name == 'MSWEP':
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

                # Calculate RMSE per grid cell
                rmse_grid = np.sqrt((forecast_temp - actual_temp) ** 2)

                # Convert to NumPy arrays for easier manipulation
                rmse_grid_np = rmse_grid.values
                if grid_rmse[model_name] is None:
                    grid_rmse[model_name] = rmse_grid_np
                else:
                    grid_rmse[model_name] += rmse_grid_np

            except FileNotFoundError:
                print(f"File not found: {model_path} for model '{model_name}' on date {forecast_date_str}.")
                continue
            except KeyError as e:
                print(e)
                continue

    current_date += timedelta(days=1)

# Calculate the average RMSE per model per grid cell across the entire period
for model_name in grid_rmse:
    if grid_rmse[model_name] is not None:
        grid_rmse[model_name] /= (end_date - start_date).days

# Convert to NumPy arrays for determining the best model per grid cell
model_names = list(grid_rmse.keys())
best_model = np.full_like(grid_rmse[model_names[0]], -1, dtype=int)  # Initialize with -1
min_rmse = np.full_like(grid_rmse[model_names[0]], np.inf)

for i, model_name in enumerate(model_names):
    model_rmse = grid_rmse[model_name]
    if model_rmse is not None:
        mask = model_rmse < min_rmse
        min_rmse[mask] = model_rmse[mask]
        best_model[mask] = i

# Plot the global map of the best-performing model using Basemap
fig = plt.figure(figsize=(14, 8))
m = Basemap(projection='cyl', resolution='c', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180)
m.drawcoastlines(linewidth=0.8)
m.drawcountries(linewidth=0.5)
m.drawmapboundary(fill_color='aqua')
m.fillcontinents(color='lightgray', lake_color='aqua', zorder=0)

# Plot the data
cmap = ListedColormap(['blue', 'green', 'red', 'orange'])
lon = np.linspace(-180, 180, best_model.shape[1])
lat = np.linspace(-90, 90, best_model.shape[0])
lon, lat = np.meshgrid(lon, lat)
im = m.pcolormesh(lon, lat, best_model, latlon=True, cmap=cmap)

# Add a legend with color blocks and model names
patches = [mpatches.Patch(color=cmap(i), label=model_names[i]) for i in range(len(model_names))]
plt.legend(handles=patches, loc='lower left', title='Models')

# Add labels
plt.title(f"Best Performing Model per Grid Cell for **{param}**\nMethod: {method}\nDate Range: {start_date_str} to {end_date_str}", fontsize=12)
plt.savefig(f'Best_Performing_Model_Map_{param}_{start_date_str}_to_{end_date_str}.png', dpi=300)
plt.show()
import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import json

def load_netcdf_data(file_path, variable_name):
    """
    Load data from a NetCDF file.
    
    Parameters:
    - file_path: str, path to the NetCDF file
    - variable_name: str, name of the variable to extract
    
    Returns:
    - data: xarray.DataArray, extracted data
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    dataset = xr.open_dataset(file_path)
    if variable_name not in dataset:
        raise KeyError(f"Variable '{variable_name}' not found in {file_path}")
    
    data = dataset[variable_name]
    return data.squeeze()  # Remove any singleton dimensions

def calculate_rmse(forecast, actual):
    """
    Calculate the Root Mean Square Error (RMSE) between forecast and actual data.
    
    Parameters:
    - forecast: xarray.DataArray, forecasted values
    - actual: xarray.DataArray, actual values
    
    Returns:
    - rmse: float, calculated RMSE
    """
    rmse = np.sqrt(((forecast - actual) ** 2).mean(dim=['lat', 'lon']))
    return rmse

def plot_global_map(data, title, output_path, cmap='viridis'):
    """
    Plot and save a global map of the data.
    
    Parameters:
    - data: xarray.DataArray, data to plot
    - title: str, title of the plot
    - output_path: str, path to save the plot
    - cmap: str, colormap to use
    """
    plt.figure(figsize=(10, 5))
    data.plot(cmap=cmap)
    plt.title(title)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Plot saved at {output_path}")

def find_best_model(global_abs_errors, models):
    """
    Identify the best performing model at each grid point.
    
    Parameters:
    - global_abs_errors: dict, containing absolute errors for each model
    - models: list of model names
    
    Returns:
    - xarray.DataArray, showing which model performed best at each grid point
    """
    stacked_data = np.stack([global_abs_errors[model] for model in models], axis=0)
    best_model_indices = np.nanargmin(stacked_data, axis=0)
    best_model_data = xr.DataArray(best_model_indices, dims=['lat', 'lon'])
    return best_model_data

def create_output_dir(output_path):
    """
    Create an output directory if it doesn't already exist.
    
    Parameters:
    - output_path: str, path of the directory to create
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"Created directory: {output_path}")

def load_config(config_file_path):
    """
    Load a configuration file.
    
    Parameters:
    - config_file_path: str, path to the configuration file
    
    Returns:
    - config: dict, loaded configuration
    """
    with open(config_file_path, 'r') as file:
        config = json.load(file)
    return config

def update_config(config_file_path, new_data):
    """
    Update the configuration file with new data.
    
    Parameters:
    - config_file_path: str, path to the configuration file
    - new_data: dict, new data to update in the config
    """
    config = load_config(config_file_path)
    config.update(new_data)
    
    with open(config_file_path, 'w') as file:
        json.dump(config, file, indent=4)
    print(f"Updated config file at {config_file_path}")

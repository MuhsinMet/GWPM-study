from datetime import datetime, timedelta
import os
import numpy as np

# Define start and end dates and parameter
start_date_str = '20240815'  # Start date
end_date_str = '20241014'    # End date
param = 'Wind'  # Options: 'Temp', 'P', 'RelHum', 'Wind'
forecast_horizons = list(range(1, 15))  # Forecast horizons from 1 to 15 days
reference_choice = 'GDAS'  # Options: 'ERA5', 'GDAS', 'Station'

config = {
    'dir_data_processed': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/',
    'dir_data_raw': '/mnt/datawaha/hyex/msn/GWPM/DATA_RAW',
    'dir_output': '/mnt/datawaha/hyex/msn/GWPM/OUTPUT',
    'dir_temp': '/tmp',
    'parameters': ['Temp', 'P', 'RelHum', 'Wind'],  # List of parameters
    'forecast_dates': ['20240816_00'],  # Default date
    'dir_station_data': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/station_data'
}

# Data availability constraints
availability = {
    'GEFS': {'max_horizon': 10},
    'ICON': {'max_horizon': 7},
    'ECMWF_IFS': {'max_horizon': 15},
    'ECMWF_AIFS': {'max_horizon': 15, 'available_predictors': ['Temp', 'P', 'Wind']}
}

# Models
models = {
    'GEFS': {
        'predictors': ['Temp', 'P', 'RelHum', 'Wind'],
        'data_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/GEFS',
        'file_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/GEFS/{parameter}/20240816_00/01/Daily/2024230.nc',
        'variable_names': {
            'Temp': 'air_temperature',
            'P': 'precipitation',
            'RelHum': 'relative_humidity',
            'Wind': 'wind_speed'
        }
    },
    'ICON': {
        'predictors': ['Temp', 'P', 'RelHum', 'Wind'],
        'data_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ICON',
        'file_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ICON/{parameter}/20240816_00/Daily/2024230.nc',
        'variable_names': {
            'Temp': 'air_temperature',
            'P': 'precipitation',
            'RelHum': 'relative_humidity',
            'Wind': 'wind_speed'
        }
    },
    'ECMWF_IFS': {
        'predictors': ['Temp', 'P', 'RelHum', 'Wind'],
        'data_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ECMWF_IFS_open_ensemble_forecasts',
        'file_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ECMWF_IFS_open_ensemble_forecasts/{parameter}/20240816_00/001/Daily/2024230.nc',
        'variable_names': {
            'Temp': 'air_temperature',
            'P': 'precipitation',
            'RelHum': 'relative_humidity',
            'Wind': 'wind_speed'
        }
    },
    'ECMWF_AIFS': {
        'predictors': ['Temp', 'P', 'Wind'],
        'data_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ECMWF_AIFS_open_ensemble_forecasts',
        'file_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ECMWF_AIFS_open_ensemble_forecasts/{parameter}/20240816_00/001/Daily/2024230.nc',
        'variable_names': {
            'Temp': 'air_temperature',
            'P': 'precipitation',
            'Wind': 'wind_speed'
        }
    }
}

# Reference datasets (ERA5, GDAS, MSWEP, and now Station data)
reference_data = {
    'ERA5': {
        'data_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ERA5_HRES',
        'file_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ERA5_HRES/{parameter}/Daily/2024230.nc',
        'variable_names': {
            'Temp': 'air_temperature',
            'P': 'precipitation',
            'RelHum': 'relative_humidity',
            'Wind': 'wind_speed'
        }
    },
    'GDAS': {
        'data_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/GDAS',
        'file_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/GDAS/{parameter}/Daily/2024230.nc',
        'variable_names': {
            'Temp': 'air_temperature',
            'P': 'precipitation',
            'RelHum': 'relative_humidity',
            'Wind': 'wind_speed'
        }
    },
    'MSWEP': {
        'data_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/MSWEP_V280',
        'file_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/MSWEP_V280/NRT/Daily/2024230.nc',
        'variable_names': {
            'P': 'precipitation'
        }
    },
    'Station': {
        'data_path': config['dir_station_data'],
        'variable_names': {
            'Temp': 'temperature', 
            'P': 'precipitation'
            # Assuming these are typical variable names in station data
        }
    }
}

variables = {
    'Temp': {
        'name': 'Temperature',
        'units': 'K',
        'description': 'Air temperature at 2 meters above ground',
        'reference_dataset': reference_choice  # Dynamically choose based on user input
    },
    'P': {
        'name': 'Precipitation',
        'units': 'mm',
        'description': 'Total precipitation accumulation',
        'reference_dataset': 'MSWEP'
    },
    'RelHum': {
        'name': 'Relative Humidity',
        'units': '%',
        'description': 'Relative humidity at 2 meters above ground',
        'reference_dataset': reference_choice  # Dynamically choose based on user input
    },
    'Wind': {
        'name': 'Wind Speed',
        'units': 'm/s',
        'description': 'Wind speed at 10 meters above ground',
        'reference_dataset': reference_choice  # Dynamically choose based on user input
    }
}

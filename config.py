from datetime import datetime, timedelta
import os
import numpy as np

config = {
    'dir_data_processed': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/',
    'dir_data_raw': '/mnt/datawaha/hyex/msn/GWPM/DATA_RAW',
    'dir_output': '/mnt/datawaha/hyex/msn/GWPM/OUTPUT',
    'dir_temp': '/tmp',
    'parameters': ['Temp', 'P', 'RelHum', 'wind'],
}

models = {
    'GEFS': {
        'predictors': ['Temp', 'P', 'RelHum', 'wind'],
        'data_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/GEFS',
        'file_path_template': '{base_path}/{parameter}/{date_time}/{ensemble}/Daily/{file_name}.nc',
        'ensemble_format': '01'  # Example for accessing the 1st ensemble member
    },
    'ICON': {
        'predictors': ['Temp', 'P', 'RelHum', 'wind'],
        'data_path': '/mnt/datawaha/hyex/becke/DATA_PROCESSED/ICON',
        'file_path_template': '{base_path}/{parameter}/{date_time}/Daily/{file_name}.nc'
    },
    'ECMWF_IFS': {
        'predictors': ['Temp', 'P', 'RelHum', 'wind'],
        'data_path': '/mnt/datawaha/hyex/becke/DATA_PROCESSED/ECMWF_IFS_open_ensemble_forecasts',
        'file_path_template': '{base_path}/{parameter}/{date_time}/{ensemble}/Daily/{file_name}.nc',
        'ensemble_format': '001'  # Example for accessing the 1st ensemble member
    },
    'ECMWF_AIFS': {
        'predictors': ['Temp', 'P', 'wind'],
        'data_path': '/mnt/datawaha/hyex/becke/DATA_PROCESSED/ECMWF_AIFS_open_ensemble_forecasts',
        'file_path_template': '{base_path}/{parameter}/{date_time}/{ensemble}/Daily/{file_name}.nc',
        'ensemble_format': '001'  # Example for accessing the 1st ensemble member
    },
    'ERA5': {
        'predictors': ['Temp', 'RelHum', 'wind'],
        'data_path': '/mnt/datawaha/hyex/becke/DATA_PROCESSED/ERA5_HRES',
        'file_path_template': '{base_path}/{parameter}/Daily/{file_name}.nc'
    },
    'MSWEP': {
        'predictors': ['P'],
        'data_path': '/mnt/datawaha/hyex/msn/GWPM/DATA_PROCESSED/MSWEP_V300',
        'file_path_template': '{base_path}/{parameter}/Daily/{file_name}.nc'
    }
}

variables = {
    'Temp': {
        'name': 'Temperature',
        'units': 'K',  # Kelvin
        'description': 'Air temperature at 2 meters above ground',
    },
    'P': {
        'name': 'Precipitation',
        'units': 'mm',
        'description': 'Total precipitation accumulation',
    },
    'RelHum': {
        'name': 'Relative Humidity',
        'units': '%',
        'description': 'Relative humidity at 2 meters above ground',
    },
    'wind': {
        'name': 'Wind Speed',
        'units': 'm/s',
        'description': 'Wind speed at 10 meters above ground',
    }
}

from datetime import datetime, timedelta
import os
import numpy as np

config = {
    'dir_data_processed': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/',
    'dir_data_raw': '/mnt/datawaha/hyex/msn/GWPM/DATA_RAW',
    'dir_output': '/mnt/datawaha/hyex/msn/GWPM/OUTPUT',
    'dir_temp': '/tmp',
    'parameters': ['Temp', 'P', 'RelHum', 'wind'],  # List of parameters that can be analyzed
    'forecast_dates': ['20240816_00'],  # This date can be adjusted as needed
}

models = {
    'GEFS': {
        'predictors': ['Temp', 'P', 'RelHum', 'wind'],
        'data_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/GEFS',
        'file_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/GEFS/{parameter}/20240816_00/01/Daily/2024230.nc',
        'variable_names': {
            'Temp': 'air_temperature',
            'P': 'precipitation',
            'RelHum': 'relative_humidity',
            'wind': 'wind_speed'
        }
    },
    'ICON': {
        'predictors': ['Temp', 'P', 'RelHum', 'wind'],
        'data_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ICON',
        'file_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ICON/{parameter}/20240816_00/Daily/2024230.nc',
        'variable_names': {
            'Temp': 'air_temperature',
            'P': 'precipitation',
            'RelHum': 'relative_humidity',
            'wind': 'wind_speed'
        }
    },
    'ECMWF_IFS': {
        'predictors': ['Temp', 'P', 'RelHum', 'wind'],
        'data_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ECMWF_IFS_open_ensemble_forecasts',
        'file_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ECMWF_IFS_open_ensemble_forecasts/{parameter}/20240816_00/001/Daily/2024230.nc',
        'variable_names': {
            'Temp': 'air_temperature',
            'P': 'precipitation',
            'RelHum': 'relative_humidity',
            'wind': 'wind_speed'
        }
    },
    'ECMWF_AIFS': {
        'predictors': ['Temp', 'P', 'wind'],
        'data_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ECMWF_AIFS_open_ensemble_forecasts',
        'file_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ECMWF_AIFS_open_ensemble_forecasts/{parameter}/20240816_00/001/Daily/2024230.nc',
        'variable_names': {
            'Temp': 'air_temperature',
            'P': 'precipitation',
            'wind': 'wind_speed'
        }
    }
}

# Reference data (ERA5 and MSWEP)
reference_data = {
    'ERA5': {
        'data_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ERA5_HRES',
        'file_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/ERA5_HRES/{parameter}/Daily/2024230.nc',
        'variable_names': {
            'Temp': 'air_temperature',
            'P': 'precipitation',
            'RelHum': 'relative_humidity',
            'wind': 'wind_speed'
        }
    },
    'MSWEP': {
        'data_path': '/mnt/datawaha/hyex/msn/GWPM/DATA_PROCESSED/MSWEP_V300',
        'file_path': '/mnt/datawaha/hyex/msn/GWPM/DATA_PROCESSED/MSWEP_V300/{parameter}/Daily/2024230.nc',
        'variable_names': {
            'P': 'precipitation'
        }
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
        'units': 'mm/d',
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

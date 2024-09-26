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
        'data_path': '/mnt/datawaha/hyex/beckhe/DATA_PROCESSED/GEFS/',
    },
    'ICON': {
        'predictors': ['Temp', 'P', 'RelHum', 'wind'],
        'data_path': '/mnt/datawaha/hyex/becke/DATA_PROCESSED/ICON',
    },
    'ECMWF_IFS': {
        'predictors': ['Temp', 'P', 'RelHum', 'wind'],
        'data_path': '/mnt/datawaha/hyex/becke/DATA_PROCESSED/ECMWF_IFS_open_ensemble_forecasts',
    },
    'ECMWF_AIFS': {
        'predictors': ['Temp', 'P',  'wind'],
        'data_path': '/mnt/datawaha/hyex/becke/DATA_PROCESSED/ECMWF_AIFS_open_ensemble_forecasts',
    },
    'ERA5': {
        'predictors': ['Temp', 'RelHum', 'wind'],
        'data_path': '/mnt/datawaha/hyex/becke/DATA_PROCESSED/ERA5_HRES',
    },
    'MSWEP': {
        'predictors': ['P'],
        'data_path': '/mnt/datawaha/hyex/msn/GWPM/DATA_PROCESSED/MSWEP_V300',
    }
}

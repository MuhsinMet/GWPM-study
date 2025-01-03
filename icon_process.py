import os
import pygrib
from datetime import datetime, timedelta

# File paths and base directory for repositories
input_file = '/mnt/datawaha/hyex/msn/GWPM/pamore/igfrf01000000' #change according to the file downloaded
base_dir = '/mnt/datawaha/hyex/msn/GWPM/pamore/data_processed/'

# Define parameters and their corresponding GRIB names
parameters = {
    'temperature': 'Temperature',
    'u_wind': 'U component of wind',
    'v_wind': 'V component of wind',
    'relative_humidity': 'Relative humidity',
    'cloud_cover': 'Cloud cover',
    'pressure': 'Pressure',
    'specific_humidity': 'Specific humidity'
}

# Open the GRIB2 file
grbs = pygrib.open(input_file)

# Extract forecast production date
forecast_date = None
for grb in grbs:
    forecast_date = grb.analDate  # Assuming all records share the same forecast production date
    break
if not forecast_date:
    raise ValueError("Unable to extract forecast production date from the file.")

forecast_date_str = datetime.strftime(forecast_date, '%Y%m%d')

# Process each parameter
for param, grib_name in parameters.items():
    try:
        # Select records for the parameter
        records = grbs.select(name=grib_name)
        
        # Create a base directory for the parameter
        param_dir = os.path.join(base_dir, param)
        os.makedirs(param_dir, exist_ok=True)
        
        # Create a directory for the forecast production date inside the parameter folder
        forecast_dir = os.path.join(param_dir, forecast_date_str)
        os.makedirs(forecast_dir, exist_ok=True)
        
        for record in records:
            # Extract the forecast time (value date) from the record
            value_date = forecast_date + timedelta(hours=record.forecastTime)
            value_date_str = datetime.strftime(value_date, '%Y%m%d')
            
            # Define output file path
            output_file = os.path.join(forecast_dir, f"{value_date_str}.grib2")
            
            # Save the record
            with open(output_file, 'wb') as f:
                f.write(record.tostring())
        print(f"Saved {param} data.")
    except ValueError as e:
        print(f"Error processing {param}: {e}")

print("Data successfully saved into organized folders.")

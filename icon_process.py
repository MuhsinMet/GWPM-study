import os
import pygrib
from datetime import datetime

# File paths and base directory for repositories
input_file = '/mnt/datawaha/hyex/msn/GWPM/pamore/igfrf01000000'
base_dir = '/mnt/datawaha/hyex/msn/GWPM/pamore/data_processed'

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

# Create directories if they don't exist
for param in parameters.keys():
    os.makedirs(os.path.join(base_dir, param), exist_ok=True)

# Open the GRIB2 file
grbs = pygrib.open(input_file)

# Process each parameter
for param, grib_name in parameters.items():
    try:
        # Select records for the parameter
        records = grbs.select(name=grib_name)
        
        for record in records:
            # Extract the date from the GRIB record
            date = record.analDate
            date_str = datetime.strftime(date, '%Y%m%d')  # Format as YYYYMMDD
            
            # Define output file path
            output_file = os.path.join(base_dir, param, f"{date_str}.grib2")
            
            # Save the record
            with open(output_file, 'wb') as f:
                f.write(record.tostring())
        print(f"Saved {param} data.")
    except ValueError as e:
        print(f"Error processing {param}: {e}")

print("Data successfully saved into parameter-specific repositories.")

from ecmwfapi import ECMWFDataServer

{
    "url"   : "https://api.ecmwf.int/v1",
    "key"   : "0e63dade9cebd2822176cb17accf1beb",
    "email" : "hylke.beck@kaust.edu.sa"
}
from ecmwfapi import ECMWFDataServer

# Initialize the ECMWF server
server = ECMWFDataServer()

# Define the parameters for your data request
server.retrieve({
    "class": "ti",                    # TIGGE class
    "dataset": "tigge",               # TIGGE dataset
    "expver": "prod",                 # Experimental version
    "stream": "enfo",                 # Ensemble forecast
    "type": "pf",                     # Perturbed forecast
    "levtype": "sfc",                 # Surface level
    "param": "167",                   # Parameter (e.g., 167 for 2m temperature)
    "step": "0/6/12/18",              # Forecast steps
    "number": "all",                  # All ensemble members
    "grid": "0.5/0.5",                # Grid resolution
    "area": "75/-20/10/60",           # Geographical area (North/West/South/East)
    "date": "20240101/to/20240107",   # Date range
    "time": "00/12",                  # Forecast times
    "format": "netcdf",               # File format
    "target": "tigge_data.nc",        # Output file
})

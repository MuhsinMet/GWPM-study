import os
from datetime import datetime

def convert_to_julian_date(date_str):
    date_obj = datetime.strptime(date_str, '%Y%m%d')
    julian_day = date_obj.strftime('%j')
    return f"{date_obj.year}{julian_day}"

def mkdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

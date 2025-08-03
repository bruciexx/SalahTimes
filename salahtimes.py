from suncalc import get_position, get_times     # module for calculating sun position and sunlight phases
from datetime import datetime                   # module for getting the current date and time from the system
import pandas as pd                             # module for data manipulation

''' setting initial initial variables '''
date = datetime.now()
lon = 4.896     # temp position (need to eventually add localization feature)
lat = 52.375

''' testing grounds '''
get_position(date, lon, lat)

get_times(date, lon, lat)


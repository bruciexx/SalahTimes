from suncalc import get_position, get_times     # module that calcs pos of sun
from datetime import datetime, timezone
import pandas as pd                             # module for data manipulation
import time

''' setting initial initial variables '''
# temp position (need to eventually add localization feature)
lon = 4.9138
lat = 52.36386
solar_phase = 'solar_noon'

# get current datetime UTC from epoch time
time_utc_epoch = time.time()
time_utc = datetime.fromtimestamp(time.time(), timezone.utc)
time_local = datetime.fromtimestamp(time_utc.timestamp())

# get standard solar phases from current datetime and given position
solar_phases = get_times(date=time_local, lng=lon, lat=lat)

# get epoch time for given solar phase


times = get_times(time_local, lon, lat)
position = get_position(time_local, lon, lat)


'''testing grounds'''

print(solar_phases)
print(time_utc_epoch)
print(time_utc)
print(time_local)

df = pd.DataFrame({
    'date': [time_local],
    'lon': [lat],
    'lat': [lat]
})

'''
print("current date and time (UTC) is:")
print(time_local)
print(20 * '-')
print("current sun position is:")
print(pd.DataFrame(get_position(df['date'], df['lon'], df['lat'])))
print(20 * '-')
print("the time for " + solar_phase + " is at:")
print(pd.DataFrame(get_times(df['date'], df['lon'], df['lat']))[solar_phase])
print(20 * '-')
'''


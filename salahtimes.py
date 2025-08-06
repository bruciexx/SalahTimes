from suncalc import get_position, get_times     # module that calcs pos of sun
from datetime import datetime, timezone
import pandas as pd                             # module for data manipulation
import time
import pytz

''' setting panda options '''
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 20)

''' setting initial initial variables '''
lon = 4.9138        # make changeable by user
lat = 52.36386
solar_phase = 'solar_noon'      # same here
local_tz = pytz.timezone('Europe/Amsterdam')    # and here

# get current datetime UTC from epoch time
time_utc_epoch = time.time()
time_utc = datetime.fromtimestamp(time.time(), timezone.utc)
time_local = datetime.fromtimestamp(time_utc.timestamp())

# get standard solar phases from current datetime and given position
solar_phases_utc = get_times(date=time_utc, lng=lon, lat=lat)

# convert to local time
solar_phases_local = {}
for p, t in solar_phases_utc.items():
    if isinstance(t, datetime):
        local_time = t.replace(tzinfo=timezone.utc).astimezone(local_tz)
        solar_phases_local[p] = local_time
    else:
        solar_phases_local[p] = t

# convert to dataframe to clean up output
solar_phases = pd.DataFrame([solar_phases_local])

'''testing grounds'''
input("do you want to set location? (Y/n)")
print(solar_phases)
# print(time_utc_epoch)
# print(time_utc)
# print(time_local)

# print(solar_phases_messy[solar_phase].time())
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


from suncalc import get_position, get_times     # module that calcs pos of sun
from datetime import datetime, timezone
import pandas as pd                             # module for data manipulation

''' setting initial initial variables '''
date = datetime.now(timezone.utc)

lon = 4.896     # temp position (need to eventually add localization feature)
lat = 52.375

times = get_times(date, lon, lat)
position = get_position(date, lon, lat)

solar_phase = 'solar_noon'

''' testing grounds '''


df = pd.DataFrame({
    'date': [date],
    'lon': [lat],
    'lat': [lat]
})

print("current date and time (UTC) is:")
print(date)
print(20 * '-')
print("current sun position is:")
print(pd.DataFrame(get_position(df['date'], df['lon'], df['lat'])))
print(20 * '-')
print("the time for " + solar_phase + " is at:")
print(pd.DataFrame(get_times(df['date'], df['lon'], df['lat']))[solar_phase])
print(20 * '-')

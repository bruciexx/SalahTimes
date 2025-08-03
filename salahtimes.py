from suncalc import get_position, get_times     # module for calculating sun position and sunlight phases
from datetime import datetime, timezone         # module for getting the current date and time from the system
import pandas as pd                             # module for data manipulation

''' setting initial initial variables '''
date = datetime.now(timezone.utc)

lon = 4.896     # temp position (need to eventually add localization feature)
lat = 52.375

times = get_times(date, lon, lat)
position = get_position(date, lon, lat)

''' testing grounds '''


df = pd.DataFrame({
    'date': [date],
    'lon': [lat],
    'lat': [lat]
})
print(date)
print(pd.DataFrame(get_position(df['date'], df['lon'], df['lat'])))


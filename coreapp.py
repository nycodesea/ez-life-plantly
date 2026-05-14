# core for testing
import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

import plotly.express as px

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 35.6895,
    "longitude": 139.6917,
    "daily": [
        "weather_code",
        "rain_sum",
        "showers_sum",
        "snowfall_sum",
        "precipitation_sum",
        "precipitation_hours",
        "precipitation_probability_max",
    ],
    "current": [
        "temperature_2m",
        "relative_humidity_2m",
        "is_day",
        "precipitation",
        "rain",
        "showers",
        "snowfall",
        "weather_code",
        "cloud_cover",
        "wind_speed_10m",
    ],
    "timezone": "Asia/Tokyo",
    "past_days": 7,
    "forecast_days": 0,
    "wind_speed_unit": "ms",
}
responses = openmeteo.weather_api(url, params=params)
response = responses[0]

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_weather_code = daily.Variables(0).ValuesAsNumpy()
daily_rain_sum = daily.Variables(1).ValuesAsNumpy()
daily_precipitation_sum = daily.Variables(4).ValuesAsNumpy()


daily_data = {
    "date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left",
    ).tz_convert(response.Timezone().decode())
}

daily_data["weather_code"] = daily_weather_code
daily_data["daily_rain_sum"] = daily_rain_sum
daily_data["daily_precipitation_sum"] = daily_precipitation_sum


daily_dataframe = pd.DataFrame(data=daily_data)
print("\nDaily data\n", daily_dataframe)

# Plotly
fig = px.bar(
    daily_dataframe,
    x="date",
    y="daily_precipitation_sum",
    title="Past 7 Days Precipitation",
)

fig.update_xaxes(dtick="D1")
fig.show()

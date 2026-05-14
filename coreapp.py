# core for testing
import openmeteo_requests
import pandas as pd
from pandas import Timedelta
import requests_cache
from retry_requests import retry
import plotly.express as px
from dash import Dash, dcc, html

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

# Weather codes
WEATHER_GROUPS = {
    "sunny": [0],
    "cloudy": [1, 2, 3],
    "fog": [45, 48],
    "drizzle": [51, 53, 55],
    "rain": [61, 63, 65, 66, 67, 80, 81, 82],
    "snow": [71, 73, 75, 77, 85, 86],
    "thunder": [95, 96, 99],
}


def get_weather_type(code):
    for weather_type, codes in WEATHER_GROUPS.items():
        if code in codes:
            return weather_type
    return "unknown"


WEATHER_ICONS = {
    "sunny": "☀️",
    "cloudy": "☁️",
    "fog": "🌫",
    "drizzle": "🌂",
    "rain": "🌧",
    "snow": "❄️",
    "thunder": "⚡",
}
daily_dataframe["weather_type"] = daily_dataframe["weather_code"].apply(
    get_weather_type
)

daily_dataframe["weather_icon"] = daily_dataframe["weather_type"].map(WEATHER_ICONS)
daily_dataframe["label"] = (
    daily_dataframe["date"].dt.strftime("%#m/%#d")
    + "<br>"
    + daily_dataframe["weather_icon"]
)

# date span
today = pd.Timestamp.now(tz=response.Timezone().decode()).normalize()
past_7days_df = daily_dataframe[daily_dataframe["date"] < today]
print("\nDaily data\n", daily_dataframe)
print("\nPast 7 Daily data\n", past_7days_df)
# Plotly
fig = px.bar(
    daily_dataframe,
    x="date",
    y="daily_precipitation_sum",
    title="Past Precipitation",
)

fig.update_xaxes(
    tickmode="array",
    tickvals=daily_dataframe["date"],
    ticktext=daily_dataframe["label"],
)
fig.update_yaxes(title="Precipitation")

# new 7days graph
fig2 = px.bar(
    past_7days_df,
    x="date",
    y="daily_precipitation_sum",
    title="Past 7days Precipitation",
)

fig2.update_xaxes(
    tickmode="array",
    tickvals=past_7days_df["date"],
    ticktext=past_7days_df["label"],
    range=[
        past_7days_df["date"].iloc[-5] - Timedelta(hours=12),
        past_7days_df["date"].iloc[-1] + Timedelta(hours=12),
    ],
)
fig2.update_yaxes(title="Precipitation")

# Dash
app = Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(figure=fig),
        dcc.Graph(figure=fig2),
    ]
)

app.run(debug=True)

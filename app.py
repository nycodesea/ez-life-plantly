import requests
from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd

app = Dash(__name__)

# サイトで必要そうなの入れたURL
# https://api.open-meteo.com/v1/forecast?latitude=35.6895&longitude=139.6917&daily=temperature_2m_max,temperature_2m_min,weather_code,rain_sum,showers_sum,sunrise,sunset,daylight_duration,sunshine_duration,uv_index_max,wind_speed_10m_max&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,rain,showers,wind_speed_10m,weather_code,cloud_cover,evapotranspiration,soil_temperature_0cm,soil_temperature_6cm,soil_moisture_0_to_1cm,soil_moisture_1_to_3cm&current=temperature_2m,relative_humidity_2m,is_day,weather_code,cloud_cover,precipitation,rain,showers,wind_speed_10m&timezone=Asia%2FTokyo&past_days=7&wind_speed_unit=ms
url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 35,
    "longitude": 139,
    "hourly": "temperature_2m,relative_humidity_2m",
}

data = requests.get(url, params=params).json()
print(data)
times = data["hourly"]["time"]
temperatures = data["hourly"]["temperature_2m"]
humidity = data["hourly"]["relative_humidity_2m"]

df = pd.DataFrame({"time": times, "temperature": temperatures, "humidity": humidity})
fig = px.line(
    df,
    x="time",
    y=["temperature", "humidity"],
    title="Temperature and Humidity Over Time",
)
app.layout = html.Div([html.H1("Plant Dashboard"), dcc.Graph(figure=fig)])


app.run(debug=True)

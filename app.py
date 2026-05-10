import requests
from dash import Dash, html

app = Dash(__name__)

url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=35"
    "&longitude=139"
    "&current=temperature_2m,relative_humidity_2m"
)

data = requests.get(url).json()
temp = data["current"]["temperature_2m"]
humidity = data["current"]["relative_humidity_2m"]

app.layout = (
    html.Div(
        [
            html.H1("Plantly dots"),
            html.P("Texter."),
            html.P(f"Temperture : {temp}"),
            html.P(f"Humidity : {humidity}"),
        ]
    ),
)


app.run(debug=True)

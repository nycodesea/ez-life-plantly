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
        "temperature_2m_max",
        "temperature_2m_min",
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
daily_precipitation_probability_max = daily.Variables(6).ValuesAsNumpy()
daily_temperature_2m_max = daily.Variables(7).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(8).ValuesAsNumpy()

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
daily_data["daily_precipitation_probability_max"] = daily_precipitation_probability_max
daily_data["daily_temperature_2m_max"] = daily_temperature_2m_max
daily_data["daily_temperature_2m_min"] = daily_temperature_2m_min

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
future_7days_df = daily_dataframe[daily_dataframe["date"] > today]

print(
    "\nfuture 7days Precipitation probability\n",
    future_7days_df["daily_precipitation_probability_max"],
)
print("\nFuture 7days Precipitation\n", future_7days_df["daily_precipitation_sum"])
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

# Past 7days graph
fig2 = px.bar(
    past_7days_df,
    x="date",
    y="daily_precipitation_sum",
)
fig2.update_layout(
    margin=dict(l=30, r=0, t=00, b=0),
    autosize=True,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(
        family="Zen Maru Gothic",
    ),
)
fig2.update_traces(marker_color="#81b8be")
fig2.update_xaxes(
    title="",
    tickmode="array",
    gridcolor="rgba(0,0,0,0)",
    tickvals=past_7days_df["date"],
    ticktext=past_7days_df["label"],
    range=[
        past_7days_df["date"].iloc[-5] - Timedelta(hours=12),
        past_7days_df["date"].iloc[-1] + Timedelta(hours=12),
    ],
)
fig2.update_yaxes(
    title="",
    gridcolor="rgba(0,0,0,0.06)",
    griddash="dot",
    gridwidth=1,
)
fig2.add_annotation(
    text="mm",
    xref="paper",
    yref="paper",
    x=0,
    y=1,
    showarrow=False,
)
# future 7days graph
# future 7days graph : temperture max - min
fig_future_temp = px.line(
    future_7days_df,
    x="date",
    y=[
        "daily_temperature_2m_max",
        "daily_temperature_2m_min",
    ],
)
fig_future_temp.update_layout(
    margin=dict(l=30, r=0, t=0, b=0),
    legend=dict(
        x=0.9,
        y=0.95,
    ),
    autosize=True,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(
        family="Zen Maru Gothic",
    ),
)
fig_future_temp.add_annotation(
    text="℃",
    xref="paper",
    yref="paper",
    x=0,
    y=1,
    showarrow=False,
)
fig_future_temp.update_traces(line_shape="spline")
fig_future_temp.update_traces(
    selector=dict(name="daily_temperature_2m_max"),
    name="Max",
    line=dict(color="#d97366"),
)
fig_future_temp.update_traces(
    selector=dict(name="daily_temperature_2m_min"),
    name="min",
    line=dict(color="#7aa38b"),
)
fig_future_temp.update_xaxes(
    showgrid=False,
    zeroline=False,
    showticklabels=False,
    title="",
    range=[
        future_7days_df["date"].iloc[0] - Timedelta(hours=12),
        future_7days_df["date"].iloc[-1] + Timedelta(hours=12),
    ],
)
fig_future_temp.update_yaxes(
    # zeroline=False,
    # showticklabels=False,
    title="",
    gridcolor="rgba(0,0,0,0.06)",
    griddash="dot",
    gridwidth=1,
)
# future 7days graph : precipitation Babble
future_7days_df["label"] = [
    (
        "明日<br>" + icon
        if date == today + Timedelta(days=1)
        else date.strftime("%#m/%#d") + "<br>" + icon
    )
    for date, icon in zip(future_7days_df["date"], future_7days_df["weather_icon"])
]
max_precipitation = future_7days_df["daily_precipitation_sum"].max()
future_7days_df["bubble_size"] = (
    future_7days_df["daily_precipitation_sum"] / max_precipitation * 100
    if max_precipitation > 0
    else 0
)

future_7days_df["bubble_text"] = future_7days_df[
    "daily_precipitation_probability_max"
].apply(lambda x: f"{int(x)}%" if int(x) >= 10 else "")

future_7days_df["bubble_opacity"] = (
    future_7days_df["daily_precipitation_probability_max"] / 100
)
fig_future_rain = px.scatter(
    future_7days_df,
    x="date",
    y=[0] * len(future_7days_df),
    size="bubble_size",
    text="bubble_text",
    color="daily_precipitation_sum",
    size_max=40,
)
fig_future_rain.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=30, r=0, t=0, b=0),
    height=140,
    autosize=True,
    font=dict(
        family="Zen Maru Gothic",
    ),
)
fig_future_rain.update_traces(
    textfont_size=15,
    textfont_color="white",
    textposition="middle center",
    marker=dict(
        color="#86b6b3",
        sizemode="area",
        opacity=future_7days_df["bubble_opacity"],
    ),
)
fig_future_rain.update_xaxes(
    title="",
    tickmode="array",
    tickvals=future_7days_df["date"],
    ticktext=future_7days_df["label"],
    showgrid=False,
    zeroline=False,
    showline=False,
    range=[
        future_7days_df["date"].iloc[0] - Timedelta(hours=12),
        future_7days_df["date"].iloc[-1] + Timedelta(hours=12),
    ],
)
fig_future_rain.update_yaxes(
    range=[-0.5, 0.5],
    visible=False,
    showticklabels=False,
    showgrid=False,
    zeroline=False,
    showline=False,
)


# Dash
app = Dash(
    __name__,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@400;500&display=swap"
    ],
)

app.layout = html.Div(
    [
        html.H1(
            "PLANTly",
            style={
                "marginTop": "0",
                "marginBottom": "16px",
                "fontSize": "32px",
                "fontWeight": "500",
                "color": "#5f6f65",
            },
        ),
        # Top
        html.Div(
            [
                # Left
                html.Div(
                    [
                        dcc.Graph(
                            figure=fig2,
                            responsive=True,
                            style={
                                "height": "100%",
                                "width": "100%",
                            },
                            config={"displayModeBar": False},
                        )
                    ],
                    style={
                        "width": "40%",
                        "height": "100%",
                        "backgroundColor": "#f3f1eb",
                        "borderRadius": "20px",
                        "padding": "10px",
                        "boxShadow": "0 4px 12px rgba(0,0,0,0.05)",
                    },
                ),
                # Right
                html.Div(
                    [
                        dcc.Graph(
                            figure=fig_future_temp,
                            style={
                                "height": "60%",
                                "minHeight": 0,
                            },
                            config={"displayModeBar": False},
                            responsive=True,
                        ),
                        dcc.Graph(
                            figure=fig_future_rain,
                            style={
                                "height": "40%",
                                "minHeight": 0,
                            },
                            config={"displayModeBar": False},
                            responsive=True,
                        ),
                    ],
                    style={
                        "width": "60%",
                        "height": "100%",
                        "display": "flex",
                        "flexDirection": "column",
                        "backgroundColor": "#f3f1eb",
                        "borderRadius": "20px",
                        "padding": "10px",
                        "boxShadow": "0 4px 12px rgba(0,0,0,0.05)",
                    },
                ),
            ],
            style={
                "display": "flex",
                "gap": "12px",
                "height": "55vh",
            },
        ),
        # Bottom
        html.Div(
            [
                # Graph
            ]
        ),
    ],
    style={
        "backgroundColor": "#eef2ea",
        "minHeight": "100vh",
        "padding": "16px",
        "fontFamily": "Zen Maru Gothic",
    },
)

app.run(debug=True)

# Plantly planet-force
import openmeteo_requests
import pandas as pd
from pandas import Timedelta
import requests_cache
from retry_requests import retry
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback, no_update, ctx
import numpy as np
from plotly.subplots import make_subplots

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
        "precipitation_probability",
        "rain",
        "showers",
        "snowfall",
        "weather_code",
        "cloud_cover",
        "wind_speed_10m",
        "evapotranspiration",
        "soil_temperature_0cm",
        "soil_temperature_6cm",
        "soil_temperature_18cm",
        "soil_moisture_0_to_1cm",
        "soil_moisture_1_to_3cm",
        "soil_moisture_3_to_9cm",
        "soil_moisture_9_to_27cm",
        "uv_index",
        "sunshine_duration",
    ],
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "is_day",
        "precipitation",
        "precipitation_probability",
        "rain",
        "showers",
        "snowfall",
        "weather_code",
        "cloud_cover",
        "wind_speed_10m",
        "evapotranspiration",
        "soil_temperature_0cm",
        "soil_temperature_6cm",
        "soil_temperature_18cm",
        "soil_moisture_0_to_1cm",
        "soil_moisture_1_to_3cm",
        "soil_moisture_3_to_9cm",
        "soil_moisture_9_to_27cm",
        "uv_index",
        "sunshine_duration",
    ],
    "timezone": "Asia/Tokyo",
    "past_days": 7,
    "wind_speed_unit": "ms",
}
responses = openmeteo.weather_api(url, params=params)
response = responses[0]

# Process daily data.
daily = response.Daily()
daily_weather_code = daily.Variables(0).ValuesAsNumpy()
# daily_rain_sum = daily.Variables(1).ValuesAsNumpy()
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
# daily_data["daily_rain_sum"] = daily_rain_sum
daily_data["daily_precipitation_sum"] = daily_precipitation_sum
daily_data["daily_precipitation_probability_max"] = daily_precipitation_probability_max
daily_data["daily_temperature_2m_max"] = daily_temperature_2m_max
daily_data["daily_temperature_2m_min"] = daily_temperature_2m_min

daily_dataframe = pd.DataFrame(data=daily_data)

# Process hourly data.
# Process hourly data
hourly = response.Hourly()

hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_is_day = hourly.Variables(2).ValuesAsNumpy()
hourly_precipitation = hourly.Variables(3).ValuesAsNumpy()
hourly_precipitation_probability = hourly.Variables(4).ValuesAsNumpy()
hourly_rain = hourly.Variables(5).ValuesAsNumpy()
hourly_showers = hourly.Variables(6).ValuesAsNumpy()
hourly_snowfall = hourly.Variables(7).ValuesAsNumpy()
hourly_weather_code = hourly.Variables(8).ValuesAsNumpy()
hourly_cloud_cover = hourly.Variables(9).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(10).ValuesAsNumpy()
hourly_evapotranspiration = hourly.Variables(11).ValuesAsNumpy()
hourly_soil_temperature_0cm = hourly.Variables(12).ValuesAsNumpy()
hourly_soil_temperature_6cm = hourly.Variables(13).ValuesAsNumpy()
hourly_soil_temperature_18cm = hourly.Variables(14).ValuesAsNumpy()
hourly_soil_moisture_0_to_1cm = hourly.Variables(15).ValuesAsNumpy()
hourly_soil_moisture_1_to_3cm = hourly.Variables(16).ValuesAsNumpy()
hourly_soil_moisture_3_to_9cm = hourly.Variables(17).ValuesAsNumpy()
hourly_soil_moisture_9_to_27cm = hourly.Variables(18).ValuesAsNumpy()
hourly_uv_index = hourly.Variables(19).ValuesAsNumpy()
hourly_sunshine_duration = hourly.Variables(20).ValuesAsNumpy()

hourly_df = pd.DataFrame()

hourly_df["temperature_2m"] = hourly_temperature_2m
hourly_df["relative_humidity_2m"] = hourly_relative_humidity_2m
hourly_df["is_day"] = hourly_is_day

hourly_df["precipitation"] = hourly_precipitation
hourly_df["precipitation_probability"] = hourly_precipitation_probability

hourly_df["rain"] = hourly_rain
hourly_df["showers"] = hourly_showers
hourly_df["snowfall"] = hourly_snowfall

hourly_df["weather_code"] = hourly_weather_code
hourly_df["cloud_cover"] = hourly_cloud_cover
hourly_df["wind_speed_10m"] = hourly_wind_speed_10m

hourly_df["evapotranspiration"] = hourly_evapotranspiration

hourly_df["soil_temperature_0cm"] = hourly_soil_temperature_0cm
hourly_df["soil_temperature_6cm"] = hourly_soil_temperature_6cm
hourly_df["soil_temperature_18cm"] = hourly_soil_temperature_18cm

hourly_df["soil_moisture_0_to_1cm"] = hourly_soil_moisture_0_to_1cm
hourly_df["soil_moisture_1_to_3cm"] = hourly_soil_moisture_1_to_3cm
hourly_df["soil_moisture_3_to_9cm"] = hourly_soil_moisture_3_to_9cm
hourly_df["soil_moisture_9_to_27cm"] = hourly_soil_moisture_9_to_27cm

hourly_df["uv_index"] = hourly_uv_index
hourly_df["sunshine_duration"] = hourly_sunshine_duration

hourly_df["date"] = pd.date_range(
    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
    freq=pd.Timedelta(seconds=hourly.Interval()),
    inclusive="left",
).tz_convert(response.Timezone().decode())

# Procdss current data.
# current = response.Current()
# current_temperature_2m = current.Variables(0).ValuesAsNumpy()
# "relative_humidity_2m"= current.Variables(1).ValuesAsNumpy()
# "is_day"= current.Variables(2).ValuesAsNumpy()
# "precipitation"= current.Variables(3).ValuesAsNumpy()
# "precipitation_probability"= current.Variables(4).ValuesAsNumpy()
# "rain"= current.Variables(5).ValuesAsNumpy()
# "showers"= current.Variables(6).ValuesAsNumpy()
# "snowfall"= current.Variables(7).ValuesAsNumpy()
# "weather_code"= current.Variables(8).ValuesAsNumpy()
# "cloud_cover"= current.Variables(9).ValuesAsNumpy()
# "wind_speed_10m"= current.Variables(10).ValuesAsNumpy()
# "evapotranspiration"= current.Variables(11).ValuesAsNumpy()
# "soil_temperature_0cm"= current.Variables(12).ValuesAsNumpy()
# "soil_temperature_6cm"= current.Variables(13).ValuesAsNumpy()
# "soil_temperature_18cm"= current.Variables(14).ValuesAsNumpy()
# "soil_moisture_0_to_1cm"= current.Variables(15).ValuesAsNumpy()
# "soil_moisture_1_to_3cm"= current.Variables(16).ValuesAsNumpy()
# "soil_moisture_3_to_9cm"= current.Variables(17).ValuesAsNumpy()
# "soil_moisture_9_to_27cm"= current.Variables(18).ValuesAsNumpy()
# "uv_index"= current.Variables(19).ValuesAsNumpy()
# "sunshine_duration"= current.Variables(20).ValuesAsNumpy()
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
    "rain": "🌧️",
    "snow": "❄️",
    "thunder": "⚡",
}
daily_dataframe["weather_type"] = daily_dataframe["weather_code"].apply(
    get_weather_type
)

daily_dataframe["weather_icon"] = daily_dataframe["weather_type"].map(WEATHER_ICONS)
daily_dataframe["label"] = (
    daily_dataframe["date"].dt.strftime("%m/%d").str.replace("/0", "/").str.lstrip("0")
    + "<br>"
    + daily_dataframe["weather_icon"]
)

# date span
today = pd.Timestamp.now(tz=response.Timezone().decode()).normalize()
past_7days_df = daily_dataframe[daily_dataframe["date"] < today]
tomorrow = today + Timedelta(days=1)
future_7days_df = daily_dataframe[daily_dataframe["date"] >= tomorrow]

# print(
#     "\nfuture 7days Precipitation probability\n",
#     future_7days_df["daily_precipitation_probability_max"],
# )
# print("\nFuture 7days Precipitation\n", future_7days_df["daily_precipitation_sum"])
# print("\nDaily data\n", daily_dataframe)
# print("\nPast 7 Daily data\n", past_7days_df)

# Plotly
# Past 7days graph
fig2 = px.bar(
    past_7days_df,
    x="date",
    y="daily_precipitation_sum",
    custom_data=["daily_precipitation_sum"],
)
fig2.update_layout(
    dragmode="zoom",
    yaxis=dict(fixedrange=True),
    height=150,
    margin=dict(l=20, r=0, t=00, b=0),
    autosize=True,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(
        family="Zen Maru Gothic",
    ),
    hoverlabel=dict(
        bgcolor="rgba(230,230,255,0.9)",
        bordercolor="rgba(0,0,0,0)",
        font=dict(
            color="#5f6f65",
            size=11,
        ),
    ),
    # hovermode="x unified",
)
fig2.update_traces(
    marker_color="#81b8be",
    hovertemplate="%{y:.2f}mm<br>" + "<extra></extra>",
)
fig2.update_xaxes(
    title=None,
    tickmode="array",
    gridcolor="rgba(0,0,0,0)",
    tickvals=past_7days_df["date"],
    ticktext=past_7days_df["label"],
    tickfont=dict(size=14),
    range=[
        past_7days_df["date"].iloc[-5] - Timedelta(hours=12),
        past_7days_df["date"].iloc[-1] + Timedelta(hours=12),
    ],
    zeroline=True,
    zerolinecolor="rgba(200,0,0,1)",
    zerolinewidth=1,
    showline=True,
    linewidth=0.2,
    linecolor="rgba(0,0,0, 0.06)",
)
y_max = max(
    past_7days_df["daily_precipitation_sum"].max() + 2,
    10,
)
fig2.update_yaxes(
    title=None,
    gridcolor="rgba(0,0,0,0.06)",
    griddash="dot",
    gridwidth=1,
    range=[0, y_max],
    tickfont=dict(size=14),
    zeroline=False,
    zerolinecolor="rgba(0,0,0,0.06)",
    zerolinewidth=0.1,
    showline=False,
    linewidth=0.1,
    linecolor="rgba(0,0,0,0.06)",
)
fig2.add_annotation(
    text="mm",
    xref="paper",
    yref="paper",
    x=0,
    y=1,
    showarrow=False,
)


# future 7days graph----------------------------------------------
# future 7days graph : temperture max - min
fig_future_temp = px.line(
    future_7days_df,
    x="date",
    y=[
        "daily_temperature_2m_max",
        "daily_temperature_2m_min",
    ],
    custom_data=[
        "daily_precipitation_probability_max",
        "daily_precipitation_sum",
        "weather_icon",
    ],
)
fig_future_temp.update_layout(
    height=150,
    margin=dict(l=20, r=20, t=0, b=0),
    legend=dict(
        x=0.9,
        y=0.95,
    ),
    hovermode="x unified",
    hoverdistance=100,
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
fig_future_temp.update_traces(
    line_shape="spline",
    hoverinfo="none",
    hovertemplate=None,
)
fig_future_temp.update_traces(
    selector=dict(name="daily_temperature_2m_max"),
    name="Max",
    line=dict(color="#d97366"),
    showlegend=False,
)
fig_future_temp.update_traces(
    selector=dict(name="daily_temperature_2m_min"),
    name="min",
    line=dict(color="#89a9c7"),
    showlegend=False,
)

fig_future_temp.update_xaxes(
    showline=True,
    linecolor="rgba(0,0,0,0.2)",
    fixedrange=True,
    showgrid=False,
    zeroline=True,
    zerolinecolor="rgba(200,0,0,0.5)",
    zerolinewidth=2,
    showticklabels=False,
    title=None,
    range=[
        future_7days_df["date"].iloc[0] - Timedelta(hours=12),
        future_7days_df["date"].iloc[-1] + Timedelta(hours=16),
    ],
    showspikes=True,
    spikecolor="rgba(120,140,170,0.5)",
    spikethickness=1,
    spikedash="dot",
    spikesnap="data",
)
temp_min = future_7days_df["daily_temperature_2m_min"].min()
temp_max = future_7days_df["daily_temperature_2m_max"].max()

fig_future_temp.update_yaxes(
    fixedrange=True,
    title=None,
    gridcolor="rgba(0,0,0,0.06)",
    griddash="dot",
    gridwidth=1,
    tickfont=dict(size=14),
    range=[-2, temp_max + 3],
    showline=False,
    linewidth=0.02,
    linecolor="rgba(0,0,0,0.06)",
    zeroline=True,
    zerolinecolor="rgba(0,0,0,0.06)",
    zerolinewidth=0.1,
)
# future 7days graph : precipitation Babble
future_7days_df["label"] = [
    (
        "Tomorrow<br>" + icon
        if date == today + Timedelta(days=1)
        else date.strftime("%m/%d").replace("/0", "/").lstrip("0") + "<br>" + icon
    )
    for date, icon in zip(future_7days_df["date"], future_7days_df["weather_icon"])
]
max_precipitation = future_7days_df["daily_precipitation_sum"].max()
future_7days_df["bubble_size"] = (
    future_7days_df["daily_precipitation_sum"] + 10 if max_precipitation > 0 else 0
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
    y=[0.15] * len(future_7days_df),
    size="bubble_size",
    text="bubble_text",
    size_max=30,
    custom_data=[
        "daily_precipitation_probability_max",
        "daily_precipitation_sum",
    ],
)
fig_future_rain.update_layout(
    hovermode="x unified",
    hoverdistance=200,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=0, b=0),
    height=140,
    autosize=True,
    font=dict(
        family="Zen Maru Gothic",
    ),
    hoverlabel=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(0,0,0,0)",
        font=dict(color="rgba(0,0,0,0)", size=1),
    ),
)
fig_future_rain.update_traces(
    textfont_size=15,
    textfont_color="white",
    textposition="middle center",
    marker=dict(
        color="#81b8be",
        sizemode="area",
        opacity=future_7days_df["bubble_opacity"],
    ),
    hovertemplate="<extra></extra>",
    # ← hoverlabelを完全透明化
    hoverlabel=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(0,0,0,0)",
        font=dict(color="rgba(0,0,0,0)", size=1),
    ),
)
fig_future_rain.update_xaxes(
    fixedrange=True,
    title=None,
    tickmode="array",
    tickvals=future_7days_df["date"],
    ticktext=future_7days_df["label"],
    tickfont=dict(size=14),
    ticklabelstandoff=-14,
    showgrid=False,
    zeroline=False,
    showline=True,
    range=[
        future_7days_df["date"].iloc[0] - Timedelta(hours=12),
        future_7days_df["date"].iloc[-1] + Timedelta(hours=16),
    ],
    linecolor="rgba(0,0,0,0)",
    showspikes=True,
    spikecolor="rgba(120,140,170,0.5)",
    spikethickness=1,
    spikedash="dot",
    spikesnap="data",
    spikemode="across",
)
fig_future_rain.update_yaxes(
    fixedrange=True,
    range=[-0.5, 0.5],
    visible=False,
    showticklabels=False,
    showgrid=False,
    zeroline=False,
    showline=True,
    linecolor="rgba(0,0,0,0.56)",
)
# fig_future_rain.add_shape(
#     type="line",
#     xref="paper",
#     yref="paper",
#     x0=0,
#     x1=1,
#     y0=1,
#     y1=1,
#     line=dict(
#         color="rgba(0,0,0,0.08)",
#         width=1.5,
#     ),
# )

# Today------------------------------------------------
tz = response.Timezone().decode()
now = pd.Timestamp.now(tz=tz).normalize()

today_df = hourly_df.copy()
today_df = today_df.reset_index(drop=True)
today_df["x"] = today_df["date"]
today_df["x_index"] = np.arange(len(today_df))
# for DEBUG --------------------------------------------
DEBUG_MODE = False
mode = "random_mix"

if DEBUG_MODE:

    def make_debug_precip(n):
        return {
            "none": np.zeros(n),
            "light": np.random.uniform(0, 1, n),
            "medium": np.random.uniform(1, 3, n),
            "heavy": np.random.uniform(3, 8, n),
            "storm": np.random.uniform(5, 15, n),
            "spike": np.concatenate(
                [
                    np.zeros(n // 3),
                    np.random.uniform(0, 2, n // 3),
                    np.random.uniform(8, 15, n - 2 * (n // 3)),
                ]
            ),
            "wave": 5 + 4 * np.sin(np.linspace(0, 3 * np.pi, n)),
            "random_mix": np.random.gamma(shape=2.0, scale=2.0, size=n),
        }

    patterns = make_debug_precip(len(today_df))

    today_df["precipitation"] = patterns[mode]
    today_df["precipitation_probability"] = np.clip(
        today_df["precipitation"] * 15 + np.random.uniform(0, 20, len(today_df)), 0, 100
    )
# --------------------------------------------------------
fig_today = make_subplots(
    rows=2,
    cols=1,
    vertical_spacing=0.008,
    row_heights=[0.8, 0.2],
    shared_xaxes=True,
    specs=[[{"secondary_y": True}], [{}]],
)
# --- 気温（メインライン）---
fig_today.add_trace(
    go.Scatter(
        x=today_df["date"],
        y=today_df["temperature_2m"],
        name="Temp",
        mode="lines+markers",
        marker=dict(
            size=12,
            opacity=0,
        ),
        line=dict(color="#6fa08a", width=3, shape="spline", smoothing=0.8),
        hovertemplate=None,
        hoverinfo="none",
        hoveron="points+fills",
    ),
    row=1,
    col=1,
    secondary_y=False,
)

# --- 雨（背景バー）---
fig_today.add_trace(
    go.Bar(
        x=today_df["date"],
        y=today_df["precipitation"],
        yaxis="y2",
        name="Rain",
        marker_color="rgba(90, 160, 255, 0.4)",
        base=0,
        hoverinfo="none",
        hovertemplate=None,
    ),
    row=1,
    col=1,
    secondary_y=True,
)


# --- 降水確率（バブル）---

MAX_R = 20  # 最大バブル半径（px相当、sizeref で調整）
bubble_size = 10 + today_df["precipitation_probability"] * 0.3

# 確率に応じた色（青の濃さ）
bubble_colors = [
    f"rgba(129,184,190,{0.15 + (p / 100) * 0.85:.2f})"
    for p in today_df["precipitation_probability"]
]

# バブル内テキスト（20%以上のみ表示）
bubble_text = [
    f"{int(p)}%" if p >= 20 else "" for p in today_df["precipitation_probability"]
]

fig_today.add_trace(
    go.Scatter(
        x=today_df["date"],
        y=[0] * len(today_df),
        mode="markers+text",
        name="precipitation_probability",
        marker=dict(
            size=bubble_size,
            sizemode="diameter",
            color=bubble_colors,
            line=dict(width=0),
        ),
        text=bubble_text,
        textposition="middle center",
        textfont=dict(size=10, color="white"),
        hoverinfo="none",
        hovertemplate=None,
        showlegend=False,
    ),
    row=2,
    col=1,
)


# --- レイアウト ---
now = pd.Timestamp.now(tz=tz)
fig_today.update_layout(
    dragmode="zoom",
    height=300,
    margin=dict(l=20, r=20, t=30, b=20),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Zen Maru Gothic", size=12, color="#5f6f65"),
    hovermode="x unified",
    hoverdistance=200,
    showlegend=False,
    spikedistance=-1,
    xaxis=dict(hoverformat="%-m/%-d %-H:%M"),
)

now = pd.Timestamp.now(tz=tz)
# ── X軸（上：非表示 / 下：時刻ラベル） ───────────────────────────────
today_df["weather_type"] = today_df["weather_code"].apply(get_weather_type)

today_df["weather_icon"] = today_df["weather_type"].map(WEATHER_ICONS)


today_df["hour"] = today_df["date"].dt.hour

# ④ label（ここで全部使う）
today_df["x_label"] = (
    today_df["date"].dt.strftime("%H:%M").str.replace("^0", "", regex=True)
    + "<br>"
    + today_df["weather_icon"]
    + np.where(
        today_df["hour"].isin([0, 12]),
        "<br>" + today_df["date"].dt.strftime("%m/%d").str.lstrip("0"),
        "",
    )
)

fig_today.update_xaxes(
    fixedrange=False,
    row=1,
    col=1,
    showspikes=True,
    spikecolor="rgba(120,140,170,0.5)",
    spikethickness=1,
    spikedash="dot",
    spikesnap="data",
    spikemode="across",
    zeroline=True,
    zerolinecolor="rgba(0,0,0,1)",
    linewidth=1,  # シャープ黒
)
fig_today.update_xaxes(
    row=2,
    col=1,
    showspikes=True,
    spikecolor="rgba(120,140,170,0.5)",
    spikethickness=1,
    spikedash="dot",
    spikesnap="data",
    spikemode="across",
    tickmode="array",
    tickvals=today_df["date"],
    ticktext=today_df["x_label"],
    tickfont=dict(size=14),
    ticks="",  # 目盛り線は無し
    ticklen=0,  # 目盛り線の長さを0にして完全に消す
    showline=False,  # ← 軸ライン出す！
    linecolor="rgba(0,0,0,0.15)",  # 薄グレー
    linewidth=1,
    showgrid=False,
    zeroline=False,
    fixedrange=False,
    range=[now - pd.Timedelta(hours=2), now + pd.Timedelta(hours=16)],
)
# 気温（左）
fig_today.update_yaxes(
    fixedrange=True,
    title=None,
    ticksuffix="℃",
    gridcolor="rgba(0,0,0,0.05)",
    griddash="dot",
    showline=True,
    linewidth=0.02,
    linecolor="rgba(0,0,0,0.06)",
    ticks="",
    ticklen=0,
    tickfont=dict(size=14),
    range=[
        0,
        today_df["temperature_2m"].max() + 5,
    ],
    row=1,
    col=1,
    secondary_y=False,
)

fig_today.update_yaxes(
    fixedrange=True,
    title=None,
    ticksuffix="mm",
    range=[0, max(today_df["precipitation"].max() * 3, 5)],
    gridcolor="rgba(0,0,0,0.0)",
    zeroline=True,
    zerolinecolor="rgba(0,0,0,0.1)",  # シャープ黒
    zerolinewidth=0.06,
    ticks="",
    ticklen=0,
    tickfont=dict(size=14),
    row=1,
    col=1,
    secondary_y=True,
)
fig_today.update_yaxes(
    title=None,
    ticks="",
    ticklen=0,
    row=2,
    col=1,
    visible=False,
    zeroline=False,
    range=[-0.01, 0.01],
)
fig_today.add_shape(
    type="rect",
    xref="x",
    yref="y2",
    x0=today_df["date"].iloc[0],
    x1=today_df["date"].iloc[-1],
    y0=-1,
    y1=0,
    fillcolor="rgba(90,160,220,0.05)",
    line_width=0,
)
# ── 「mm」「℃」アノテーション ────────────────────────────────────────
# fig_today.add_annotation(
#     text="℃",
#     xref="paper",
#     yref="paper",
#     x=0,
#     y=1.02,
#     showarrow=False,
#     font=dict(size=10, color="#9aaa9f"),
# )
# fig_today.add_annotation(
#     text="mm",
#     xref="paper",
#     yref="paper",
#     x=1,
#     y=1.02,
#     showarrow=False,
#     font=dict(size=10, color="#9aaa9f"),
# )
fig_today.add_annotation(
    text="",
    xref="paper",
    yref="paper",
    x=0,
    y=0.22,
    showarrow=False,
    font=dict(size=10, color="#9aaa9f"),
    xanchor="left",
)
# ── 現在時刻の縦線 ────────────────────────────────────────────────────
now = pd.Timestamp.now(tz="Asia/Tokyo").floor("h")
fig_today.add_vline(
    x=now,
    line_width=1,
    line_dash="dash",
    line_color="rgba(120,140,170,0.45)",
    row="all",
    col=1,
)

# Information Card
rain_5days = past_7days_df["daily_precipitation_sum"].tail(5).sum()
df_12h = today_df[
    (today_df["date"] >= now) & (today_df["date"] <= now + pd.Timedelta(hours=12))
]
temp_max_12h = df_12h["temperature_2m"].max()
temp_min_12h = df_12h["temperature_2m"].min()

current_row = today_df[
    (today_df["date"] <= now) & (today_df["date"] > now - pd.Timedelta(minutes=30))
].tail(1)

is_raining_now = not current_row.empty and current_row["precipitation"].iloc[0] > 0
rain_future = today_df[(today_df["date"] > now) & (today_df["precipitation"] > 0)]

if is_raining_now:
    rain_start_time = "now"
elif not rain_future.empty:
    rain_start_time = rain_future["date"].iloc[0]
else:
    rain_start_time = "not rain"


def format_time(x):
    if x in ["now", "not rain"]:
        return x
    dt = pd.to_datetime(x)
    return f"{dt.month}/{dt.day} {dt.hour}:{dt.minute:02d}"


rain_start_time = format_time(rain_start_time)

# insight Card
insight_title = "💧 水やり推奨"
insight_text = (
    f"ここ5日間の降水量は{rain_5days:.0f}mmです。"
    f"今後12時間は最高{temp_max_12h:.0f}℃まで上がる予報です。"
)

if rain_start_time == "not rain" and rain_5days < 10:
    insight_title = "💧 水やり推奨"
    insight_text = "しばらく雨予報がなく、土が乾きやすい状況です。"

elif rain_start_time != "not rain":
    insight_title = "🌧️ 水やり不要"
    insight_text = "雨が予想されているため、水やりは様子見で良さそうです。"

else:
    insight_title = "🌱 状態良好"
    insight_text = "極端な乾燥や降雨は予想されていません。"

# Dash-------------------------------------------
app = Dash(
    __name__,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@400;500&display=swap"
    ],
    title="Plantly",
)


# future graph (Top-right) hover
@app.callback(
    Output("future-tooltip", "show"),
    Output("future-tooltip", "bbox"),
    Output("future-tooltip", "children"),
    Input("future-temp-graph", "hoverData"),
    Input("future-rain-graph", "hoverData"),
)
def display_hover_card(temp_hover, rain_hover):
    trigger = ctx.triggered_id

    if trigger == "future-temp-graph":
        hoverData = temp_hover
    elif trigger == "future-rain-graph":
        hoverData = rain_hover
    else:
        hoverData = None

    if hoverData is None:
        return False, no_update, no_update

    point = hoverData["points"][0]
    bbox = point["bbox"]
    date = pd.to_datetime(point["x"]).date()

    matched = future_7days_df[future_7days_df["date"].dt.date == date]

    if matched.empty:
        return False, no_update, no_update

    row = matched.iloc[0]

    return (
        True,
        bbox,
        html.Div(
            [
                # Top
                html.Div(
                    f"{row['date'].strftime('%m/%d').replace('/0', '/').lstrip('0')}"
                    f"{row['weather_icon']}",
                    style={
                        "fontSize": "16px",
                        "paddingLeft": "4px",
                        "marginBottom": "8px",
                    },
                ),
                # Bottom
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    f"{row['daily_temperature_2m_max']:.0f}℃",
                                    style={"color": "#d97366"},
                                ),
                                html.Div(
                                    f"{row['daily_temperature_2m_min']:.1f}℃",
                                    style={"color": "#7aa38b"},
                                ),
                            ],
                            style={"width": "62px"},
                        ),
                        html.Div(f"☔"),
                        html.Div(
                            [
                                html.Div(f"{row['daily_precipitation_sum']:.1f} mm"),
                                html.Div(
                                    f"{row['daily_precipitation_probability_max']:.0f}%"
                                ),
                            ],
                            style={"color": "#6f8fb8"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "center",
                        # "gap": "4px",
                        "fontSize": "12px",
                        "lineHeight": "1.4",
                    },
                ),
            ]
        ),
    )


# Current graph hover info-card
@app.callback(
    Output("today-tooltip", "show"),
    Output("today-tooltip", "bbox"),
    Output("today-tooltip", "children"),
    Input("today-graph", "hoverData"),
)
def display_today_hover(hoverData):

    if not hoverData:
        return False, no_update, no_update

    point = hoverData["points"][0]

    if "bbox" not in point:
        return False, no_update, no_update

    bbox = point["bbox"]

    date = pd.to_datetime(point["x"]).tz_localize(tz)
    matched = today_df[today_df["date"].dt.floor("h") == date.floor("h")]

    if matched.empty:
        return False, no_update, no_update

    row = matched.iloc[0]

    return (
        True,
        bbox,
        html.Div(
            [
                html.Div(
                    f"{row['date'].strftime('%H:%M')[1:] if row['date'].strftime('%H').startswith('0') else row['date'].strftime('%H:%M')} "
                    f"{row['weather_icon']}",
                    style={
                        "fontSize": "16px",
                        "marginBottom": "8px",
                    },
                ),
                html.Div(
                    [
                        html.Div(
                            f"{row['temperature_2m']:.1f}℃",
                            style={
                                "color": "#6fa08a",
                                "fontSize": "18px",
                                "fontWeight": "500",
                            },
                        ),
                        html.Div(
                            [
                                html.Div(
                                    f"☔",
                                    style={
                                        "marginRight": "6px",
                                    },
                                ),
                                html.Div(
                                    [
                                        html.Div(f"{row['precipitation']:.1f} mm"),
                                        html.Div(
                                            f"{row['precipitation_probability']:.0f}%"
                                        ),
                                    ],
                                ),
                            ],
                            style={
                                "display": "flex",
                                "color": "#6f8fb8",
                                "fontSize": "12px",
                            },
                        ),
                    ]
                ),
            ],
            style={
                "padding": "4px",
                "minWidth": "90px",
            },
        ),
    )


# #Interval
# @app.callback(
#     Output(...),
#     Input("interval-component", "n_intervals")
# )
# def update_data(n):
#     # API取得
#     # dataframe更新
#     # graph返す

# Dash---------------------------------------
app.layout = html.Div(
    [
        # dcc.Interval(
        #     id="interval-component",
        #     interval=60 * 60 * 1000,
        #     n_intervals=0,
        # ),
        # Most-Top
        html.Div(
            [
                # Title and insight card
                html.Div(
                    [
                        # Title Top-left
                        html.Div(
                            [
                                html.Img(
                                    src="assets/Plantly_icon.png",
                                    style={
                                        "width": "34px",
                                        "height": "34px",
                                        "marginLeft": "8px",
                                        "marginBottom": "-10px",
                                    },
                                ),
                                html.H1(
                                    "PLANTly",
                                    style={
                                        "marginTop": "0",
                                        "marginBottom": "-8px",
                                        "marginLeft": "6px",
                                        "fontSize": "38px",
                                        "fontWeight": "500",
                                        "color": "#5f6f65",
                                    },
                                ),
                            ],
                            style={
                                "display": "flex",
                                "alignItems": "center",
                                "gap": "0px",
                                "borderBottom": "4px solid rgba(120, 92, 62, 0.75)",
                                "paddingBottom": "0",
                            },
                        ),
                        html.Div(
                            [
                                html.Div(
                                    insight_title,
                                    style={
                                        "fontSize": "16px",
                                        "fontWeight": "500",
                                        "color": "#5f6f65",
                                    },
                                ),
                                html.Div(
                                    insight_text,
                                    style={
                                        "fontSize": "14px",
                                        "marginTop": "8px",
                                        "lineHeight": "1.5",
                                    },
                                ),
                            ],
                            style={
                                "backgroundColor": "#ece7dc",
                                "padding": "14px 18px",
                                "borderRadius": "20px",
                                "marginTop": "10px",
                                "boxShadow": "0 2px 8px rgba(0,0,0,0.05)",
                            },
                        ),
                    ]
                ),
                # Info card Top-right
                html.Div(
                    [
                        html.Div("💧Past 5days"),
                        html.Div(f"{rain_5days:.0f} mm"),
                        html.Div("🕰️Next"),
                        html.Div(
                            "------",
                            style={"color": "rgba(0,0,0,0.6)"},
                        ),
                        html.Div("🌡️12h Max"),
                        html.Div(
                            f"{temp_max_12h:.1f} ℃",
                            style={"color": "#e74c3c"},
                        ),
                        html.Div("🌡️12h min"),
                        html.Div(
                            f"{temp_min_12h:.1f} ℃",
                            style={"color": "#4dabf7"},
                        ),
                        html.Div("🌂Rain start"),
                        html.Div(f"{rain_start_time}"),
                    ],
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "auto 1fr",
                        "rowGap": "4px",
                        "columnGap": "8px",
                        "padding": "12px",
                        "backgroundColor": "#f3f1eb",
                        "borderRadius": "20px",
                        "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.1)",
                        "width": "220px",
                        "hight": "180px",
                        "fontSize": "16px",
                        "lineHeight": "1.2",
                        "marginLeft": "auto",
                        "position": "relative",
                        "zIndex": 10,
                    },
                ),
            ],
            style={"display": "flex", "gap": "10px", "alignItems": "flex-start"},
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
                        "height": "300px",
                        "backgroundColor": "#ece7dc",
                        "borderRadius": "20px",
                        "padding": "6px",
                        "boxShadow": "0 4px 12px rgba(0,0,0,0.05)",
                    },
                ),
                # Right
                html.Div(
                    [
                        dcc.Graph(
                            id="future-temp-graph",
                            figure=fig_future_temp,
                            clear_on_unhover=True,
                            style={
                                "flex": 7,
                                "minHeight": 0,
                                "marginBottom": "0px",
                            },
                            config={"displayModeBar": False},
                            responsive=True,
                        ),
                        dcc.Graph(
                            id="future-rain-graph",
                            figure=fig_future_rain,
                            clear_on_unhover=True,
                            style={"flex": 3, "minHeight": 0, "marginTop": "-10px,"},
                            config={"displayModeBar": False},
                            responsive=True,
                        ),
                        dcc.Tooltip(
                            id="future-tooltip",
                            targetable=False,
                            style={
                                "pointerEvents": "none",
                                "zIndex": 9999,
                                "backgroundColor": "rgba(255,255,255,0.95)",
                                "borderRadius": "19px",
                                "padding": "8px",
                                "boxShadow": "0 4px 12px rgba(0,0,0,0.12)",
                            },
                        ),
                    ],
                    style={
                        "width": "60%",
                        "height": "300px",
                        "display": "flex",
                        "flexDirection": "column",
                        "backgroundColor": "#ece7dc",
                        "borderRadius": "20px",
                        "padding": "6px",
                        "boxShadow": "0 4px 12px rgba(0,0,0,0.05)",
                        "position": "relative",
                    },
                ),
            ],
            style={
                "display": "flex",
                "gap": "15px",
            },
        ),
        # Bottom
        html.Div(
            [
                # left
                html.Div(""),
                # center
                html.Div(
                    [
                        dcc.Graph(
                            id="today-graph",
                            figure=fig_today,
                            clear_on_unhover=True,
                            style={
                                "height": "400px",
                                "width": "100%",
                                "padding": "0px",
                                "margin": "0",
                            },
                            config={"displayModeBar": False, "displaylogo": False},
                            responsive=True,
                        ),
                        dcc.Tooltip(
                            id="today-tooltip",
                            # direction="top",
                            style={
                                "zIndex": 9999,
                                "backgroundColor": "rgba(255,255,255,0.95)",
                                "borderRadius": "12px",
                                "padding": "8px",
                                "boxShadow": "0 4px 12px rgba(0,0,0,0.12)",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "position": "relative",
                        "overflow": "visible",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "padding": "0",
                        "margin": "0",
                        "width": "100%",
                        "height": "100%",
                    },
                ),
                # right
                html.Div(""),
            ],
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "stretch",
                "backgroundColor": "#ece7dc",
                "borderRadius": "20px",
                "padding": "4px",
                "marginTop": "15px",
                "boxShadow": "0 4px 12px rgba(0,0,0,0.05)",
            },
        ),
    ],
    style={
        "backgroundColor": "#c7e3c7",
        "minHeight": "60vh",
        "borderRadius": "20px",
        "padding": "20px",
        "margin": "0",
        "fontFamily": "Zen Maru Gothic",
        "position": "relative",
    },
)

app.run(debug=True)

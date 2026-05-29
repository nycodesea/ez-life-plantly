# Plantly
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
from config import URL, TZ, WEATHER_GROUPS, WEATHER_ICONS, API_PARAMS
import weather

weather_data = weather.load_weather_data()

past_7days_df = weather_data["past_7days_df"]
future_7days_df = weather_data["future_7days_df"]
daily_dataframe = weather_data["daily_dataframe"]
hourly_df = weather_data["hourly_df"]
today = weather_data["today"]


# Plotly
# Past 7days graph
def build_past7days_figure(past_7days_df):
    fig_past = px.bar(
        past_7days_df,
        x="date",
        y="precipitation_sum",
        custom_data=["precipitation_sum"],
    )
    fig_past.update_layout(
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
    )
    fig_past.update_traces(
        marker_color="#81b8be",
        hovertemplate="%{y:.2f}mm<br>" + "<extra></extra>",
    )
    fig_past.update_xaxes(
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
        past_7days_df["precipitation_sum"].max() + 2,
        10,
    )
    fig_past.update_yaxes(
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
    fig_past.add_annotation(
        text="mm",
        xref="paper",
        yref="paper",
        x=0,
        y=1,
        showarrow=False,
    )
    return fig_past


# future 7days graph
# future 7days graph : temperture max - min
def build_future7days_figure(future_7days_df):
    fig_future_temp = px.line(
        future_7days_df,
        x="date",
        y=[
            "temperature_2m_max",
            "temperature_2m_min",
        ],
        custom_data=[
            "precipitation_probability_max",
            "precipitation_sum",
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
        selector=dict(name="temperature_2m_max"),
        name="Max",
        line=dict(color="#d97366"),
        showlegend=False,
    )
    fig_future_temp.update_traces(
        selector=dict(name="temperature_2m_min"),
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
    temp_min = future_7days_df["temperature_2m_min"].min()
    temp_max = future_7days_df["temperature_2m_max"].max()

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
    future_7days_df = future_7days_df.copy()
    future_7days_df["label"] = [
        (
            "Tomorrow<br>" + icon
            if date == today + Timedelta(days=1)
            else date.strftime("%m/%d").replace("/0", "/").lstrip("0") + "<br>" + icon
        )
        for date, icon in zip(future_7days_df["date"], future_7days_df["weather_icon"])
    ]
    max_precipitation = future_7days_df["precipitation_sum"].max()
    future_7days_df["bubble_size"] = (
        future_7days_df["precipitation_sum"] + 40 if max_precipitation > 0 else 0
    )

    future_7days_df["bubble_text"] = future_7days_df[
        "precipitation_probability_max"
    ].apply(lambda x: f"{int(x)}%" if int(x) >= 10 else "")

    future_7days_df["bubble_opacity"] = (
        future_7days_df["precipitation_probability_max"] / 100
    )
    fig_future_rain = px.scatter(
        future_7days_df,
        x="date",
        y=[0.15] * len(future_7days_df),
        size="bubble_size",
        text="bubble_text",
        size_max=30,
        custom_data=[
            "precipitation_probability_max",
            "precipitation_sum",
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
    return fig_future_temp, fig_future_rain


# Today(hourly) graph
def build_today_figure(hourly_df):
    NOW = pd.Timestamp.now(tz=TZ)
    NOW_HOUR = NOW.floor("h")
    NOW_DAY = NOW.normalize()

    today_df = hourly_df.copy()
    today_df = today_df.reset_index(drop=True)
    today_df["x"] = today_df["date"]
    today_df["x_index"] = np.arange(len(today_df))

    fig_today = make_subplots(
        rows=2,
        cols=1,
        vertical_spacing=0.008,
        row_heights=[0.8, 0.2],
        shared_xaxes=True,
        specs=[[{"secondary_y": True}], [{}]],
    )
    # Temperature
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

    # Rain bar
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

    # Precipitation probability bubble

    bubble_size = 10 + today_df["precipitation_probability"] * 0.3

    bubble_colors = [
        f"rgba(129,184,190,{0.15 + (p / 100) * 0.85:.2f})"
        for p in today_df["precipitation_probability"]
    ]

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

    today_df["weather_type"] = today_df["weather_code"].apply(weather.get_weather_type)

    today_df["weather_icon"] = today_df["weather_type"].map(WEATHER_ICONS)

    today_df["hour"] = today_df["date"].dt.hour

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
        linewidth=1,
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
        ticks="",
        ticklen=0,
        showline=False,
        linecolor="rgba(0,0,0,0.15)",
        linewidth=1,
        showgrid=False,
        zeroline=False,
        fixedrange=False,
        range=[NOW_HOUR - pd.Timedelta(hours=2), NOW_HOUR + pd.Timedelta(hours=16)],
    )
    # temperature y-axis left
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
        zerolinecolor="rgba(0,0,0,0.1)",
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
    # bubble background for precipitation
    fig_today.add_shape(
        type="rect",
        xref="x",
        yref="y2",
        x0=today_df["date"].iloc[0],
        x1=today_df["date"].iloc[-1],
        y0=-1,
        y1=0,
        fillcolor="rgba(90,160,220,0.08)",
        line_width=0,
    )
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
    # vertical line for current time
    fig_today.add_vline(
        x=NOW_HOUR,
        line_width=1,
        line_dash="dash",
        line_color="rgba(120,140,170,0.45)",
        row="all",
        col=1,
    )
    return fig_today


# Information Card
def build_info_card(past_7days_df, today_hourly_df, now):
    rain_5days = past_7days_df["precipitation_sum"].tail(5).sum()
    df_12h = today_hourly_df[
        (today_hourly_df["date"] >= now)
        & (today_hourly_df["date"] <= now + pd.Timedelta(hours=12))
    ]
    if df_12h.empty:
        temp_max_12h = np.nan
    else:
        temp_max_12h = df_12h["temperature_2m"].max()

    if df_12h.empty:
        temp_min_12h = np.nan
    else:
        temp_min_12h = df_12h["temperature_2m"].min()

    current_row = today_hourly_df[
        (today_hourly_df["date"] <= now)
        & (today_hourly_df["date"] > now - pd.Timedelta(minutes=30))
    ].tail(1)

    is_raining_now = not current_row.empty and current_row["precipitation"].iloc[0] > 0
    rain_future = today_hourly_df[
        (today_hourly_df["date"] > now) & (today_hourly_df["precipitation"] > 0)
    ]

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
    return rain_5days, temp_max_12h, temp_min_12h, rain_start_time


# insight Card
def build_insight_card(
    rain_start_time, rain_5days, temp_max_12h, daily_dataframe, today
):
    # insight Water
    insight_water_title = "💧 Watering : "
    insight_water_text = (
        f"The total precipitation over the last 5 days is {rain_5days:.0f}mm."
        f"Over the next 12 hours, the temperature is expected to reach up to {temp_max_12h:.0f}℃."
    )

    if rain_start_time == "not rain" and rain_5days < 10:
        insight_water_title = "💧 Watering Recommended : "
        insight_water_text = (
            "No rain forecast for a while, and the soil is prone to drying out."
        )

    elif rain_start_time != "not rain":
        insight_water_title = "🌧️ No Need to Water : "
        insight_water_text = "Rain is forecast, so watering can be skipped for now."

    else:
        insight_water_title = "🌱 Good Conditions : "
        insight_water_text = "No extreme drought or rainfall expected."
    # insight Solar-ray
    today_uv = daily_dataframe.loc[
        daily_dataframe["date"].dt.normalize() == today,
        "uv_index_max",
    ].iloc[0]

    insight_solar_title = ""
    insight_solar_text = f""

    if today_uv >= 8:
        insight_solar_title = "⛱️UV : "
        insight_solar_text = "Danger⚡"
    elif today_uv > 5:
        insight_solar_title = "⛱️UV : "
        insight_solar_text = "Careful⚠️"
    else:
        insight_solar_title = "⛱️UV : "
        insight_solar_text = "👌"

    # insight some peaky scores

    return (
        insight_water_title,
        insight_water_text,
        insight_solar_title,
        insight_solar_text,
    )


# Dash
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
                                    f"{row['temperature_2m_max']:.0f}℃",
                                    style={"color": "#d97366"},
                                ),
                                html.Div(
                                    f"{row['temperature_2m_min']:.1f}℃",
                                    style={"color": "#7aa38b"},
                                ),
                            ],
                            style={"width": "62px"},
                        ),
                        html.Div(f"☔"),
                        html.Div(
                            [
                                html.Div(f"{row['precipitation_sum']:.1f} mm"),
                                html.Div(
                                    f"{row['precipitation_probability_max']:.0f}%"
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

    bbox = point.get("bbox")

    if bbox is None:
        return False, no_update, no_update

    date = pd.to_datetime(point["x"])
    if date.tzinfo is None:
        date = date.tz_localize(TZ)
    else:
        date = date.tz_convert(TZ)
    global hourly_df
    matched = hourly_df[hourly_df["date"].dt.floor("h") == date.floor("h")]

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


# Interval
@app.callback(
    Output("past-graph", "figure"),
    Output("future-temp-graph", "figure"),
    Output("future-rain-graph", "figure"),
    Output("today-graph", "figure"),
    Output("rain-5days-value", "children"),
    Output("temp-max-value", "children"),
    Output("temp-min-value", "children"),
    Output("rain-start-value", "children"),
    Output("insight-water", "children"),
    Output("insight-solar", "children"),
    Input("interval-component", "n_intervals"),
)
def update_data(n):
    weather_data = weather.load_weather_data()

    past_7days_df = weather_data["past_7days_df"]
    future_7days_df = weather_data["future_7days_df"]
    daily_dataframe = weather_data["daily_dataframe"]
    hourly_df = weather_data["hourly_df"]
    today = weather_data["today"]

    # graph rebuild
    fig_past = build_past7days_figure(past_7days_df)
    fig_future_temp, fig_future_rain = build_future7days_figure(future_7days_df)
    fig_today = build_today_figure(hourly_df)

    # info rebuild
    now = pd.Timestamp.now(tz=TZ)

    (
        rain_5days,
        temp_max_12h,
        temp_min_12h,
        rain_start_time,
    ) = build_info_card(
        past_7days_df,
        hourly_df,
        now,
    )

    # insight rebuild
    (
        insight_water_title,
        insight_water_text,
        insight_solar_title,
        insight_solar_text,
    ) = build_insight_card(
        rain_start_time,
        rain_5days,
        temp_max_12h,
        daily_dataframe,
        today,
    )

    return (
        fig_past,
        fig_future_temp,
        fig_future_rain,
        fig_today,
        f"{rain_5days:.0f} mm",
        f"{temp_max_12h:.1f} ℃",
        f"{temp_min_12h:.1f} ℃",
        rain_start_time,
        f"{insight_water_title}{insight_water_text}",
        f"{insight_solar_title}{insight_solar_text}",
    )


# Initial figures
fig_past = build_past7days_figure(past_7days_df)
fig_future_temp, fig_future_rain = build_future7days_figure(future_7days_df)
fig_today = build_today_figure(hourly_df)

# Initial info card
now = pd.Timestamp.now(tz=TZ)

(
    rain_5days,
    temp_max_12h,
    temp_min_12h,
    rain_start_time,
) = build_info_card(
    past_7days_df,
    hourly_df,
    now,
)

# Initial insight
(
    insight_water_title,
    insight_water_text,
    insight_solar_title,
    insight_solar_text,
) = build_insight_card(
    rain_start_time,
    rain_5days,
    temp_max_12h,
    daily_dataframe,
    today,
)
# Dash layout
app.layout = html.Div(
    [
        dcc.Interval(
            id="interval-component",
            interval=60 * 60 * 1000,
            n_intervals=0,
        ),
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
                                "borderBottom": "4px solid rgba(120, 92, 62, 0.65)",
                                "paddingBottom": "0",
                            },
                        ),
                        html.Div(
                            [
                                html.Div(
                                    id="insight-water",
                                    style={
                                        "fontSize": "14px",
                                        "fontWeight": "500",
                                        "color": "#5f6f65",
                                    },
                                ),
                                html.Div(
                                    id="insight-solar",
                                    style={
                                        "fontSize": "14px",
                                        "fontWeight": "500",
                                        "color": "#5f6f65",
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
                        html.Div(f"{rain_5days:.0f} mm", id="rain-5days-value"),
                        html.Div("🕰️Next"),
                        html.Div(
                            "------",
                            style={"color": "rgba(0,0,0,0.6)"},
                        ),
                        html.Div("🌡️12h Max"),
                        html.Div(
                            f"{temp_max_12h:.1f} ℃",
                            id="temp-max-value",
                            style={"color": "#e74c3c"},
                        ),
                        html.Div("🌡️12h min"),
                        html.Div(
                            f"{temp_min_12h:.1f} ℃",
                            id="temp-min-value",
                            style={"color": "#4dabf7"},
                        ),
                        html.Div("🌂Rain start"),
                        html.Div(f"{rain_start_time}", id="rain-start-value"),
                    ],
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "auto 1fr",
                        "rowGap": "1",
                        "columnGap": "8px",
                        "padding": "12px",
                        "backgroundColor": "#f3f1eb",
                        "borderRadius": "20px",
                        "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.1)",
                        "width": "220px",
                        "height": "auto",
                        "fontSize": "16px",
                        "lineHeight": "1.4",
                        "marginLeft": "auto",
                        "position": "relative",
                        "zIndex": 10,
                    },
                ),
            ],
            style={"display": "flex", "gap": "10px", "alignItems": "flex-start"},
        ),
        # Top graphs
        html.Div(
            [
                # Left
                html.Div(
                    [
                        dcc.Graph(
                            id="past-graph",
                            figure=fig_past,
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
                            style={
                                "flex": 3,
                                "minHeight": 0,
                                "marginTop": "-10px",
                            },
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
        # Bottom Graph
        html.Div(
            [
                # left
                # html.Div(""),
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
                # html.Div(""),
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

# if __name__ == "__main__":
#     app.run(debug=False, host="0.0.0.0", port=8050)

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pandas import Timedelta
from plotly.subplots import make_subplots
from utils import get_now
import numpy as np
from config import WEATHER_ICONS
import weather


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
def build_future7days_figure(future_7days_df, today):
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
        showline=False,
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
        future_7days_df["precipitation_sum"] + 60 if max_precipitation > 0 else 0
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
        textfont_size=12,
        textfont_color="white",
        textposition="middle center",
        marker=dict(
            color="#81b8be",
            sizemode="area",
            opacity=future_7days_df["bubble_opacity"],
            line=dict(width=0),
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
        showline=False,
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
        showline=False,
        linecolor="rgba(0,0,0,0)",
    )
    return fig_future_temp, fig_future_rain


# Today(hourly) graph
def build_today_figure(hourly_df):
    time_info = get_now()
    now = time_info["now"]
    now_hour = time_info["hour"]
    now_day = time_info["day"]

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
        tickvals=today_df["date"][::2],
        ticktext=today_df["x_label"][::2],
        tickfont=dict(size=14),
        ticks="",
        ticklen=0,
        showline=False,
        linecolor="rgba(0,0,0,0.15)",
        linewidth=1,
        showgrid=False,
        zeroline=False,
        fixedrange=False,
        range=[now_hour - pd.Timedelta(hours=2), now_hour + pd.Timedelta(hours=16)],
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
        x=now_hour,
        line_width=1,
        line_dash="dash",
        line_color="rgba(120,140,170,0.45)",
        row="all",
        col=1,
    )
    return fig_today

# Plantly
from dash import Dash
from callbacks import register_callbacks
from layout import create_layout
from graphs import (
    build_past7days_figure,
    build_future7days_figure,
    build_today_figure,
)
import weather
from utils import get_now
from cards import build_info_card, build_insight_card
from database import (
    init_db,
    save_missing_7days,
)
from flask import request, jsonify

weather_data = weather.load_weather_data()

past_7days_df = weather_data["past_7days_df"]
future_7days_df = weather_data["future_7days_df"]
daily_dataframe = weather_data["daily_dataframe"]
hourly_df = weather_data["hourly_df"]
today = weather_data["today"]

print(daily_dataframe)
# Dash
app = Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@400;500&display=swap"
    ],
    title="Plantly",
)
# API
server = app.server
latest_humidity_data = {}


# API receives humidity data
@server.route("/api/sensor", methods=["POST"])
def receive_humidity_data():
    global latest_humidity_data

    latest_humidity_data = request.get_json()
    print("Received humidity data:", latest_humidity_data)

    return jsonify({"message": "Data received successfully"}), 200


# API Send next 3days weather rain sum
@server.route("/api/weather")
def get_weather():
    rain_3days_sum = round(float(daily_dataframe["rain_sum"][7:11].sum()), 1)
    return jsonify({"next_3days_rain_sum": rain_3days_sum})


# Register callbacks
register_callbacks(app, weather_data)

# Initial figures
fig_past = build_past7days_figure(past_7days_df)
fig_future_temp, fig_future_rain = build_future7days_figure(future_7days_df, today)
fig_today = build_today_figure(hourly_df)

now = get_now()["now"]
# Initial info card
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

# Initial insight card
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
app.layout = create_layout(
    fig_past,
    fig_future_temp,
    fig_future_rain,
    fig_today,
    rain_5days,
    temp_max_12h,
    temp_min_12h,
    rain_start_time,
)
# for Debug
# app.run(debug=True)

# for Server
if __name__ == "__main__":
    init_db()
    save_missing_7days(past_7days_df)
    app.run(debug=False, host="0.0.0.0", port=8050)

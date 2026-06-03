import json

with open("settings.json", encoding="utf-8") as f:
    settings = json.load(f)

# URL OpenMeteo
URL = "https://api.open-meteo.com/v1/forecast"

# Timezone
TZ = settings["timezone"]
LATITUDE = settings["latitude"]
LONGITUDE = settings["longitude"]
REFRESH_INTERVAL = 60 * 60 * 1000
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

WEATHER_ICONS = {
    "sunny": "☀️",
    "cloudy": "☁️",
    "fog": "🌫",
    "drizzle": "🌂",
    "rain": "🌧️",
    "snow": "❄️",
    "thunder": "⚡",
}

API_PARAMS = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
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
        "uv_index_max",
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
    "timezone": TZ,
    "past_days": 7,
    "wind_speed_unit": "ms",
}

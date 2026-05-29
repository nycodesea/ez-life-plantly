from config import WEATHER_GROUPS, WEATHER_ICONS, URL, API_PARAMS, TZ
import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
from pandas import Timedelta

cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


# get api and data process
def load_weather_data():
    responses = openmeteo.weather_api(URL, params=API_PARAMS)
    response = responses[0]

    hourly_df = process_hourly_data(response)
    daily_dataframe = process_daily_data(response)

    today, past_7days_df, future_7days_df = make_date_span(daily_dataframe)

    return {
        "hourly_df": hourly_df,
        "daily_dataframe": daily_dataframe,
        "today": today,
        "past_7days_df": past_7days_df,
        "future_7days_df": future_7days_df,
    }


def process_daily_data(response):
    # Process daily data.
    daily = response.Daily()
    daily_vars = API_PARAMS["daily"]

    daily_data = {
        var: daily.Variables(i).ValuesAsNumpy() for i, var in enumerate(daily_vars)
    }

    daily_data["date"] = pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left",
    ).tz_convert(response.Timezone().decode())

    daily_dataframe = pd.DataFrame(data=daily_data)
    daily_dataframe = add_weather_columns(daily_dataframe)

    daily_dataframe["label"] = (
        daily_dataframe["date"]
        .dt.strftime("%m/%d")
        .str.replace("/0", "/")
        .str.lstrip("0")
        + "<br>"
        + daily_dataframe["weather_icon"]
    )

    return daily_dataframe


def process_hourly_data(response):
    # Process hourly data
    hourly = response.Hourly()

    hourly_vars = API_PARAMS["hourly"]

    hourly_data = {
        var: hourly.Variables(i).ValuesAsNumpy() for i, var in enumerate(hourly_vars)
    }

    hourly_df = pd.DataFrame(hourly_data)
    hourly_df = add_weather_columns(hourly_df)

    hourly_df["date"] = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left",
    ).tz_convert(response.Timezone().decode())

    return hourly_df


def get_weather_type(code):
    for weather_type, codes in WEATHER_GROUPS.items():
        if code in codes:
            return weather_type
    return "unknown"


def add_weather_columns(df):
    df["weather_type"] = df["weather_code"].apply(get_weather_type)
    df["weather_icon"] = df["weather_type"].map(WEATHER_ICONS)
    return df


def make_date_span(daily_dataframe):
    # date span
    today = pd.Timestamp.now(tz=TZ).normalize()
    tomorrow = today + Timedelta(days=1)

    past_7days_df = daily_dataframe[daily_dataframe["date"] < today]
    future_7days_df = daily_dataframe[daily_dataframe["date"] >= tomorrow]

    return today, past_7days_df, future_7days_df

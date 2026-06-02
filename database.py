import sqlite3
from utils import get_now
import pandas as pd

DB_PATH = "weather.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS weather_history (
        date TEXT PRIMARY KEY,
        temp_max REAL,
        temp_min REAL,
        precipitation_sum REAL,
        uv_max REAL
    )
    """)

    conn.commit()
    conn.close()


def save_daily_weather(
    date,
    temp_max,
    temp_min,
    precipitation_sum,
    uv_max,
):
    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        """
        INSERT OR IGNORE INTO weather_history
        (date, temp_max, temp_min, precipitation_sum, uv_max)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            date,
            temp_max,
            temp_min,
            precipitation_sum,
            uv_max,
        ),
    )

    conn.commit()
    conn.close()


def save_yesterday_weather(past_7days_df):
    yesterday = get_now()["day"] - pd.Timedelta(days=1)
    yesterday_df = past_7days_df[past_7days_df["date"].dt.date == yesterday.date()]
    # Save the yesterday's weather data to the database
    if not yesterday_df.empty:
        row = yesterday_df.iloc[0]
        save_daily_weather(
            date=str(row["date"].date()),
            temp_max=float(row["temperature_2m_max"]),
            temp_min=float(row["temperature_2m_min"]),
            precipitation_sum=float(row["precipitation_sum"]),
            uv_max=float(row["uv_index_max"]),
        )
    else:
        print("No weather data available for yesterday.")

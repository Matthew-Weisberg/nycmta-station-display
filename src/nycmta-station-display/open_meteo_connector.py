import openmeteo_requests

import numpy as np
import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import datetime, timedelta
import pytz

class OpenMeteoConnector():
    def __init__(self,
                 latitude,
                 longitude,
                 timezone="America/New_York",
                 temperature_unit="fahrenheit",
                 wind_speed_unit="mph",
                 precipitation_units="inch"):
            
        # Setup the Open-Meteo API client with cache and retry on error
        self.cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        self.retry_session = retry(self.cache_session, retries = 5, backoff_factor = 0.2)
        self.openmeteo = openmeteo_requests.Client(session = self.retry_session)

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        self.url = "https://api.open-meteo.com/v1/forecast"
        self.params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "uv_index_max",
            "hourly": ["weather_code", "temperature_2m", "precipitation_probability"],
            "current": ["temperature_2m", "weather_code", "apparent_temperature", "relative_humidity_2m", "precipitation", "wind_speed_10m"],
            "timezone": timezone,
            "forecast_days": 2,
            "wind_speed_unit": wind_speed_unit,
            "temperature_unit": temperature_unit,
            "precipitation_unit": precipitation_units
        }

    def update_lat_lon(self,
                       latitude,
                       longitude):
        self.params['latitude'] = latitude
        self.params['longitude'] = longitude

    def get_response(self):
        responses = self.openmeteo.weather_api(self.url, 
                                               params=self.params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation {response.Elevation()} m asl")
        print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        # Current values. The order of variables needs to be the same as requested.
        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()
        current_weather_code = current.Variables(1).Value()
        current_apparent_temperature = current.Variables(2).Value()
        current_relative_humidity_2m = current.Variables(3).Value()
        current_precipitation = current.Variables(4).Value()
        current_wind_speed_10m = current.Variables(5).Value()

        current_data = {
            "temperature_2m" : str(round(current_temperature_2m)),
            "weather_code" : str(int(current_weather_code)),
            "apparent_temperature" : str(round(current_apparent_temperature)),
            "relative_humidity_2m" : str(round(current_relative_humidity_2m)),
            "precipitation" : str(round(current_precipitation)),
            "wind_speed_10m" : str(round(current_wind_speed_10m, 1))
        }

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_weather_code = hourly.Variables(0).ValuesAsNumpy()
        hourly_temperature_2m = hourly.Variables(1).ValuesAsNumpy()
        hourly_precipitation_probability = hourly.Variables(2).ValuesAsNumpy()

        # Generate UTC date range
        hourly_utc = pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )

        # Convert to local timezone
        hourly_local = hourly_utc.tz_convert(self.params["timezone"])

        hourly_data = {"date": hourly_local}

        hourly_data["weather_code"] = hourly_weather_code
        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["precipitation_probability"] = hourly_precipitation_probability

        hourly_dataframe = pd.DataFrame(data = hourly_data)

        # Get current time rounded to nearest hour
        now = pd.Timestamp.now(tz=self.params["timezone"])
        minute = now.minute
        if minute < 30:
            rounded = now.replace(minute=0, second=0, microsecond=0)
        else:
            rounded = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

        # Generate target times: next 8 hours in 2-hour intervals
        interval_times = [rounded + timedelta(hours=2 * i - 1) for i in range(1, 5)]

        # Initialize list for selected rows
        rows = []

        for target_time in interval_times:
            # Find the exact row for the target time
            row = hourly_dataframe.loc[hourly_dataframe['date'] == target_time]

            # Calculate the max precipitation probability in the previous hour
            prev_start = target_time - timedelta(hours=1)
            prev_hour = hourly_dataframe[
                (hourly_dataframe['date'] >= prev_start) &
                (hourly_dataframe['date'] < target_time)
            ]
            
            max_precip = prev_hour['precipitation_probability'].max() if not prev_hour.empty else np.nan

            # Append the row with the max_precip info
            if not row.empty:
                row = row.copy()
                row['max_precip_last_hour'] = max_precip

                # Convert weather_code to string int (no decimal)
                row['weather_code'] = row['weather_code'].astype(int).astype(str)

                # Add hour label in AM/PM format
                row['hour_label'] = pd.to_datetime(row['date']).dt.strftime("%I %p").str.lstrip('0')  # Always remove leading zero


                rows.append(row)

        # Combine all selected rows
        hourly_dataframe = pd.concat(rows).reset_index(drop=True)
        print(hourly_dataframe)

        # Process daily data. The order of variables needs to be the same as requested.
        daily = response.Daily()
        daily_uv_index_max = daily.Variables(0).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        )}

        daily_data["uv_index_max"] = daily_uv_index_max

        daily_dataframe = pd.DataFrame(data = daily_data)
        print(daily_dataframe)

        return [current_data, hourly_dataframe, daily_data]
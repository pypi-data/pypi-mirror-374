import io
import csv
import base64
import matplotlib.pyplot as plt
import requests
from .geocode import geocode_city


BASE_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def get_forecast_by_city(city: str, days: int = 3):
    """Prévisions météo (1-7 jours) pour une ville donnée."""
    lat, lon = geocode_city(city)
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
    }
    resp = requests.get(BASE_FORECAST_URL, params=params)
    resp.raise_for_status()
    data = resp.json()
    return {
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "dates": data["daily"]["time"][:days],
        "temp_max": data["daily"]["temperature_2m_max"][:days],
        "temp_min": data["daily"]["temperature_2m_min"][:days],
        "precipitation": data["daily"]["precipitation_sum"][:days],
    }


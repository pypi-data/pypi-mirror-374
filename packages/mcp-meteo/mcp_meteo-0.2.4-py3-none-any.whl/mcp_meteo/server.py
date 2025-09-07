from fastmcp import FastMCP
import requests
from mcp_meteo.geocode import geocode_city

BASE_GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
BASE_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
BASE_AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
BASE_MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"
BASE_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
BASE_SEASONAL_URL = "https://seasonal-api.open-meteo.com/v1/seasonal"
BASE_ENSEMBLE_URL = "https://ensemble-api.open-meteo.com/v1/ensemble"



def main():
    mcp = FastMCP("mcp-meteo")

    @mcp.tool
    def get_weather_by_city(city: str):
        """Météo actuelle pour une ville donnée."""
        lat, lon = geocode_city(city)
        params = {"latitude": lat, "longitude": lon, "current_weather": True}
        resp = requests.get(BASE_FORECAST_URL, params=params)
        resp.raise_for_status()
        return {
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "current_weather": resp.json().get("current_weather", {}),
        }

    @mcp.tool
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
    
    @mcp.tool
    def get_air_quality_by_city(city: str):
        """Qualité de l'air pour une ville donnée."""
        lat, lon = geocode_city(city)
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone",
        }
        resp = requests.get(BASE_AIR_QUALITY_URL, params=params)
        resp.raise_for_status()
        return {"city": city, "data": resp.json()}

    @mcp.tool
    def get_marine_forecast_by_city(city: str):
        """Prévisions marines (vagues, houle, etc.) pour une ville donnée."""
        lat, lon = geocode_city(city)
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "wave_height,wave_direction,wave_period,wind_wave_height",
            "timezone": "auto",
        }
        resp = requests.get(BASE_MARINE_URL, params=params)
        resp.raise_for_status()
        return {"city": city, "data": resp.json()}

    @mcp.tool
    def get_archive_weather_by_city(city: str, start_date: str, end_date: str):
        """Données météo historiques pour une ville (format date YYYY-MM-DD)."""
        lat, lon = geocode_city(city)
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto",
        }
        resp = requests.get(BASE_ARCHIVE_URL, params=params)
        resp.raise_for_status()
        return {"city": city, "data": resp.json()}

    @mcp.tool
    def get_seasonal_forecast_by_city(city: str):
        """Prévisions saisonnières (long terme) pour une ville donnée."""
        lat, lon = geocode_city(city)
        params = {"latitude": lat, "longitude": lon}
        resp = requests.get(BASE_SEASONAL_URL, params=params)
        resp.raise_for_status()
        return {"city": city, "data": resp.json()}

    @mcp.tool
    def get_ensemble_forecast_by_city(city: str):
        """Prévisions probabilistes (ensembles) pour une ville donnée."""
        lat, lon = geocode_city(city)
        params = {"latitude": lat, "longitude": lon, "hourly": "temperature_2m"}
        resp = requests.get(BASE_ENSEMBLE_URL, params=params)
        resp.raise_for_status()
        return {"city": city, "data": resp.json()}

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

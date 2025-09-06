# server.py
from fastmcp import FastMCP
import requests



BASE_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
BASE_GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"


def main():
    mcp = FastMCP("mcp-meteo")


    @mcp.tool
    def get_weather(latitude: float, longitude: float):
        """
        Récupère la météo actuelle à partir de l'API Open-Meteo.
        Args:
            latitude: Latitude du lieu
            longitude: Longitude du lieu
        """
        params = {"latitude": latitude, "longitude": longitude, "current_weather": True}
        response = requests.get(BASE_FORECAST_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("current_weather", {})


    @mcp.tool
    def get_weather_by_city(city: str):
        """
        Récupère la météo actuelle pour une ville donnée.
        Args:
            city: Nom de la ville (ex: "Paris")
        """
        geo_params = {"name": city, "count": 1}
        geo_resp = requests.get(BASE_GEOCODE_URL, params=geo_params)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()

        if not geo_data.get("results"):
            return {"error": f"Ville '{city}' introuvable"}

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        weather_params = {"latitude": lat, "longitude": lon, "current_weather": True}
        weather_resp = requests.get(BASE_FORECAST_URL, params=weather_params)
        weather_resp.raise_for_status()
        weather_data = weather_resp.json()

        return {
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "current_weather": weather_data.get("current_weather", {}),
        }


    @mcp.tool
    def get_forecast(latitude: float, longitude: float, days: int = 3):
        """
        Récupère la prévision météo pour plusieurs jours.
        Args:
            latitude: Latitude du lieu
            longitude: Longitude du lieu
            days: Nombre de jours (1-7)
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto",
        }
        response = requests.get(BASE_FORECAST_URL, params=params)
        response.raise_for_status()
        data = response.json()

        return {
            "dates": data["daily"]["time"][:days],
            "temp_max": data["daily"]["temperature_2m_max"][:days],
            "temp_min": data["daily"]["temperature_2m_min"][:days],
            "precipitation": data["daily"]["precipitation_sum"][:days],
        }


    @mcp.tool
    def get_forecast_by_city(city: str, days: int = 3):
        """
        Récupère la prévision météo pour plusieurs jours, à partir du nom d'une ville.
        Args:
            city: Nom de la ville (ex: "Paris")
            days: Nombre de jours (1-7)
        """
        geo_params = {"name": city, "count": 1}
        geo_resp = requests.get(BASE_GEOCODE_URL, params=geo_params)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()

        if not geo_data.get("results"):
            return {"error": f"Ville '{city}' introuvable"}

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        forecast_params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto",
        }
        forecast_resp = requests.get(BASE_FORECAST_URL, params=forecast_params)
        forecast_resp.raise_for_status()
        forecast_data = forecast_resp.json()

        return {
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "dates": forecast_data["daily"]["time"][:days],
            "temp_max": forecast_data["daily"]["temperature_2m_max"][:days],
            "temp_min": forecast_data["daily"]["temperature_2m_min"][:days],
            "precipitation": forecast_data["daily"]["precipitation_sum"][:days],
        }

    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
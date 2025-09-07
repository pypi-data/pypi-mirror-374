import requests


BASE_GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"

def geocode_city(city: str):
    """Renvoie (lat, lon) pour une ville donnée."""
    geo_params = {"name": city, "count": 1}
    geo_resp = requests.get(BASE_GEOCODE_URL, params=geo_params)
    geo_resp.raise_for_status()
    geo_data = geo_resp.json()
    if not geo_data.get("results"):
        raise ValueError(f"Ville '{city}' introuvable")
    return geo_data["results"][0]["latitude"], geo_data["results"][0]["longitude"]

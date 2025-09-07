
# MCP-Meteo

Ce projet est un serveur MCP (Model Context Protocol) permettant d'obtenir des informations météo en temps réel ou en prévision, basé sur l'API Open-Meteo.

## Fonctionnalités

- **Météo actuelle par coordonnées** : Obtenez la météo actuelle en fournissant la latitude et la longitude.
- **Météo actuelle par ville** : Obtenez la météo actuelle en indiquant le nom d'une ville.
- **Prévisions météo (1 à 7 jours) par coordonnées** : Récupérez les prévisions pour plusieurs jours en fournissant la latitude et la longitude.
- **Prévisions météo (1 à 7 jours) par ville** : Récupérez les prévisions pour plusieurs jours en indiquant le nom d'une ville.

## Installation

1. Clonez le dépôt :
	```sh
	git clone <url-du-repo>
	```
2. Installez les dépendances (voir `pyproject.toml`) :
	```sh
	pip install -r requirements.txt
	```
	ou
	```sh
	pip install fastmcp requests
	```

## Utilisation

Lancez le serveur MCP :
```sh
python -m mcp-meteo.server
```
Le serveur démarre en mode `stdio` et expose plusieurs outils MCP pour interroger la météo.

## Intégrer directement à Claude Desktop/VS code

Config json nécessaire 

```json
{
    "mcpServers":{
        "meteo":{
            "command":"uvx",
            "args": "mcp-meteo"
        }
    }
}
```

## Structure du projet

- `mcp-meteo/server.py` : Serveur MCP principal, expose les outils météo.
- `client_test.py` : Exemple de client.
- `pyproject.toml` : Dépendances et configuration du projet.


## API utilisées

- [Open-Meteo Forecast](https://open-meteo.com/)
- [Open-Meteo Geocoding](https://open-meteo.com/en/docs/geocoding-api)

## Liste d'outils MCP

- `get_weather(latitude, longitude)`
- `get_weather_by_city(city)`
- `get_forecast(latitude, longitude, days)`
- `get_forecast_by_city(city, days)`



## Licence

Ce projet est open-source, voir le fichier `LICENSE` si présent.
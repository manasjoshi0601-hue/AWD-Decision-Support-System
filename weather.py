import requests
import earth_engine



BASE_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather_data():
    """
    Returns weather information required
    for the AWD model.
    """

    latitude, longitude = earth_engine.get_field_center()

    params = {
    "latitude": latitude,
    "longitude": longitude,

    "current": [
        "temperature_2m"
    ],

    "daily": [
        "et0_fao_evapotranspiration",
        "rain_sum"
    ],

    "forecast_days": 3,
    "timezone": "auto"
}

    response = requests.get(BASE_URL, params=params)

    response.raise_for_status()

    data = response.json()

    current = data["current"]
    daily = data["daily"]

    return {

        "temperature": current["temperature_2m"],

        "eto": daily["et0_fao_evapotranspiration"][0],

        "forecast": {

            "day1": daily["rain_sum"][0],
            "day2": daily["rain_sum"][1],
            "day3": daily["rain_sum"][2]

        }

    }
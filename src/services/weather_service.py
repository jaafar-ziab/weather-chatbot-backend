from collections import defaultdict
from datetime import datetime
import requests
from fastapi import HTTPException
import logging
import math
from ..config import config, CommonTileProviders


def geocode(location: str) -> dict:
    """
    This function uses OpenWeatherMap geocoding API to convert a place name into latitude/longitude.
    """
    params = {"q": location, "limit": 1, "appid": config.OWM_KEY}
    r = requests.get(config.OWM_URL, params=params, timeout=20)
    r.raise_for_status()
    items = r.json()
    if not items:
        raise HTTPException(404, "Location not found")
    item = items[0]
    logging.info(f"get the latitude and longitude for {location}")
    return item


def get_weather(location: str, units: str) -> list[dict]:
    """
    This function uses OWM_CURRENT to fetch current weather data.
    """
    coordinates = geocode(location)
    latitude = float(coordinates["lat"])
    longitude = float(coordinates["lon"])
    u = "imperial" if units=="F" else "metric"
    params = {"lat": latitude, "lon": longitude, "appid": config.OWM_KEY, "units": u}
    r = requests.get(config.OWM_CURRENT, params=params, timeout=20)
    r.raise_for_status()
    weather = r.json()
    main = weather["weather"][0]["description"].capitalize()
    temp = round(weather["main"]["temp"])
    reply = f"{location}: {main}, {temp}{units}"
    follow_up_message = "would you like to know the 5 days forecast"
    logging.info(f"get the current weather for {location}")
    return [{
        "weather": reply,
        "followups": follow_up_message
    }]

def get_forcast(location: str, units: str):
    """
    This function uses OWM_FORECAST to fetch 5-day weather forecast data.
    """
    coordinates = geocode(location)
    latitude = float(coordinates["lat"])
    longitude = float(coordinates["lon"])
    u = "metric" if units=="C" else "imperial"
    params = {"lat": latitude, "lon": longitude, "appid": config.OWM_KEY, "units": u}
    r = requests.get(config.OWM_FORECAST, params=params, timeout=20)
    r.raise_for_status()
    raw =r.json()
    daily = defaultdict(list)
    for entry in raw["list"]:
        dt = datetime.fromtimestamp(entry["dt"])
        date_key = dt.strftime("%Y-%m-%d")
        temp = entry["main"]["temp"]
        desc = entry["weather"][0]["description"]
        daily[date_key].append((temp, desc, dt))
    weather_forecast = []
    for i, (date_key, items) in enumerate(sorted(daily.items())):
        if i >= 5:
            break
        avg_temp = round(sum(t for t, _, _ in items) / len(items))
        _, main_desc, dt = items[len(items) // 2]  # midday description
        day_label = dt.strftime("%A %Y-%m-%d")
        weather_forecast.append(f"{day_label}: {main_desc}, {avg_temp}°{units}\n")
    logging.info(f"get the forecast for {location}")
    return weather_forecast

def get_air_quality(location: str) -> list[dict]:
    """
    This function uses OWM_AIR to fetch air quality data.
    """
    coordinates = geocode(location)
    latitude = float(coordinates["lat"])
    longitude = float(coordinates["lon"])
    params = {"lat": latitude, "lon": longitude, "appid": config.OWM_KEY}
    r = requests.get(config.OWM_AIR, params=params, timeout=20)

    r.raise_for_status()
    data = r.json()
    follow_up_message = "would you like to provide you with the coordinates for the location"
    logging.info(f"get the air quality data for {location}")
    return [{
        "air-quality": data,
        "followups": follow_up_message
    }]


def get_map_tile_url(location: str, zoom: int = 10,
                     map_type: str = CommonTileProviders.STANDARD) -> dict:
    """
    This function generates a map tile URL for a given location using common tile providers.
    """
    coordinates = geocode(location)
    latitude = float(coordinates["lat"])
    longitude = float(coordinates["lon"])

    def deg2num(lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return (xtile, ytile)

    x, y = deg2num(latitude, longitude, zoom)

    base_url = CommonTileProviders.STANDARD
    tile_url = base_url.replace("{z}", str(zoom)).replace("{x}", str(x)).replace("{y}", str(y))
    logging.info(f"get the map tile URL for {location}")
    return {
        "tile_url": tile_url,
        "latitude": latitude,
        "longitude": longitude,
        "zoom": zoom,
        "tile_x": x,
        "tile_y": y,
        "map_type": map_type
    }
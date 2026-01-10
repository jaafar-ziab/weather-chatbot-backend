## Geocoding Strategy
Purpose: Converts human-readable location names to GPS coordinates.
Implementation:
```python
def geocode(location: str) -> dict:
    """
    Convert location name to latitude/longitude using OpenWeatherMap Geocoding API.
    
    Returns: {
        "name": "Berlin",
        "lat": 52.5200,
        "lon": 13.4050,
        "country": "DE"
    }
    """
    params = {"q": location, "limit": 1, "appid": config.OWM_KEY}
    r = requests.get(config.OWM_URL, params=params, timeout=20)
    r.raise_for_status()
    items = r.json()
    
    if not items:
        raise HTTPException(404, "Location not found")
    
    return items[0]
```
Why Separate Function:
 * Centralized error handling for "location not found"
 * Reused by all weather functions (DRY principle)
 * Single point for caching implementation (future optimization)
 * Consistent coordinate precision across services

API Choice: OpenWeatherMap's geocoding returns standardized results with country codes, alternative spellings, and coordinate precision indicators.

## Current Weather Implementation
Data Extraction Philosophy:
```python
def get_weather(location: str, units: str) -> list[dict]:
    """
    Fetch current weather conditions.
    
    Returns: [{
        "weather": "Berlin: Cloudy, 15C",
        "followups": "would you like to know the 5 days forecast"
    }]
    """
    coordinates = geocode(location)
    u = "imperial" if units == "F" else "metric"
    
    params = {"lat": coordinates["lat"], "lon": coordinates["lon"], 
              "appid": config.OWM_KEY, "units": u}
    r = requests.get(config.OWM_CURRENT, params=params, timeout=20)
    r.raise_for_status()
    weather = r.json()
    
    main = weather["weather"][0]["description"].capitalize()
    temp = round(weather["main"]["temp"])
    return [{"weather": f"{location}: {main}, {temp}{units}", 
             "followups": "would you like to know the 5 days forecast"}]
```
Why Simplify Data:
Raw API responses contain 50+ fields (humidity, pressure, wind speed, visibility, etc.). Returning everything:
 * Overwhelms AI with irrelevant data
 * Increases token usage (costs more, slower responses)
 * Makes caching less effective
 * Complicates error handling

Unit Conversion Handling:
 * API accepts "metric" or "imperial"
 * Users think in "C" or "F"
 * Conversion happens at boundary (user input → API format)
 * Temperature rounded for readability

## Forecast Processing
Challenge: API returns 40 data points (5 days × 8 timestamps/day).
Aggregation Strategy:
```python
def get_forcast(location: str, units: str):
    """
    Fetch 5-day forecast with daily aggregation.
    
    Returns: [
        "Monday 2025-01-06: Clear sky, 18°C\n",
        "Tuesday 2025-01-07: Rainy, 15°C\n",
        ...
    ]
    """
    # Fetch forecast data
    raw = requests.get(config.OWM_FORECAST, params=params).json()
    
    # Group by date
    daily = defaultdict(list)
    for entry in raw["list"]:
        dt = datetime.fromtimestamp(entry["dt"])
        date_key = dt.strftime("%Y-%m-%d")
        daily[date_key].append((entry["main"]["temp"], 
                                entry["weather"][0]["description"], dt))
    
    # Calculate daily averages
    weather_forecast = []
    for date_key, items in sorted(daily.items())[:5]:
        avg_temp = round(sum(t for t, _, _ in items) / len(items))
        _, main_desc, dt = items[len(items) // 2]  # Midday description
        day_label = dt.strftime("%A %Y-%m-%d")
        weather_forecast.append(f"{day_label}: {main_desc}, {avg_temp}°{units}\n")
    
    return weather_forecast
```
Why Average Temperature:
 * Represents typical conditions better than max/min
 * Matches user expectations ("What will tomorrow be like?")
 * Reduces confusion from overnight lows in daytime-focused conversations

Why Midday Description:
 * Most representative of "daytime" weather
 * Users asking about forecast typically care about waking hours
 * Avoids overnight rain/snow skewing perception

Format Choice:Returns list of strings rather than structured objects because:
 * AI formatting becomes easier (just join strings)
 * Human-readable in logs and debugging
 * Simpler error handling (partial data doesn't break structure)
 * Frontend can display immediately without parsing

## Air Quality Design
Return Full Data:
```python
def get_air_quality(location: str) -> list[dict]:
    """
    Fetch air quality index and pollutant levels.
    
    Returns: [{
        "air-quality": {
            "list": [{
                "main": {"aqi": 2},  # 1-5 scale
                "components": {
                    "co": 201.94,
                    "no2": 0.77,
                    "o3": 68.66,
                    "pm2_5": 3.0,
                    "pm10": 3.5
                }
            }]
        },
        "followups": "would you like coordinates for the location"
    }]
    """
```

Reasoning:
Unlike other functions, returns complete API response because:
 * AQI scale (1-5) needs explanation (varies by pollutant)
 * Components (CO, NO₂, O₃, PM2.5) have different health implications
 * AI can explain significance based on values
 * Users may want specific pollutant information

AQI Scale:
 * 1: Good (minimal health impact)
 * 2: Fair (acceptable for most)
 * 3: Moderate (sensitive groups may be affected)
 * 4: Poor (general population affected)
 * 5: Very Poor (serious health effects)

## Follow-Up Pattern:
Each function suggests next logical step:

Current Weather → Forecast → Air Quality → Coordinates → Map Tile
This creates a guided conversation flow without overwhelming users.

## Map Tile Generation
Tile Coordinate Mathematics:
```python
def get_map_tile_url(location: str, zoom: int = 10, 
                     map_type: str = CommonTileProviders.STANDARD) -> dict:
    """
    Generate OpenStreetMap tile URL for location visualization.
    
    Returns: {
        "tile_url": "https://tile.openstreetmap.org/10/550/335.png",
        "latitude": 52.5200,
        "longitude": 13.4050,
        "zoom": 10,
        "tile_x": 550,
        "tile_y": 335,
        "map_type": "standard"
    }
    """
    coordinates = geocode(location)
    
    def deg2num(lat_deg, lon_deg, zoom):
        """Convert GPS coordinates to tile coordinates"""
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return (xtile, ytile)
    
    x, y = deg2num(coordinates["lat"], coordinates["lon"], zoom)
    tile_url = CommonTileProviders.STANDARD.replace("{z}", str(zoom)) \
                                           .replace("{x}", str(x)) \
                                           .replace("{y}", str(y))
    return {"tile_url": tile_url, "latitude": coordinates["lat"], 
            "longitude": coordinates["lon"], "zoom": zoom, 
            "tile_x": x, "tile_y": y, "map_type": map_type}
```
Formula Insight:
Web Mercator projection converts spherical Earth to flat tiles:
x_tile = (longitude + 180) / 360 × 2^zoom
y_tile = (1 - asinh(tan(latitude)) / π) / 2 × 2^zoom

Why This Matters:
 * Web maps pre-render tiles into 256×256 pixel images
 * Knowing exact tile coordinates enables direct URL construction
 * No extra API calls needed for map display
 * Predictable caching behavior (tiles are static)
 * Support for multiple providers (OSM, satellite, terrain)

Tile Provider Strategy:
```python
class CommonTileProviders:
    STANDARD = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    SATELLITE = "https://server.arcgisonline.com/.../tile/{z}/{y}/{x}"
    TERRAIN = "https://tile.opentopomap.org/{z}/{x}/{y}.png"
```
System supports multiple providers through configuration. Switching from standard map to satellite view requires only changing the base URL template.
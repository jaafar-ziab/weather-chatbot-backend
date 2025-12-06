import unittest
from unittest.mock import Mock, patch
from  weather_chatbot.src.services.service import geocode, get_weather, get_forcast, get_air_quality, get_map_tile_url


class TestGeocode(unittest.TestCase):
    def test_geocode_success(self):
            with patch('src.services.service.requests.get') as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = [{
                    "name": "Berlin",
                    "lat": 52.5200,
                    "lon": 13.4050,
                    "country": "DE"
                }]
                mock_response.raise_for_status = Mock()
                mock_get.return_value = mock_response

                result = geocode("Berlin")
                self.assertEqual(result["lat"], 52.5200)
                self.assertEqual(result["lon"], 13.4050)

    def test_get_weather_success(self):
        with patch('src.services.service.requests.get') as mock_get:
            # Mock geocode response
            mock_geocode_response = Mock()
            mock_geocode_response.json.return_value = [{
                "name": "Berlin",
                "lat": 52.5200,
                "lon": 13.4050,
                "country": "DE"
            }]
            mock_geocode_response.raise_for_status = Mock()

            # Mock weather response
            mock_weather_response = Mock()
            mock_weather_response.json.return_value = {
                "weather": [{"description": "'overcast clouds"}],
                "main": {"temp": 9.11}
            }
            mock_weather_response.raise_for_status = Mock()

            # Side effects for sequential calls
            mock_get.side_effect = [mock_geocode_response, mock_weather_response]

            result = get_weather("Berlin", "C")
            print (result)
            self.assertEqual(result[0]["weather"], "Berlin: 'overcast clouds, 9C")

    def test_get_forcast_success(self):
        with patch('src.services.service.requests.get') as mock_get:
            # Mock geocode response
            mock_geocode_response = Mock()
            mock_geocode_response.json.return_value = [{
                "name": "Berlin",
                "lat": 52.5200,
                "lon": 13.4050,
                "country": "DE"
            }]
            mock_geocode_response.raise_for_status = Mock()

            # Mock forecast response
            mock_forecast_response = Mock()
            mock_forecast_response.json.return_value = {
                "list": [
                    {'dt': 1762689600, "main": {"temp": 15}, "weather": [{"description": "light rain"}], "dt_txt": "2025-11-09 12:00:00"},
                    {'dt': 1762776000, "main": {"temp": 17}, "weather": [{"description": "scattered clouds"}], "dt_txt": "2025-11-10 12:00:00"},
                    {'dt': 1762862400, "main": {"temp": 16}, "weather": [{"description": "clear sky"}], "dt_txt": "2025-11-11 12:00:00"},
                    {'dt': 1762948800, "main": {"temp": 14}, "weather": [{"description": "overcast clouds"}], "dt_txt": "2025-11-12 12:00:00"},
                    {'dt': 1763035200, "main": {"temp": 13}, "weather": [{"description": "moderate rain"}], "dt_txt": "2025-11-13 12:00:00"},
                ]
            }
            mock_forecast_response.raise_for_status = Mock()

            # Side effects for sequential calls
            mock_get.side_effect = [mock_geocode_response, mock_forecast_response]

            result = get_forcast("Berlin", "C")
            print (result)
            self.assertIn("Sunday 2025-11-09: light rain, 15°C", result[0].strip())
            self.assertIn("Monday 2025-11-10: scattered clouds, 17°C", result[1].strip())
            self.assertIn("Tuesday 2025-11-11: clear sky, 16°C", result[2].strip())
            self.assertIn("Wednesday 2025-11-12: overcast clouds, 14°C", result[3].strip())
            self.assertIn("Thursday 2025-11-13: moderate rain, 13°C", result[4].strip())

    def test_air_quality(self):
        with patch('src.services.service.requests.get') as mock_get:
            mock_geocode_response = Mock()
            mock_geocode_response.json.return_value = [{
                "name": "Berlin",
                "lat": 52.5200,
                "lon": 13.4050,
                "country": "DE"
            }]

            mock_air_quality_response = Mock()
            mock_air_quality_response.json.return_value = {
                "list": [
                    {
                        "main": {"aqi": 2},
                        "components": {
                            "co": 201.94053649902344,
                            "no": 0.01877197064459324,
                            "no2": 0.7711354494094849,
                            "o3": 68.66455078125,
                            "so2": 0.6407499313354492,
                            "pm2_5": 3.0,
                            "pm10": 3.5,
                            "nh3": 0.12369127571582794
                        },
                        "dt": 1605182400
                    }
                ]
            }
            mock_air_quality_response.raise_for_status = Mock()
            mock_geocode_response.raise_for_status = Mock()
            mock_get.side_effect = [mock_geocode_response, mock_air_quality_response]
            result = get_air_quality("Berlin")
            print (result)
            self.assertEqual(result[0]["air-quality"]["list"][0]["main"]["aqi"], 2)

    def test_get_map_tile_url(self):
            result = get_map_tile_url("Berlin", zoom=10, map_type="standard")
            print(result)
            self.assertTrue(result["tile_url"].startswith('https://tile.openstreetmap.org'))
            self.assertTrue(result["tile_url"].endswith('.png'))
            self.assertEqual(result["zoom"], 10)
            self.assertEqual(result["tile_x"], 550)
            self.assertEqual(result["tile_y"], 335)
            self.assertEqual(result["map_type"], "standard")

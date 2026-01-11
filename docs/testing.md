## Unit Tests
Located in `src/test/test_services.py`:
Testing Philosophy:
 * Mock external API calls.
 * Test business logic in isolation
 * Verify error handling
 * Ensure edge cases covered

Example Test Structure:
```python
class TestServices(unittest.TestCase):
    def test_geocode_success(self):
        """Test successful geocoding"""
        with patch('src.services.weather_service.requests.get') as mock_get:
            # Mock API response
            mock_response = Mock()
            mock_response.json.return_value = [{
                "name": "Berlin",
                "lat": 52.5200,
                "lon": 13.4050,
                "country": "DE"
            }]
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Test function
            result = geocode("Berlin")
            self.assertEqual(result["lat"], 52.5200)
            self.assertEqual(result["lon"], 13.4050)
```
Why Mock External APIs:
 * Speed: Tests run in milliseconds instead of seconds
 * Reliability: No network failures breaking tests
 * Cost: Avoid API quota consumption
 * Isolation: Test logic independent of external services

Running Tests
```bash
# Run all tests
python -m unittest discover src/test

# Run specific test file
python -m unittest src.test.test_services
```
# Manual Testing with Swagger

Interactive API Testing:
1. Start server: `python main.py`
2. Open http://127.0.0.1:8000/docs
3. Test workflow:
 * Register user → Check your email email
 * Login → Copy access_token
 * Click "Authorize" button → Paste token
 * Test /chat endpoint with authenticated requests
 * Test /sessions endpoints

Why Swagger/OpenAPI:
 * Automatic documentation from code
 * Interactive testing interface
 * Request/response schemas visible
 * No Postman setup needed
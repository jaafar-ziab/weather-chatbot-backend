### environment Configuration setup
This guide outlines the steps to set up the development environment for the Backend app. Follow these instructions to ensure a smooth setup process.

## Prerequisites
1. make an OpenWeatherMap account and obtain an API key from https://openweathermap.org/api.
then fill in the OWM config variables in the .env file.
```env
OWM_KEY='YOUR_API_KEY_HERE'
OWM_URL=".."                         # Geocoding API endpoint for example(http://api.openweathermap.org/geo/1.0/direct)
OWM_CURRENT="..."                    # Current weather data API endpoint (https://api.openweathermap.org/data/2.5/weather)
OWM_FORECAST="..."                   # Weather forecast API endpoint (https://api.openweathermap.org/data/2.5/forecast)
OWM_AIR="..."                        # Air pollution data API endpoint (http://api.openweathermap.org/data/2.5/air_pollution)
Standard="..."                       # Standard map tile URL template (https://tile.openstreetmap.org/{z}/{x}/{y}.png)
SATELLITE="..."                      # Satellite map tile URL template (https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x})
TERRAIN="..."                        # Terrain map tile URL template (https://tile.opentopomap.org/{z}/{x}/{y}.png)
```
2. Create Google AI Studio account and create Google Gemini API key from https://aistudio.google.com/.
then fill in the GOOGLE config variables in the .env file.
```env
LLM_API_KEY="YOUR_Google_Gemini_API_Key_Here"
```
3. Create JWT secret key for authentication.
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
then fill in the JWT config variable in the .env file.
```env
JWT_SECRET_KEY="YOUR_JWT_SECRET_KEY_HERE"
```
4. Set up SMTP server for email functionality. You can use Gmail SMTP or any other SMTP server.
```env
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587
SMTP_USERNAME="YOUR_EMAIL@gmail.com"
SMTP_PASSWORD="YOUR_EMAIL_APP_PASSWORD"
```
or you can create a free account on https://maileroo.com/ and create API KEY.
then fill in the MAILEROO config variables in the .env file.
```env
MAILEROO_API_KEY="YOUR_MAILEROO_API_KEY_HERE"
MAILEROO_FROM_EMAIL="YOUR_VERIFIED_EMAIL_HERE"
```
5. Configure CORS settings by specifying allowed origins.
```env
ALLOW_ORIGINS="http://localhost:5173"   # for local development with frontend
```
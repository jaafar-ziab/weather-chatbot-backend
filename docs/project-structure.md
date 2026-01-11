# Project Structure

weather_chatbot/
├── src/
│   ├── models/
│   │   ├── users.py         # SQLAlchemy models (User, ChatSession, ChatMessage)
│   │   └── schemas.py       # Pydantic models (request/response validation)
│   ├── routers/
│   │   ├── auth.py         # /register, /login, /verify-email
│   │   ├── chat.py         # /chat, /sessions, ..
│   │   └── root.py         # /API documentation and health check
│   ├── services/
│   │   ├── helper.py       # Auth helpers (hash, tokens, get_current_user)
│   │   ├── email_services.py  # Send verification emails
│   │   └── weather_service.py # OpenWeatherMap integration
│   ├── templates/
│   │   └── verification_email.html  # Email template
│   ├── test/
│   │   └── test_services.py  # Unit tests for weather services
│   ├── app.py              # FastAPI app initialization
│   ├── config.py           # Configuration & environment variables
│   └── llm_schema.py       # Gemini AI integration & function calling
├── main.py                 # Application entry point
├── docs/                    # Project documentation
├── .env                    # Environment variables (not in git)
├── pyproject.toml          # Python dependencies
└── weather_bot.db         # SQLite database (created on first run)

# Key Files Explained

 * models/users.py: Defines database tables using SQLAlchemy. `User` stores authentication and user data, `ChatSession` groups conversations, `ChatMessage` stores individual messages. Relationships use `back_populates` for bidirectional navigation.
 * models/schemas.py: Pydantic models validate API requests/responses. `UserRegister` validates registration data (email format, password length), `ChatIn` validates chat messages, `Token` structures authentication responses.
 * routers/: Each router handles related endpoints. `auth.py` manages registration/login, `chat.py` handles messaging/sessions, `root.py` provides health checks and API info.
 * services/helper.py: Contains reusable auth functions. `hash_password()` uses SHA256→Argon2 pipeline, `create_access_token()` generates JWTs, `get_current_user()` is a FastAPI dependency that validates tokens.
 * services/email_services.py: Loads HTML template, replaces variables (username, verification URL), sends via SMTP. Uses `Gmail SMTP` for email delivery.
 * services/weather_service.py: Integrates OpenWeatherMap API. `geocode()` converts location names to coordinates, `get_weather()` fetches current conditions, `get_forcast()` retrieves 5-day forecast, `get_air_quality` retrieves the air quality(good, bad), `get_map_tile_url` get the map tile url .
 * llm_schema.py: Defines Gemini function calling schema. Declares available functions (get_weather, get_forcast, etc.) with descriptions and parameters. `llm_extract()` processes conversation history, calls Gemini, executes functions, returns formatted response.
 * config.py: Loads environment variables via `python-dotenv`, initializes database engine, configures password hashing context, creates Gemini client.
 * app.py: Creates FastAPI instance, adds CORS middleware, includes routers with tags. Defines health check endpoint showing uptime.
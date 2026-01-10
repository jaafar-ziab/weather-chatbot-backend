## Prerequisites
Python 3.11+, pip, virtual environment
OpenWeatherMap API key (free tier sufficient)
Google Gemini API key (you can generate from Google Cloud Console)
Mailtrap account (for email testing)

Installation
bash# Clone and navigate
git clone <repo-url>
cd weather_chatbot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install .

# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Environment Configuration
Create .env file:
```env
OWM_URL="..."
OWM_KEY="..."
OWM_CURRENT="...."
OWM_FORECAST="...."
OWM_AIR="...."
LLM_API_KEY="....."
STANDARD="....."
SATELLITE="....."
TERRAIN="....."
ALLOW_ORIGINS="http://localhost:5173"
JWT_SECRET_KEY="......"
DATABASE_URL=sqlite:///./weather_bot.db
SMTP_SERVER="sandbox.smtp.mailtrap.io"
SMTP_PORT=2525
SMTP_USERNAME="....."
SMTP_PASSWORD="....."
```
## Running the Server

```bash
# Start server
python main.py

# Or with uvicorn
uvicorn src.app:app --reload --host 127.0.0.1 --port 8000

# Verify
curl http://127.0.0.1:8000/health
# Response: {"status":"ok","uptime_seconds":X.XX}

# View docs
# http://127.0.0.1:8000/docs
``


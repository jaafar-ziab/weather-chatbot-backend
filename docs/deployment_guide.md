Production Checklist
Environment Variables:
```bash
# Generate secure secret (64 characters)
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Set production values
JWT_SECRET_KEY=<generated_64_char_key>
DATABASE_URL=postgresql://user:pass@host:5432/dbname
ALLOW_ORIGINS=https://yourdomain.com
SMTP_SERVER=smtp.sendgrid.net
SMTP_USERNAME=apikey
SMTP_PASSWORD=<sendgrid_api_key>
```
Database Migration:
```bash
# Install Alembic
pip install alembic

# Initialize migrations
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial tables"

# Apply migrations
alembic upgrade head
```

Security Hardening:
```python
# app.py - Add security headers
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])

# Restrict CORS in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # No wildcards
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```
Deployment Platform
Render.com:
```yaml
# render.yaml
services:
  - type: web
    name: weather-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.app:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: JWT_SECRET_KEY
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: weather-db
          property: connectionString
```
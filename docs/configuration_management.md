# Config Class
The Config class in config.py centralizes all environment variables:

```python
class Config:
    def __init__(self):
        self.OWM_KEY = os.getenv("OWM_KEY")              # Weather API key
        self.LLM_API_KEY = os.getenv("LLM_API_KEY")      # Gemini API key
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") # Token signing
        self.DATABASE_URL = os.getenv("DATABASE_URL")    # DB connection
        self.SMTP_SERVER = os.getenv("SMTP_SERVER")      # Email server
        # ... other config values
```

Why centralize? Single source of truth, easy testing (mock Config), validation at startup, type hints for IDE support.

## Key Configurations
# JWT Settings:

```python
SECRET_KEY = config.JWT_SECRET_KEY  # Must be cryptographically secure
ALGORITHM = "HS256"                 # HMAC-SHA256 signing
ACCESS_TOKEN_EXPIRE_MINUTES = 10080 # 7 days
VERIFICATION_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
```

# Database Setup:

```python
DATABASE_URL = config.DATABASE_URL
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

# Password Hashing:

```python
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
# Uses Argon2id by default - memory-hard algorithm resistant to GPU attacks
```

# Gemini Client:

```python
client = genai.Client(api_key=config.LLM_API_KEY)
# Initialized once, reused for all LLM calls
```

# Environment Variables
Required variables throw errors if missing:

```python
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY not found! Generate one and add to .env file")
```

Security Note: Never commit .env to git. Use .env.example template with placeholder values. In production, use secure secret management (AWS Secrets Manager, Azure Key Vault).
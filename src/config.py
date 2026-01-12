from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from fastapi.security import HTTPBearer
from google import genai

load_dotenv()


class Config:
    def __init__(self):
        self.OWM_KEY = os.getenv("OWM_KEY")
        self.LLM_API_KEY = os.getenv("LLM_API_KEY")
        self.OWM_URL = os.getenv("OWM_URL")
        self.OWM_CURRENT = os.getenv("OWM_CURRENT")
        self.OWM_FORECAST = os.getenv("OWM_FORECAST")
        self.OWM_AIR = os.getenv("OWM_AIR")
        self.STANDARD = os.getenv("STANDARD")
        self.SATELLITE = os.getenv("SATELLITE")
        self.TERRAIN = os.getenv("TERRAIN")
        self.ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS")
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.SMTP_SERVER = os.getenv("SMTP_SERVER")
        self.SMTP_PORT = os.getenv("SMTP_PORT")
        self.SMTP_USERNAME = os.getenv("SMTP_USERNAME")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        self.MAILEROO_API_KEY = os.getenv("MAILEROO_API_KEY")
        self.MAILEROO_FROM_EMAIL = os.getenv("MAILEROO_FROM_EMAIL")

config = Config()


# Gemini Configuration
client = genai.Client(api_key=config.LLM_API_KEY)

SECRET_KEY = config.JWT_SECRET_KEY
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY not found! Generate one and add to .env file")

ALGORITHM = "HS256"


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
security = HTTPBearer()


# Database Setup
DATABASE_URL = config.DATABASE_URL
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Email Configuration
SMTP_SERVER = config.SMTP_SERVER
SMTP_PORT = config.SMTP_PORT
SMTP_USERNAME = config.SMTP_USERNAME
SMTP_PASSWORD = config.SMTP_PASSWORD

class CommonTileProviders:
    STANDARD = config.STANDARD
    SATELLITE = config.SATELLITE
    TERRAIN = config.TERRAIN
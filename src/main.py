import uvicorn
from src.app import app  # import app from app.py
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
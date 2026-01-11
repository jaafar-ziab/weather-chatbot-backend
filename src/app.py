
from fastapi.middleware.cors import CORSMiddleware
from .config import config
from fastapi import FastAPI, status

from .routers.auth import router as auth_router
from .routers.chat import router as chat_router
from .routers.root import router as root_router


app = FastAPI(title="Weather Chatbot", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(root_router, tags=["Root"])
app.include_router(auth_router, tags=["authentication"])
app.include_router(chat_router, tags=["chat"])
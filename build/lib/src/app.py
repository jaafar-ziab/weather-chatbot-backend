from time import time
from fastapi.middleware.cors import CORSMiddleware
from config import config
from fastapi import FastAPI, status
from models.schemas import HealthOut
from routers.auth import router


app = FastAPI(title="Weather Chatbot", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


START_TIME = time()

@app.get("/health", response_model=HealthOut, status_code=status.HTTP_200_OK)
async def health():
    return HealthOut(status="ok", uptime_seconds=time() - START_TIME)


app.include_router(router.root)
app.include_router(router.auth)
app.include_router(router.chat)
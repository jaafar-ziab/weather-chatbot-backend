import uuid
from fastapi import FastAPI
from time import time
from fastapi import status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import logging
from services.service import Config
from llm_schema import llm_extract

app = FastAPI(title="Weather Chatbot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config().ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatIn(BaseModel):
    message: str
    session_id: str | None = None


class HealthOut(BaseModel):
    status: str
    uptime_seconds: float | None = None


START_TIME = time()
SESSIONS = {}


@app.get("/health", response_model=HealthOut, status_code=status.HTTP_200_OK)
async def health():
    return HealthOut(status="ok", uptime_seconds=time() - START_TIME)


@app.post("/chat")
async def chat(input: ChatIn):
    if input.session_id is None:
        sessions_id = str(uuid.uuid4())
        SESSIONS[sessions_id] = {"collections": {}, "history": []}
    else:
        sessions_id = input.session_id
        if sessions_id not in SESSIONS:
            SESSIONS[sessions_id] = {"collections": {}, "history": []}

    # Add user message to history
    SESSIONS[sessions_id]["history"].append({"role": "user", "content": input.message})
    history = SESSIONS[sessions_id]["history"]
    logging.info(f"receive message: {input.message} in session: {sessions_id}")

    result = llm_extract(history)
    SESSIONS[sessions_id]["history"].extend(result["history_update"])
    return {
        "session_id": sessions_id,
        "response": result["response"],
        "history": SESSIONS[sessions_id]["history"]
    }
import uuid
from fastapi import FastAPI
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


SESSIONS = {}


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
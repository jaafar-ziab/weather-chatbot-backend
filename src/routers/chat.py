from fastapi import APIRouter
import logging
from ..services.helper import get_current_user, get_db
from ..llm_schema import llm_extract
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException, Depends
from ..models.schemas import ChatResponse, ChatIn
from ..models.users import User, ChatSession, ChatMessage


router = APIRouter(tags=["chat"])


SESSIONS = {}


@router.post("/chat", response_model=ChatResponse)
async def chat(
        input: ChatIn,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Chat with the weather bot (requires authentication)
    - **message**: User's message to the bot
    - **session_id**: session ID to continue conversation
    """
    if input.session_id is None:
        session = ChatSession(user_id=current_user.id)
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = session.id
        user_session_key = f"{current_user.id}_{session_id}"
        SESSIONS[user_session_key] = {"collections": {}, "history": []}
        logging.info(f"Created new session: {session_id} for user: {current_user.username}")
    else:
        session = db.query(ChatSession).filter(
            ChatSession.id == input.session_id,
            ChatSession.user_id == current_user.id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        session_id = session.id
        logging.info(f"Using existing session: {session_id} for user: {current_user.username}")

    # Save user message to database
    user_message = ChatMessage(
        session_id=session_id,
        role="user",
        content=input.message
    )
    db.add(user_message)
    db.commit()

    # Get conversation history from database
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    history = [{"role": msg.role, "content": msg.content} for msg in messages]
    logging.info(f"User {current_user.username} sent message in session {session_id}")

    try:
        # Call LLM
        result = llm_extract(history)
        # Save assistant responses to database
        for update in result.get("history_update", []):
            if update["role"] == "assistant":
                assistant_message = ChatMessage(
                    session_id=session_id,
                    role="assistant",
                    content=update["content"]
                )
                db.add(assistant_message)

        # Update session timestamp
        session.updated_at = datetime.utcnow()

        # Update title based on first message
        if session.title == "New Conversation" and len(history) == 1:
            session.title = input.message[:50] + ("..." if len(input.message) > 50 else "")
        db.commit()
        logging.info(f"Bot responded in session {session_id}")

        return ChatResponse(
            session_id=session_id,
            response=result["response"],
            history=history + result.get("history_update", [])
        )
    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.get("/sessions")
async def get_user_sessions(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get all chat sessions for current user"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.updated_at.desc()).all()
    logging.info(f"Found {len(sessions)} chat sessions for user {current_user.username}")
    return {
        "sessions": [
            {
                "id": session.id,
                "title": session.title,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": len(session.messages)
            }
            for session in sessions
        ],
        "total": len(sessions)
    }


@router.get("/sessions/{session_id}")
async def get_session(
        session_id: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get specific chat session with messages"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    logging.info(f"Retrieved session {session_id} for user {current_user.username}")
    return {
        "id": session.id,
        "title": session.title,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at
            }
            for msg in messages
        ]
    }


@router.delete("/sessions/{session_id}")
async def delete_session(
        session_id: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Delete a chat session and all its messages"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    logging.info(f"Deleted session {session_id} for user {current_user.username}")
    return {"message": "Session deleted successfully"}
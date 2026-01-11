from fastapi import APIRouter
from ..models.schemas import HealthOut
from time import time
from fastapi import status


router = APIRouter(tags=["Root"])
START_TIME = time()


@router.get("/health", response_model=HealthOut, status_code=status.HTTP_200_OK)
async def health():
    return HealthOut(status="ok", uptime_seconds=time() - START_TIME)


@router.get("/")
async def root():
    """API documentation"""
    return {
        "message": "Weather Assistant API with Email Verification",
        "version": "2.0",
        "features": [
            "User registration with email verification",
            "Secure authentication with JWT tokens",
            "Chat history saved in database",
            "Session management"
        ],
        "endpoints": {
            "auth": {
                "POST /register": "Register new user (sends verification email)",
                "POST /verify-email": "Verify email address",
                "POST /resend-verification": "Resend verification email",
                "POST /login": "Login user",
                "GET /me": "Get current user info"
            },
            "chat": {
                "POST /chat": "Chat with bot (saves to database)",
                "GET /sessions": "Get all user sessions",
                "GET /sessions/{id}": "Get specific session with messages",
                "DELETE /sessions/{id}": "Delete session"
            }
        },
        "docs": "/docs"
    }
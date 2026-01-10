from fastapi import APIRouter
import uuid
import logging
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, BackgroundTasks
from ..services.email_services import send_verification_email
from ..services.helper import (get_db, create_verification_token, hash_password,\
    create_access_token, decode_access_token, get_current_user)
from ..models.schemas import Token, UserRegister, EmailVerificationRequest, UserLogin
from ..models.users import User


router = APIRouter(tags=["authentication"])

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
VERIFICATION_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

@router.post("/register", response_model=Token)
async def register(user_data: UserRegister,
                   background_tasks: BackgroundTasks,
                   db: Session = Depends(get_db)):
    """Register a new user"""
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create verification token
    temp_user_id = str(uuid.uuid4())
    verification_token = create_verification_token(temp_user_id)

    # Create new user
    new_user = User(
        id = temp_user_id,
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        is_verified=False,
        verification_token=verification_token,
        verification_token_expires=datetime.utcnow() + timedelta(minutes=VERIFICATION_TOKEN_EXPIRE_MINUTES)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logging.info(f"added {new_user.username}'s information to the database")

    background_tasks.add_task(
        send_verification_email,
        new_user.email,
        new_user.username,
        verification_token
    )

    # Create access token
    access_token = create_access_token(data={"sub": new_user.id})

    logging.info(f"New user registered: {new_user.username}")

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=new_user.id,
        username=new_user.username,
        is_verified=new_user.is_verified
    )


@router.post("/verify-email")
async def verify_email(
        verification_data: EmailVerificationRequest,
        db: Session = Depends(get_db)
):
    """Verify user's email address"""
    try:
        payload = decode_access_token(verification_data.token)
        user_id = payload.get("sub")
        token_type = payload.get("type")

        if token_type != "verification":
            raise HTTPException(status_code=400, detail="Invalid token type")

        # Find user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_verified:
            return {"message": "Email already verified"}

        # Verify email
        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires = None
        db.commit()

        logging.info(f"Email verified for user: {user.username}")

        return {"message": "Email verified successfully!"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Verification link has expired")
    except Exception as e:
        logging.error(f"Email verification error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid verification token")



@router.post("/resend-verification")
async def resend_verification(
        current_user: User = Depends(get_current_user),
        background_tasks: BackgroundTasks = None,
        db: Session = Depends(get_db)
):
    """Resend verification email"""
    if current_user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    # Create new token
    verification_token = create_verification_token(current_user.id)
    current_user.verification_token = verification_token
    current_user.verification_token_expires = datetime.utcnow() + timedelta(minutes=VERIFICATION_TOKEN_EXPIRE_MINUTES)
    db.commit()

    # Send email
    if background_tasks:
        background_tasks.add_task(
            send_verification_email,
            current_user.email,
            current_user.username,
            verification_token
        )
    logging.info(f"verification email resent to user: {current_user.username}")
    return {"message": "Verification email sent"}


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.email == user_data.email).first()
    print(user)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    if not User.is_verified:
        raise HTTPException(status_code=401, detail="Please verify your account to login")

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Create token
    access_token = create_access_token(data={"sub": user.id})

    logging.info(f"User logged in: {user.username}")

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        is_verified=user.is_verified
    )
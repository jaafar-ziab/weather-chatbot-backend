## SQLAlchemy Models

# User Model:
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=False, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String, nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationship
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
```

Key Features: UUID primary keys for security, indexed email/username for fast lookups, `cascade="all, delete-orphan"`ensures deleting a user removes all their sessions and messages.

# ChatSession Model:

```python
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
```
Title auto-generated from first message. `updated_at` automatically updates on any change via `onupdate`.

# ChatMessage Model:

```python
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("ChatSession", back_populates="messages")
```
`Text` type handles long messages. Role distinguishes user input from AI responses.

## Database Operations

# Creating Records:
```python
# Create user
new_user = User(
    id=str(uuid.uuid4()),
    email="test@example.com",
    username="testuser",
    hashed_password=hash_password("password123"),
    is_verified=False
)
db.add(new_user)
db.commit()
db.refresh(new_user)  # Populate generated fields
```

# Querying:
```python
# Find user by email
user = db.query(User).filter(User.email == email).first()

# Get all sessions for user (ordered)
sessions = db.query(ChatSession).filter(
    ChatSession.user_id == user_id
).order_by(ChatSession.updated_at.desc()).all()

# Get messages in session (ordered)
messages = db.query(ChatMessage).filter(
    ChatMessage.session_id == session_id
).order_by(ChatMessage.created_at).all()
```

# Cascade Deletes:
```python
# Deleting user automatically deletes all sessions and messages
db.delete(user)
db.commit()  # Cascades to chat_sessions and chat_messages
```

# Table Creation
Tables auto-create on first run:
```python
Base.metadata.create_all(bind=engine)
```
For production migrations, use Alembic instead of auto-creation.
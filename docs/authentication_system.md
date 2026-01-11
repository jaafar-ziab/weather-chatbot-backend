## Password Security
# Hashing Pipeline:
```python
def hash_password(password: str) -> str:
    # Step 1: SHA256 pre-hash (handles passwords >72 bytes)
    password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # Step 2: Argon2 hash (memory-hard, GPU-resistant)
    return pwd_context.hash(password)
```
Why this approach? Argon2 has a 72-byte limit. SHA256 produces consistent 64-byte output, bypassing this limit while maintaining security. SHA256 is fast (not a weakness here since Argon2 provides slowness), and the combination is more secure than Argon2 alone.

## JWT Tokens
# Token Structure:
```python
{
  "sub": "user-uuid-here",     # Subject (user ID)
  "type": "verification",      # Token type (optional)
  "exp": 1735689600            # Expiration timestamp
}
```

# Creating Tokens:
```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=10080))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

# Validating Tokens:
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials  # Extract from "Bearer <token>"
    payload = decode_access_token(token)  # Validate signature & expiration
    user_id = payload.get("sub")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user  # Injected into endpoint
```

### Authentication Flow

# Registration:
1. Validate input (Pydantic)
2. Check email/username uniqueness
3. Hash password (SHA256 → Argon2)
4. Generate verification token (JWT, 24h expiration)
5. Store user in database (is_verified=False)
6. Send verification email (background task)

# Email Verification:
1. Extract token from URL query parameter
2. Decode JWT token
3. Validate expiration (24 hours)
4. Find user by ID from token
5. Set is_verified=True
6. Clear verification_token fields
7. Return success message

# Login:
1. Find user by email
2. Verify password hash
3. Check is_verified status (reject if False)
4. Update last_login timestamp
5. Generate access token (7 days)
6. Return token + user info

### Protected Endpoints
Endpoints requiring authentication use `Depends(get_current_user)`:
```python
@router.post("/chat")
async def chat(
    input: ChatIn,
    current_user: User = Depends(get_current_user),  # ← Validates token
    db: Session = Depends(get_db)
):
    # current_user is automatically available
    # If token invalid → 401 raised before reaching here
```
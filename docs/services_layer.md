### Helper Functions (services/helper.py)

# Password Operations:
```python
def hash_password(password: str) -> str:
    # SHA256 pre-hash to handle any password length
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # Argon2 final hash for security
    return pwd_context.hash(password_hash)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Must use same SHA256 pre-hash
    password_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    return pwd_context.verify(password_hash, hashed_password)
```

# Token Operations:

```python
def create_verification_token(user_id: str) -> str:
    data = {
        "sub": user_id,
        "type": "verification",  # Distinguishes from access tokens
        "exp": datetime.utcnow() + timedelta(minutes=1440)  # 24 hours
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=10080))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Database Dependency:
```python
def get_db():
    db = SessionLocal()
    try:
        yield db  # Provides session to endpoint
    finally:
        db.close()  # Ensures cleanup even if error occurs
```

### Authentication Dependency:
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
```
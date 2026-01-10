### Root Endpoints

# GET /
```python
@router.get("/")
async def root():
    return {
        "message": "Weather Assistant API",
        "version": "2.0",
        "endpoints": {...},
        "docs": "/docs"
    }
```
Purpose: API documentation and available endpoints.

# GET /health
```python
@router.get("/health", response_model=HealthOut)
async def health():
    return HealthOut(status="ok", uptime_seconds=time() - START_TIME)
```
Purpose: Health checks for monitoring/load balancers.

### Authentication Endpoints

# POST /register
```python
Request:
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepass123"
}

Response:
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user_id": "uuid",
  "username": "johndoe",
  "is_verified": false
}
```
Creates user, sends verification email, returns token for immediate app access.

# POST /login
```python
Request:
{
  "email": "user@example.com",
  "password": "securepass123"
}

Response:
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user_id": "uuid",
  "username": "johndoe",
  "is_verified": true
}
```
Validates credentials, checks verification status, returns token.

# POST /verify-email
```python
Request:
{
  "token": "eyJhbGci..."
}

Response:
{
  "message": "Email verified successfully!"
}
```
Token from email link, marks user as verified.

# POST /resend-verification (Protected)
```
Headers: Authorization: Bearer <token>
Response: {"message": "Verification email sent"}
```
Generates new verification token, sends email.

### Chat Endpoints

# POST /chat (Protected)
```python
Request:
{
  "message": "What's the weather in Berlin?",
  "session_id": "uuid"  # Optional
}

Response:
{
  "session_id": "uuid",
  "response": "The weather in Berlin is 15°C and cloudy...",
  "history": [
    {"role": "user", "content": "What's the weather in Berlin?"},
    {"role": "assistant", "content": "The weather in Berlin is..."}
  ]
}
```
Processes message with Gemini AI, calls weather APIs, saves to database.

# GET /sessions (Protected)
```python
Response:
{
  "sessions": [
    {
      "id": "uuid",
      "title": "Weather in Berlin",
      "created_at": "2025-01-01T10:00:00",
      "updated_at": "2025-01-01T10:05:00",
      "message_count": 4
    }
  ],
  "total": 1
}
```
Lists all user's chat sessions, ordered by most recent.

# GET /sessions/{session_id} (Protected)
```python
Response:
{
  "id": "uuid",
  "title": "Weather in Berlin",
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "What's the weather in Berlin?",
      "created_at": "2025-01-01T10:00:00"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "The weather in Berlin is...",
      "created_at": "2025-01-01T10:00:05"
    }
  ]
}
```
Retrieves full conversation history for session.

# DELETE /sessions/{session_id} (Protected)
```python
Response:
{
  "message": "Session deleted successfully"
}
```
Deletes session and all messages (cascade).

### Error Responses
All endpoints return consistent error format:
```python
{
  "detail": "Error message here"
}
```
Common Status Codes:
 * 200: Success
 * 400: Bad Request (validation error)
 * 401: Unauthorized (invalid/missing token)
 * 404: Not Found
 * 500: Internal Server Error


### Layered Error Handling
## Three-Level Approach:
1. Validation Layer (Pydantic): Catches malformed requests before business logic:
```python
class ChatIn(BaseModel):
    message: str
    session_id: str | None = None
```
 * Invalid JSON → 422 Unprocessable Entity
 * Missing required fields → Detailed error message
 * Type mismatches → Automatic conversion or rejection

2. Business Logic Layer: Domain-specific errors:
```python
if not user:
    raise HTTPException(status_code=401, detail="User not found")

if not user.is_verified:
    raise HTTPException(status_code=401, detail="Please verify your email")
```
3. Infrastructure Layer: External API failures:
```python
try:
    r = requests.get(url, timeout=20)
    r.raise_for_status()
except requests.exceptions.Timeout:
    raise HTTPException(504, "Weather service timeout")
except requests.exceptions.HTTPError:
    raise HTTPException(502, "Weather service unavailable")
```
Why Layered: Each layer handles errors it understands:
 * Pydantic knows about data formats, not business rules
 * Business logic knows about domain constraints, not network failures
 * Infrastructure layer handles unpredictable external failures

## Logging Strategy
Structured Logging:
```python
logging.info(f"User {username} registered successfully")
logging.info(f"Function {function_name} called with args {required_args}")
logging.error(f"Weather API error for {location}: {str(e)}")
```
Why Context Matters:
 * "Error occurred" → Useless for debugging
 * "Weather API timeout for Berlin after 20s" → Actionable

Log Levels:
 * INFO: Normal operations (user registered, weather fetched, email sent)
 * WARNING: Unusual but handled (slow API response, cache miss)
 * ERROR: Failures requiring attention (API down, database error, auth failure)

Production Tip: Configure log aggregation (CloudWatch, Datadog, Sentry) to alert on ERROR level. Manual log reading doesn't scale beyond ~100 requests/day.

External API Failure Handling
Timeout Strategy: All external API calls include timeout=20 parameter:
```python
r = requests.get(url, params=params, timeout=20)
```
Why Timeouts: Without timeouts, a slow API can:
 * Hang requests indefinitely
 * Tie up server resources (workers blocked)
 * Make entire application appear unresponsive
 * Prevent automatic recovery

20-Second Choice: Balance between:
 * Patience: Allow for slow networks/servers
 * Responsiveness: Don't make users wait too long
 * Resource efficiency: Free workers for other requests


## HTTP Status Code Strategy
 * 200: Success (OK)
 * 400: Client error (bad input, validation failure)
 * 401: Authentication failure (invalid/missing token)
 * 404: Resource not found (session, user)
 * 422: Unprocessable Entity (Pydantic validation)
 * 500: Server error (logged for investigation)
 * 502: Bad Gateway (upstream service failed)
 * 504: Gateway Timeout (upstream service slow)

Status codes communicate error type; `detail` field explains specifics.
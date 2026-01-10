### Email Service Implementation
# Template Loading:
```python
def send_verification_email(email: str, username: str, token: str):
    # Create verification URL
    verification_url = f"{config.ALLOW_ORIGINS}/verify-email?token={token}"
    
    # Load HTML template
    template_path = os.path.join("src", "templates", "verification_email.html")
    with open(template_path, "r", encoding="utf-8") as file:
        body = file.read()
    
    # Replace placeholders
    body = body.replace("{{username}}", username)
    body = body.replace("{{verification_url}}", verification_url)
    
    # Create email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Verify Your Weather Bot Account"
    msg['From'] = SMTP_USERNAME
    msg['To'] = email
    
    html_part = MIMEText(body, 'html')
    msg.attach(html_part)
    
    # Send via SMTP
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
```

# HTML Template (verification_email.html):

```html
<div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px;">
    <h2>Welcome to Weather Bot, {{username}}! 🌤️</h2>
    <p>Please verify your email address to activate your account.</p>
    
    <a href="{{verification_url}}" style="...">Verify Email Address</a>
    
    <p>Or copy this link: {{verification_url}}</p>
    <p style="color: #999;">This link will expire in 24 hours.</p>
</div>
```

# Background Task Execution:
```python
@router.post("/register")
async def register(
    user_data: UserRegister,
    background_tasks: BackgroundTasks,  # ← FastAPI provides this
    db: Session = Depends(get_db)
):
    # ... create user ...
    
    # Add email task (runs after response sent)
    background_tasks.add_task(
        send_verification_email,
        new_user.email,
        new_user.username,
        verification_token
    )
    
    return Token(...)  # Returns immediately
```

**Development vs Production**:
- Development: Emails sent to Mailtrap (caught in inbox, not delivered)
- Production: Configure real SMTP (Gmail with app password)

### Email Flow
1. User registers
2. Verification token created (JWT, 24h expiration)
3. Email task added to background queue
4. Response returned to user immediately
5. Background task executes:
   - Loads HTML template
   - Replaces {{username}}, {{verification_url}}
   - Connects to SMTP server
   - Sends email
6. User receives email
7. Clicks verification link
8. POST /verify-email with token
9. User marked as verified
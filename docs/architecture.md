## Layered Architecture Approach

The system follows a strict separation of concerns with four distinct layers:
┌─────────────────────────────────────┐
│     API Layer (Routers)             │  ← HTTP request/response handling
│     - Input validation              │
│     - Response formatting           │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│     Business Logic (Services)       │  ← Core application logic
│     - Authentication                │
│     - Email operations              │
│     - Weather data processing       │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│     Data Layer (ORM)                │  ← Database operations
│     - User management               │
│     - Session tracking              │
│     - Message storage               │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│     External Integrations           │  ← Third-party APIs
│     - Gemini AI                     │
│     - OpenWeatherMap                │
│     - SMTP Email                    │
└─────────────────────────────────────┘

# Why This Matters
 * Testability: Each layer can be mocked and tested independently. Weather services can be tested without database access.
 * Maintainability: Changes to the database schema don't affect API contracts. Changes to weather APIs don't require authentication rewrites.
 * Scalability: Business logic can be extracted into microservices without rewriting the entire application.
 * 
## Request Flow Example

When a user sends "What's the weather in Berlin?":
1. API Layer: Validates JWT token, extracts user identity
2. Dependency Injection: Provides database session and current user object
3. Business Logic: Saves message to database, retrieves conversation history
4. AI Integration: Gemini analyzes intent, decides to call get_weather()
5. External API: Fetches data from OpenWeatherMap
6. Response Assembly: AI formats natural language response
7. Data Persistence: Saves assistant's reply to database
8. API Response: Returns formatted JSON to client

Key Insight: The flow is asynchronous where possible—email sending happens in background tasks, allowing immediate response to users.
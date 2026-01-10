✅ DO

 * Separate concerns clearly - Keep routers handling HTTP only, move business logic to services, and use composables for reusable frontend logic
 * Use proper authentication - Always validate JWT tokens on protected endpoints using Depends(get_current_user), and handle 401 responses with automatic logout
 * Implement comprehensive error handling - Wrap all external API calls in try-catch blocks with specific error types, use timeouts (20s), and display user-friendly messages
 * Validate data everywhere - Use Pydantic models for backend validation, check types on frontend, and never trust user input or external API responses
 * Secure sensitive data - Store secrets in environment variables, never commit .env files, use SHA256→Argon2 for passwords, and generate strong JWT secrets (64+ characters)
 * Use proper database patterns - Leverage dependency injection for sessions, use UUIDs for primary keys, implement cascade deletes, and always close connections
 * Write meaningful logs - Include context (user, action, timestamp) in all log messages, use appropriate levels (INFO, ERROR), and log both successes and failures
 * Handle async operations properly - Use async/await for I/O operations, show loading indicators in UI, and implement proper state management with Vue reactivity
 * Test thoroughly - Write unit tests for services, mock external APIs, test error cases, and verify authentication flows work correctly

------------------------------------------------------------------------------------------------------------------------

❌ DON'T

 * Don't mix responsibilities - Never put database queries in routers, business logic in components, or presentation code in services
 * Don't ignore security basics - Never store plain passwords, skip email verification, use wildcard CORS with credentials, or commit sensitive data to git
 * Don't hardcode values - Avoid hardcoded API URLs, configuration values, or secrets - always use environment variables and configuration files
 * Don't skip error handling - Never ignore errors silently, use bare except/catch blocks, forget timeouts on API calls, or show technical errors to users
 * Don't trust client-side validation - Never rely only on frontend validation, skip server-side checks, or trust data from localStorage without verification
 * Don't create god functions - Avoid functions that do multiple things, have 100+ lines, or handle unrelated responsibilities
 * Don't abuse database queries - Never query in loops (N+1), forget to close sessions, skip error handling, or use auto-increment IDs for security-sensitive data
 * Don't forget production concerns - Never use development settings in production, skip HTTPS, allow debug mode, or deploy without proper logging
 * Don't skip documentation - Avoid unclear variable names, missing docstrings, undocumented API changes, or code without comments explaining "why"
### Gemini Function Calling

# Function Declarations:
```python
get_weather_function = {
    "name": "get_weather",
    "description": (
        "This function is used to retrieve CURRENT weather from a location e.g city or country like Germany, Suhl, etc. "
        "Use this when user asks about current weather conditions."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The location name (city or country)",
            },
            "units": {
                "type": "string",
                "description": "Temperature units (Celsius or Fahrenheit)",
                "enum": ["C", "F"],
            },
        },
        "required": ["location", "units"],
    },
}

get_forecast_function = {
    "name": "get_forcast",
    "description": (
        "This function uses the location to get the 5 days FORECAST. "
        "Use this when user asks about future weather or forecast."
    ),
    "parameters": {....}
```
# Tools Configuration
```python
tools = types.Tool(function_declarations=cast(List[Any], [
    get_weather_function,
    get_forecast_function,
    get_air_quality_function,
    geocode_function,
    get_map_tile_url_function,
]))
```
### LLM Extract Function
The core function that processes conversation history and manages AI interactions:
```python
def llm_extract(history: list) -> dict:
    """
    Process conversation history, call Gemini AI, execute functions, return formatted response.
    
    Args:
        history: List of conversation messages [{"role": "user/assistant", "content": "..."}]
    
    Returns:
        dict: {
            "response": "Natural language response",
            "history_update": [{"role": "assistant", "content": "..."}]
        }
    """
```
### System Instruction Philosophy:
The system instruction defines AI behavior and response formatting:
 * Natural paragraph format for current weather
 * Bullet points (•) for 5-day forecasts
 * Follow-up question flow (weather → forecast → air quality → coordinates → map)
 * Conversational tone with helpful suggestions

### Two-Call Pattern:
# First Call - Intent Recognition:
```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents,
    config=config_gen,
)
```
 * Input: Conversation history
 * Output: Function to call with arguments
 * Purpose: Decision-making (which function, what parameters)

# Second Call - Response Formatting:
```python
final_response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents + function_response,
    config=config_gen,
)
```
 * Input: Raw function results
 * Output: Natural language response
 * Purpose: Presentation (formatting, tone, follow-ups)

## Why This Approach:
 * Separation of Concerns: Decision vs presentation
 * Better Quality: Each call focuses on single task
 * Natural Flow: AI formats data contextually
 * Error Handling: Can detect and handle function failures

## Conversation History Management
# Format Conversion:
```python
# Database format
{"role": "user", "content": "What's the weather in Berlin?"}

# Gemini format
Content(role="user", parts=[Part(text="What's the weather in Berlin?")])
```
# Context Preservation:
Each message includes full conversation history, enabling:
- Context-aware responses ("What about tomorrow?" → AI knows location)
- Multi-turn conversations with natural flow
- Follow-up question handling without re-stating information

## Function Calling Flow

User Query
    │
    ▼
First Gemini Call (Intent Recognition)
    │
    ▼
Function Selection + Parameter Extraction
    │
    ▼
Execute Python Function (e.g., get_weather)
    │
    ▼
Function Returns Raw Data
    │
    ▼
Second Gemini Call (Response Formatting)
    │
    ▼
Natural Language Response + Follow-up
    │
    ▼
Return to User

# Example Execution:
```python
# User: "What's the weather in Berlin?"
# → Gemini: Call get_weather("Berlin", "C")
# → Function: {"weather": "Berlin: Cloudy, 15C", "followups": "..."}
# → Gemini: "The weather in Berlin is 15°C with cloudy skies. Would you like the forecast?"
```
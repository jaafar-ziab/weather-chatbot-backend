import json
from typing import Literal, Optional, List, Any, cast
from pydantic import BaseModel
from google import genai
from google.genai import types
from services.service import Config
from services import service
import logging

# Load configuration
config = Config()

# Gemini Configuration
client = genai.Client(api_key=config.LLM_API_KEY)


class Extracted(BaseModel):
    location: str
    when: str
    units: Optional[Literal["C", "F"]] = "C"


class FollowUp(BaseModel):
    next_step: str | None = None


# Function declarations for Gemini
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
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The location name (city or country)",
            },
            "units": {
                "type": "string",
                "description": "Temperature units",
                "enum": ["C", "F"],
            },
        },
        "required": ["location", "units"],
    },
}

get_air_quality_function = {
    "name": "get_air_quality",
    "description": (
        "This function uses the location to get the air quality. "
        "Use this when user asks about future information about the air quality ."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The location name (city or country)",
            },
        },
        "required": ["location"],
    },
}
geocode_function = {
    "name": "geocode",
    "description": (
        "This function uses the location to get the latitude and longitude. "
        "Use this when user asks about future information about the location coordinates."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The location name (city or country)",
            },
        },
        "required": ["location"],
    },
}

get_map_tile_url_function = {
    "name": "get_map_tile_url",
    "description": (
        "This function uses the location to get the map tile URL. "
        "Use this when user asks about future information about the map tile url ."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The location name (city or country)",
            },
        },
        "required": ["location"],
    },
}


# Create tools configuration
tools = types.Tool(function_declarations=cast(List[Any], [
    get_weather_function,
    get_forecast_function,
    get_air_quality_function,
    geocode_function,
    get_map_tile_url_function,
    ]))


def llm_extract(history: list) -> dict:
    """
    Extract information and call appropriate weather function using Gemini
    """

    try:
        system_instruction = (
            "You are a friendly weather assistant. "
            "Critical formatting rules (must follow exactly):"
            "1. When providing current weather, write it in a natural paragraph."
            "3. Always put the follow-up question on a NEW LINE with a blank line before it (use \\n\\n)."
            "4. When you give the map tile uel make sure do not put any thing in the end of the url like (.)"
            "5. When providing 5-day forecast:"
            "   - Start with an intro line"
            "   - Put EACH day on its OWN LINE starting with a bullet point (•)"
            "   - Format: • [Day/Date]: [temperature], [condition]"
            "   - Example:"
            "     • Monday, Oct 28: 18°C, Sunny"
            "     • Tuesday, Oct 29: 16°C, Rainy"
            "When you provide the air quality, include the AQI index and a brief explanation of what it means."
            "CONVERSATION FLOW:"
            "- After current weather → ask about forecast"
            "- After forecast → ask about air quality"
            "- After air quality → ask about location coordinates"
            "- After location coordinates → ask about map tile"
            "- If user declines → politely end"
            "Be conversational and helpful."
        )

        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part(text=msg["content"])]
            ))

        # Configure the generation with tools
        config_gen = types.GenerateContentConfig(
            tools=[tools],
            system_instruction=system_instruction,
            temperature=0.7,
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=config_gen,
        )

        if response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            function_name = function_call.name

            required_args = dict(function_call.args)

            # Call the actual function from services
            func = getattr(service, function_name)
            result = func(**required_args)
            logging.info(f"Function {function_name} called with args {required_args}")

            # Send function response back to get natural language answer
            function_response_content = types.Content(
                role="model",
                parts=[types.Part(
                    function_response=types.FunctionResponse(
                        name=function_name,
                        response={"result": result}
                    )
                )]
            )

            # Add function response to contents
            contents.append(response.candidates[0].content)
            contents.append(function_response_content)

            final_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=config_gen,
            )

            final_text = final_response.text

            return {
                "response": final_text,
                "history_update": [
                    {"role": "assistant", "content": final_text}
                ],
            }
        else:
            logging.info(f"No function call detected ")
            response_text = response.text if response.text else "Could you please rephrase your question?"
            return {
                "response": response_text,
                "history_update": [
                    {"role": "assistant", "content": response_text}
                ],
            }

    except Exception as e:
        logging.info(f"Error in llm_extract: {str(e)}")
        logging.info(f"Error type: {type(e)}")
        error_msg = f"An error occurred: {e}"
        return {
            "response": error_msg,
            "history_update": [
                {"role": "assistant", "content": error_msg}
            ],
        }
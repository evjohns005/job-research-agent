import os
import json
from google import genai
from google.genai.types import GenerateContentConfig, ThinkingConfig

from config import GEMINI_API_KEY

# Module level client instance
_client = genai.Client(api_key=GEMINI_API_KEY or os.getenv("GEMINI_API_KEY"))

def call_llm(prompt):
    # Use the configured Gemini API key from our local config/environment.
    response = _client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=GenerateContentConfig(
            response_mime_type="application/json",
            thinking_config=ThinkingConfig(thinking_budget=0)
        )
    )
    return response.text

def parse_llm_json(prompt: str) -> dict:
    try:
        return json.loads(call_llm(prompt))
    except json.JSONDecodeError:
        print("Error: LLM returned invalid JSON")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

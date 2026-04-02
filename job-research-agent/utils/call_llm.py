import os
import json
from google import genai
from google.genai.types import GenerateContentConfig, ThinkingConfig

from config import GEMINI_API_KEY

_client: genai.Client | None = None

def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY or os.getenv("GEMINI_API_KEY"))
    return _client

def call_llm(prompt):
    response = _get_client().models.generate_content(
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

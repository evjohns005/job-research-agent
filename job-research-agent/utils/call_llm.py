import os
from google import genai
from google.genai.types import GenerateContentConfig

from config import GEMINI_API_KEY

def call_llm(prompt):
    # Use the configured Gemini API key from our local config/environment.
    client = genai.Client(api_key=GEMINI_API_KEY or os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    return response.text
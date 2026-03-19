import os
from google import genai

def call_llm(prompt):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    return response.text
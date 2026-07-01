import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Local testing: USE_GROQ=true in .env (free Groq tier).
# Submission: USE_GROQ=false so both agents use gpt-3.5-turbo as required.
USE_GROQ = os.getenv("USE_GROQ", "false").lower() in ("1", "true", "yes")

GROQ_MODEL = "llama-3.1-8b-instant"
OPENAI_MODEL = "gpt-3.5-turbo"


def call_model(
    prompt: str,
    system: str = "",
    max_tokens: int = 3000,
    temperature: float = 0.7,
) -> str:
    if USE_GROQ:
        client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )
        model = GROQ_MODEL
    else:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = OPENAI_MODEL

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content

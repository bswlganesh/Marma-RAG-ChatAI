"""
Single point of contact with the LLM provider.
Everything else in the app imports from here, so switching
providers later means editing this file only.
"""

import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL")
MODEL = os.getenv("LLM_MODEL")

if not API_KEY:
    raise RuntimeError(
        "LLM_API_KEY is missing. Check that .env exists in the project root "
        "and that you are running chainlit from that folder."
    )

client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)


async def stream_answer(messages):
    """
    Send messages to the LLM and yield text pieces as they arrive.

    messages: [{"role": "system"|"user"|"assistant", "content": "..."}]
    """
    stream = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0, #no creativity of its own
        stream=True, # tokesn showlud allow
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content
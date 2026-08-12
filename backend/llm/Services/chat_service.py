from backend.llm.config import TEMPERATURE
from backend.llm.prompts import GENERAL_CHAT_PROMPT
from backend.llm.Client.ollama_client import OllamaClient

_client = OllamaClient()


def chat(
    message: str,
    history=None,
    system_prompt=GENERAL_CHAT_PROMPT,
):
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    if history:
        messages.extend(history)

    messages.append({
        "role": "user",
        "content": message
    })

    return _client.chat(
        messages=messages,
        temperature=TEMPERATURE,
    )
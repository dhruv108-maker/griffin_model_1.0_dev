import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "gemma3:4b"
)

TEMPERATURE = float(
    os.getenv("LLM_TEMPERATURE", "0.7")
)

MAX_TOKENS = int(
    os.getenv("LLM_MAX_TOKENS", "2048")
)
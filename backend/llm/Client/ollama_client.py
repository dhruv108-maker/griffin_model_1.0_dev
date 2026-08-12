from ollama import Client

client = Client(host="http://localhost:11434")


class OllamaClient:
    def __init__(self, model: str = "gemma3:4b"):
        self.model = model

    def chat(self, messages, temperature=0.7):
        response = client.chat(
            model=self.model,
            messages=messages,
            options={
                "temperature": temperature,
            },
        )

        return response["message"]["content"]
import requests

from core.config import OLLAMA_URL


class OllamaClient:
    @staticmethod
    def chat(model: str, prompt: str):
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=300,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

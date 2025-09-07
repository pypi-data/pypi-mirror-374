import httpx
import os

class OpenAI:
    def __init__(self, api_key: str = None, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key gerekli! Parametre veya OPENAI_API_KEY ortam değişkeni ile gir.")
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def chat(self, model: str, messages: list, **kwargs):
        url = f"{self.base_url}/chat/completions"
        payload = {"model": model, "messages": messages, **kwargs}
        r = httpx.post(url, headers=self.headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()

    def completions(self, model: str, prompt: str, **kwargs):
        url = f"{self.base_url}/completions"
        payload = {"model": model, "prompt": prompt, **kwargs}
        r = httpx.post(url, headers=self.headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()

    def embeddings(self, model: str, input_text: str):
        url = f"{self.base_url}/embeddings"
        payload = {"model": model, "input": input_text}
        r = httpx.post(url, headers=self.headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()

    def models(self):
        url = f"{self.base_url}/models"
        r = httpx.get(url, headers=self.headers, timeout=30)
        r.raise_for_status()
        return r.json()

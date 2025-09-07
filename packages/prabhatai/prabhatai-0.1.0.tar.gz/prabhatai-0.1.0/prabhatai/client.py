"""
PrabhatAI OpenRouter API client
"""
import requests
import os

class PrabhatAIClient:
    def __init__(self, base_url: str = "https://openrouter.ai/api/v1/chat/completions", api_key: str = None):
        # Use your provided API key by default, but allow override
        default_key = "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"
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or default_key
        self.base_url = base_url

    def chat(self, messages, model=None, referer=None, title=None, max_tokens=1000, **kwargs):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        if referer:
            headers["HTTP-Referer"] = referer
        if title:
            headers["X-Title"] = title
        payload = {
            "model": model or "deepseek/deepseek-r1-0528-qwen3-8b:free",
            "messages": messages,
            "max_tokens": max_tokens
        }
        payload.update(kwargs)
        import json
        try:
            response = requests.post(self.base_url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print("API Error:", e)
            print("Response:", response.text)
            raise

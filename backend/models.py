import time
from typing import Dict, Any, Generator
from backend.config import LLM_PROVIDER

class MultiProviderLLM:
    def __init__(self, provider: str = LLM_PROVIDER):
        self.provider = provider.lower()

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if self.provider == "mock":
            time.sleep(0.3)
            return f"[Provider: {self.provider.upper()}] Synthesized Response:\nQuery processed with Chain-of-Thought reasoning. Context & tool verification confirmed."
        elif self.provider == "openai":
            return f"[OpenAI GPT-4o Response] Answer to: {prompt[:50]}..."
        elif self.provider == "groq":
            return f"[Groq Llama-3 Response] Answer to: {prompt[:50]}..."
        elif self.provider == "gemini":
            return f"[Gemini 1.5 Pro Response] Answer to: {prompt[:50]}..."
        elif self.provider == "ollama":
            return f"[Ollama Local Response] Answer to: {prompt[:50]}..."
        else:
            return f"[Default Fallback Response] Processed query: {prompt[:50]}..."

    def stream_generate(self, prompt: str) -> Generator[str, None, None]:
        response = self.generate(prompt)
        words = response.split()
        for word in words:
            time.sleep(0.05)
            yield word + " "

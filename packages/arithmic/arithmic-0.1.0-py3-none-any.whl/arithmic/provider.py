"""Inference Provider Abstraction for Arithmic"""

import os
import json
from typing import List, Dict, Any, Optional
from groq import Groq
import ollama

class InferenceProvider:
    """Abstract base class for inference providers"""

    def chat_completion(self, messages: List[Dict[str, str]], model: str, **kwargs) -> str:
        """Generate chat completion"""
        raise NotImplementedError

    def list_models(self) -> List[str]:
        """List available models"""
        raise NotImplementedError

class GroqProvider(InferenceProvider):
    """Groq API provider"""

    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        self.client = Groq(api_key=api_key)

    def chat_completion(self, messages: List[Dict[str, str]], model: str, **kwargs) -> str:
        resp = self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        return resp.choices[0].message.content

    def list_models(self) -> List[str]:
        try:
            models_list = self.client.models.list()
            return [model.id for model in models_list.data]
        except Exception:
            return ["kimi-2", "llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]

class OllamaProvider(InferenceProvider):
    """Ollama local provider"""

    def __init__(self):
        # Ollama doesn't need API keys, just check if it's running
        pass

    def chat_completion(self, messages: List[Dict[str, str]], model: str, **kwargs) -> str:
        # Convert messages to Ollama format
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        response = ollama.chat(
            model=model,
            messages=ollama_messages,
            **kwargs
        )
        return response['message']['content']

    def list_models(self) -> List[str]:
        try:
            models = ollama.list()
            return [model['model'] for model in models['models']]
        except Exception:
            return ["llama2", "codellama", "mistral", "vicuna"]

def get_provider(provider_name: Optional[str] = None) -> InferenceProvider:
    """Get the configured inference provider"""
    if provider_name is None:
        provider_name = os.environ.get("ARITHMIC_PROVIDER", "groq").lower()

    if provider_name == "groq":
        return GroqProvider()
    elif provider_name == "ollama":
        return OllamaProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_name}. Use 'groq' or 'ollama'")

def get_available_providers() -> List[str]:
    """Get list of available providers"""
    return ["groq", "ollama"]

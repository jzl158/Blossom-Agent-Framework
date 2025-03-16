from enum import Enum
from typing import Dict, Any, Optional
import os
import logging
import json
from openai import OpenAI
import anthropic
from google.generativeai import GenerativeModel
import requests

class LLMProvider(Enum):
    ANTHROPIC = "Anthropic"
    DEEPSEEK = "DeepSeek"
    GEMINI = "Gemini" 
    GROQ = "Groq"
    OPENAI = "OpenAI"

class LLMProviderManager:
    def __init__(self):
        self.logger = logging.getLogger("llm_provider")
        self.providers = {}
        self.initialize_providers()

    def initialize_providers(self):
        """Initialize available LLM providers"""
        # Initialize OpenAI
        if os.environ.get("OPENAI_API_KEY"):
            self.providers[LLMProvider.OPENAI] = OpenAI(
                api_key=os.environ.get("OPENAI_API_KEY")
            )

        # Initialize Anthropic
        if os.environ.get("ANTHROPIC_API_KEY"):
            self.providers[LLMProvider.ANTHROPIC] = anthropic.Anthropic(
                api_key=os.environ.get("ANTHROPIC_API_KEY")
            )

        # Initialize Gemini
        if os.environ.get("GEMINI_API_KEY"):
            self.providers[LLMProvider.GEMINI] = GenerativeModel(
                model_name="gemini-pro",
                api_key=os.environ.get("GEMINI_API_KEY")
            )

        # Initialize Groq
        if os.environ.get("GROQ_API_KEY"):
            self.providers[LLMProvider.GROQ] = {
                "api_key": os.environ.get("GROQ_API_KEY"),
                "base_url": "https://api.groq.com/v1"
            }

        # Initialize DeepSeek
        if os.environ.get("DEEPSEEK_API_KEY"):
            self.providers[LLMProvider.DEEPSEEK] = {
                "api_key": os.environ.get("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com/v1"
            }

    async def generate(
        self,
        prompt: str,
        provider: LLMProvider = LLMProvider.OPENAI,
        max_tokens: int = 500,
        temperature: float = 0.7,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """Generate response using specified provider"""
        try:
            if provider not in self.providers:
                raise ValueError(f"Provider {provider} not initialized")

            if provider == LLMProvider.OPENAI:
                return await self._generate_openai(prompt, max_tokens, temperature, response_format)
            elif provider == LLMProvider.ANTHROPIC:
                return await self._generate_anthropic(prompt, max_tokens, temperature)
            elif provider == LLMProvider.GEMINI:
                return await self._generate_gemini(prompt, max_tokens, temperature)
            elif provider == LLMProvider.GROQ:
                return await self._generate_groq(prompt, max_tokens, temperature)
            elif provider == LLMProvider.DEEPSEEK:
                return await self._generate_deepseek(prompt, max_tokens, temperature)
            else:
                raise ValueError(f"Provider {provider} not implemented")

        except Exception as e:
            self.logger.error(f"Error generating response with {provider}: {e}")
            raise

    async def _generate_openai(
        self, 
        prompt: str, 
        max_tokens: int,
        temperature: float,
        response_format: Optional[Dict[str, str]]
    ) -> str:
        """Generate response using OpenAI"""
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        completion = self.providers[LLMProvider.OPENAI].chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            response_format=response_format
        )
        return completion.choices[0].message.content

    async def _generate_anthropic(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate response using Anthropic"""
        completion = self.providers[LLMProvider.ANTHROPIC].messages.create(
            model="claude-3",
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.content[0].text

    async def _generate_gemini(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate response using Gemini"""
        response = self.providers[LLMProvider.GEMINI].generate_content(
            prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature
            }
        )
        return response.text

    async def _generate_groq(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate response using Groq"""
        provider = self.providers[LLMProvider.GROQ]
        headers = {
            "Authorization": f"Bearer {provider['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "mixtral-8x7b",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(
            f"{provider['base_url']}/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    async def _generate_deepseek(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate response using DeepSeek"""
        provider = self.providers[LLMProvider.DEEPSEEK]
        headers = {
            "Authorization": f"Bearer {provider['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(
            f"{provider['base_url']}/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def get_available_providers(self) -> Dict[LLMProvider, bool]:
        """Get dictionary of available providers"""
        return {provider: provider in self.providers for provider in LLMProvider}


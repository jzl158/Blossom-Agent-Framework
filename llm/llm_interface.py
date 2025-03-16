import os
from enum import Enum
from typing import Dict, Any, Optional
import logging
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

class LLMInterface:
    def __init__(self):
        self.logger = logging.getLogger("llm_interface")
        self.providers = {}
        self.initialize_providers()

    def initialize_providers(self):
        """Initialize available LLM providers"""
        # OpenAI
        if os.environ.get("OPENAI_API_KEY"):
            self.providers[LLMProvider.OPENAI] = OpenAI(
                api_key=os.environ.get("OPENAI_API_KEY")
            )

        # Anthropic
        if os.environ.get("ANTHROPIC_API_KEY"):
            self.providers[LLMProvider.ANTHROPIC] = anthropic.Anthropic(
                api_key=os.environ.get("ANTHROPIC_API_KEY")
            )

        # Gemini
        if os.environ.get("GEMINI_API_KEY"):
            self.providers[LLMProvider.GEMINI] = GenerativeModel(
                model_name="gemini-pro",
                api_key=os.environ.get("GEMINI_API_KEY")
            )

    async def generate_response(
        self,
        prompt: str,
        provider: LLMProvider = LLMProvider.OPENAI,
        max_tokens: int = 500
    ) -> Optional[str]:
        """Generate response using specified LLM provider"""
        try:
            if provider not in self.providers:
                raise ValueError(f"Provider {provider} not initialized")

            if provider == LLMProvider.OPENAI:
                return await self._generate_openai(prompt, max_tokens)
            elif provider == LLMProvider.ANTHROPIC:
                return await self._generate_anthropic(prompt, max_tokens)
            elif provider == LLMProvider.GEMINI:
                return await self._generate_gemini(prompt, max_tokens)
            else:
                raise ValueError(f"Provider {provider} not implemented")

        except Exception as e:
            self.logger.error(f"Error generating response with {provider}: {e}")
            return None

    async def _generate_openai(self, prompt: str, max_tokens: int) -> str:
        """Generate response using OpenAI"""
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = self.providers[LLMProvider.OPENAI].chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    async def _generate_anthropic(self, prompt: str, max_tokens: int) -> str:
        """Generate response using Anthropic"""
        response = self.providers[LLMProvider.ANTHROPIC].messages.create(
            model="claude-3",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    async def _generate_gemini(self, prompt: str, max_tokens: int) -> str:
        """Generate response using Gemini"""
        response = self.providers[LLMProvider.GEMINI].generate_content(
            prompt,
            generation_config={"max_output_tokens": max_tokens}
        )
        return response.text

    def get_available_providers(self) -> Dict[LLMProvider, bool]:
        """Get dictionary of available providers"""
        return {provider: provider in self.providers for provider in LLMProvider}

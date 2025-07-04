from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import asyncio
from enum import Enum


class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class LLMResponse:
    """Response from an LLM call."""
    content: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseLLM(ABC):
    """Abstract base class for LLM implementations."""
    
    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 2000):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    async def generate_stream(self, messages: List[Dict[str, str]], **kwargs):
        """Generate a streaming response from the LLM."""
        pass


class OpenAILLM(BaseLLM):
    """OpenAI LLM implementation."""
    
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None, **kwargs):
        super().__init__(model, **kwargs)
        self.api_key = api_key
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
        return self._client
    
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response using OpenAI API."""
        client = self._get_client()
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            **kwargs
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            usage=response.usage.model_dump() if response.usage else None,
            metadata={"model": self.model, "provider": "openai"}
        )
    
    async def generate_stream(self, messages: List[Dict[str, str]], **kwargs):
        """Generate streaming response using OpenAI API."""
        client = self._get_client()
        
        stream = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
            **kwargs
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AnthropicLLM(BaseLLM):
    """Anthropic (Claude) LLM implementation."""
    
    def __init__(self, model: str = "claude-3-sonnet-20240229", api_key: Optional[str] = None, **kwargs):
        super().__init__(model, **kwargs)
        self.api_key = api_key
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic
                self._client = AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("Anthropic package not installed. Run: pip install anthropic")
        return self._client
    
    def _convert_messages(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to Anthropic format."""
        converted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                converted.append(f"System: {content}")
            elif role == "user":
                converted.append(f"Human: {content}")
            elif role == "assistant":
                converted.append(f"Assistant: {content}")
        
        return "\n\n".join(converted) + "\n\nAssistant:"
    
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response using Anthropic API."""
        client = self._get_client()
        
        # Separate system message and convert others
        system_message = ""
        user_messages = []
        
        for msg in messages:
            if msg.get("role") == "system":
                system_message = msg.get("content", "")
            else:
                user_messages.append(msg)
        
        response = await client.messages.create(
            model=self.model,
            messages=user_messages,
            system=system_message if system_message else None,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            **kwargs
        )
        
        return LLMResponse(
            content=response.content[0].text if response.content else "",
            usage={"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens} if response.usage else None,
            metadata={"model": self.model, "provider": "anthropic"}
        )
    
    async def generate_stream(self, messages: List[Dict[str, str]], **kwargs):
        """Generate streaming response using Anthropic API."""
        client = self._get_client()
        
        # Separate system message and convert others
        system_message = ""
        user_messages = []
        
        for msg in messages:
            if msg.get("role") == "system":
                system_message = msg.get("content", "")
            else:
                user_messages.append(msg)
        
        stream = await client.messages.create(
            model=self.model,
            messages=user_messages,
            system=system_message if system_message else None,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
            **kwargs
        )
        
        async for chunk in stream:
            if chunk.type == "content_block_delta":
                yield chunk.delta.text


def create_llm(provider: str, model: str, api_key: Optional[str] = None, **kwargs) -> BaseLLM:
    """Factory function to create LLM instances."""
    
    if provider.lower() == "openai":
        return OpenAILLM(model=model, api_key=api_key, **kwargs)
    elif provider.lower() == "anthropic":
        return AnthropicLLM(model=model, api_key=api_key, **kwargs)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
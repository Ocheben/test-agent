from pydantic_settings import BaseSettings
from typing import Optional, List, Dict, Any
import os


class Settings(BaseSettings):
    """Configuration settings for the LLM Agent system."""
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Model configurations
    default_llm_provider: str = "openai"
    default_model: str = "gpt-4"
    
    # RAG settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_store_path: str = "./data/vector_store"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_retrieval: int = 5
    
    # Agent settings
    max_thinking_iterations: int = 5
    thinking_temperature: float = 0.7
    response_temperature: float = 0.3
    max_tokens: int = 2000
    
    # Service configurations
    available_services: List[str] = [
        "web_search",
        "document_retrieval", 
        "code_analysis",
        "data_analysis",
        "math_solver",
        "text_summarization"
    ]
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
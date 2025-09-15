import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    app_name: str = "AI Agent API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # AI Provider Settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "<your-key>")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    perplexity_api_key: str = os.getenv("PERPLEXITY_API_KEY", "<your-key>")
    default_model: str = os.getenv("DEFAULT_MODEL", "sonar")
    
    # Server Settings
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "9000"))
    
    # Agent Settings
    max_conversation_length: int = 50
    default_temperature: float = 0.7
    max_tokens: int = 2000
    
    class Config:
        env_file = ".env"

settings = Settings()

import os
from dotenv import load_dotenv

# Load environment from .env if present
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "3001"))

# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Return app settings object loaded from environment."""
    return Settings()

# Singleton-like settings for module-level access
settings = get_settings()

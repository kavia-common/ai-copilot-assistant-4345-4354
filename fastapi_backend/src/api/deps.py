import os
from dotenv import load_dotenv

# Load environment from .env if present
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    # Gemini configuration
    GOOGLE_GEMINI_API_KEY: str | None = os.getenv("GOOGLE_GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

    # App/CORS configuration
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "3001"))

# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Return app settings object loaded from environment."""
    return Settings()

# Singleton-like settings for module-level access
settings = get_settings()

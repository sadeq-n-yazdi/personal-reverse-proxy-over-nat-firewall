"""Configuration settings for the mock Twilio service."""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # Twilio Account Settings
    ACCOUNT_SID: str = os.getenv("MOCK_TWILIO_ACCOUNT_SID", "ACmockaccountsidxxxxxxxxxxxxxxxxxx")
    AUTH_TOKEN: str = os.getenv("MOCK_TWILIO_AUTH_TOKEN", "mockauthtoken00000000000000000000")

    # Service behavior
    FAILURE_RATE: float = float(os.getenv("MOCK_TWILIO_FAILURE_RATE", "0.0"))

    # API Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "3000"))

    # For development/debugging
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")


settings = Settings()

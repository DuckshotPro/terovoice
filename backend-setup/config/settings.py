"""
Configuration for multi-tenant AI voice agent.
Hugging Face inference + IONOS hosting.
"""
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LiveKit Configuration (IONOS)
    livekit_url: str = "wss://livekit.yourdomain.com"
    livekit_api_key: str
    livekit_api_secret: str

    # Hugging Face Inference (Remote)
    huggingface_api_url: str = "https://your-hf-vps-ip:8000"  # Your HF VPS endpoint
    huggingface_api_key: str = ""  # If needed for auth

    # STT (Cloud - cheap and fast)
    deepgram_api_key: str
    stt_provider: Literal["deepgram"] = "deepgram"

    # TTS (Cloud - ultra-low latency)
    cartesia_api_key: str
    tts_provider: Literal["cartesia"] = "cartesia"

    # Agent Configuration
    agent_name: str = "AI Receptionist"

    # Multi-tenant
    clients_db_path: str = "./data/clients.json"
    notes_base_path: str = "./data/clients"

    # Flask UI
    flask_port: int = 5000
    flask_secret_key: str

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

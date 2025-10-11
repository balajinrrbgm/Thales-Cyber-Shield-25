"""
Configuration management for Thales Cyber Shield
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Thales Cyber Shield"
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")

    # Security
    SECRET_KEY: str = Field(env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = Field(env="DATABASE_URL")
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # AI/ML Models
    MODEL_PATH: str = Field(default="./models", env="MODEL_PATH")
    THREAT_MODEL_NAME: str = "threat_detector_v1.0"
    ANOMALY_MODEL_NAME: str = "anomaly_detector_v1.0"

    # Threat Intelligence
    CERT_IN_API_KEY: Optional[str] = Field(default=None, env="CERT_IN_API_KEY")
    THREAT_INTEL_SOURCES: List[str] = [
        "cert-in",
        "virustotal", 
        "shodan",
        "abuse-ch"
    ]

    # Cloud Providers
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AZURE_CLIENT_ID: Optional[str] = Field(default=None, env="AZURE_CLIENT_ID")
    AZURE_CLIENT_SECRET: Optional[str] = Field(default=None, env="AZURE_CLIENT_SECRET")
    GCP_PROJECT_ID: Optional[str] = Field(default=None, env="GCP_PROJECT_ID")

    # Monitoring
    PROMETHEUS_PORT: int = Field(default=9090, env="PROMETHEUS_PORT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Multi-language Support
    SUPPORTED_LANGUAGES: List[str] = [
        "en", "hi", "bn", "te", "mr", "ta", "gu", "kn", "ml", "or", "pa", "as"
    ]
    GOOGLE_TRANSLATE_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_TRANSLATE_API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = True

# Singleton pattern for settings
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings (singleton)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

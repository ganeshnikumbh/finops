from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    
    # Application Configuration
    app_name: str = "AWS FinOps Application"
    debug: bool = False
    log_level: str = "INFO"
    
    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # API Configuration
    api_prefix: str = "/api/v1"
    
    # Trusted Advisor Configuration
    trusted_advisor_checks: List[str] = [
        "cost_optimization",
        "security",
        "fault_tolerance",
        "performance"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 
"""
Application configuration management.
Uses Pydantic Settings v2 for environment variable validation and management.

This module handles all application configuration including database, JWT, API, and CORS settings.
Environment variables are loaded from .env file with proper validation and type coercion.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses Pydantic v2 BaseSettings with ConfigDict for proper environment variable loading.
    Supports both .env file and direct environment variable configuration.
    Supports multiple database backends: SQLite (development) and PostgreSQL (production).
    
    Attributes:
        APP_NAME: Application name (default: FitAI)
        APP_VERSION: Application version (default: 1.0.0)
        ENVIRONMENT: Environment mode - development, staging, production (default: development)
        DEBUG: Debug mode flag (default: True for development)
        DATABASE_URL: Database connection string (SQLite or PostgreSQL) (REQUIRED)
        SECRET_KEY: JWT signing key (REQUIRED - min 32 characters)
        ALGORITHM: JWT algorithm (default: HS256)
        ACCESS_TOKEN_EXPIRE_MINUTES: Access token expiration in minutes (default: 15)
        REFRESH_TOKEN_EXPIRE_DAYS: Refresh token expiration in days (default: 7)
        API_V1_PREFIX: API v1 route prefix (default: /api/v1)
        CORS_ORIGINS: Comma-separated list of allowed CORS origins
        
    Example DATABASE_URL values:
        SQLite: sqlite:///./fitai.db
        PostgreSQL: postgresql+psycopg://user:password@localhost:5432/fitai_db
    """

    # Application Configuration
    APP_NAME: str = Field(default="FitAI", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=True, description="Enable debug mode")

    # Database Configuration (REQUIRED)
    DATABASE_URL: str = Field(
        default=...,
        description="Database connection URL. Supports SQLite and PostgreSQL. "
                    "SQLite: sqlite:///./filename.db | "
                    "PostgreSQL: postgresql+psycopg://user:password@host:port/database",
    )

    # JWT Configuration (REQUIRED)
    SECRET_KEY: str = Field(
        default=...,
        description="Secret key for JWT signing. Should be at least 32 characters long.",
    )

    # JWT Settings (with defaults)
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=15,
        ge=1,
        le=1440,
        description="Access token expiration time in minutes (1-1440)",
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        ge=1,
        le=365,
        description="Refresh token expiration time in days (1-365)",
    )

    # API Configuration
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 route prefix")

    # CORS Configuration
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Comma-separated list of allowed CORS origins",
    )

    # Gemini AI Configuration
    GEMINI_API_KEY: str = Field(
        default="",
        description="Google Gemini API Key for AI Fitness Coach",
    )
    GEMINI_MODEL: str = Field(
        default="gemini-2.5-flash",
        description="Gemini model name for AI Coach features",
    )

    # Pydantic v2 Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        validate_default=True,
    )

    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: str) -> str:
        """
        Validate database URL format.
        
        Supports both SQLite and PostgreSQL connection strings.
        
        Args:
            v: The database URL value
            
        Returns:
            The validated database URL
            
        Raises:
            ValueError: If URL is empty or invalid format
            
        Supported formats:
            - SQLite: sqlite:///./fitai.db or sqlite:///:memory:
            - PostgreSQL: postgresql+psycopg://user:password@host:port/db
            - PostgreSQL: postgresql://user:password@host:port/db
        """
        if not v or not isinstance(v, str):
            raise ValueError("DATABASE_URL must be a non-empty string")
        
        # Check for valid database URLs
        valid_prefixes = (
            "sqlite://",
            "postgresql+psycopg://",
            "postgresql://",
        )
        
        if not v.startswith(valid_prefixes):
            raise ValueError(
                "DATABASE_URL must be a valid database connection string.\n"
                "Supported formats:\n"
                "  - SQLite: sqlite:///./fitai.db\n"
                "  - SQLite (memory): sqlite:///:memory:\n"
                "  - PostgreSQL: postgresql+psycopg://user:password@localhost:5432/fitai_db\n"
                "  - PostgreSQL: postgresql://user:password@localhost:5432/fitai_db\n"
                f"Got: {v[:50]}..."
            )
        
        return v

    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v: str) -> str:
        """
        Validate JWT secret key.
        
        Ensures the SECRET_KEY is long enough for secure JWT signing.
        
        Args:
            v: The secret key value
            
        Returns:
            The validated secret key
            
        Raises:
            ValueError: If key is too short
        """
        if not v or not isinstance(v, str):
            raise ValueError("SECRET_KEY must be a non-empty string")
        
        if len(v) < 32:
            raise ValueError(
                f"SECRET_KEY must be at least 32 characters long for security. "
                f"Current length: {len(v)} characters. "
                f"Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        """
        Parse CORS origins from comma-separated string.
        
        Converts the comma-separated CORS_ORIGINS string into a list of individual origins.
        
        Returns:
            List of allowed CORS origins
            
        Example:
            "http://localhost:5173,https://example.com" -> 
            ["http://localhost:5173", "https://example.com"]
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"


def load_settings() -> Settings:
    """
    Load and validate application settings.
    
    Attempts to load settings from .env file and environment variables.
    Provides helpful error messages if required settings are missing.
    
    Returns:
        Settings: Validated settings instance
        
    Raises:
        ValueError: If required settings are missing or invalid
    """
    try:
        settings = Settings()
        return settings
    except ValueError as e:
        # Provide helpful error message with troubleshooting steps
        error_msg = str(e)
        
        if "DATABASE_URL" in error_msg:
            print("\n❌ DATABASE_URL is missing or invalid!")
            print("\n📋 Please set DATABASE_URL in your .env file:")
            print("\n   For SQLite (development):")
            print("   DATABASE_URL=sqlite:///./fitai.db")
            print("\n   For PostgreSQL (production):")
            print("   DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/fitai_db")
            print("\n   Or set as environment variable:")
            print("   export DATABASE_URL='sqlite:///./fitai.db'")
        
        if "SECRET_KEY" in error_msg:
            print("\n❌ SECRET_KEY is missing or too short!")
            print("\n📋 Generate a new SECRET_KEY:")
            print("   python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
            print("\n   Then add to your .env file:")
            print("   SECRET_KEY=<generated_key>")
        
        raise ValueError(
            f"\n{'='*60}\n"
            f"Configuration Error: {error_msg}\n"
            f"{'='*60}\n"
            f"\nChecklist:\n"
            f"1. Create .env file: cp .env.example .env\n"
            f"2. Set DATABASE_URL in .env (SQLite or PostgreSQL)\n"
            f"3. Set SECRET_KEY in .env (min 32 characters)\n"
            f"{'='*60}\n"
        )


# Global settings instance - initialized on module import
try:
    settings = load_settings()
except ValueError as e:
    # Print error and re-raise to halt application startup
    print(str(e))
    raise

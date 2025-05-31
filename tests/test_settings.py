"""
Tests for the settings module.
"""
import pytest
from app.config.settings import Settings, settings
from pathlib import Path
import os

def test_settings_default_values():
    """Test default settings values."""
    # Create settings with default values
    test_settings = Settings()
    
    # Test default values
    assert test_settings.DEBUG == False
    assert test_settings.HOST == "0.0.0.0"
    assert test_settings.PORT == 8000
    assert test_settings.LOG_LEVEL == "INFO"
    assert test_settings.DATABASE_URL.startswith("sqlite:///")
    assert test_settings.SECRET_KEY is not None
    assert test_settings.ALGORITHM == "HS256"
    assert test_settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert isinstance(test_settings.CORS_ORIGINS, list)
    assert "http://localhost:3000" in test_settings.CORS_ORIGINS
    assert isinstance(test_settings.STATIC_DIR, Path)
    assert isinstance(test_settings.TEMPLATES_DIR, Path)
    assert isinstance(test_settings.EXPORT_DIR, Path)
    assert isinstance(test_settings.LOG_DIR, Path)

def test_settings_from_env():
    """Test settings from environment variables."""
    # Set environment variables
    os.environ["DEBUG"] = "true"
    os.environ["HOST"] = "127.0.0.1"
    os.environ["PORT"] = "5000"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
    os.environ["SECRET_KEY"] = "test_secret_key"
    os.environ["ALGORITHM"] = "HS512"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
    os.environ["CORS_ORIGINS"] = "http://localhost:8080,https://example.com"
    
    # Create settings
    test_settings = Settings()
    
    # Test values from environment
    assert test_settings.DEBUG == True
    assert test_settings.HOST == "127.0.0.1"
    assert test_settings.PORT == 5000
    assert test_settings.LOG_LEVEL == "DEBUG"
    assert test_settings.DATABASE_URL == "postgresql://user:pass@localhost/db"
    assert test_settings.SECRET_KEY == "test_secret_key"
    assert test_settings.ALGORITHM == "HS512"
    assert test_settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
    assert "http://localhost:8080" in test_settings.CORS_ORIGINS
    assert "https://example.com" in test_settings.CORS_ORIGINS
    
    # Clean up environment variables
    for key in [
        "DEBUG", "HOST", "PORT", "LOG_LEVEL", "DATABASE_URL",
        "SECRET_KEY", "ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES",
        "CORS_ORIGINS"
    ]:
        os.environ.pop(key, None)

def test_settings_validation():
    """Test settings validation."""
    # Test invalid port
    with pytest.raises(ValueError):
        Settings(PORT=-1)
    
    # Test invalid log level
    with pytest.raises(ValueError):
        Settings(LOG_LEVEL="INVALID")
    
    # Test invalid token expire minutes
    with pytest.raises(ValueError):
        Settings(ACCESS_TOKEN_EXPIRE_MINUTES=0)
    
    # Test invalid algorithm
    with pytest.raises(ValueError):
        Settings(ALGORITHM="INVALID")

def test_settings_singleton():
    """Test settings singleton pattern."""
    # Get settings instance
    settings1 = settings
    settings2 = settings
    
    # Test singleton
    assert settings1 is settings2
    
    # Test values are the same
    assert settings1.DEBUG == settings2.DEBUG
    assert settings1.HOST == settings2.HOST
    assert settings1.PORT == settings2.PORT
    assert settings1.LOG_LEVEL == settings2.LOG_LEVEL
    assert settings1.DATABASE_URL == settings2.DATABASE_URL
    assert settings1.SECRET_KEY == settings2.SECRET_KEY
    assert settings1.ALGORITHM == settings2.ALGORITHM
    assert settings1.ACCESS_TOKEN_EXPIRE_MINUTES == settings2.ACCESS_TOKEN_EXPIRE_MINUTES
    assert settings1.CORS_ORIGINS == settings2.CORS_ORIGINS

def test_settings_directory_creation():
    """Test directory creation."""
    # Create settings with custom directories
    test_settings = Settings(
        STATIC_DIR=Path("test_static"),
        TEMPLATES_DIR=Path("test_templates"),
        EXPORT_DIR=Path("test_export"),
        LOG_DIR=Path("test_logs")
    )
    
    # Test directories exist
    assert test_settings.STATIC_DIR.exists()
    assert test_settings.TEMPLATES_DIR.exists()
    assert test_settings.EXPORT_DIR.exists()
    assert test_settings.LOG_DIR.exists()
    
    # Clean up
    for directory in [
        test_settings.STATIC_DIR,
        test_settings.TEMPLATES_DIR,
        test_settings.EXPORT_DIR,
        test_settings.LOG_DIR
    ]:
        directory.rmdir() 
"""
Configuration tests for the application.
"""
import pytest
import os
from app.config.settings import Settings, get_settings
from app.core.exceptions import ConfigurationError

def test_settings_initialization():
    """Test settings initialization."""
    settings = Settings()
    
    # Test default values
    assert settings.app_name == "Walmart Sales Analytics"
    assert settings.debug is False
    assert settings.api_version == "1.0.0"
    assert settings.database_url is not None
    assert settings.secret_key is not None
    assert settings.token_expire_minutes == 30
    assert settings.log_level == "INFO"

def test_environment_variables():
    """Test environment variable configuration."""
    # Set test environment variables
    os.environ["APP_NAME"] = "Test App"
    os.environ["DEBUG"] = "true"
    os.environ["API_VERSION"] = "2.0.0"
    os.environ["DATABASE_URL"] = "sqlite:///test.db"
    os.environ["SECRET_KEY"] = "test_secret"
    os.environ["TOKEN_EXPIRE_MINUTES"] = "60"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    # Initialize settings
    settings = Settings()
    
    # Test environment variable values
    assert settings.app_name == "Test App"
    assert settings.debug is True
    assert settings.api_version == "2.0.0"
    assert settings.database_url == "sqlite:///test.db"
    assert settings.secret_key == "test_secret"
    assert settings.token_expire_minutes == 60
    assert settings.log_level == "DEBUG"
    
    # Clean up environment variables
    for key in [
        "APP_NAME", "DEBUG", "API_VERSION", "DATABASE_URL",
        "SECRET_KEY", "TOKEN_EXPIRE_MINUTES", "LOG_LEVEL"
    ]:
        os.environ.pop(key, None)

def test_settings_validation():
    """Test settings validation."""
    # Test invalid database URL
    with pytest.raises(ConfigurationError):
        Settings(database_url="invalid_url")
    
    # Test invalid token expiration
    with pytest.raises(ConfigurationError):
        Settings(token_expire_minutes=-1)
    
    # Test invalid log level
    with pytest.raises(ConfigurationError):
        Settings(log_level="INVALID_LEVEL")
    
    # Test invalid API version format
    with pytest.raises(ConfigurationError):
        Settings(api_version="invalid_version")

def test_settings_singleton():
    """Test settings singleton pattern."""
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2
    assert settings1.app_name == settings2.app_name
    assert settings1.debug == settings2.debug
    assert settings1.api_version == settings2.api_version

def test_development_settings():
    """Test development environment settings."""
    os.environ["ENVIRONMENT"] = "development"
    settings = Settings()
    
    assert settings.debug is True
    assert settings.log_level == "DEBUG"
    assert "dev" in settings.database_url.lower()
    
    os.environ.pop("ENVIRONMENT", None)

def test_production_settings():
    """Test production environment settings."""
    os.environ["ENVIRONMENT"] = "production"
    settings = Settings()
    
    assert settings.debug is False
    assert settings.log_level == "INFO"
    assert "prod" in settings.database_url.lower()
    
    os.environ.pop("ENVIRONMENT", None)

def test_testing_settings():
    """Test testing environment settings."""
    os.environ["ENVIRONMENT"] = "testing"
    settings = Settings()
    
    assert settings.debug is True
    assert settings.log_level == "DEBUG"
    assert "test" in settings.database_url.lower()
    
    os.environ.pop("ENVIRONMENT", None)

def test_custom_settings():
    """Test custom settings configuration."""
    custom_settings = {
        "app_name": "Custom App",
        "debug": True,
        "api_version": "3.0.0",
        "database_url": "sqlite:///custom.db",
        "secret_key": "custom_secret",
        "token_expire_minutes": 120,
        "log_level": "DEBUG"
    }
    
    settings = Settings(**custom_settings)
    
    assert settings.app_name == "Custom App"
    assert settings.debug is True
    assert settings.api_version == "3.0.0"
    assert settings.database_url == "sqlite:///custom.db"
    assert settings.secret_key == "custom_secret"
    assert settings.token_expire_minutes == 120
    assert settings.log_level == "DEBUG"

def test_settings_file():
    """Test settings file configuration."""
    # Create test settings file
    with open("test_settings.env", "w") as f:
        f.write("""
        APP_NAME=File App
        DEBUG=true
        API_VERSION=4.0.0
        DATABASE_URL=sqlite:///file.db
        SECRET_KEY=file_secret
        TOKEN_EXPIRE_MINUTES=90
        LOG_LEVEL=DEBUG
        """)
    
    # Load settings from file
    settings = Settings(_env_file="test_settings.env")
    
    assert settings.app_name == "File App"
    assert settings.debug is True
    assert settings.api_version == "4.0.0"
    assert settings.database_url == "sqlite:///file.db"
    assert settings.secret_key == "file_secret"
    assert settings.token_expire_minutes == 90
    assert settings.log_level == "DEBUG"
    
    # Clean up test file
    os.remove("test_settings.env")

def test_settings_export():
    """Test settings export functionality."""
    settings = Settings()
    
    # Export settings to dictionary
    settings_dict = settings.dict()
    
    assert isinstance(settings_dict, dict)
    assert "app_name" in settings_dict
    assert "debug" in settings_dict
    assert "api_version" in settings_dict
    assert "database_url" in settings_dict
    assert "secret_key" in settings_dict
    assert "token_expire_minutes" in settings_dict
    assert "log_level" in settings_dict

def test_settings_import():
    """Test settings import functionality."""
    settings_dict = {
        "app_name": "Imported App",
        "debug": True,
        "api_version": "5.0.0",
        "database_url": "sqlite:///imported.db",
        "secret_key": "imported_secret",
        "token_expire_minutes": 150,
        "log_level": "DEBUG"
    }
    
    settings = Settings.parse_obj(settings_dict)
    
    assert settings.app_name == "Imported App"
    assert settings.debug is True
    assert settings.api_version == "5.0.0"
    assert settings.database_url == "sqlite:///imported.db"
    assert settings.secret_key == "imported_secret"
    assert settings.token_expire_minutes == 150
    assert settings.log_level == "DEBUG" 
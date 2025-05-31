"""
Application settings and configuration management.
"""
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator, PostgresDsn, RedisDsn, AnyUrl, field_validator, Field
import secrets

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Walmart Sales Analytics Dashboard"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "walmart_db"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DATABASE_URL: str = Field(
        default="mysql+pymysql://root:@localhost:3306/walmart_db",
        description="Database connection URL. Supports MySQL and PostgreSQL."
    )

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v):
        allowed_schemes = [
            "postgres", "postgresql", "postgresql+asyncpg", "postgresql+pg8000",
            "postgresql+psycopg", "postgresql+psycopg2", "postgresql+psycopg2cffi",
            "postgresql+py-postgresql", "postgresql+pygresql",
            "mysql", "mysql+pymysql", "mysql+mysqldb", "mysql+mysqlconnector", "mysql+cymysql"
        ]
        if not any(v.startswith(f"{scheme}:") for scheme in allowed_schemes):
            raise ValueError(
                f"DATABASE_URL scheme should be one of {allowed_schemes}. Got: {v}"
            )
        return v

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None

    @validator("REDIS_URL", pre=True)
    def assemble_redis_url(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        auth = f":{values.get('REDIS_PASSWORD')}@" if values.get('REDIS_PASSWORD') else ""
        return f"redis://{auth}{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"

    # Security
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_MULTIPROC_DIR: Path = Path("/tmp")

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Path = Path("logs/app.log")

    # Export
    EXPORT_DIR: Path = Path("exports")
    MAX_EXPORT_SIZE: int = 1_000_000

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 3600

    CORS_ORIGINS: List[str] = ["*"]

    STATIC_DIR: Path = Path("static")

    TEMPLATES_DIR: Path = Path("templates")

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Create necessary directories
for path in [settings.EXPORT_DIR, settings.LOG_FILE.parent]:
    path.mkdir(parents=True, exist_ok=True)

def get_settings():
    return settings 
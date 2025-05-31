"""
Walmart Sales Analytics Dashboard
A comprehensive analytics dashboard for Walmart sales data analysis.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from loguru import logger
import sys
from pathlib import Path
from app.core.logging import get_logger

# Configure logging
log_path = Path("logs")
log_path.mkdir(exist_ok=True)

logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    log_path / "app.log",
    rotation="500 MB",
    retention="10 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG"
)

# Import key components
from app.config import settings
from app.models import database
from app.services import auth, data_processor, analytics
from app.api import routes

__all__ = [
    "settings",
    "database",
    "auth",
    "data_processor",
    "analytics",
    "routes",
    "logger"
]

# Initialize logger
logger = get_logger(__name__) 
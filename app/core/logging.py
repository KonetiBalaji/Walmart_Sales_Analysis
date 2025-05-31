"""
Logging configuration for the application.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional
from app.config.settings import settings

def setup_logging(log_level: str = None) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        log_level: The logging level to use (defaults to settings.LOG_LEVEL)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Get log level from settings if not provided
    if log_level is None:
        log_level = settings.LOG_LEVEL
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    loggers = {
        'app': logging.INFO,
        'sqlalchemy.engine': logging.WARNING,
        'uvicorn': logging.INFO,
        'fastapi': logging.INFO
    }
    
    for logger_name, level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        logger.propagate = True

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance for the specified name.
    
    Args:
        name: The name for the logger (default: None)
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)

# Initialize logging
setup_logging() 
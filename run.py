"""
Script to run the application.
"""
import uvicorn
from app.config.settings import settings
from app import logger

def main():
    """Run the application."""
    try:
        logger.info("Starting application...")
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower()
        )
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        raise

if __name__ == "__main__":
    main() 
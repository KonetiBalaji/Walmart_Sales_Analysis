"""
Database initialization script.
"""
from sqlalchemy.orm import Session
from app.models.database import engine, Base, get_db
from app.services.auth import create_user
from app.models.schemas import UserCreate
from app import logger
from app.config.settings import settings

def init_db():
    """Initialize the database with initial data."""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Create initial superuser
        db = next(get_db())
        try:
            superuser = UserCreate(
                username=settings.SUPERUSER_USERNAME,
                email=settings.SUPERUSER_EMAIL,
                password=settings.SUPERUSER_PASSWORD,
                is_superuser=True,
                is_active=True
            )
            create_user(db, superuser)
            logger.info("Superuser created successfully")
        except Exception as e:
            logger.error(f"Error creating superuser: {e}")
            raise
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_db() 
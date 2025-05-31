"""
Test fixtures for the application.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base
from app.config.settings import Settings
from fastapi.testclient import TestClient
from app.main import app

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def settings():
    """Create test settings."""
    return Settings(
        database_url=TEST_DATABASE_URL,
        debug=True,
        log_level="DEBUG"
    )

@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db(engine):
    """Create test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture(scope="function")
def test_user(db):
    """Create test user."""
    from app.models.database import User
    from app.services.auth import get_password_hash
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_sale(db):
    """Create test sale."""
    from app.models.database import Sale
    from datetime import datetime
    
    sale = Sale(
        invoice_id="INV001",
        branch="A",
        city="City1",
        customer_type="Member",
        gender="Male",
        product_line="Product1",
        unit_price=10.0,
        quantity=2,
        total=20.0,
        date=datetime(2023, 1, 1),
        time="10:00",
        payment="Cash",
        cogs=10.0,
        gross_margin_percentage=0.5,
        gross_income=10.0,
        rating=4.5
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale 
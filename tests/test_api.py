"""
Tests for the API.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models.database import Base, get_db
from app.config.settings import settings
from app.services.auth import create_access_token
from app.models.schemas import UserCreate
from app.services.auth import create_user

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override get_db for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override get_db
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_user(db):
    """Create a test user."""
    user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        is_superuser=False,
        is_active=True
    )
    return create_user(db, user)

@pytest.fixture(scope="function")
def test_superuser(db):
    """Create a test superuser."""
    user = UserCreate(
        username="testsuperuser",
        email="super@example.com",
        password="testpass123",
        is_superuser=True,
        is_active=True
    )
    return create_user(db, user)

@pytest.fixture(scope="function")
def test_user_token(test_user):
    """Create a token for the test user."""
    return create_access_token(data={"sub": test_user.username})

@pytest.fixture(scope="function")
def test_superuser_token(test_superuser):
    """Create a token for the test superuser."""
    return create_access_token(data={"sub": test_superuser.username})

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "docs" in response.json()
    assert "version" in response.json()

def test_login(test_user):
    """Test login endpoint."""
    response = client.post(
        "/api/token",
        data={
            "username": test_user.username,
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password(test_user):
    """Test login with wrong password."""
    response = client.post(
        "/api/token",
        data={
            "username": test_user.username,
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401

def test_create_user(test_superuser_token):
    """Test creating a new user."""
    response = client.post(
        "/api/users/",
        headers={"Authorization": f"Bearer {test_superuser_token}"},
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass123",
            "is_superuser": False,
            "is_active": True
        }
    )
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"
    assert response.json()["email"] == "new@example.com"
    assert "password" not in response.json()

def test_create_user_unauthorized(test_user_token):
    """Test creating a user without superuser privileges."""
    response = client.post(
        "/api/users/",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass123",
            "is_superuser": False,
            "is_active": True
        }
    )
    assert response.status_code == 403

def test_update_user(test_superuser_token, test_user):
    """Test updating a user."""
    response = client.put(
        f"/api/users/{test_user.id}",
        headers={"Authorization": f"Bearer {test_superuser_token}"},
        json={
            "email": "updated@example.com",
            "is_active": False
        }
    )
    assert response.status_code == 200
    assert response.json()["email"] == "updated@example.com"
    assert response.json()["is_active"] == False

def test_delete_user(test_superuser_token, test_user):
    """Test deleting a user."""
    response = client.delete(
        f"/api/users/{test_user.id}",
        headers={"Authorization": f"Bearer {test_superuser_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"

def test_delete_user_unauthorized(test_user_token, test_superuser):
    """Test deleting a user without superuser privileges."""
    response = client.delete(
        f"/api/users/{test_superuser.id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 403

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "version" in response.json()

def test_load_data_endpoint():
    """Test the data loading endpoint."""
    response = client.post("/data/load", json={"file_path": "test_data.csv"})
    assert response.status_code == 400  # Should fail as file doesn't exist

def test_get_data_sample_endpoint():
    """Test the data sample endpoint."""
    response = client.get("/data/sample")
    assert response.status_code == 400  # Should fail as no data is loaded

def test_get_sales_trends_endpoint():
    """Test the sales trends endpoint."""
    response = client.get("/analytics/sales-trends")
    assert response.status_code == 400  # Should fail as no data is loaded

def test_get_store_performance_endpoint():
    """Test the store performance endpoint."""
    response = client.get("/analytics/store-performance")
    assert response.status_code == 400  # Should fail as no data is loaded

def test_get_holiday_impact_endpoint():
    """Test the holiday impact endpoint."""
    response = client.get("/analytics/holiday-impact")
    assert response.status_code == 400  # Should fail as no data is loaded

def test_export_data_endpoint():
    """Test the data export endpoint."""
    response = client.post("/export/csv", json={"file_path": "test_export.csv"})
    assert response.status_code == 400  # Should fail as no data is loaded 
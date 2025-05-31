"""
Tests for the main application functionality.
"""
import pytest
from fastapi.testclient import TestClient
from app.api.main import app
from app.models.database import User, Sale
from app.services.auth import get_password_hash
from datetime import datetime

def test_app_initialization():
    """Test that the application initializes correctly."""
    assert app is not None
    assert app.title == "Walmart Sales Analysis API"
    assert app.version == "1.0.0"

def test_health_check(client: TestClient):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_database_connection(client: TestClient, db):
    """Test database connection."""
    # Create a test user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Verify user was created
    saved_user = db.query(User).filter(User.username == "testuser").first()
    assert saved_user is not None
    assert saved_user.email == "test@example.com"

def test_sales_data_operations(client: TestClient, db):
    """Test sales data operations."""
    # Create a test sale
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
    
    # Test retrieving sales data
    response = client.get("/sales/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["invoice_id"] == "INV001"

def test_analytics_endpoints(client: TestClient, db):
    """Test analytics endpoints."""
    # Create test sales data
    sales = [
        Sale(
            invoice_id=f"INV00{i}",
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
        ) for i in range(1, 4)
    ]
    db.add_all(sales)
    db.commit()
    
    # Test sales trends endpoint
    response = client.get("/analytics/trends")
    assert response.status_code == 200
    data = response.json()
    assert "daily_sales" in data
    assert "monthly_sales" in data
    
    # Test product analysis endpoint
    response = client.get("/analytics/products")
    assert response.status_code == 200
    data = response.json()
    assert "product_performance" in data
    assert "category_breakdown" in data

def test_export_functionality(client: TestClient, db):
    """Test export functionality."""
    # Create test sales data
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
    
    # Test CSV export
    response = client.get("/export/csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv"
    
    # Test Excel export
    response = client.get("/export/excel")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def test_error_handling(client: TestClient):
    """Test error handling."""
    # Test 404 error
    response = client.get("/nonexistent")
    assert response.status_code == 404
    
    # Test invalid data
    response = client.post("/sales/", json={"invalid": "data"})
    assert response.status_code == 422
    
    # Test invalid date range
    response = client.get("/analytics/trends?start_date=invalid")
    assert response.status_code == 422

def test_rate_limiting(client: TestClient):
    """Test rate limiting."""
    # Make multiple requests in quick succession
    for _ in range(10):
        response = client.get("/health")
    
    # The next request should be rate limited
    response = client.get("/health")
    assert response.status_code == 429 
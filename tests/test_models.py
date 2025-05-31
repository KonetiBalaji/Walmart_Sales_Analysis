"""
Tests for the database models.
"""
import pytest
from datetime import datetime
from app.models.database import User, Sale
from app.models.schemas import UserCreate, SaleCreate

def test_user_model(db):
    """Test User model."""
    # Create user
    user = User(
        username="testuser",
        email="test@example.com",
        password="hashed_password",
        is_superuser=False,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Test user attributes
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "hashed_password"
    assert user.is_superuser == False
    assert user.is_active == True
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)
    
    # Test user string representation
    assert str(user) == f"User(id={user.id}, username='testuser')"
    
    # Test user from schema
    user_schema = UserCreate(
        username="newuser",
        email="new@example.com",
        password="newpass123",
        is_superuser=False,
        is_active=True
    )
    new_user = User(**user_schema.dict(exclude={'password'}))
    assert new_user.username == "newuser"
    assert new_user.email == "new@example.com"
    assert new_user.is_superuser == False
    assert new_user.is_active == True

def test_sale_model(db):
    """Test Sale model."""
    # Create sale
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
    
    # Test sale attributes
    assert sale.id is not None
    assert sale.invoice_id == "INV001"
    assert sale.branch == "A"
    assert sale.city == "City1"
    assert sale.customer_type == "Member"
    assert sale.gender == "Male"
    assert sale.product_line == "Product1"
    assert sale.unit_price == 10.0
    assert sale.quantity == 2
    assert sale.total == 20.0
    assert sale.date == datetime(2023, 1, 1)
    assert sale.time == "10:00"
    assert sale.payment == "Cash"
    assert sale.cogs == 10.0
    assert sale.gross_margin_percentage == 0.5
    assert sale.gross_income == 10.0
    assert sale.rating == 4.5
    assert isinstance(sale.created_at, datetime)
    assert isinstance(sale.updated_at, datetime)
    
    # Test sale string representation
    assert str(sale) == f"Sale(id={sale.id}, invoice_id='INV001')"
    
    # Test sale from schema
    sale_schema = SaleCreate(
        invoice_id="INV002",
        branch="B",
        city="City2",
        customer_type="Normal",
        gender="Female",
        product_line="Product2",
        unit_price=20.0,
        quantity=3,
        total=60.0,
        date=datetime(2023, 1, 2),
        time="11:00",
        payment="Credit card",
        cogs=30.0,
        gross_margin_percentage=0.5,
        gross_income=30.0,
        rating=4.0
    )
    new_sale = Sale(**sale_schema.dict())
    assert new_sale.invoice_id == "INV002"
    assert new_sale.branch == "B"
    assert new_sale.city == "City2"
    assert new_sale.customer_type == "Normal"
    assert new_sale.gender == "Female"
    assert new_sale.product_line == "Product2"
    assert new_sale.unit_price == 20.0
    assert new_sale.quantity == 3
    assert new_sale.total == 60.0
    assert new_sale.date == datetime(2023, 1, 2)
    assert new_sale.time == "11:00"
    assert new_sale.payment == "Credit card"
    assert new_sale.cogs == 30.0
    assert new_sale.gross_margin_percentage == 0.5
    assert new_sale.gross_income == 30.0
    assert new_sale.rating == 4.0

def test_user_unique_constraints(db):
    """Test User model unique constraints."""
    # Create first user
    user1 = User(
        username="testuser",
        email="test@example.com",
        password="hashed_password",
        is_superuser=False,
        is_active=True
    )
    db.add(user1)
    db.commit()
    
    # Try to create user with same username
    user2 = User(
        username="testuser",  # Same username
        email="test2@example.com",
        password="hashed_password",
        is_superuser=False,
        is_active=True
    )
    db.add(user2)
    with pytest.raises(Exception):
        db.commit()
    db.rollback()
    
    # Try to create user with same email
    user3 = User(
        username="testuser2",
        email="test@example.com",  # Same email
        password="hashed_password",
        is_superuser=False,
        is_active=True
    )
    db.add(user3)
    with pytest.raises(Exception):
        db.commit()
    db.rollback()

def test_sale_unique_constraints(db):
    """Test Sale model unique constraints."""
    # Create first sale
    sale1 = Sale(
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
    db.add(sale1)
    db.commit()
    
    # Try to create sale with same invoice ID
    sale2 = Sale(
        invoice_id="INV001",  # Same invoice ID
        branch="B",
        city="City2",
        customer_type="Normal",
        gender="Female",
        product_line="Product2",
        unit_price=20.0,
        quantity=3,
        total=60.0,
        date=datetime(2023, 1, 2),
        time="11:00",
        payment="Credit card",
        cogs=30.0,
        gross_margin_percentage=0.5,
        gross_income=30.0,
        rating=4.0
    )
    db.add(sale2)
    with pytest.raises(Exception):
        db.commit()
    db.rollback()

def test_user_relationships(db):
    """Test User model relationships."""
    # Create user
    user = User(
        username="testuser",
        email="test@example.com",
        password="hashed_password",
        is_superuser=False,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Create sales for user
    sales = [
        Sale(
            invoice_id=f"INV{i:03d}",
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
            rating=4.5,
            user_id=user.id
        )
        for i in range(1, 4)
    ]
    db.add_all(sales)
    db.commit()
    
    # Test user-sales relationship
    assert len(user.sales) == 3
    assert all(sale.user_id == user.id for sale in user.sales)
    assert all(sale.user == user for sale in user.sales)

def test_sale_relationships(db):
    """Test Sale model relationships."""
    # Create user
    user = User(
        username="testuser",
        email="test@example.com",
        password="hashed_password",
        is_superuser=False,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Create sale
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
        rating=4.5,
        user_id=user.id
    )
    db.add(sale)
    db.commit()
    
    # Test sale-user relationship
    assert sale.user_id == user.id
    assert sale.user == user
    assert sale in user.sales 
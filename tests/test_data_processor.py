"""
Tests for the data processor service.
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from app.services.data_processor import DataProcessor
from app.models.database import Sale

def test_validate_dataframe():
    """Test DataFrame validation."""
    # Create test data
    data = {
        'Invoice ID': ['INV001', 'INV002', 'INV003'],
        'Branch': ['A', 'B', 'C'],
        'City': ['City1', 'City2', 'City3'],
        'Customer type': ['Member', 'Normal', 'Member'],
        'Gender': ['Male', 'Female', 'Male'],
        'Product line': ['Product1', 'Product2', 'Product3'],
        'Unit price': [10.0, 20.0, 30.0],
        'Quantity': [2, 3, 1],
        'Date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'Time': ['10:00', '11:00', '12:00'],
        'Payment': ['Cash', 'Credit card', 'Ewallet'],
        'Rating': [4.5, 3.5, 5.0]
    }
    df = pd.DataFrame(data)
    
    # Test validation
    result = DataProcessor.validate_dataframe(df)
    assert result["success"] == True
    assert len(result["expectations"]) > 0

def test_validate_dataframe_invalid():
    """Test DataFrame validation with invalid data."""
    # Create test data with invalid values
    data = {
        'Invoice ID': ['INV001', 'INV001', 'INV003'],  # Duplicate invoice ID
        'Branch': ['A', 'B', 'C'],
        'City': ['City1', 'City2', 'City3'],
        'Customer type': ['Member', 'Normal', 'Member'],
        'Gender': ['Male', 'Female', 'Male'],
        'Product line': ['Product1', 'Product2', 'Product3'],
        'Unit price': [-10.0, 20.0, 30.0],  # Negative unit price
        'Quantity': [2, 3, 1],
        'Date': ['2023-01-01', 'invalid_date', '2023-01-03'],  # Invalid date
        'Time': ['10:00', '11:00', '12:00'],
        'Payment': ['Cash', 'Credit card', 'Ewallet'],
        'Rating': [4.5, 3.5, 5.0]
    }
    df = pd.DataFrame(data)
    
    # Test validation
    result = DataProcessor.validate_dataframe(df)
    assert result["success"] == False
    assert len(result["expectations"]) > 0

def test_clean_dataframe():
    """Test DataFrame cleaning."""
    # Create test data with some issues
    data = {
        'Invoice ID': ['INV001', 'INV002', 'INV003', 'INV003'],  # Duplicate
        'Branch': ['A', 'B', 'C', 'C'],
        'City': ['City1', 'City2', 'City3', 'City3'],
        'Customer type': ['Member', 'Normal', 'Member', 'Member'],
        'Gender': ['Male', 'Female', 'Male', 'Male'],
        'Product line': ['Product1', 'Product2', 'Product3', 'Product3'],
        'Unit price': [10.0, 20.0, 30.0, 30.0],
        'Quantity': [2, 3, 1, 1],
        'Date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-03'],
        'Time': ['10:00', '11:00', '12:00', '12:00'],
        'Payment': ['Cash', 'Credit card', 'Ewallet', 'Ewallet'],
        'Rating': [4.5, 3.5, 5.0, 5.0]
    }
    df = pd.DataFrame(data)
    
    # Test cleaning
    cleaned_df = DataProcessor.clean_dataframe(df)
    assert len(cleaned_df) == 3  # Duplicates removed
    assert all(col.islower() for col in cleaned_df.columns)  # Column names lowercase
    assert 'total' in cleaned_df.columns  # Total calculated
    assert 'cogs' in cleaned_df.columns  # COGS calculated
    assert 'gross_income' in cleaned_df.columns  # Gross income calculated

def test_process_sales_data(db):
    """Test processing sales data."""
    # Create test data
    data = {
        'Invoice ID': ['INV001', 'INV002', 'INV003'],
        'Branch': ['A', 'B', 'C'],
        'City': ['City1', 'City2', 'City3'],
        'Customer type': ['Member', 'Normal', 'Member'],
        'Gender': ['Male', 'Female', 'Male'],
        'Product line': ['Product1', 'Product2', 'Product3'],
        'Unit price': [10.0, 20.0, 30.0],
        'Quantity': [2, 3, 1],
        'Date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'Time': ['10:00', '11:00', '12:00'],
        'Payment': ['Cash', 'Credit card', 'Ewallet'],
        'Rating': [4.5, 3.5, 5.0]
    }
    df = pd.DataFrame(data)
    
    # Test processing
    result = DataProcessor.process_sales_data(df, db)
    assert result["success"] == True
    assert result["rows_processed"] == 3
    
    # Verify data in database
    sales = db.query(Sale).all()
    assert len(sales) == 3
    assert all(s.invoice_id in ['INV001', 'INV002', 'INV003'] for s in sales)

def test_get_sales_metrics(db):
    """Test getting sales metrics."""
    # Create test sales data
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
            date=datetime(2023, 1, 1) + timedelta(days=i),
            time="10:00",
            payment="Cash",
            cogs=10.0,
            gross_margin_percentage=0.5,
            gross_income=10.0,
            rating=4.5
        )
        for i in range(1, 4)
    ]
    db.add_all(sales)
    db.commit()
    
    # Test getting metrics
    metrics = DataProcessor.get_sales_metrics(db)
    assert metrics["total_sales"] == 60.0
    assert metrics["total_transactions"] == 3
    assert metrics["average_order_value"] == 20.0
    assert metrics["total_products_sold"] == 6
    assert metrics["average_rating"] == 4.5

def test_get_sales_metrics_with_date_range(db):
    """Test getting sales metrics with date range."""
    # Create test sales data
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
            date=datetime(2023, 1, 1) + timedelta(days=i),
            time="10:00",
            payment="Cash",
            cogs=10.0,
            gross_margin_percentage=0.5,
            gross_income=10.0,
            rating=4.5
        )
        for i in range(1, 4)
    ]
    db.add_all(sales)
    db.commit()
    
    # Test getting metrics with date range
    start_date = datetime(2023, 1, 2)
    end_date = datetime(2023, 1, 3)
    metrics = DataProcessor.get_sales_metrics(db, start_date, end_date)
    assert metrics["total_sales"] == 40.0
    assert metrics["total_transactions"] == 2
    assert metrics["average_order_value"] == 20.0
    assert metrics["total_products_sold"] == 4
    assert metrics["average_rating"] == 4.5 
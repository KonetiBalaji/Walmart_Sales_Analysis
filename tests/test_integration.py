"""
Integration tests for the application.
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from app.services.data_processing import DataProcessor
from app.services.analytics import Analytics
from app.services.dashboard import Dashboard
from app.services.export import ExportService
from app.models.database import Sale, User
from app.services.auth import create_user, authenticate_user
from app.models.schemas import UserCreate

def test_data_processing_to_analytics(db):
    """Test integration between data processing and analytics services."""
    # Create test data
    data = {
        'Invoice ID': ['INV001', 'INV002'],
        'Branch': ['A', 'B'],
        'City': ['City1', 'City2'],
        'Customer type': ['Member', 'Normal'],
        'Gender': ['Male', 'Female'],
        'Product line': ['Product1', 'Product2'],
        'Unit price': [10.0, 20.0],
        'Quantity': [2, 3],
        'Total': [20.0, 60.0],
        'Date': ['2023-01-01', '2023-01-02'],
        'Time': ['10:00', '11:00'],
        'Payment': ['Cash', 'Credit card'],
        'cogs': [10.0, 30.0],
        'gross margin percentage': [0.5, 0.5],
        'gross income': [10.0, 30.0],
        'Rating': [4.5, 4.0]
    }
    df = pd.DataFrame(data)
    
    # Process data
    processor = DataProcessor()
    processor.process_data(df, db)
    
    # Run analytics
    analytics = Analytics()
    time_series, summary = analytics.get_time_series_data(db)
    
    # Verify integration
    assert isinstance(time_series, pd.DataFrame)
    assert len(time_series) == 2
    assert "total_sales" in time_series.columns
    assert isinstance(summary, dict)
    assert "total_sales" in summary
    assert summary["total_sales"] == 80.0

def test_analytics_to_dashboard(db):
    """Test integration between analytics and dashboard services."""
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
    
    # Run analytics
    analytics = Analytics()
    time_series, summary = analytics.get_time_series_data(db)
    
    # Create dashboard
    dashboard = Dashboard()
    result = dashboard.create_dashboard(db)
    
    # Verify integration
    assert isinstance(result, dict)
    assert "overview" in result
    assert "trends" in result
    assert result["overview"]["total_sales"] == summary["total_sales"]
    assert len(result["trends"]["daily_sales"]) == len(time_series)

def test_dashboard_to_export(db, tmp_path):
    """Test integration between dashboard and export services."""
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
    
    # Create dashboard
    dashboard = Dashboard()
    dashboard_data = dashboard.create_dashboard(db)
    
    # Export data
    export_service = ExportService()
    file_path = tmp_path / "dashboard_export.xlsx"
    result = export_service.export_to_excel(db, file_path)
    
    # Verify integration
    assert result == str(file_path)
    assert file_path.exists()
    
    # Verify exported data matches dashboard
    df = pd.read_excel(file_path)
    assert len(df) == 3
    assert df["total"].sum() == dashboard_data["overview"]["total_sales"]

def test_auth_to_data_processing(db):
    """Test integration between authentication and data processing services."""
    # Create test user
    user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        is_superuser=False,
        is_active=True
    )
    db_user = create_user(db, user)
    
    # Authenticate user
    authenticated_user = authenticate_user(db, "testuser", "testpass123")
    
    # Create test data
    data = {
        'Invoice ID': ['INV001', 'INV002'],
        'Branch': ['A', 'B'],
        'City': ['City1', 'City2'],
        'Customer type': ['Member', 'Normal'],
        'Gender': ['Male', 'Female'],
        'Product line': ['Product1', 'Product2'],
        'Unit price': [10.0, 20.0],
        'Quantity': [2, 3],
        'Total': [20.0, 60.0],
        'Date': ['2023-01-01', '2023-01-02'],
        'Time': ['10:00', '11:00'],
        'Payment': ['Cash', 'Credit card'],
        'cogs': [10.0, 30.0],
        'gross margin percentage': [0.5, 0.5],
        'gross income': [10.0, 30.0],
        'Rating': [4.5, 4.0]
    }
    df = pd.DataFrame(data)
    
    # Process data
    processor = DataProcessor()
    result = processor.process_data(df, db)
    
    # Verify integration
    assert authenticated_user is not None
    assert authenticated_user.username == "testuser"
    assert result == 2  # Two records processed

def test_full_pipeline(db, tmp_path):
    """Test complete application pipeline."""
    # Create test user
    user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        is_superuser=False,
        is_active=True
    )
    db_user = create_user(db, user)
    
    # Create test data
    data = {
        'Invoice ID': ['INV001', 'INV002'],
        'Branch': ['A', 'B'],
        'City': ['City1', 'City2'],
        'Customer type': ['Member', 'Normal'],
        'Gender': ['Male', 'Female'],
        'Product line': ['Product1', 'Product2'],
        'Unit price': [10.0, 20.0],
        'Quantity': [2, 3],
        'Total': [20.0, 60.0],
        'Date': ['2023-01-01', '2023-01-02'],
        'Time': ['10:00', '11:00'],
        'Payment': ['Cash', 'Credit card'],
        'cogs': [10.0, 30.0],
        'gross margin percentage': [0.5, 0.5],
        'gross income': [10.0, 30.0],
        'Rating': [4.5, 4.0]
    }
    df = pd.DataFrame(data)
    
    # Process data
    processor = DataProcessor()
    processor.process_data(df, db)
    
    # Run analytics
    analytics = Analytics()
    time_series, summary = analytics.get_time_series_data(db)
    
    # Create dashboard
    dashboard = Dashboard()
    dashboard_data = dashboard.create_dashboard(db)
    
    # Export data
    export_service = ExportService()
    file_path = tmp_path / "pipeline_export.xlsx"
    export_service.export_to_excel(db, file_path)
    
    # Verify pipeline
    assert db_user is not None
    assert isinstance(time_series, pd.DataFrame)
    assert isinstance(dashboard_data, dict)
    assert file_path.exists()
    
    # Verify data consistency
    df = pd.read_excel(file_path)
    assert len(df) == 2
    assert df["total"].sum() == dashboard_data["overview"]["total_sales"]
    assert df["total"].sum() == summary["total_sales"] 
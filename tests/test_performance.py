"""
Performance tests for the application.
"""
import pytest
import pandas as pd
import time
from datetime import datetime, timedelta
from app.services.data_processing import DataProcessor
from app.services.analytics import Analytics
from app.services.dashboard import Dashboard
from app.services.export import ExportService
from app.models.database import Sale

def generate_large_dataset(size=10000):
    """Generate a large dataset for performance testing."""
    data = {
        'Invoice ID': [f'INV{i:06d}' for i in range(size)],
        'Branch': ['A', 'B', 'C'] * (size // 3 + 1),
        'City': [f'City{i % 10 + 1}' for i in range(size)],
        'Customer type': ['Member', 'Normal'] * (size // 2 + 1),
        'Gender': ['Male', 'Female'] * (size // 2 + 1),
        'Product line': [f'Product{i % 5 + 1}' for i in range(size)],
        'Unit price': [10.0 * (i % 10 + 1) for i in range(size)],
        'Quantity': [i % 10 + 1 for i in range(size)],
        'Total': [10.0 * (i % 10 + 1) * (i % 10 + 1) for i in range(size)],
        'Date': [(datetime(2023, 1, 1) + timedelta(days=i % 365)).strftime('%Y-%m-%d') for i in range(size)],
        'Time': [f'{i % 24:02d}:00' for i in range(size)],
        'Payment': ['Cash', 'Credit card', 'E-wallet'] * (size // 3 + 1),
        'cogs': [5.0 * (i % 10 + 1) * (i % 10 + 1) for i in range(size)],
        'gross margin percentage': [0.5] * size,
        'gross income': [5.0 * (i % 10 + 1) * (i % 10 + 1) for i in range(size)],
        'Rating': [4.0 + (i % 10) / 10 for i in range(size)]
    }
    return pd.DataFrame(data)

def test_data_processing_performance(db):
    """Test data processing performance with large dataset."""
    # Generate large dataset
    df = generate_large_dataset(10000)
    
    # Measure processing time
    start_time = time.time()
    processor = DataProcessor()
    result = processor.process_data(df, db)
    end_time = time.time()
    
    # Verify performance
    processing_time = end_time - start_time
    assert processing_time < 30.0  # Should process 10k records in under 30 seconds
    assert result == 10000  # All records should be processed

def test_analytics_performance(db):
    """Test analytics performance with large dataset."""
    # Generate and process large dataset
    df = generate_large_dataset(10000)
    processor = DataProcessor()
    processor.process_data(df, db)
    
    # Measure analytics time
    start_time = time.time()
    analytics = Analytics()
    time_series, summary = analytics.get_time_series_data(db)
    end_time = time.time()
    
    # Verify performance
    analytics_time = end_time - start_time
    assert analytics_time < 5.0  # Should analyze 10k records in under 5 seconds
    assert isinstance(time_series, pd.DataFrame)
    assert isinstance(summary, dict)

def test_dashboard_performance(db):
    """Test dashboard performance with large dataset."""
    # Generate and process large dataset
    df = generate_large_dataset(10000)
    processor = DataProcessor()
    processor.process_data(df, db)
    
    # Measure dashboard creation time
    start_time = time.time()
    dashboard = Dashboard()
    result = dashboard.create_dashboard(db)
    end_time = time.time()
    
    # Verify performance
    dashboard_time = end_time - start_time
    assert dashboard_time < 10.0  # Should create dashboard in under 10 seconds
    assert isinstance(result, dict)
    assert "overview" in result
    assert "trends" in result

def test_export_performance(db, tmp_path):
    """Test export performance with large dataset."""
    # Generate and process large dataset
    df = generate_large_dataset(10000)
    processor = DataProcessor()
    processor.process_data(df, db)
    
    # Measure export time
    start_time = time.time()
    export_service = ExportService()
    file_path = tmp_path / "large_export.xlsx"
    result = export_service.export_to_excel(db, file_path)
    end_time = time.time()
    
    # Verify performance
    export_time = end_time - start_time
    assert export_time < 15.0  # Should export 10k records in under 15 seconds
    assert result == str(file_path)
    assert file_path.exists()
    
    # Verify exported data
    df = pd.read_excel(file_path)
    assert len(df) == 10000

def test_memory_usage(db):
    """Test memory usage with large dataset."""
    import psutil
    import os
    
    # Get initial memory usage
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Generate and process large dataset
    df = generate_large_dataset(10000)
    processor = DataProcessor()
    processor.process_data(df, db)
    
    # Get final memory usage
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Verify memory usage
    memory_increase = final_memory - initial_memory
    assert memory_increase < 500  # Should use less than 500MB additional memory

def test_concurrent_operations(db):
    """Test concurrent operations performance."""
    import concurrent.futures
    
    # Generate and process large dataset
    df = generate_large_dataset(10000)
    processor = DataProcessor()
    processor.process_data(df, db)
    
    # Define operations
    def run_analytics():
        analytics = Analytics()
        return analytics.get_time_series_data(db)
    
    def create_dashboard():
        dashboard = Dashboard()
        return dashboard.create_dashboard(db)
    
    # Measure concurrent execution time
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        analytics_future = executor.submit(run_analytics)
        dashboard_future = executor.submit(create_dashboard)
        
        time_series, summary = analytics_future.result()
        dashboard_data = dashboard_future.result()
    end_time = time.time()
    
    # Verify performance
    concurrent_time = end_time - start_time
    assert concurrent_time < 12.0  # Should complete both operations in under 12 seconds
    assert isinstance(time_series, pd.DataFrame)
    assert isinstance(dashboard_data, dict)

def test_database_query_performance(db):
    """Test database query performance."""
    # Generate and process large dataset
    df = generate_large_dataset(10000)
    processor = DataProcessor()
    processor.process_data(df, db)
    
    # Measure query time
    start_time = time.time()
    sales = db.query(Sale).all()
    end_time = time.time()
    
    # Verify performance
    query_time = end_time - start_time
    assert query_time < 2.0  # Should query 10k records in under 2 seconds
    assert len(sales) == 10000 
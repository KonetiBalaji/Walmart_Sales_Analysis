"""
Tests for the data processing functionality.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from app.services.data_processing import (
    DataProcessor,
    validate_data,
    clean_data,
    transform_data,
    aggregate_data
)

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame({
        'Invoice ID': ['INV001', 'INV002', 'INV003', 'INV004', 'INV005'],
        'Branch': ['A', 'B', 'A', 'C', 'B'],
        'City': ['City1', 'City2', 'City1', 'City3', 'City2'],
        'Customer type': ['Member', 'Normal', 'Member', 'Member', 'Normal'],
        'Gender': ['Male', 'Female', 'Male', 'Female', 'Male'],
        'Product line': ['Product1', 'Product2', 'Product1', 'Product3', 'Product2'],
        'Unit price': [10.0, 15.0, 20.0, 25.0, 30.0],
        'Quantity': [2, 1, 3, 2, 1],
        'Total': [20.0, 15.0, 60.0, 50.0, 30.0],
        'Date': [
            datetime(2023, 1, 1),
            datetime(2023, 1, 2),
            datetime(2023, 1, 3),
            datetime(2023, 1, 4),
            datetime(2023, 1, 5)
        ],
        'Time': ['10:00', '11:00', '12:00', '13:00', '14:00'],
        'Payment': ['Cash', 'Credit card', 'Cash', 'Credit card', 'Cash'],
        'cogs': [10.0, 7.5, 30.0, 25.0, 15.0],
        'gross margin percentage': [0.5, 0.5, 0.5, 0.5, 0.5],
        'gross income': [10.0, 7.5, 30.0, 25.0, 15.0],
        'Rating': [4.5, 4.0, 5.0, 4.5, 4.0]
    })

@pytest.fixture
def data_processor():
    """Create a DataProcessor instance."""
    return DataProcessor()

def test_validate_data(sample_data):
    """Test data validation."""
    # Test valid data
    is_valid, errors = validate_data(sample_data)
    assert is_valid
    assert len(errors) == 0
    
    # Test missing required columns
    invalid_data = sample_data.drop('Invoice ID', axis=1)
    is_valid, errors = validate_data(invalid_data)
    assert not is_valid
    assert len(errors) > 0
    
    # Test invalid data types
    invalid_data = sample_data.copy()
    invalid_data['Unit price'] = 'invalid'
    is_valid, errors = validate_data(invalid_data)
    assert not is_valid
    assert len(errors) > 0
    
    # Test negative values
    invalid_data = sample_data.copy()
    invalid_data.loc[0, 'Unit price'] = -10.0
    is_valid, errors = validate_data(invalid_data)
    assert not is_valid
    assert len(errors) > 0

def test_clean_data(sample_data):
    """Test data cleaning."""
    # Add some dirty data
    dirty_data = sample_data.copy()
    dirty_data.loc[0, 'Invoice ID'] = '  INV001  '  # Extra spaces
    dirty_data.loc[1, 'Branch'] = 'b'  # Lowercase
    dirty_data.loc[2, 'City'] = 'CITY1'  # Uppercase
    dirty_data.loc[3, 'Customer type'] = '  member  '  # Extra spaces and lowercase
    
    # Clean the data
    cleaned_data = clean_data(dirty_data)
    
    # Verify cleaning results
    assert cleaned_data['Invoice ID'].iloc[0] == 'INV001'
    assert cleaned_data['Branch'].iloc[1] == 'B'
    assert cleaned_data['City'].iloc[2] == 'City1'
    assert cleaned_data['Customer type'].iloc[3] == 'Member'
    
    # Test handling of missing values
    dirty_data.loc[0, 'Rating'] = np.nan
    cleaned_data = clean_data(dirty_data)
    assert cleaned_data['Rating'].iloc[0] == cleaned_data['Rating'].mean()

def test_transform_data(sample_data):
    """Test data transformation."""
    # Transform the data
    transformed_data = transform_data(sample_data)
    
    # Verify transformations
    assert 'Year' in transformed_data.columns
    assert 'Month' in transformed_data.columns
    assert 'Day' in transformed_data.columns
    assert 'Hour' in transformed_data.columns
    assert 'Weekday' in transformed_data.columns
    
    # Verify date components
    assert transformed_data['Year'].iloc[0] == 2023
    assert transformed_data['Month'].iloc[0] == 1
    assert transformed_data['Day'].iloc[0] == 1
    assert transformed_data['Hour'].iloc[0] == 10
    assert transformed_data['Weekday'].iloc[0] == 6  # Sunday
    
    # Verify calculated fields
    assert 'Profit' in transformed_data.columns
    assert 'Profit Margin' in transformed_data.columns
    assert transformed_data['Profit'].iloc[0] == 10.0
    assert transformed_data['Profit Margin'].iloc[0] == 0.5

def test_aggregate_data(sample_data):
    """Test data aggregation."""
    # Aggregate by branch
    branch_agg = aggregate_data(sample_data, 'Branch')
    assert 'total_sales' in branch_agg.columns
    assert 'total_transactions' in branch_agg.columns
    assert 'average_transaction' in branch_agg.columns
    assert len(branch_agg) == 3  # Three unique branches
    
    # Verify branch A aggregation
    branch_a = branch_agg[branch_agg['Branch'] == 'A'].iloc[0]
    assert branch_a['total_sales'] == 80.0  # 20 + 60
    assert branch_a['total_transactions'] == 2
    assert branch_a['average_transaction'] == 40.0
    
    # Aggregate by product
    product_agg = aggregate_data(sample_data, 'Product line')
    assert len(product_agg) == 3  # Three unique products
    
    # Verify product aggregation
    product1 = product_agg[product_agg['Product line'] == 'Product1'].iloc[0]
    assert product1['total_sales'] == 80.0  # 20 + 60
    assert product1['total_transactions'] == 2

def test_data_processor_pipeline(data_processor, sample_data):
    """Test the complete data processing pipeline."""
    # Process the data
    processed_data = data_processor.process(sample_data)
    
    # Verify the result
    assert isinstance(processed_data, pd.DataFrame)
    assert len(processed_data) == len(sample_data)
    assert 'Year' in processed_data.columns
    assert 'Month' in processed_data.columns
    assert 'Profit' in processed_data.columns
    assert 'Profit Margin' in processed_data.columns
    
    # Verify data quality
    assert not processed_data.isnull().any().any()
    assert not processed_data.duplicated().any()
    assert all(processed_data['Unit price'] > 0)
    assert all(processed_data['Quantity'] > 0)
    assert all(processed_data['Total'] > 0)

def test_error_handling(data_processor):
    """Test error handling in data processing."""
    # Test empty DataFrame
    empty_df = pd.DataFrame()
    with pytest.raises(ValueError):
        data_processor.process(empty_df)
    
    # Test invalid data types
    invalid_df = pd.DataFrame({'Unit price': ['invalid']})
    with pytest.raises(ValueError):
        data_processor.process(invalid_df)
    
    # Test missing required columns
    missing_cols_df = pd.DataFrame({'Invalid': [1]})
    with pytest.raises(ValueError):
        data_processor.process(missing_cols_df)

def test_performance(data_processor, sample_data):
    """Test performance of data processing."""
    # Create a larger dataset
    large_data = pd.concat([sample_data] * 1000)
    
    # Measure processing time
    import time
    start_time = time.time()
    processed_data = data_processor.process(large_data)
    end_time = time.time()
    
    # Verify processing time is reasonable (less than 5 seconds)
    processing_time = end_time - start_time
    assert processing_time < 5.0
    
    # Verify memory usage
    memory_usage = processed_data.memory_usage(deep=True).sum()
    assert memory_usage < 1e9  # Less than 1GB 
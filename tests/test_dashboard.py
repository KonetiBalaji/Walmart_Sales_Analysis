"""
Tests for the Streamlit dashboard functionality.
"""
import pytest
import streamlit as st
import pandas as pd
from datetime import datetime
from app.dashboard.main import (
    load_data,
    process_data,
    create_overview_metrics,
    create_sales_trends,
    create_product_analysis,
    create_customer_analysis,
    create_geographic_analysis
)

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame({
        'Invoice ID': ['INV001', 'INV002', 'INV003'],
        'Branch': ['A', 'B', 'A'],
        'City': ['City1', 'City2', 'City1'],
        'Customer type': ['Member', 'Normal', 'Member'],
        'Gender': ['Male', 'Female', 'Male'],
        'Product line': ['Product1', 'Product2', 'Product1'],
        'Unit price': [10.0, 15.0, 20.0],
        'Quantity': [2, 1, 3],
        'Total': [20.0, 15.0, 60.0],
        'Date': [datetime(2023, 1, 1), datetime(2023, 1, 2), datetime(2023, 1, 3)],
        'Time': ['10:00', '11:00', '12:00'],
        'Payment': ['Cash', 'Credit card', 'Cash'],
        'cogs': [10.0, 7.5, 30.0],
        'gross margin percentage': [0.5, 0.5, 0.5],
        'gross income': [10.0, 7.5, 30.0],
        'Rating': [4.5, 4.0, 5.0]
    })

def test_load_data():
    """Test data loading functionality."""
    # Test loading from CSV
    data = load_data("tests/data/sample_sales.csv")
    assert isinstance(data, pd.DataFrame)
    assert not data.empty
    
    # Test loading from Excel
    data = load_data("tests/data/sample_sales.xlsx")
    assert isinstance(data, pd.DataFrame)
    assert not data.empty

def test_process_data(sample_data):
    """Test data processing functionality."""
    processed_data = process_data(sample_data)
    
    # Check data types
    assert processed_data['Date'].dtype == 'datetime64[ns]'
    assert processed_data['Time'].dtype == 'object'
    assert processed_data['Unit price'].dtype == 'float64'
    assert processed_data['Total'].dtype == 'float64'
    
    # Check for missing values
    assert not processed_data.isnull().any().any()
    
    # Check for duplicates
    assert not processed_data.duplicated().any()

def test_overview_metrics(sample_data):
    """Test overview metrics calculation."""
    metrics = create_overview_metrics(sample_data)
    
    assert 'total_sales' in metrics
    assert 'total_transactions' in metrics
    assert 'average_transaction_value' in metrics
    assert 'total_customers' in metrics
    
    assert metrics['total_sales'] == 95.0  # 20 + 15 + 60
    assert metrics['total_transactions'] == 3
    assert metrics['average_transaction_value'] == pytest.approx(31.67, 0.01)
    assert metrics['total_customers'] == 2  # Unique customer types

def test_sales_trends(sample_data):
    """Test sales trends visualization."""
    trends = create_sales_trends(sample_data)
    
    assert 'daily_sales' in trends
    assert 'monthly_sales' in trends
    assert 'hourly_sales' in trends
    
    # Check daily sales
    daily_sales = trends['daily_sales']
    assert len(daily_sales) == 3
    assert daily_sales.iloc[0]['Total'] == 20.0
    assert daily_sales.iloc[1]['Total'] == 15.0
    assert daily_sales.iloc[2]['Total'] == 60.0

def test_product_analysis(sample_data):
    """Test product analysis visualization."""
    analysis = create_product_analysis(sample_data)
    
    assert 'product_performance' in analysis
    assert 'category_breakdown' in analysis
    
    # Check product performance
    product_perf = analysis['product_performance']
    assert len(product_perf) == 2  # Two unique products
    assert product_perf['Product1']['total_sales'] == 80.0  # 20 + 60
    assert product_perf['Product2']['total_sales'] == 15.0

def test_customer_analysis(sample_data):
    """Test customer analysis visualization."""
    analysis = create_customer_analysis(sample_data)
    
    assert 'customer_type_breakdown' in analysis
    assert 'gender_breakdown' in analysis
    assert 'payment_method_breakdown' in analysis
    
    # Check customer type breakdown
    customer_breakdown = analysis['customer_type_breakdown']
    assert customer_breakdown['Member'] == 2
    assert customer_breakdown['Normal'] == 1

def test_geographic_analysis(sample_data):
    """Test geographic analysis visualization."""
    analysis = create_geographic_analysis(sample_data)
    
    assert 'branch_performance' in analysis
    assert 'city_performance' in analysis
    
    # Check branch performance
    branch_perf = analysis['branch_performance']
    assert branch_perf['A']['total_sales'] == 80.0  # 20 + 60
    assert branch_perf['B']['total_sales'] == 15.0

def test_filter_interactions(sample_data):
    """Test filter interactions."""
    # Test date range filter
    filtered_data = sample_data[
        (sample_data['Date'] >= datetime(2023, 1, 1)) &
        (sample_data['Date'] <= datetime(2023, 1, 2))
    ]
    assert len(filtered_data) == 2
    
    # Test branch filter
    filtered_data = sample_data[sample_data['Branch'] == 'A']
    assert len(filtered_data) == 2
    
    # Test product filter
    filtered_data = sample_data[sample_data['Product line'] == 'Product1']
    assert len(filtered_data) == 2

def test_chart_interactions(sample_data):
    """Test chart interactions."""
    # Test bar chart
    trends = create_sales_trends(sample_data)
    daily_sales = trends['daily_sales']
    assert isinstance(daily_sales, pd.DataFrame)
    assert 'Date' in daily_sales.columns
    assert 'Total' in daily_sales.columns
    
    # Test pie chart
    analysis = create_customer_analysis(sample_data)
    customer_breakdown = analysis['customer_type_breakdown']
    assert isinstance(customer_breakdown, dict)
    assert sum(customer_breakdown.values()) == len(sample_data)

def test_data_table_interactions(sample_data):
    """Test data table interactions."""
    # Test sorting
    sorted_data = sample_data.sort_values('Total', ascending=False)
    assert sorted_data.iloc[0]['Total'] == 60.0
    assert sorted_data.iloc[-1]['Total'] == 15.0
    
    # Test filtering
    filtered_data = sample_data[sample_data['Total'] > 30]
    assert len(filtered_data) == 1
    assert filtered_data.iloc[0]['Total'] == 60.0

def test_export_functionality(sample_data):
    """Test export functionality."""
    # Test CSV export
    csv_data = sample_data.to_csv(index=False)
    assert isinstance(csv_data, str)
    assert 'Invoice ID,Branch,City' in csv_data
    
    # Test Excel export
    excel_data = sample_data.to_excel(index=False)
    assert excel_data is None  # to_excel returns None when successful 
"""
Tests for the analytics functionality.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.services.analytics import (
    Analytics,
    calculate_sales_metrics,
    analyze_sales_trends,
    analyze_product_performance,
    analyze_customer_behavior,
    analyze_geographic_distribution
)

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(30)]
    return pd.DataFrame({
        'Invoice ID': [f'INV{i:03d}' for i in range(1, 31)],
        'Branch': np.random.choice(['A', 'B', 'C'], 30),
        'City': np.random.choice(['City1', 'City2', 'City3'], 30),
        'Customer type': np.random.choice(['Member', 'Normal'], 30),
        'Gender': np.random.choice(['Male', 'Female'], 30),
        'Product line': np.random.choice(['Product1', 'Product2', 'Product3'], 30),
        'Unit price': np.random.uniform(10, 100, 30),
        'Quantity': np.random.randint(1, 5, 30),
        'Total': np.random.uniform(20, 200, 30),
        'Date': dates,
        'Time': [f'{h:02d}:00' for h in np.random.randint(9, 18, 30)],
        'Payment': np.random.choice(['Cash', 'Credit card', 'Debit card'], 30),
        'cogs': np.random.uniform(10, 100, 30),
        'gross margin percentage': np.random.uniform(0.4, 0.6, 30),
        'gross income': np.random.uniform(10, 100, 30),
        'Rating': np.random.uniform(3, 5, 30)
    })

@pytest.fixture
def analytics():
    """Create an Analytics instance."""
    return Analytics()

def test_calculate_sales_metrics(sample_data):
    """Test calculation of sales metrics."""
    metrics = calculate_sales_metrics(sample_data)
    
    # Verify basic metrics
    assert 'total_sales' in metrics
    assert 'total_transactions' in metrics
    assert 'average_transaction_value' in metrics
    assert 'total_customers' in metrics
    
    # Verify calculations
    assert metrics['total_sales'] == sample_data['Total'].sum()
    assert metrics['total_transactions'] == len(sample_data)
    assert metrics['average_transaction_value'] == sample_data['Total'].mean()
    assert metrics['total_customers'] == sample_data['Customer type'].nunique()
    
    # Verify additional metrics
    assert 'sales_by_payment_method' in metrics
    assert 'sales_by_customer_type' in metrics
    assert 'sales_by_gender' in metrics
    
    # Verify payment method breakdown
    payment_sales = metrics['sales_by_payment_method']
    assert len(payment_sales) == sample_data['Payment'].nunique()
    assert sum(payment_sales.values()) == sample_data['Total'].sum()

def test_analyze_sales_trends(sample_data):
    """Test analysis of sales trends."""
    trends = analyze_sales_trends(sample_data)
    
    # Verify trend components
    assert 'daily_sales' in trends
    assert 'monthly_sales' in trends
    assert 'hourly_sales' in trends
    assert 'growth_rate' in trends
    
    # Verify daily sales
    daily_sales = trends['daily_sales']
    assert isinstance(daily_sales, pd.DataFrame)
    assert 'Date' in daily_sales.columns
    assert 'Total' in daily_sales.columns
    assert len(daily_sales) == sample_data['Date'].nunique()
    
    # Verify monthly sales
    monthly_sales = trends['monthly_sales']
    assert isinstance(monthly_sales, pd.DataFrame)
    assert 'Month' in monthly_sales.columns
    assert 'Total' in monthly_sales.columns
    
    # Verify hourly sales
    hourly_sales = trends['hourly_sales']
    assert isinstance(hourly_sales, pd.DataFrame)
    assert 'Hour' in hourly_sales.columns
    assert 'Total' in hourly_sales.columns
    
    # Verify growth rate
    assert isinstance(trends['growth_rate'], float)
    assert -1 <= trends['growth_rate'] <= 1

def test_analyze_product_performance(sample_data):
    """Test analysis of product performance."""
    performance = analyze_product_performance(sample_data)
    
    # Verify performance metrics
    assert 'product_sales' in performance
    assert 'product_quantity' in performance
    assert 'product_rating' in performance
    assert 'product_profitability' in performance
    
    # Verify product sales
    product_sales = performance['product_sales']
    assert isinstance(product_sales, pd.DataFrame)
    assert 'Product line' in product_sales.columns
    assert 'Total' in product_sales.columns
    assert len(product_sales) == sample_data['Product line'].nunique()
    
    # Verify product quantity
    product_quantity = performance['product_quantity']
    assert isinstance(product_quantity, pd.DataFrame)
    assert 'Product line' in product_quantity.columns
    assert 'Quantity' in product_quantity.columns
    
    # Verify product rating
    product_rating = performance['product_rating']
    assert isinstance(product_rating, pd.DataFrame)
    assert 'Product line' in product_rating.columns
    assert 'Rating' in product_rating.columns
    
    # Verify product profitability
    product_profitability = performance['product_profitability']
    assert isinstance(product_profitability, pd.DataFrame)
    assert 'Product line' in product_profitability.columns
    assert 'Profit' in product_profitability.columns

def test_analyze_customer_behavior(sample_data):
    """Test analysis of customer behavior."""
    behavior = analyze_customer_behavior(sample_data)
    
    # Verify behavior metrics
    assert 'customer_segments' in behavior
    assert 'customer_preferences' in behavior
    assert 'customer_satisfaction' in behavior
    assert 'customer_loyalty' in behavior
    
    # Verify customer segments
    segments = behavior['customer_segments']
    assert isinstance(segments, pd.DataFrame)
    assert 'Customer type' in segments.columns
    assert 'Total' in segments.columns
    assert len(segments) == sample_data['Customer type'].nunique()
    
    # Verify customer preferences
    preferences = behavior['customer_preferences']
    assert isinstance(preferences, dict)
    assert 'payment_methods' in preferences
    assert 'product_preferences' in preferences
    assert 'time_preferences' in preferences
    
    # Verify customer satisfaction
    satisfaction = behavior['customer_satisfaction']
    assert isinstance(satisfaction, pd.DataFrame)
    assert 'Customer type' in satisfaction.columns
    assert 'Rating' in satisfaction.columns
    
    # Verify customer loyalty
    loyalty = behavior['customer_loyalty']
    assert isinstance(loyalty, pd.DataFrame)
    assert 'Customer type' in loyalty.columns
    assert 'Transaction_count' in loyalty.columns

def test_analyze_geographic_distribution(sample_data):
    """Test analysis of geographic distribution."""
    distribution = analyze_geographic_distribution(sample_data)
    
    # Verify distribution metrics
    assert 'branch_performance' in distribution
    assert 'city_performance' in distribution
    assert 'regional_trends' in distribution
    
    # Verify branch performance
    branch_perf = distribution['branch_performance']
    assert isinstance(branch_perf, pd.DataFrame)
    assert 'Branch' in branch_perf.columns
    assert 'Total' in branch_perf.columns
    assert len(branch_perf) == sample_data['Branch'].nunique()
    
    # Verify city performance
    city_perf = distribution['city_performance']
    assert isinstance(city_perf, pd.DataFrame)
    assert 'City' in city_perf.columns
    assert 'Total' in city_perf.columns
    assert len(city_perf) == sample_data['City'].nunique()
    
    # Verify regional trends
    regional_trends = distribution['regional_trends']
    assert isinstance(regional_trends, pd.DataFrame)
    assert 'Region' in regional_trends.columns
    assert 'Growth_rate' in regional_trends.columns

def test_analytics_pipeline(analytics, sample_data):
    """Test the complete analytics pipeline."""
    # Run the analytics pipeline
    results = analytics.analyze(sample_data)
    
    # Verify results structure
    assert isinstance(results, dict)
    assert 'sales_metrics' in results
    assert 'sales_trends' in results
    assert 'product_performance' in results
    assert 'customer_behavior' in results
    assert 'geographic_distribution' in results
    
    # Verify sales metrics
    metrics = results['sales_metrics']
    assert isinstance(metrics, dict)
    assert 'total_sales' in metrics
    assert 'total_transactions' in metrics
    
    # Verify sales trends
    trends = results['sales_trends']
    assert isinstance(trends, dict)
    assert 'daily_sales' in trends
    assert 'monthly_sales' in trends
    
    # Verify product performance
    performance = results['product_performance']
    assert isinstance(performance, dict)
    assert 'product_sales' in performance
    assert 'product_quantity' in performance
    
    # Verify customer behavior
    behavior = results['customer_behavior']
    assert isinstance(behavior, dict)
    assert 'customer_segments' in behavior
    assert 'customer_preferences' in behavior
    
    # Verify geographic distribution
    distribution = results['geographic_distribution']
    assert isinstance(distribution, dict)
    assert 'branch_performance' in distribution
    assert 'city_performance' in distribution

def test_error_handling(analytics):
    """Test error handling in analytics."""
    # Test empty DataFrame
    empty_df = pd.DataFrame()
    with pytest.raises(ValueError):
        analytics.analyze(empty_df)
    
    # Test missing required columns
    invalid_df = pd.DataFrame({'Invalid': [1]})
    with pytest.raises(ValueError):
        analytics.analyze(invalid_df)
    
    # Test invalid data types
    invalid_df = pd.DataFrame({
        'Total': ['invalid'],
        'Date': ['invalid'],
        'Product line': ['Product1']
    })
    with pytest.raises(ValueError):
        analytics.analyze(invalid_df)

def test_performance(analytics, sample_data):
    """Test performance of analytics."""
    # Create a larger dataset
    large_data = pd.concat([sample_data] * 100)
    
    # Measure processing time
    import time
    start_time = time.time()
    results = analytics.analyze(large_data)
    end_time = time.time()
    
    # Verify processing time is reasonable (less than 10 seconds)
    processing_time = end_time - start_time
    assert processing_time < 10.0
    
    # Verify memory usage
    import sys
    memory_usage = sum(
        sys.getsizeof(v) for v in results.values()
        if isinstance(v, (pd.DataFrame, dict))
    )
    assert memory_usage < 1e9  # Less than 1GB 
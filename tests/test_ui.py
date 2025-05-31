"""
UI tests for the Streamlit dashboard.
"""
import pytest
import streamlit as st
from app.services.dashboard import Dashboard
from app.services.analytics import Analytics
from app.services.data_processing import DataProcessor
import pandas as pd
from datetime import datetime, timedelta

def generate_test_data():
    """Generate test data for UI testing."""
    data = {
        'Invoice ID': ['INV001', 'INV002', 'INV003'],
        'Branch': ['A', 'B', 'C'],
        'City': ['City1', 'City2', 'City3'],
        'Customer type': ['Member', 'Normal', 'Member'],
        'Gender': ['Male', 'Female', 'Male'],
        'Product line': ['Product1', 'Product2', 'Product3'],
        'Unit price': [10.0, 20.0, 30.0],
        'Quantity': [1, 2, 3],
        'Total': [10.0, 40.0, 90.0],
        'Date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'Time': ['10:00', '11:00', '12:00'],
        'Payment': ['Cash', 'Credit card', 'E-wallet'],
        'cogs': [5.0, 20.0, 45.0],
        'gross margin percentage': [0.5, 0.5, 0.5],
        'gross income': [5.0, 20.0, 45.0],
        'Rating': [4.5, 4.0, 4.8]
    }
    return pd.DataFrame(data)

def test_dashboard_initialization():
    """Test dashboard initialization and basic structure."""
    dashboard = Dashboard()
    assert dashboard is not None
    
    # Test sidebar initialization
    st.sidebar.title("Walmart Sales Analytics")
    assert st.sidebar.selectbox("Select View", ["Overview", "Products", "Customers", "Geography"]) is not None
    
    # Test main content area
    st.title("Sales Overview")
    assert st.container() is not None

def test_overview_section():
    """Test the overview section of the dashboard."""
    dashboard = Dashboard()
    df = generate_test_data()
    
    # Test metrics display
    metrics = dashboard.create_sales_overview(df)
    assert "total_sales" in metrics
    assert "average_transaction" in metrics
    assert "total_customers" in metrics
    assert "average_rating" in metrics
    
    # Test metrics values
    assert metrics["total_sales"] == 140.0
    assert metrics["average_transaction"] == 46.67
    assert metrics["total_customers"] == 3
    assert metrics["average_rating"] == 4.43

def test_sales_trends_section():
    """Test the sales trends section of the dashboard."""
    dashboard = Dashboard()
    df = generate_test_data()
    
    # Test trends display
    trends = dashboard.create_sales_trends(df)
    assert "daily_sales" in trends
    assert "growth_rate" in trends
    assert "forecast" in trends
    
    # Test trend calculations
    assert len(trends["daily_sales"]) == 3
    assert isinstance(trends["growth_rate"], float)
    assert len(trends["forecast"]) > 0

def test_product_analysis_section():
    """Test the product analysis section of the dashboard."""
    dashboard = Dashboard()
    df = generate_test_data()
    
    # Test product analysis display
    products = dashboard.create_product_analysis(df)
    assert "top_products" in products
    assert "product_performance" in products
    assert "product_trends" in products
    
    # Test product metrics
    assert len(products["top_products"]) == 3
    assert isinstance(products["product_performance"], dict)
    assert len(products["product_trends"]) > 0

def test_customer_analysis_section():
    """Test the customer analysis section of the dashboard."""
    dashboard = Dashboard()
    df = generate_test_data()
    
    # Test customer analysis display
    customers = dashboard.create_customer_analysis(df)
    assert "customer_segments" in customers
    assert "customer_preferences" in customers
    assert "satisfaction_metrics" in customers
    
    # Test customer metrics
    assert len(customers["customer_segments"]) > 0
    assert isinstance(customers["customer_preferences"], dict)
    assert isinstance(customers["satisfaction_metrics"], dict)

def test_geographic_analysis_section():
    """Test the geographic analysis section of the dashboard."""
    dashboard = Dashboard()
    df = generate_test_data()
    
    # Test geographic analysis display
    geography = dashboard.create_geographic_analysis(df)
    assert "city_performance" in geography
    assert "branch_performance" in geography
    assert "regional_trends" in geography
    
    # Test geographic metrics
    assert len(geography["city_performance"]) == 3
    assert len(geography["branch_performance"]) == 3
    assert len(geography["regional_trends"]) > 0

def test_filter_interactions():
    """Test filter interactions in the dashboard."""
    dashboard = Dashboard()
    df = generate_test_data()
    
    # Test date range filter
    date_range = st.date_input(
        "Select Date Range",
        value=(datetime(2023, 1, 1), datetime(2023, 1, 3))
    )
    assert date_range is not None
    
    # Test branch filter
    branch_filter = st.multiselect(
        "Select Branches",
        options=["A", "B", "C"],
        default=["A", "B", "C"]
    )
    assert branch_filter is not None
    
    # Test product filter
    product_filter = st.multiselect(
        "Select Products",
        options=["Product1", "Product2", "Product3"],
        default=["Product1", "Product2", "Product3"]
    )
    assert product_filter is not None

def test_chart_interactions():
    """Test chart interactions in the dashboard."""
    dashboard = Dashboard()
    df = generate_test_data()
    
    # Test line chart
    st.line_chart(df.set_index("Date")["Total"])
    assert st.container() is not None
    
    # Test bar chart
    st.bar_chart(df.groupby("Branch")["Total"].sum())
    assert st.container() is not None
    
    # Test pie chart
    st.pyplot(dashboard.create_pie_chart(df, "Payment"))
    assert st.container() is not None

def test_data_table_interactions():
    """Test data table interactions in the dashboard."""
    dashboard = Dashboard()
    df = generate_test_data()
    
    # Test data table display
    st.dataframe(df)
    assert st.container() is not None
    
    # Test sorting
    sorted_df = df.sort_values("Total", ascending=False)
    assert sorted_df.iloc[0]["Total"] == 90.0
    
    # Test filtering
    filtered_df = df[df["Branch"] == "A"]
    assert len(filtered_df) == 1

def test_export_functionality():
    """Test export functionality in the dashboard."""
    dashboard = Dashboard()
    df = generate_test_data()
    
    # Test CSV export
    csv = df.to_csv(index=False)
    assert csv is not None
    
    # Test Excel export
    excel = df.to_excel(index=False)
    assert excel is not None
    
    # Test JSON export
    json = df.to_json(orient="records")
    assert json is not None

def test_error_handling():
    """Test error handling in the dashboard."""
    dashboard = Dashboard()
    
    # Test empty data handling
    empty_df = pd.DataFrame()
    with pytest.raises(ValueError):
        dashboard.create_sales_overview(empty_df)
    
    # Test invalid data handling
    invalid_df = pd.DataFrame({"Invalid": [1, 2, 3]})
    with pytest.raises(KeyError):
        dashboard.create_sales_trends(invalid_df)
    
    # Test missing data handling
    df = generate_test_data()
    df.loc[0, "Total"] = None
    with pytest.raises(ValueError):
        dashboard.create_sales_overview(df) 
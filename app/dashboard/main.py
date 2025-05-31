"""
Dashboard module for data visualization and reporting.
"""

import pandas as pd
from typing import Dict, List, Any
from app.core.exceptions import DataProcessingError
from app.services.analytics import (
    analyze_sales_trends,
    analyze_store_performance,
    analyze_holiday_impact,
    analyze_product_performance
)

def generate_sales_dashboard(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate sales dashboard data.
    
    Args:
        data: DataFrame containing sales data
        
    Returns:
        Dictionary containing dashboard data
    """
    try:
        sales_trends = analyze_sales_trends(data)
        store_performance = analyze_store_performance(data)
        holiday_impact = analyze_holiday_impact(data)
        product_performance = analyze_product_performance(data)
        
        return {
            "sales_trends": sales_trends,
            "store_performance": store_performance,
            "holiday_impact": holiday_impact,
            "product_performance": product_performance
        }
    except Exception as e:
        raise DataProcessingError(f"Error generating sales dashboard: {str(e)}")

def generate_store_dashboard(data: pd.DataFrame, store_id: int) -> Dict[str, Any]:
    """
    Generate store-specific dashboard data.
    
    Args:
        data: DataFrame containing sales data
        store_id: ID of the store to analyze
        
    Returns:
        Dictionary containing store dashboard data
    """
    try:
        store_data = data[data['Store'] == store_id]
        
        if store_data.empty:
            raise DataProcessingError(f"No data found for store {store_id}")
        
        sales_trends = analyze_sales_trends(store_data)
        holiday_impact = analyze_holiday_impact(store_data)
        product_performance = analyze_product_performance(store_data)
        
        return {
            "store_id": store_id,
            "sales_trends": sales_trends,
            "holiday_impact": holiday_impact,
            "product_performance": product_performance
        }
    except Exception as e:
        raise DataProcessingError(f"Error generating store dashboard: {str(e)}")

def generate_product_dashboard(data: pd.DataFrame, dept_id: int) -> Dict[str, Any]:
    """
    Generate product-specific dashboard data.
    
    Args:
        data: DataFrame containing sales data
        dept_id: ID of the department to analyze
        
    Returns:
        Dictionary containing product dashboard data
    """
    try:
        dept_data = data[data['Dept'] == dept_id]
        
        if dept_data.empty:
            raise DataProcessingError(f"No data found for department {dept_id}")
        
        sales_trends = analyze_sales_trends(dept_data)
        store_performance = analyze_store_performance(dept_data)
        holiday_impact = analyze_holiday_impact(dept_data)
        
        return {
            "dept_id": dept_id,
            "sales_trends": sales_trends,
            "store_performance": store_performance,
            "holiday_impact": holiday_impact
        }
    except Exception as e:
        raise DataProcessingError(f"Error generating product dashboard: {str(e)}")

def load_data(file_path: str) -> pd.DataFrame:
    """
    Load data from a CSV file into a pandas DataFrame.
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        raise Exception(f"Error loading data: {str(e)}") 
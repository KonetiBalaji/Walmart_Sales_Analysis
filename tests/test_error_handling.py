"""
Error handling tests for the application.
"""
import pytest
from app.core.exceptions import (
    DataProcessingError,
    AnalyticsError,
    DashboardError,
    ExportError,
    AuthenticationError,
    ValidationError,
    DatabaseError
)
from app.services.data_processing import DataProcessor
from app.services.analytics import Analytics
from app.services.dashboard import Dashboard
from app.services.export import ExportService
from app.services.auth import AuthService
import pandas as pd
from datetime import datetime

def test_data_processing_errors():
    """Test error handling in data processing service."""
    processor = DataProcessor()
    
    # Test empty data error
    with pytest.raises(DataProcessingError) as exc_info:
        processor.process_data(pd.DataFrame())
    assert "Empty dataset" in str(exc_info.value)
    
    # Test invalid data error
    invalid_df = pd.DataFrame({"Invalid": [1, 2, 3]})
    with pytest.raises(DataProcessingError) as exc_info:
        processor.process_data(invalid_df)
    assert "Invalid data format" in str(exc_info.value)
    
    # Test missing columns error
    missing_cols_df = pd.DataFrame({"Invoice ID": [1, 2, 3]})
    with pytest.raises(DataProcessingError) as exc_info:
        processor.process_data(missing_cols_df)
    assert "Missing required columns" in str(exc_info.value)
    
    # Test data type error
    type_error_df = pd.DataFrame({
        "Invoice ID": [1, 2, 3],
        "Total": ["invalid", "invalid", "invalid"]
    })
    with pytest.raises(DataProcessingError) as exc_info:
        processor.process_data(type_error_df)
    assert "Invalid data type" in str(exc_info.value)

def test_analytics_errors():
    """Test error handling in analytics service."""
    analytics = Analytics()
    
    # Test empty data error
    with pytest.raises(AnalyticsError) as exc_info:
        analytics.get_time_series_data(pd.DataFrame())
    assert "No data available" in str(exc_info.value)
    
    # Test invalid date range error
    with pytest.raises(AnalyticsError) as exc_info:
        analytics.get_time_series_data(
            pd.DataFrame(),
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2022, 1, 1)
        )
    assert "Invalid date range" in str(exc_info.value)
    
    # Test missing required data error
    with pytest.raises(AnalyticsError) as exc_info:
        analytics.get_product_analysis(pd.DataFrame())
    assert "Missing required data" in str(exc_info.value)
    
    # Test calculation error
    with pytest.raises(AnalyticsError) as exc_info:
        analytics.calculate_growth_rate(pd.DataFrame())
    assert "Calculation failed" in str(exc_info.value)

def test_dashboard_errors():
    """Test error handling in dashboard service."""
    dashboard = Dashboard()
    
    # Test empty data error
    with pytest.raises(DashboardError) as exc_info:
        dashboard.create_dashboard(pd.DataFrame())
    assert "No data available" in str(exc_info.value)
    
    # Test invalid view error
    with pytest.raises(DashboardError) as exc_info:
        dashboard.create_view("invalid_view", pd.DataFrame())
    assert "Invalid view" in str(exc_info.value)
    
    # Test chart creation error
    with pytest.raises(DashboardError) as exc_info:
        dashboard.create_chart("invalid_chart", pd.DataFrame())
    assert "Chart creation failed" in str(exc_info.value)
    
    # Test metric calculation error
    with pytest.raises(DashboardError) as exc_info:
        dashboard.calculate_metrics(pd.DataFrame())
    assert "Metric calculation failed" in str(exc_info.value)

def test_export_errors():
    """Test error handling in export service."""
    export_service = ExportService()
    
    # Test empty data error
    with pytest.raises(ExportError) as exc_info:
        export_service.export_to_csv(pd.DataFrame(), "test.csv")
    assert "No data to export" in str(exc_info.value)
    
    # Test invalid file format error
    with pytest.raises(ExportError) as exc_info:
        export_service.export_to_csv(pd.DataFrame({"test": [1, 2, 3]}), "test.invalid")
    assert "Invalid file format" in str(exc_info.value)
    
    # Test file permission error
    with pytest.raises(ExportError) as exc_info:
        export_service.export_to_csv(
            pd.DataFrame({"test": [1, 2, 3]}),
            "/invalid/path/test.csv"
        )
    assert "File permission error" in str(exc_info.value)
    
    # Test export format error
    with pytest.raises(ExportError) as exc_info:
        export_service.export_to_format(
            pd.DataFrame({"test": [1, 2, 3]}),
            "invalid_format"
        )
    assert "Invalid export format" in str(exc_info.value)

def test_authentication_errors():
    """Test error handling in authentication service."""
    auth_service = AuthService()
    
    # Test invalid credentials error
    with pytest.raises(AuthenticationError) as exc_info:
        auth_service.authenticate_user("invalid_user", "invalid_password")
    assert "Invalid credentials" in str(exc_info.value)
    
    # Test token expiration error
    with pytest.raises(AuthenticationError) as exc_info:
        auth_service.validate_token("expired_token")
    assert "Token expired" in str(exc_info.value)
    
    # Test invalid token error
    with pytest.raises(AuthenticationError) as exc_info:
        auth_service.validate_token("invalid_token")
    assert "Invalid token" in str(exc_info.value)
    
    # Test account locked error
    with pytest.raises(AuthenticationError) as exc_info:
        auth_service.check_account_status("locked_user")
    assert "Account locked" in str(exc_info.value)

def test_validation_errors():
    """Test error handling in validation."""
    # Test data validation error
    with pytest.raises(ValidationError) as exc_info:
        validate_data(pd.DataFrame())
    assert "Validation failed" in str(exc_info.value)
    
    # Test input validation error
    with pytest.raises(ValidationError) as exc_info:
        validate_input("invalid_input")
    assert "Invalid input" in str(exc_info.value)
    
    # Test parameter validation error
    with pytest.raises(ValidationError) as exc_info:
        validate_parameters({"invalid": "parameter"})
    assert "Invalid parameters" in str(exc_info.value)
    
    # Test format validation error
    with pytest.raises(ValidationError) as exc_info:
        validate_format("invalid_format")
    assert "Invalid format" in str(exc_info.value)

def test_database_errors():
    """Test error handling in database operations."""
    # Test connection error
    with pytest.raises(DatabaseError) as exc_info:
        connect_to_database("invalid_connection")
    assert "Database connection failed" in str(exc_info.value)
    
    # Test query error
    with pytest.raises(DatabaseError) as exc_info:
        execute_query("invalid_query")
    assert "Query execution failed" in str(exc_info.value)
    
    # Test transaction error
    with pytest.raises(DatabaseError) as exc_info:
        execute_transaction("invalid_transaction")
    assert "Transaction failed" in str(exc_info.value)
    
    # Test constraint violation error
    with pytest.raises(DatabaseError) as exc_info:
        insert_record("duplicate_record")
    assert "Constraint violation" in str(exc_info.value)

def test_error_logging():
    """Test error logging functionality."""
    # Test error logging
    try:
        raise DataProcessingError("Test error")
    except DataProcessingError as e:
        log_error(e)
    
    # Verify error was logged
    with open(f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log", "r") as f:
        log_content = f.read()
        assert "ERROR" in log_content
        assert "Test error" in log_content
        assert "DataProcessingError" in log_content

def test_error_recovery():
    """Test error recovery mechanisms."""
    # Test retry mechanism
    result = retry_operation(failing_operation, max_retries=3)
    assert result is not None
    
    # Test fallback mechanism
    result = fallback_operation(failing_operation, fallback_operation)
    assert result is not None
    
    # Test circuit breaker
    result = circuit_breaker_operation(failing_operation)
    assert result is not None 
"""
Logging tests for the application.
"""
import pytest
import logging
import os
from datetime import datetime
from app.core.logging import setup_logging, get_logger
from app.services.data_processing import DataProcessor
from app.services.analytics import Analytics
from app.services.dashboard import Dashboard
from app.services.export import ExportService
import pandas as pd

def test_logging_setup():
    """Test logging setup and configuration."""
    # Setup logging
    setup_logging()
    
    # Get logger
    logger = get_logger(__name__)
    
    # Test logger configuration
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0
    
    # Test log file creation
    log_file = f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log"
    assert os.path.exists(log_file)

def test_logging_levels():
    """Test different logging levels."""
    logger = get_logger(__name__)
    
    # Test debug logging
    logger.debug("Debug message")
    with open(f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log", "r") as f:
        log_content = f.read()
        assert "DEBUG" not in log_content  # Debug messages should not be logged
    
    # Test info logging
    logger.info("Info message")
    with open(f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log", "r") as f:
        log_content = f.read()
        assert "INFO" in log_content
        assert "Info message" in log_content
    
    # Test warning logging
    logger.warning("Warning message")
    with open(f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log", "r") as f:
        log_content = f.read()
        assert "WARNING" in log_content
        assert "Warning message" in log_content
    
    # Test error logging
    logger.error("Error message")
    with open(f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log", "r") as f:
        log_content = f.read()
        assert "ERROR" in log_content
        assert "Error message" in log_content

def test_data_processing_logging():
    """Test logging in data processing service."""
    logger = get_logger("data_processing")
    processor = DataProcessor()
    
    # Test successful data processing logging
    df = pd.DataFrame({"test": [1, 2, 3]})
    processor.process_data(df)
    
    with open(f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log", "r") as f:
        log_content = f.read()
        assert "INFO" in log_content
        assert "Data processing started" in log_content
        assert "Data processing completed" in log_content
    
    # Test error logging
    with pytest.raises(ValueError):
        processor.process_data(pd.DataFrame())
    
    with open(f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log", "r") as f:
        log_content = f.read()
        assert "ERROR" in log_content
        assert "Data processing failed" in log_content

def test_analytics_logging():
    """Test logging in analytics service."""
    logger = get_logger("analytics")
    analytics = Analytics()
    
    # Test successful analytics logging
    analytics.get_time_series_data()
    
    with open(f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log", "r") as f:
        log_content = f.read()
        assert "INFO" in log_content
        assert "Analytics processing started" in log_content
        assert "Analytics processing completed" in log_content
    
    # Test error logging
    with pytest.raises(ValueError):
        analytics.get_time_series_data(pd.DataFrame())
    
    with open(f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log", "r") as f:
        log_content = f.read()
        assert "ERROR" in log_content
        assert "Analytics processing failed" in log_content

def test_dashboard_logging():
    """Test logging in dashboard service."""
    logger = get_logger("dashboard")
    dashboard = Dashboard()
    
    # Test successful dashboard creation logging
    dashboard.create_dashboard()
    
    with open(f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log", "r") as f:
        log_content = f.read()
        assert "INFO" in log_content
        assert "Dashboard creation started" in log_content
        assert "Dashboard creation completed" in log_content
    
    # Test error logging
    with pytest.raises(ValueError):
        dashboard.create_dashboard(pd.DataFrame())
    
    with open(f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log", "r") as f:
        log_content = f.read()
        assert "ERROR" in log_content
        assert "Dashboard creation failed" in log_content

def test_export_logging():
    """Test logging in export service."""
    logger = get_logger("export")
    export_service = ExportService()
    
    # Test successful export logging
    df = pd.DataFrame({"test": [1, 2, 3]})
    export_service.export_to_csv(df, "test.csv")
    
    with open(f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log", "r") as f:
        log_content = f.read()
        assert "INFO" in log_content
        assert "Export started" in log_content
        assert "Export completed" in log_content
    
    # Test error logging
    with pytest.raises(ValueError):
        export_service.export_to_csv(pd.DataFrame(), "test.csv")
    
    with open(f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log", "r") as f:
        log_content = f.read()
        assert "ERROR" in log_content
        assert "Export failed" in log_content

def test_log_rotation():
    """Test log rotation functionality."""
    # Setup logging
    setup_logging()
    logger = get_logger(__name__)
    
    # Generate logs for multiple days
    for i in range(5):
        logger.info(f"Test log message {i}")
    
    # Check log files
    log_files = [f for f in os.listdir("logs") if f.startswith("app_")]
    assert len(log_files) > 0
    
    # Check log file size
    for log_file in log_files:
        file_size = os.path.getsize(os.path.join("logs", log_file))
        assert file_size > 0

def test_log_format():
    """Test log message format."""
    logger = get_logger(__name__)
    logger.info("Test message")
    
    with open(f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log", "r") as f:
        log_content = f.read()
        assert "[" in log_content  # Timestamp
        assert "]" in log_content  # Log level
        assert "test_logging" in log_content  # Module name
        assert "Test message" in log_content  # Message

def test_log_cleanup():
    """Test log cleanup functionality."""
    # Setup logging
    setup_logging()
    logger = get_logger(__name__)
    
    # Generate some logs
    logger.info("Test message")
    
    # Clean up old logs
    setup_logging(cleanup=True)
    
    # Check if old logs are removed
    log_files = [f for f in os.listdir("logs") if f.startswith("app_")]
    assert len(log_files) <= 1  # Only current day's log should remain 
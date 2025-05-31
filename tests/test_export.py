"""
Tests for the export functionality.
"""
import pytest
import pandas as pd
import os
import json
from datetime import datetime
from app.services.export import (
    ExportService,
    export_to_csv,
    export_to_excel,
    export_to_json,
    export_to_database
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

@pytest.fixture
def export_service():
    """Create an ExportService instance."""
    return ExportService()

def test_export_to_csv(sample_data, tmp_path):
    """Test exporting data to CSV."""
    # Create a temporary file path
    file_path = tmp_path / "test_export.csv"
    
    # Export data
    export_to_csv(sample_data, str(file_path))
    
    # Verify file exists
    assert file_path.exists()
    
    # Read back the data
    exported_data = pd.read_csv(file_path)
    
    # Verify data integrity
    assert len(exported_data) == len(sample_data)
    assert list(exported_data.columns) == list(sample_data.columns)
    assert exported_data['Invoice ID'].tolist() == sample_data['Invoice ID'].tolist()
    assert exported_data['Total'].tolist() == sample_data['Total'].tolist()

def test_export_to_excel(sample_data, tmp_path):
    """Test exporting data to Excel."""
    # Create a temporary file path
    file_path = tmp_path / "test_export.xlsx"
    
    # Export data
    export_to_excel(sample_data, str(file_path))
    
    # Verify file exists
    assert file_path.exists()
    
    # Read back the data
    exported_data = pd.read_excel(file_path)
    
    # Verify data integrity
    assert len(exported_data) == len(sample_data)
    assert list(exported_data.columns) == list(sample_data.columns)
    assert exported_data['Invoice ID'].tolist() == sample_data['Invoice ID'].tolist()
    assert exported_data['Total'].tolist() == sample_data['Total'].tolist()

def test_export_to_json(sample_data, tmp_path):
    """Test exporting data to JSON."""
    # Create a temporary file path
    file_path = tmp_path / "test_export.json"
    
    # Export data
    export_to_json(sample_data, str(file_path))
    
    # Verify file exists
    assert file_path.exists()
    
    # Read back the data
    with open(file_path, 'r') as f:
        exported_data = json.load(f)
    
    # Verify data integrity
    assert len(exported_data) == len(sample_data)
    assert list(exported_data[0].keys()) == list(sample_data.columns)
    assert [record['Invoice ID'] for record in exported_data] == sample_data['Invoice ID'].tolist()
    assert [record['Total'] for record in exported_data] == sample_data['Total'].tolist()

def test_export_to_database(sample_data, db):
    """Test exporting data to database."""
    # Export data
    export_to_database(sample_data, db)
    
    # Verify data in database
    from app.models.database import Sale
    sales = db.query(Sale).all()
    
    # Verify data integrity
    assert len(sales) == len(sample_data)
    assert sales[0].invoice_id == sample_data['Invoice ID'].iloc[0]
    assert sales[0].total == sample_data['Total'].iloc[0]
    assert sales[1].invoice_id == sample_data['Invoice ID'].iloc[1]
    assert sales[1].total == sample_data['Total'].iloc[1]

def test_export_service_pipeline(export_service, sample_data, tmp_path):
    """Test the complete export pipeline."""
    # Test CSV export
    csv_path = tmp_path / "test_export.csv"
    export_service.export(sample_data, str(csv_path), format='csv')
    assert csv_path.exists()
    
    # Test Excel export
    excel_path = tmp_path / "test_export.xlsx"
    export_service.export(sample_data, str(excel_path), format='excel')
    assert excel_path.exists()
    
    # Test JSON export
    json_path = tmp_path / "test_export.json"
    export_service.export(sample_data, str(json_path), format='json')
    assert json_path.exists()

def test_error_handling(export_service, sample_data, tmp_path):
    """Test error handling in export."""
    # Test invalid file path
    with pytest.raises(ValueError):
        export_service.export(sample_data, "/invalid/path/file.csv", format='csv')
    
    # Test invalid format
    with pytest.raises(ValueError):
        export_service.export(sample_data, str(tmp_path / "test.txt"), format='invalid')
    
    # Test empty DataFrame
    with pytest.raises(ValueError):
        export_service.export(pd.DataFrame(), str(tmp_path / "test.csv"), format='csv')
    
    # Test invalid data types
    invalid_data = sample_data.copy()
    invalid_data['Total'] = 'invalid'
    with pytest.raises(ValueError):
        export_service.export(invalid_data, str(tmp_path / "test.csv"), format='csv')

def test_file_permissions(export_service, sample_data, tmp_path):
    """Test file permissions handling."""
    # Test read-only directory
    read_only_dir = tmp_path / "readonly"
    read_only_dir.mkdir()
    os.chmod(str(read_only_dir), 0o444)
    
    with pytest.raises(PermissionError):
        export_service.export(
            sample_data,
            str(read_only_dir / "test.csv"),
            format='csv'
        )
    
    # Test existing file
    existing_file = tmp_path / "existing.csv"
    existing_file.touch()
    os.chmod(str(existing_file), 0o444)
    
    with pytest.raises(PermissionError):
        export_service.export(
            sample_data,
            str(existing_file),
            format='csv'
        )

def test_large_data_export(export_service, tmp_path):
    """Test exporting large datasets."""
    # Create a large dataset
    large_data = pd.DataFrame({
        'Invoice ID': [f'INV{i:03d}' for i in range(10000)],
        'Total': np.random.uniform(10, 1000, 10000)
    })
    
    # Test CSV export
    csv_path = tmp_path / "large_export.csv"
    export_service.export(large_data, str(csv_path), format='csv')
    assert csv_path.exists()
    assert csv_path.stat().st_size > 0
    
    # Test Excel export
    excel_path = tmp_path / "large_export.xlsx"
    export_service.export(large_data, str(excel_path), format='excel')
    assert excel_path.exists()
    assert excel_path.stat().st_size > 0
    
    # Test JSON export
    json_path = tmp_path / "large_export.json"
    export_service.export(large_data, str(json_path), format='json')
    assert json_path.exists()
    assert json_path.stat().st_size > 0

def test_export_format_options(export_service, sample_data, tmp_path):
    """Test export format options."""
    # Test CSV with different delimiters
    csv_path = tmp_path / "test_tab.csv"
    export_service.export(sample_data, str(csv_path), format='csv', delimiter='\t')
    assert csv_path.exists()
    
    # Test Excel with different sheets
    excel_path = tmp_path / "test_sheets.xlsx"
    export_service.export(
        sample_data,
        str(excel_path),
        format='excel',
        sheet_name='Sales Data'
    )
    assert excel_path.exists()
    
    # Test JSON with different orientations
    json_path = tmp_path / "test_json.json"
    export_service.export(
        sample_data,
        str(json_path),
        format='json',
        orient='records'
    )
    assert json_path.exists() 
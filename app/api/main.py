"""
Main API module for the application.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import pandas as pd

from app.services.data_processing import DataProcessor
from app.services.analytics import (
    analyze_sales_trends,
    analyze_store_performance,
    analyze_holiday_impact
)
from app.services.export import ExportService
from app.core.exceptions import DataProcessingError, ExportError

app = FastAPI(
    title="Walmart Sales Analysis API",
    description="API for analyzing Walmart sales data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
data_processor = DataProcessor()
export_service = ExportService()

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint returning API information."""
    return {
        "message": "Welcome to Walmart Sales Analysis API",
        "version": "1.0.0"
    }

@app.post("/data/load")
async def load_data(file_path: str) -> Dict[str, Any]:
    """
    Load data from a file.
    
    Args:
        file_path: Path to the data file
        
    Returns:
        Dictionary containing data loading status
    """
    try:
        data_processor.load_data(file_path)
        return {"message": "Data loaded successfully"}
    except DataProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/data/sample")
async def get_data_sample(n: int = 5) -> Dict[str, Any]:
    """
    Get a sample of the loaded data.
    
    Args:
        n: Number of rows to return
        
    Returns:
        Dictionary containing sample data
    """
    try:
        sample = data_processor.get_data_sample(n)
        return {"sample": sample}
    except DataProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/analytics/sales-trends")
async def get_sales_trends() -> Dict[str, Any]:
    """
    Get sales trends analysis.
    
    Returns:
        Dictionary containing sales trends analysis
    """
    try:
        if data_processor.data is None:
            raise DataProcessingError("No data loaded")
        return analyze_sales_trends(data_processor.data)
    except DataProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/analytics/store-performance")
async def get_store_performance() -> Dict[str, Any]:
    """
    Get store performance analysis.
    
    Returns:
        Dictionary containing store performance analysis
    """
    try:
        if data_processor.data is None:
            raise DataProcessingError("No data loaded")
        return analyze_store_performance(data_processor.data)
    except DataProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/analytics/holiday-impact")
async def get_holiday_impact() -> Dict[str, Any]:
    """
    Get holiday impact analysis.
    
    Returns:
        Dictionary containing holiday impact analysis
    """
    try:
        if data_processor.data is None:
            raise DataProcessingError("No data loaded")
        return analyze_holiday_impact(data_processor.data)
    except DataProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/export/{format}")
async def export_data(format: str, file_path: str) -> Dict[str, str]:
    """
    Export data to specified format.
    
    Args:
        format: Export format (csv, excel, json)
        file_path: Path where the file will be saved
        
    Returns:
        Dictionary containing export status
    """
    try:
        if data_processor.data is None:
            raise ExportError("No data to export")
        
        export_service.set_data(data_processor.data)
        
        if format == "csv":
            export_service.export_to_csv(file_path)
        elif format == "excel":
            export_service.export_to_excel(file_path)
        elif format == "json":
            export_service.export_to_json(file_path)
        else:
            raise ExportError(f"Unsupported export format: {format}")
        
        return {"message": f"Data exported successfully to {file_path}"}
    except ExportError as e:
        raise HTTPException(status_code=400, detail=str(e)) 
"""
Data processing service for handling data operations.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
from app.core.exceptions import DataProcessingError

class DataProcessor:
    """Class for processing and transforming data."""
    
    def __init__(self):
        """Initialize the DataProcessor."""
        self.data: Optional[pd.DataFrame] = None
    
    def load_data(self, file_path: str) -> None:
        """
        Load data from a file.
        
        Args:
            file_path: Path to the data file
        """
        try:
            self.data = pd.read_csv(file_path)
        except Exception as e:
            raise DataProcessingError(f"Error loading data: {str(e)}")
    
    def process_data(self) -> Dict[str, Any]:
        """
        Process the loaded data.
        
        Returns:
            Dictionary containing processed data statistics
        """
        if self.data is None:
            raise DataProcessingError("No data loaded")
        
        try:
            return {
                "total_rows": len(self.data),
                "columns": list(self.data.columns),
                "summary": self.data.describe().to_dict()
            }
        except Exception as e:
            raise DataProcessingError(f"Error processing data: {str(e)}")
    
    def get_data_sample(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get a sample of the data.
        
        Args:
            n: Number of rows to return
            
        Returns:
            List of dictionaries containing sample data
        """
        if self.data is None:
            raise DataProcessingError("No data loaded")
        
        try:
            return self.data.head(n).to_dict('records')
        except Exception as e:
            raise DataProcessingError(f"Error getting data sample: {str(e)}")

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate the data in the DataFrame.
        """
        if df.empty:
            return False
        # Example validation: check for required columns
        required_columns = ['date', 'total', 'customer_type']
        return all(col in df.columns for col in required_columns) 
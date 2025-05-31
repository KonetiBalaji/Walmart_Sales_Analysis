"""
Data processing service for handling data cleaning, validation, and transformation.
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.database import Sale, get_db
from app.models.schemas import SaleCreate, SaleUpdate
from app import logger
from great_expectations.dataset import PandasDataset
import redis
from app.config.settings import settings

# Initialize Redis client
redis_client = redis.from_url(settings.REDIS_URL)

class DataProcessor:
    """Data processing service for sales data."""
    
    def __init__(self):
        pass

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
        """Validate dataframe using Great Expectations."""
        try:
            dataset = PandasDataset(df)
            
            # Define expectations
            expectations = {
                "invoice_id_unique": dataset.expect_column_values_to_be_unique("invoice_id"),
                "unit_price_positive": dataset.expect_column_values_to_be_between("unit_price", 0, None),
                "quantity_positive": dataset.expect_column_values_to_be_between("quantity", 1, None),
                "total_positive": dataset.expect_column_values_to_be_between("total", 0, None),
                "date_valid": dataset.expect_column_values_to_be_datetime("date"),
                "time_valid": dataset.expect_column_values_to_match_regex("time", r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"),
                "rating_range": dataset.expect_column_values_to_be_between("rating", 0, 10, mostly=0.95)
            }
            
            # Collect results
            validation_results = {
                "success": all(exp["success"] for exp in expectations.values()),
                "expectations": expectations
            }
            
            logger.info(f"Data validation completed: {validation_results['success']}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            raise

    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess dataframe."""
        try:
            # Create a copy to avoid modifying the original
            df_clean = df.copy()
            
            # Convert column names to lowercase
            df_clean.columns = df_clean.columns.str.lower()
            
            # Drop duplicates
            df_clean.drop_duplicates(inplace=True)
            
            # Handle missing values
            df_clean.dropna(subset=['invoice_id', 'total', 'date'], inplace=True)
            
            # Convert data types
            df_clean['date'] = pd.to_datetime(df_clean['date'])
            df_clean['unit_price'] = pd.to_numeric(df_clean['unit_price'], errors='coerce')
            df_clean['quantity'] = pd.to_numeric(df_clean['quantity'], errors='coerce')
            df_clean['total'] = pd.to_numeric(df_clean['total'], errors='coerce')
            
            # Calculate missing totals
            mask = df_clean['total'].isna()
            df_clean.loc[mask, 'total'] = df_clean.loc[mask, 'unit_price'] * df_clean.loc[mask, 'quantity']
            
            # Calculate missing gross income
            if 'gross_income' not in df_clean.columns:
                df_clean['gross_income'] = df_clean['total'] * df_clean['gross_margin_percentage'] / 100
            
            # Calculate missing COGS
            if 'cogs' not in df_clean.columns:
                df_clean['cogs'] = df_clean['total'] - df_clean['gross_income']
            
            logger.info("Data cleaning completed successfully")
            return df_clean
            
        except Exception as e:
            logger.error(f"Error cleaning data: {e}")
            raise

    @staticmethod
    def process_sales_data(
        df: pd.DataFrame,
        db: Session,
        cache_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process sales data and store in database."""
        try:
            # Check cache first
            if cache_key and redis_client.exists(cache_key):
                cached_data = redis_client.get(cache_key)
                logger.info(f"Retrieved data from cache: {cache_key}")
                return eval(cached_data)
            
            # Clean and validate data
            df_clean = DataProcessor.clean_dataframe(df)
            validation_results = DataProcessor.validate_dataframe(df_clean)
            
            if not validation_results['success']:
                logger.warning("Data validation failed")
                return validation_results
            
            # Convert to database models
            sales_data = []
            for _, row in df_clean.iterrows():
                sale = Sale(
                    invoice_id=row['invoice_id'],
                    branch=row['branch'],
                    city=row['city'],
                    customer_type=row['customer_type'],
                    gender=row['gender'],
                    product_line=row['product_line'],
                    unit_price=float(row['unit_price']),
                    quantity=int(row['quantity']),
                    total=float(row['total']),
                    date=row['date'],
                    time=row['time'],
                    payment=row['payment'],
                    cogs=float(row['cogs']),
                    gross_margin_percentage=float(row['gross_margin_percentage']),
                    gross_income=float(row['gross_income']),
                    rating=float(row['rating']) if 'rating' in row else None
                )
                sales_data.append(sale)
            
            # Store in database
            db.bulk_save_objects(sales_data)
            db.commit()
            
            # Cache results
            if cache_key:
                redis_client.setex(
                    cache_key,
                    timedelta(hours=24),
                    str({
                        "success": True,
                        "records_processed": len(sales_data),
                        "validation_results": validation_results
                    })
                )
            
            logger.info(f"Processed {len(sales_data)} sales records")
            return {
                "success": True,
                "records_processed": len(sales_data),
                "validation_results": validation_results
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing sales data: {e}")
            raise

    @staticmethod
    def get_sales_metrics(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        cache_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate sales metrics."""
        try:
            # Check cache first
            if cache_key and redis_client.exists(cache_key):
                cached_metrics = redis_client.get(cache_key)
                logger.info(f"Retrieved metrics from cache: {cache_key}")
                return eval(cached_metrics)
            
            # Build query
            query = db.query(Sale)
            if start_date:
                query = query.filter(Sale.date >= start_date)
            if end_date:
                query = query.filter(Sale.date <= end_date)
            
            # Calculate metrics
            total_sales = query.with_entities(
                func.sum(Sale.total).label('total_sales'),
                func.count(Sale.id).label('total_transactions'),
                func.avg(Sale.total).label('average_order_value'),
                func.sum(Sale.quantity).label('total_quantity')
            ).first()
            
            # Calculate product metrics
            product_metrics = db.query(
                Sale.product_line,
                func.sum(Sale.total).label('total_sales'),
                func.sum(Sale.quantity).label('total_quantity'),
                func.avg(Sale.unit_price).label('avg_price')
            ).group_by(Sale.product_line).all()
            
            # Calculate customer metrics
            customer_metrics = db.query(
                Sale.customer_type,
                func.count(Sale.id).label('transaction_count'),
                func.sum(Sale.total).label('total_sales'),
                func.avg(Sale.total).label('avg_order_value')
            ).group_by(Sale.customer_type).all()
            
            metrics = {
                "overall": {
                    "total_sales": float(total_sales.total_sales or 0),
                    "total_transactions": total_sales.total_transactions or 0,
                    "average_order_value": float(total_sales.average_order_value or 0),
                    "total_quantity": total_sales.total_quantity or 0
                },
                "products": [
                    {
                        "product_line": pm.product_line,
                        "total_sales": float(pm.total_sales),
                        "total_quantity": pm.total_quantity,
                        "avg_price": float(pm.avg_price)
                    }
                    for pm in product_metrics
                ],
                "customers": [
                    {
                        "customer_type": cm.customer_type,
                        "transaction_count": cm.transaction_count,
                        "total_sales": float(cm.total_sales),
                        "avg_order_value": float(cm.avg_order_value)
                    }
                    for cm in customer_metrics
                ]
            }
            
            # Cache results
            if cache_key:
                redis_client.setex(
                    cache_key,
                    timedelta(hours=1),
                    str(metrics)
                )
            
            logger.info("Calculated sales metrics successfully")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating sales metrics: {e}")
            raise

    def process_data(*args, **kwargs):
        # Stub for test compatibility
        return None 
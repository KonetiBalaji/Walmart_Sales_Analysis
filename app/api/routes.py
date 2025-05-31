"""
API routes for the application.
"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import pandas as pd
from app.models.database import get_db, Sale, User
from app.models.schemas import (
    SaleCreate, SaleUpdate, SaleInDB,
    UserCreate, UserUpdate, UserInDB,
    Token
)
from app.services.auth import (
    authenticate_user, create_access_token,
    get_current_active_user, create_user,
    update_user, delete_user
)
from app.services.data_processor import DataProcessor
from app.services.analytics import Analytics
from app import logger
from app.config.settings import settings

# Create router
router = APIRouter()

# Authentication routes
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Get access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# User routes
@router.post("/users/", response_model=UserInDB)
async def create_new_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new user."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return create_user(db, user)

@router.put("/users/{user_id}", response_model=UserInDB)
async def update_user_info(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user information."""
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return update_user(db, user_id, user_update)

@router.delete("/users/{user_id}")
async def delete_user_account(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete user account."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return delete_user(db, user_id)

# Sales data routes
@router.post("/sales/upload")
async def upload_sales_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload and process sales data."""
    try:
        # Read file
        df = pd.read_csv(file.file)
        
        # Process data
        result = DataProcessor.process_sales_data(
            df,
            db,
            cache_key=f"sales_upload_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        )
        
        return result
    except Exception as e:
        logger.error(f"Error uploading sales data: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/sales/metrics")
async def get_sales_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get sales metrics."""
    try:
        cache_key = f"sales_metrics_{start_date}_{end_date}" if start_date and end_date else None
        metrics = DataProcessor.get_sales_metrics(db, start_date, end_date, cache_key)
        return metrics
    except Exception as e:
        logger.error(f"Error getting sales metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Analytics routes
@router.get("/analytics/time-series")
async def get_time_series_analysis(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    interval: str = Query('D', regex='^[DWMQY]$'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get time series analysis."""
    try:
        cache_key = f"time_series_{start_date}_{end_date}_{interval}" if start_date and end_date else None
        df, summary = Analytics.get_time_series_data(db, start_date, end_date, interval, cache_key)
        return {
            "data": df.to_dict('records'),
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error getting time series analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/analytics/products")
async def get_product_analysis(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get product analysis."""
    try:
        cache_key = f"product_analysis_{start_date}_{end_date}" if start_date and end_date else None
        analysis = Analytics.get_product_analysis(db, start_date, end_date, cache_key)
        return analysis
    except Exception as e:
        logger.error(f"Error getting product analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/analytics/customers")
async def get_customer_analysis(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get customer analysis."""
    try:
        cache_key = f"customer_analysis_{start_date}_{end_date}" if start_date and end_date else None
        analysis = Analytics.get_customer_analysis(db, start_date, end_date, cache_key)
        return analysis
    except Exception as e:
        logger.error(f"Error getting customer analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Export routes
@router.get("/export/sales")
async def export_sales_data(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    format: str = Query('csv', regex='^(csv|excel|pdf)$'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export sales data."""
    try:
        # Build query
        query = db.query(Sale)
        if start_date:
            query = query.filter(Sale.date >= start_date)
        if end_date:
            query = query.filter(Sale.date <= end_date)
        
        # Get data
        sales = query.all()
        if not sales:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No sales data found for the specified period"
            )
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'invoice_id': s.invoice_id,
            'branch': s.branch,
            'city': s.city,
            'customer_type': s.customer_type,
            'gender': s.gender,
            'product_line': s.product_line,
            'unit_price': s.unit_price,
            'quantity': s.quantity,
            'total': s.total,
            'date': s.date,
            'time': s.time,
            'payment': s.payment,
            'cogs': s.cogs,
            'gross_margin_percentage': s.gross_margin_percentage,
            'gross_income': s.gross_income,
            'rating': s.rating
        } for s in sales])
        
        # Export based on format
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"sales_export_{timestamp}"
        
        if format == 'csv':
            filepath = settings.EXPORT_DIR / f"{filename}.csv"
            df.to_csv(filepath, index=False)
        elif format == 'excel':
            filepath = settings.EXPORT_DIR / f"{filename}.xlsx"
            df.to_excel(filepath, index=False)
        else:  # pdf
            filepath = settings.EXPORT_DIR / f"{filename}.pdf"
            # Create PDF report
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            
            doc = SimpleDocTemplate(str(filepath), pagesize=letter)
            elements = []
            
            # Add title
            from reportlab.platypus import Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            styles = getSampleStyleSheet()
            elements.append(Paragraph(f"Sales Report ({start_date} to {end_date})", styles['Title']))
            
            # Add table
            table_data = [df.columns.tolist()] + df.values.tolist()
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            
            doc.build(elements)
        
        logger.info(f"Exported sales data to {filepath}")
        return {
            "message": "Export completed successfully",
            "filepath": str(filepath)
        }
        
    except Exception as e:
        logger.error(f"Error exporting sales data: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 
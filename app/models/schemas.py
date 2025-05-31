"""
Pydantic schemas for data validation and serialization.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserInDB(UserBase):
    """Schema for user in database."""
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User(UserBase):
    """Schema for user response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SaleBase(BaseModel):
    """Base sale schema."""
    invoice_id: str
    branch: str
    city: str
    customer_type: str
    gender: str
    product_line: str
    unit_price: float
    quantity: int
    total: float
    date: datetime
    time: str
    payment: str
    cogs: float
    gross_margin_percentage: float
    gross_income: float
    rating: Optional[float] = None

class SaleCreate(SaleBase):
    """Schema for creating a sale."""
    pass

class SaleUpdate(BaseModel):
    """Schema for updating a sale."""
    branch: Optional[str] = None
    city: Optional[str] = None
    customer_type: Optional[str] = None
    gender: Optional[str] = None
    product_line: Optional[str] = None
    unit_price: Optional[float] = None
    quantity: Optional[int] = None
    total: Optional[float] = None
    date: Optional[datetime] = None
    time: Optional[str] = None
    payment: Optional[str] = None
    cogs: Optional[float] = None
    gross_margin_percentage: Optional[float] = None
    gross_income: Optional[float] = None
    rating: Optional[float] = None

class SaleInDB(SaleBase):
    """Schema for sale in database."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Sale(SaleBase):
    """Schema for sale response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for token data."""
    username: Optional[str] = None 
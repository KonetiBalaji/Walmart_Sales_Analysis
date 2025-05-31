"""
Authentication service for user management.
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.exceptions import AuthenticationError
from app.models.database import User, get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config.settings import settings
from app.models.schemas import TokenData, UserCreate, UserUpdate

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        
    Returns:
        JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """
    Verify a JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        Decoded token data
        
    Raises:
        AuthenticationError: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise AuthenticationError("Invalid token")

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with username and password.
    
    Args:
        db: Database session
        username: Username to authenticate
        password: Password to authenticate
        
    Returns:
        User object if authentication successful, None otherwise
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user 

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Retrieve the current user from the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Check if the current user is active.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user 

def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user in the database.
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_superuser=getattr(user, 'is_superuser', False)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user 

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
    """
    Update user information in the database.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user_update.dict(exclude_unset=True).items():
        if key == "password" and value:
            setattr(user, "hashed_password", get_password_hash(value))
        elif key != "password":
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user 

def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user from the database.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return True 

class AuthService:
    """
    Service class for authentication operations.
    """
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        return authenticate_user(self.db, username, password)

    def create_user(self, user: UserCreate) -> User:
        return create_user(self.db, user)

    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        return update_user(self.db, user_id, user_update)

    def delete_user(self, user_id: int) -> bool:
        return delete_user(self.db, user_id) 
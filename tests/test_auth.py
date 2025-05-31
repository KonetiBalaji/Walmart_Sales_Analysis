"""
Tests for the authentication functionality.
"""
import pytest
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.services.auth import (
    AuthService,
    create_access_token,
    verify_password,
    get_password_hash,
    authenticate_user,
    get_current_user,
    get_current_active_user
)
from app.models.database import User
from app.config.settings import settings

@pytest.fixture
def auth_service():
    """Create an AuthService instance."""
    return AuthService()

@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def test_password_hashing():
    """Test password hashing and verification."""
    # Test password hashing
    password = "testpass123"
    hashed_password = get_password_hash(password)
    assert hashed_password != password
    assert verify_password(password, hashed_password)
    
    # Test password verification
    wrong_password = "wrongpass"
    assert not verify_password(wrong_password, hashed_password)

def test_token_creation_and_validation(auth_service, test_user):
    """Test token creation and validation."""
    # Create access token
    access_token = create_access_token(
        data={"sub": test_user.username}
    )
    assert access_token is not None
    
    # Decode token
    payload = jwt.decode(
        access_token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    assert payload["sub"] == test_user.username
    assert "exp" in payload

def test_token_expiration(auth_service, test_user):
    """Test token expiration."""
    # Create expired token
    expired_token = create_access_token(
        data={"sub": test_user.username},
        expires_delta=timedelta(microseconds=1)
    )
    
    # Wait for token to expire
    import time
    time.sleep(0.1)
    
    # Verify token is expired
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(
            expired_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

def test_invalid_token(auth_service):
    """Test invalid token handling."""
    # Test invalid token format
    with pytest.raises(jwt.JWTError):
        jwt.decode(
            "invalid_token",
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    
    # Test tampered token
    token = create_access_token(data={"sub": "testuser"})
    tampered_token = token[:-1] + "X"
    with pytest.raises(jwt.JWTError):
        jwt.decode(
            tampered_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

def test_user_authentication(db, auth_service, test_user):
    """Test user authentication."""
    # Test successful authentication
    authenticated_user = authenticate_user(
        db,
        test_user.username,
        "testpass123"
    )
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username
    
    # Test failed authentication
    failed_user = authenticate_user(
        db,
        test_user.username,
        "wrongpass"
    )
    assert failed_user is False

def test_password_policy():
    """Test password policy enforcement."""
    # Test password length
    short_password = "short"
    with pytest.raises(ValueError):
        get_password_hash(short_password)
    
    # Test password complexity
    simple_password = "password123"
    with pytest.raises(ValueError):
        get_password_hash(simple_password)
    
    # Test valid password
    valid_password = "ComplexPass123!"
    hashed_password = get_password_hash(valid_password)
    assert hashed_password is not None

def test_rate_limiting(auth_service, db, test_user):
    """Test rate limiting for authentication attempts."""
    # Make multiple failed attempts
    for _ in range(5):
        authenticate_user(db, test_user.username, "wrongpass")
    
    # Verify account is locked
    locked_user = db.query(User).filter(User.username == test_user.username).first()
    assert not locked_user.is_active

def test_session_management(auth_service, test_user):
    """Test session management."""
    # Create session token
    session_token = auth_service.create_session_token(test_user)
    assert session_token is not None
    
    # Verify session token
    session_data = auth_service.verify_session_token(session_token)
    assert session_data["username"] == test_user.username
    
    # Test session expiration
    expired_session = auth_service.create_session_token(
        test_user,
        expires_delta=timedelta(microseconds=1)
    )
    import time
    time.sleep(0.1)
    with pytest.raises(jwt.ExpiredSignatureError):
        auth_service.verify_session_token(expired_session)

def test_user_roles(auth_service, db):
    """Test user role management."""
    # Create regular user
    regular_user = User(
        username="regular",
        email="regular@example.com",
        hashed_password=get_password_hash("ComplexPass123!"),
        is_active=True,
        is_superuser=False
    )
    db.add(regular_user)
    
    # Create superuser
    superuser = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("ComplexPass123!"),
        is_active=True,
        is_superuser=True
    )
    db.add(superuser)
    db.commit()
    
    # Verify roles
    assert not auth_service.is_superuser(regular_user)
    assert auth_service.is_superuser(superuser)

def test_password_reset(auth_service, db, test_user):
    """Test password reset functionality."""
    # Generate reset token
    reset_token = auth_service.create_password_reset_token(test_user)
    assert reset_token is not None
    
    # Verify reset token
    token_data = auth_service.verify_password_reset_token(reset_token)
    assert token_data["username"] == test_user.username
    
    # Reset password
    new_password = "NewComplexPass123!"
    auth_service.reset_password(db, test_user, new_password)
    
    # Verify new password
    assert verify_password(new_password, test_user.hashed_password)

def test_account_locking(auth_service, db, test_user):
    """Test account locking functionality."""
    # Lock account
    auth_service.lock_account(db, test_user)
    assert not test_user.is_active
    
    # Unlock account
    auth_service.unlock_account(db, test_user)
    assert test_user.is_active

def test_audit_logging(auth_service, db, test_user):
    """Test audit logging for authentication events."""
    # Test login logging
    auth_service.log_login_attempt(db, test_user, success=True)
    logs = auth_service.get_login_logs(db, test_user)
    assert len(logs) > 0
    assert logs[0].success
    
    # Test failed login logging
    auth_service.log_login_attempt(db, test_user, success=False)
    logs = auth_service.get_login_logs(db, test_user)
    assert not logs[0].success 
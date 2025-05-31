"""
Security tests for the application.
"""
import pytest
import jwt
from datetime import datetime, timedelta
from app.services.auth import AuthService
from app.models.database import User
from app.config.settings import settings

def test_password_hashing():
    """Test password hashing and verification."""
    auth_service = AuthService()
    password = "test_password123"
    
    # Test password hashing
    hashed_password = auth_service.get_password_hash(password)
    assert hashed_password != password
    assert len(hashed_password) > len(password)
    
    # Test password verification
    assert auth_service.verify_password(password, hashed_password)
    assert not auth_service.verify_password("wrong_password", hashed_password)

def test_token_creation_and_validation():
    """Test JWT token creation and validation."""
    auth_service = AuthService()
    user_data = {
        "sub": "testuser",
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }
    
    # Test token creation
    token = auth_service.create_access_token(user_data)
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Test token validation
    payload = auth_service.decode_token(token)
    assert payload["sub"] == "testuser"
    assert "exp" in payload

def test_token_expiration():
    """Test JWT token expiration."""
    auth_service = AuthService()
    user_data = {
        "sub": "testuser",
        "exp": datetime.utcnow() - timedelta(minutes=1)  # Expired token
    }
    
    # Create expired token
    token = auth_service.create_access_token(user_data)
    
    # Test token validation
    with pytest.raises(jwt.ExpiredSignatureError):
        auth_service.decode_token(token)

def test_invalid_token():
    """Test handling of invalid tokens."""
    auth_service = AuthService()
    
    # Test invalid token format
    with pytest.raises(jwt.InvalidTokenError):
        auth_service.decode_token("invalid_token")
    
    # Test tampered token
    user_data = {
        "sub": "testuser",
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }
    token = auth_service.create_access_token(user_data)
    tampered_token = token[:-1] + "X"  # Modify last character
    
    with pytest.raises(jwt.InvalidSignatureError):
        auth_service.decode_token(tampered_token)

def test_user_authentication(db):
    """Test user authentication process."""
    auth_service = AuthService()
    
    # Create test user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=auth_service.get_password_hash("test_password123")
    )
    db.add(user)
    db.commit()
    
    # Test successful authentication
    authenticated_user = auth_service.authenticate_user(db, "testuser", "test_password123")
    assert authenticated_user is not None
    assert authenticated_user.username == "testuser"
    
    # Test failed authentication
    assert auth_service.authenticate_user(db, "testuser", "wrong_password") is None
    assert auth_service.authenticate_user(db, "nonexistent_user", "test_password123") is None

def test_password_policy():
    """Test password policy enforcement."""
    auth_service = AuthService()
    
    # Test password length
    assert not auth_service.validate_password("short")  # Too short
    assert not auth_service.validate_password("a" * 51)  # Too long
    assert auth_service.validate_password("ValidPass123!")  # Valid length
    
    # Test password complexity
    assert not auth_service.validate_password("password123")  # No special character
    assert not auth_service.validate_password("Password!")  # No number
    assert not auth_service.validate_password("password123!")  # No uppercase
    assert not auth_service.validate_password("PASSWORD123!")  # No lowercase
    assert auth_service.validate_password("ValidPass123!")  # Meets all requirements

def test_rate_limiting():
    """Test rate limiting for authentication attempts."""
    auth_service = AuthService()
    
    # Simulate multiple failed login attempts
    for _ in range(5):
        auth_service.record_failed_attempt("testuser")
    
    # Check if account is locked
    assert auth_service.is_account_locked("testuser")
    
    # Test lockout duration
    auth_service.failed_attempts["testuser"]["timestamp"] = datetime.utcnow() - timedelta(minutes=16)
    assert not auth_service.is_account_locked("testuser")

def test_session_management():
    """Test session management."""
    auth_service = AuthService()
    
    # Create session
    session_id = auth_service.create_session("testuser")
    assert session_id is not None
    
    # Verify session
    assert auth_service.verify_session(session_id)
    
    # Invalidate session
    auth_service.invalidate_session(session_id)
    assert not auth_service.verify_session(session_id)

def test_sql_injection_prevention(db):
    """Test SQL injection prevention."""
    auth_service = AuthService()
    
    # Attempt SQL injection in username
    malicious_username = "testuser' OR '1'='1"
    assert auth_service.authenticate_user(db, malicious_username, "password") is None
    
    # Attempt SQL injection in password
    malicious_password = "password' OR '1'='1"
    assert auth_service.authenticate_user(db, "testuser", malicious_password) is None

def test_xss_prevention():
    """Test XSS prevention."""
    auth_service = AuthService()
    
    # Test XSS in username
    xss_username = "<script>alert('xss')</script>"
    assert auth_service.sanitize_input(xss_username) != xss_username
    
    # Test XSS in email
    xss_email = "test<script>alert('xss')</script>@example.com"
    assert auth_service.sanitize_input(xss_email) != xss_email

def test_csrf_protection():
    """Test CSRF protection."""
    auth_service = AuthService()
    
    # Generate CSRF token
    csrf_token = auth_service.generate_csrf_token()
    assert csrf_token is not None
    
    # Verify CSRF token
    assert auth_service.verify_csrf_token(csrf_token)
    
    # Test invalid CSRF token
    assert not auth_service.verify_csrf_token("invalid_token") 
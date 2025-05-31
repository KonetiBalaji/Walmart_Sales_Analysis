"""
API documentation tests for the application.
"""
import pytest
from app.api.main import app
from fastapi.testclient import TestClient
import json

client = TestClient(app)

def test_openapi_schema():
    """Test OpenAPI schema generation and structure."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    schema = response.json()
    
    # Test basic schema structure
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema
    assert "components" in schema
    
    # Test API version
    assert schema["openapi"].startswith("3.0")
    
    # Test API info
    assert "title" in schema["info"]
    assert "version" in schema["info"]
    assert "description" in schema["info"]

def test_api_endpoints_documentation():
    """Test API endpoints documentation."""
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Test authentication endpoints
    assert "/auth/login" in schema["paths"]
    assert "/auth/register" in schema["paths"]
    assert "/auth/refresh" in schema["paths"]
    
    # Test sales endpoints
    assert "/sales/overview" in schema["paths"]
    assert "/sales/trends" in schema["paths"]
    assert "/sales/products" in schema["paths"]
    assert "/sales/customers" in schema["paths"]
    assert "/sales/geography" in schema["paths"]
    
    # Test export endpoints
    assert "/export/csv" in schema["paths"]
    assert "/export/excel" in schema["paths"]
    assert "/export/json" in schema["paths"]

def test_endpoint_parameters():
    """Test endpoint parameters documentation."""
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Test sales/trends endpoint parameters
    trends_path = schema["paths"]["/sales/trends"]
    assert "get" in trends_path
    assert "parameters" in trends_path["get"]
    
    parameters = trends_path["get"]["parameters"]
    assert any(p["name"] == "start_date" for p in parameters)
    assert any(p["name"] == "end_date" for p in parameters)
    assert any(p["name"] == "branch" for p in parameters)

def test_request_body_schemas():
    """Test request body schemas documentation."""
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Test login endpoint request body
    login_path = schema["paths"]["/auth/login"]
    assert "post" in login_path
    assert "requestBody" in login_path["post"]
    
    request_body = login_path["post"]["requestBody"]
    assert "content" in request_body
    assert "application/json" in request_body["content"]
    assert "schema" in request_body["content"]["application/json"]

def test_response_schemas():
    """Test response schemas documentation."""
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Test sales/overview endpoint responses
    overview_path = schema["paths"]["/sales/overview"]
    assert "get" in overview_path
    assert "responses" in overview_path["get"]
    
    responses = overview_path["get"]["responses"]
    assert "200" in responses
    assert "content" in responses["200"]
    assert "application/json" in responses["200"]["content"]
    assert "schema" in responses["200"]["content"]["application/json"]

def test_security_schemes():
    """Test security schemes documentation."""
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Test security schemes
    assert "components" in schema
    assert "securitySchemes" in schema["components"]
    
    security_schemes = schema["components"]["securitySchemes"]
    assert "bearerAuth" in security_schemes
    assert security_schemes["bearerAuth"]["type"] == "http"
    assert security_schemes["bearerAuth"]["scheme"] == "bearer"

def test_error_responses():
    """Test error responses documentation."""
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Test common error responses
    for path in schema["paths"].values():
        for method in path.values():
            if "responses" in method:
                assert "400" in method["responses"]  # Bad Request
                assert "401" in method["responses"]  # Unauthorized
                assert "403" in method["responses"]  # Forbidden
                assert "404" in method["responses"]  # Not Found
                assert "500" in method["responses"]  # Internal Server Error

def test_data_models():
    """Test data models documentation."""
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Test component schemas
    assert "components" in schema
    assert "schemas" in schema["components"]
    
    schemas = schema["components"]["schemas"]
    assert "User" in schemas
    assert "Sale" in schemas
    assert "Token" in schemas
    assert "TokenData" in schemas

def test_examples():
    """Test API examples documentation."""
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Test example values in schemas
    for path in schema["paths"].values():
        for method in path.values():
            if "requestBody" in method:
                content = method["requestBody"]["content"]
                for media_type in content.values():
                    if "schema" in media_type:
                        assert "example" in media_type["schema"]

def test_tags():
    """Test API tags documentation."""
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Test tags
    assert "tags" in schema
    tags = [tag["name"] for tag in schema["tags"]]
    assert "authentication" in tags
    assert "sales" in tags
    assert "export" in tags
    
    # Test endpoint tags
    for path in schema["paths"].values():
        for method in path.values():
            assert "tags" in method
            assert len(method["tags"]) > 0 
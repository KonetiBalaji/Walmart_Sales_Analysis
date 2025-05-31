"""
Script to run tests.
"""
import pytest
import sys
from app import logger

def main():
    """Run tests."""
    try:
        logger.info("Running tests...")
        # Run pytest with coverage
        sys.exit(pytest.main([
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html",
            "tests/"
        ]))
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
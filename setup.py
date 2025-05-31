"""
Setup configuration for the Walmart Sales Analysis application.
"""
from setuptools import setup, find_packages

setup(
    name="walmart-sales-analysis",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "sqlalchemy>=1.4.0",
        "pydantic>=1.8.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.5",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "plotly>=5.3.0",
        "redis>=4.0.0",
        "great-expectations>=0.14.0",
        "pytest>=6.2.5",
        "pytest-cov>=2.12.0",
        "httpx>=0.23.0",
    ],
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="Walmart Sales Analysis Dashboard and API",
    long_description="A comprehensive dashboard and API for analyzing Walmart sales data",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/walmart-sales-analysis",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 
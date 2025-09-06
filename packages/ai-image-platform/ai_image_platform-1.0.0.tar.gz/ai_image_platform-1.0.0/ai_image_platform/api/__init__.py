"""
Flask API Module
===============

This package contains the Flask web application and API endpoints
for the AI Image Platform.

Modules:
    flask_app: Main Flask application with all endpoints
    routes: Additional route handlers (if needed)
"""

from .flask_app import create_app

__all__ = ['create_app']
# tests/__init__.py
"""
Suite de tests para Triboka Backend
"""

# Configuración de testing
import os
import sys
import pytest
from flask import Flask
from flask_jwt_extended import JWTManager

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuración de testing
os.environ['FLASK_ENV'] = 'testing'
os.environ['SECRET_KEY'] = 'test_secret_key'
os.environ['JWT_SECRET_KEY'] = 'test_jwt_secret'

def pytest_configure(config):
    """Configuración global de pytest"""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
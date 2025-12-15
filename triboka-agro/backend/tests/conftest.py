# tests/conftest.py
"""
Configuración común para tests de Triboka
"""

import os
import pytest
import tempfile
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import sys

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models_simple import db, User, Company
from app_web3 import create_app

@pytest.fixture(scope='session')
def app():
    """Crear aplicación Flask para testing"""
    # Usar base de datos en memoria para tests
    app = create_app(testing=True)

    # Configurar base de datos de test
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['JWT_SECRET_KEY'] = 'test_jwt_secret'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='session')
def client(app):
    """Cliente de test para la aplicación"""
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """Sesión de base de datos para cada test"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_user(db_session):
    """Usuario de prueba"""
    user = User(
        email='test@example.com',
        password_hash='hashed_password',
        name='Test User',
        role='admin',
        active=True
    )
    db_session.session.add(user)
    db_session.session.commit()
    return user

@pytest.fixture
def test_company(db_session):
    """Empresa de prueba"""
    company = Company(
        name='Test Company',
        company_type='exporter',
        email='test@company.com'
    )
    db_session.session.add(company)
    db_session.session.commit()
    return company

@pytest.fixture
def auth_headers(client, test_user):
    """Headers de autenticación para tests"""
    # Login para obtener token JWT
    response = client.post('/api/auth/login', json={
        'email': test_user.email,
        'password': 'test_password'
    })

    if response.status_code == 200:
        data = response.get_json()
        token = data.get('access_token')
        return {'Authorization': f'Bearer {token}'}
    else:
        # Para tests donde no hay login implementado, usar token mock
        return {'Authorization': 'Bearer mock_token'}
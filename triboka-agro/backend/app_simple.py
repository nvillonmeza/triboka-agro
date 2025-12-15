#!/usr/bin/env python3
"""
Aplicación Flask simplificada para desarrollo local de TRIBOKA Agro
Sin dependencias complejas como pandas para facilitar el desarrollo
"""

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar extensiones
db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*")

# Crear aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///triboka.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev_jwt_secret')

# Inicializar extensiones con la app
db.init_app(app)
jwt.init_app(app)
socketio.init_app(app)

# Importar modelos
from models_simple import User, Company, ExportContract

# Rutas básicas
@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "triboka-agro-dev"})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            "access_token": access_token,
            "user": user.to_dict()
        }), 200

    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name', '')

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    user = User(email=email, name=name)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

@app.route('/api/companies')
@jwt_required()
def get_companies():
    companies = Company.query.all()
    return jsonify([{
        "id": c.id,
        "name": c.name,
        "email": c.email,
        "company_type": c.company_type
    } for c in companies])

@app.route('/api/lots')
@jwt_required()
def get_lots():
    # Simular datos de lotes
    return jsonify([
        {
            "id": 1,
            "product_name": "Cacao Premium Orgánico",
            "quantity": 1000,
            "unit": "kg",
            "quality_grade": "Premium",
            "price_per_unit": 8.50
        },
        {
            "id": 2,
            "product_name": "Café Especial Altura",
            "quantity": 500,
            "unit": "kg",
            "quality_grade": "Especial",
            "price_per_unit": 12.00
        }
    ])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5003, debug=True)
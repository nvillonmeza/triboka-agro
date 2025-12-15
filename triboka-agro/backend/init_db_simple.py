#!/usr/bin/env python3
"""
Script simple de inicialización de base de datos para desarrollo local
"""

import os
import sys
from flask import Flask
from models_simple import db, Company, User, ExportContract

# Configurar aplicación
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///triboka.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def init_db():
    with app.app_context():
        print("📊 Creando tablas...")
        db.create_all()

        print("👤 Creando usuario demo...")
        # Crear empresa demo
        company = Company(
            name="AgroExport Demo S.A.",
            email="info@agroexport.com",
            company_type="exporter",
            country="Perú",
            api_key="demo_key_123"
        )
        db.session.add(company)
        db.session.commit()

        # Crear usuario demo
        user = User(
            email="demo@agroexport.com",
            name="Demo User",
            first_name="Demo",
            last_name="User",
            role="admin",
            company_id=company.id
        )
        user.set_password("demo123")
        db.session.add(user)
        db.session.commit()

        print("✅ Base de datos inicializada exitosamente!")
        print(f"📧 Usuario demo: {user.email}")
        print(f"🔑 Password: demo123")

if __name__ == "__main__":
    init_db()
#!/usr/bin/env python3
"""
Inicialización básica de base de datos SQLite para Triboka
"""

import sqlite3
import os
import hashlib
from datetime import datetime

def create_database():
    """Crear base de datos SQLite con datos básicos"""
    # Usar la misma lógica que app_web3.py para la ubicación de la BD
    from flask import Flask
    app = Flask(__name__)
    db_path = os.path.join(app.instance_path, 'triboka_production.db')
    
    # Eliminar base de datos existente
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️  Base de datos anterior eliminada")
    
    # Crear conexión
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🏗️  Creando estructura de base de datos...")
    
    # Crear tabla de usuarios
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        company_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Crear tabla de empresas
    cursor.execute('''
    CREATE TABLE companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        company_type TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        address TEXT,
        contact_person TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Crear tabla de contratos
    cursor.execute('''
    CREATE TABLE export_contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_code TEXT UNIQUE NOT NULL,
        buyer_company_id INTEGER,
        exporter_company_id INTEGER,
        product_type TEXT NOT NULL,
        product_grade TEXT,
        total_volume_mt REAL NOT NULL,
        differential_usd REAL NOT NULL,
        contract_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        start_date TIMESTAMP,
        end_date TIMESTAMP,
        delivery_date TIMESTAMP,
        created_by_user_id INTEGER,
        fixed_volume_mt REAL DEFAULT 0.0,
        blockchain_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (buyer_company_id) REFERENCES companies (id),
        FOREIGN KEY (exporter_company_id) REFERENCES companies (id),
        FOREIGN KEY (created_by_user_id) REFERENCES users (id)
    )
    ''')
    
    # Crear tabla de lotes
    cursor.execute('''
    CREATE TABLE producer_lots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producer_company_id INTEGER,
        farm_name TEXT NOT NULL,
        location TEXT,
        product_type TEXT NOT NULL,
        weight_kg REAL NOT NULL,
        quality_grade TEXT,
        harvest_date TIMESTAMP,
        certifications TEXT,
        blockchain_token_id INTEGER,
        nft_metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (producer_company_id) REFERENCES companies (id)
    )
    ''')
    
    print("👤 Creando usuarios de ejemplo...")
    
    # Hash para contraseñas
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    # Insertar usuarios de ejemplo
    users = [
        ('admin@triboka.com', 'Admin Triboka', hash_password('admin123'), 'admin'),
        ('operator@triboka.com', 'Operador Sistema', hash_password('op123'), 'operator'),
        ('producer@triboka.com', 'Productor Demo', hash_password('prod123'), 'producer'),
        ('exporter@triboka.com', 'Exportador Demo', hash_password('exp123'), 'exporter'),
        ('buyer@triboka.com', 'Comprador Demo', hash_password('buy123'), 'buyer')
    ]
    
    cursor.executemany('''
    INSERT INTO users (email, name, password_hash, role) 
    VALUES (?, ?, ?, ?)
    ''', users)
    
    print("🏢 Creando empresas de ejemplo...")
    
    # Insertar empresas de ejemplo
    companies = [
        ('Triboka Exportadora', 'exporter', 'export@triboka.com', '+51-1-234-5678', 'Lima, Perú', 'Carlos Pérez'),
        ('CacaoFarms Producers', 'producer', 'info@cacaofarms.com', '+51-1-234-5679', 'Cusco, Perú', 'María González'),
        ('Hershey International', 'buyer', 'procurement@hershey.com', '+1-717-534-4000', 'Pennsylvania, USA', 'John Smith'),
        ('Nestlé Trading', 'buyer', 'trading@nestle.com', '+41-21-924-1111', 'Vevey, Switzerland', 'Pierre Dubois')
    ]
    
    cursor.executemany('''
    INSERT INTO companies (name, company_type, email, phone, address, contact_person) 
    VALUES (?, ?, ?, ?, ?, ?)
    ''', companies)
    
    # Confirmar cambios
    conn.commit()
    conn.close()
    
    print("✅ Base de datos creada exitosamente")
    print(f"📁 Ubicación: {db_path}")
    print("\n👥 Usuarios creados:")
    print("📧 Admin: admin@triboka.com / admin123")
    print("📧 Operador: operator@triboka.com / op123") 
    print("📧 Productor: producer@triboka.com / prod123")
    print("📧 Exportador: exporter@triboka.com / exp123")
    print("📧 Comprador: buyer@triboka.com / buy123")

if __name__ == '__main__':
    create_database()
    print("\n🎉 ¡Base de datos lista para usar!")
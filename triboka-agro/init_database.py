#!/usr/bin/env python3
"""
Triboka Agro - Corrector de Base de Datos
Inicializa la base de datos con datos de prueba para testing
"""

import sqlite3
import os
from datetime import datetime, timedelta
import hashlib

def create_database():
    """Crea la base de datos con estructura completa"""
    
    # Crear directorio si no existe
    os.makedirs('database', exist_ok=True)
    
    # Conectar a la base de datos
    conn = sqlite3.connect('database/triboka.db')
    cursor = conn.cursor()
    
    print("🗄️  Creando estructura de base de datos...")
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            company_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active INTEGER DEFAULT 1,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Tabla de empresas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            country TEXT,
            city TEXT,
            contact_email TEXT,
            certification_level TEXT,
            sustainability_score REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active INTEGER DEFAULT 1
        )
    ''')
    
    # Tabla de contratos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            buyer_id INTEGER,
            seller_id INTEGER,
            quantity REAL,
            unit TEXT,
            price_per_unit REAL,
            total_value REAL,
            quality_grade TEXT,
            delivery_date DATE,
            sustainability_requirements TEXT,
            blockchain_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (buyer_id) REFERENCES companies (id),
            FOREIGN KEY (seller_id) REFERENCES companies (id)
        )
    ''')
    
    # Tabla de lotes NFT
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_number TEXT UNIQUE NOT NULL,
            producer_id INTEGER,
            product_type TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            quality_score REAL,
            sustainability_score REAL,
            origin_farm TEXT,
            harvest_date DATE,
            processing_date DATE,
            certifications TEXT,
            blockchain_token_id TEXT,
            nft_metadata TEXT,
            status TEXT DEFAULT 'available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producer_id) REFERENCES companies (id)
        )
    ''')
    
    # Tabla de notificaciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            data TEXT,
            read_status INTEGER DEFAULT 0,
            priority TEXT DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    print("✅ Estructura de tablas creada")
    
    # Insertar datos de prueba
    print("📊 Insertando datos de prueba...")
    
    # Empresas de prueba
    companies_data = [
        ('Cooperativa Cacao Triboka', 'producer', 'Colombia', 'Buenaventura', 'info@triboka.com', 'organic', 92.5),
        ('Exportadora Global', 'exporter', 'Colombia', 'Bogotá', 'export@global.com', 'standard', 78.3),
        ('Chocolates Premium EU', 'buyer', 'Netherlands', 'Amsterdam', 'buy@premium.eu', 'organic', 85.7),
        ('Fair Trade Solutions', 'cooperative', 'Peru', 'Lima', 'contact@fairtrade.pe', 'fairtrade', 89.2),
        ('Sustainable Cocoa Inc', 'processor', 'USA', 'New York', 'info@sustainable.us', 'rainforest', 91.8)
    ]
    
    cursor.executemany('''
        INSERT INTO companies (name, type, country, city, contact_email, certification_level, sustainability_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', companies_data)
    
    # Usuarios de prueba
    users_data = [
        ('Administrador Sistema', 'admin@triboka.com', 'admin123', 'admin', 1),
        ('Juan Productor', 'juan@triboka.com', 'producer123', 'producer', 1),
        ('María Exportadora', 'maria@global.com', 'export123', 'exporter', 2),
        ('Peter Buyer', 'peter@premium.eu', 'buyer123', 'buyer', 3),
        ('Ana Cooperativa', 'ana@fairtrade.pe', 'coop123', 'operator', 4),
        ('Carlos Procesador', 'carlos@sustainable.us', 'process123', 'processor', 5)
    ]
    
    # Hash de contraseñas (simulado - en producción usar bcrypt)
    hashed_users = []
    for name, email, password, role, company_id in users_data:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        hashed_users.append((name, email, hashed_password, role, company_id))
    
    cursor.executemany('''
        INSERT INTO users (name, email, password, role, company_id)
        VALUES (?, ?, ?, ?, ?)
    ''', hashed_users)
    
    # Contratos de prueba
    contracts_data = [
        ('Contrato Cacao Premium Q1 2025', 'Suministro de cacao orgánico certificado', 'supply', 'active', 3, 1, 1000, 'kg', 4.50, 4500, 'A+', '2025-03-31', 'Orgánico, Fair Trade', 'blockchain_hash_001'),
        ('Exportación Cacao Europa', 'Lote especial para chocolates premium', 'export', 'active', 3, 2, 2500, 'kg', 4.25, 10625, 'A', '2025-04-15', 'Rainforest Alliance', 'blockchain_hash_002'),
        ('Contrato Sostenibilidad', 'Cacao con certificación triple', 'sustainability', 'pending', 5, 4, 800, 'kg', 5.00, 4000, 'AA', '2025-05-20', 'Orgánico, Fair Trade, Rainforest', 'blockchain_hash_003')
    ]
    
    cursor.executemany('''
        INSERT INTO contracts (title, description, type, status, buyer_id, seller_id, quantity, unit, price_per_unit, total_value, quality_grade, delivery_date, sustainability_requirements, blockchain_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', contracts_data)
    
    # Lotes NFT de prueba
    lots_data = [
        ('LOT-2025-001', 1, 'Cacao Criollo', 500, 'kg', 95.5, 92.8, 'Finca La Esperanza', '2024-12-15', '2024-12-20', 'Orgánico,Fair Trade', 'NFT_001', '{"quality": "premium", "origin": "Valle del Cauca"}', 'tokenized'),
        ('LOT-2025-002', 1, 'Cacao Trinitario', 750, 'kg', 88.2, 89.5, 'Finca El Paraíso', '2024-12-10', '2024-12-18', 'Rainforest Alliance', 'NFT_002', '{"quality": "high", "origin": "Chocó"}', 'available'),
        ('LOT-2025-003', 4, 'Cacao Nacional', 300, 'kg', 92.1, 94.2, 'Cooperativa Andina', '2024-12-08', '2024-12-22', 'Orgánico,UTZ', 'NFT_003', '{"quality": "super premium", "origin": "Amazonas"}', 'reserved')
    ]
    
    cursor.executemany('''
        INSERT INTO lots (lot_number, producer_id, product_type, quantity, unit, quality_score, sustainability_score, origin_farm, harvest_date, processing_date, certifications, blockchain_token_id, nft_metadata, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', lots_data)
    
    # Notificaciones de prueba
    notifications_data = [
        (1, 'system', 'Sistema Inicializado', 'La base de datos ha sido inicializada correctamente', '{"type": "system_init"}', 0, 'high'),
        (2, 'contract', 'Nuevo Contrato Disponible', 'Hay un nuevo contrato de cacao premium disponible', '{"contract_id": 1}', 0, 'medium'),
        (3, 'blockchain', 'NFT Tokenizado', 'El lote LOT-2025-001 ha sido tokenizado exitosamente', '{"lot_id": 1, "nft_id": "NFT_001"}', 1, 'medium'),
        (1, 'analytics', 'Reporte ESG Generado', 'El reporte mensual de sostenibilidad está listo', '{"report_type": "monthly_esg"}', 0, 'low'),
        (4, 'quality', 'Certificación Aprobada', 'La certificación orgánica ha sido aprobada', '{"certification": "organic"}', 0, 'high')
    ]
    
    cursor.executemany('''
        INSERT INTO notifications (user_id, type, title, message, data, read_status, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', notifications_data)
    
    # Confirmar cambios
    conn.commit()
    
    # Verificar datos insertados
    print("\n📈 Resumen de datos insertados:")
    
    tables = ['companies', 'users', 'contracts', 'lots', 'notifications']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   ✅ {table}: {count} registros")
    
    conn.close()
    print("\n🎉 Base de datos inicializada correctamente!")
    print("👤 Usuario de prueba: admin@triboka.com / admin123")

if __name__ == "__main__":
    create_database()
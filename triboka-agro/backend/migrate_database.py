#!/usr/bin/env python3
"""
Script para migrar la base de datos al nuevo esquema de contratos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models_simple import db
from app_web3 import app

def migrate_database():
    """Migrar base de datos al nuevo esquema"""
    with app.app_context():
        print("🔄 Migrando base de datos...")

        # Eliminar todas las tablas existentes
        db.drop_all()
        print("✅ Tablas anteriores eliminadas")

        # Crear todas las tablas con el nuevo esquema
        db.create_all()
        print("✅ Nuevas tablas creadas")

        # Crear usuario admin si no existe
        from models_simple import User
        from werkzeug.security import generate_password_hash

        admin_user = User.query.filter_by(email='admin@triboka.com').first()
        if not admin_user:
            admin_user = User(
                email='admin@triboka.com',
                name='Admin Triboka',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                active=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Usuario admin creado")
        else:
            print("ℹ️ Usuario admin ya existe")

        print("🎉 Migración completada exitosamente!")

if __name__ == '__main__':
    migrate_database()
#!/usr/bin/env python3
"""
Script de migración para agregar columnas faltantes a la tabla companies
"""
import sys
import os
import sqlite3

def migrate_companies_table():
    """Agregar columnas faltantes a la tabla companies"""

    # Ruta a la base de datos
    db_path = os.path.join(os.path.dirname(__file__), 'backend', 'instance', 'triboka_production.db')

    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada en: {db_path}")
        return False

    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar qué columnas ya existen
        cursor.execute("PRAGMA table_info(companies)")
        columns = [row[1] for row in cursor.fetchall()]

        print(f"📋 Columnas existentes en companies: {columns}")

        # Agregar columna country si no existe
        if 'country' not in columns:
            print("➕ Agregando columna 'country'...")
            cursor.execute("ALTER TABLE companies ADD COLUMN country VARCHAR(100)")
            print("✅ Columna 'country' agregada")

        # Agregar columna api_key si no existe
        if 'api_key' not in columns:
            print("➕ Agregando columna 'api_key'...")
            cursor.execute("ALTER TABLE companies ADD COLUMN api_key VARCHAR(100)")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_companies_api_key ON companies(api_key)")
            print("✅ Columna 'api_key' agregada con índice único")

        # Agregar columna blockchain_address si no existe
        if 'blockchain_address' not in columns:
            print("➕ Agregando columna 'blockchain_address'...")
            cursor.execute("ALTER TABLE companies ADD COLUMN blockchain_address VARCHAR(100)")
            print("✅ Columna 'blockchain_address' agregada")

        # Agregar columna is_active si no existe
        if 'is_active' not in columns:
            print("➕ Agregando columna 'is_active'...")
            cursor.execute("ALTER TABLE companies ADD COLUMN is_active BOOLEAN DEFAULT 1")
            print("✅ Columna 'is_active' agregada")

        # Commit de los cambios
        conn.commit()
        print("✅ Migración completada exitosamente")

        # Verificar el resultado
        cursor.execute("PRAGMA table_info(companies)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Columnas después de migración: {new_columns}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

if __name__ == '__main__':
    print("🔄 Iniciando migración de tabla companies...")
    success = migrate_companies_table()
    if success:
        print("🎯 Migración completada. Ahora puedes crear las empresas de prueba.")
    else:
        print("💥 Migración fallida.")
        sys.exit(1)
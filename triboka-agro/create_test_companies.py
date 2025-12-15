#!/usr/bin/env python3
"""
Script para crear empresas de prueba para validación multi-tenant
"""
import sys
import os
import secrets

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models_simple import db, Company
from app_web3 import app

def create_test_companies():
    """Crear empresas de prueba para validación multi-tenant"""

    with app.app_context():
        # Verificar si ya existen las empresas
        agrocorp = Company.query.filter_by(name='AgroCorp Ecuador').first()
        cacaoglobal = Company.query.filter_by(name='CacaoGlobal Peru').first()

        if agrocorp:
            print(f"✅ AgroCorp Ecuador ya existe (ID: {agrocrop.id})")
        else:
            # Crear AgroCorp Ecuador
            agrocorp = Company(
                name='AgroCorp Ecuador',
                email='contact@agrocrop-ec.com',
                company_type='producer',
                country='Ecuador',
                api_key=secrets.token_urlsafe(32),
                blockchain_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
                is_active=True
            )
            db.session.add(agrocrop)
            print(f"✅ Creada AgroCorp Ecuador con API key: {agrocrop.api_key[:16]}...")

        if cacaoglobal:
            print(f"✅ CacaoGlobal Peru ya existe (ID: {cacaoglobal.id})")
        else:
            # Crear CacaoGlobal Peru
            cacaoglobal = Company(
                name='CacaoGlobal Peru',
                email='contact@cacaoglobal-pe.com',
                company_type='exporter',
                country='Peru',
                api_key=secrets.token_urlsafe(32),
                blockchain_address='0x8ba1f109551bD4328030126452617686aF2D0518',
                is_active=True
            )
            db.session.add(cacaoglobal)
            print(f"✅ Creada CacaoGlobal Peru con API key: {cacaoglobal.api_key[:16]}...")

        # Commit de los cambios
        db.session.commit()

        # Mostrar resumen
        print("\n📋 Resumen de empresas creadas:")
        companies = Company.query.all()
        for company in companies:
            print(f"  - {company.name} (ID: {company.id}, País: {company.country}, API Key: {company.api_key[:16]}...)")

        print("\n🎯 Empresas listas para pruebas multi-tenant!")

if __name__ == '__main__':
    create_test_companies()

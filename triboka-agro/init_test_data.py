#!/usr/bin/env python3
"""
Script para inicializar datos de prueba para Triboka
"""
from backend.app_web3 import app, db, Company, ProducerLot, User
from backend.models_simple import TraceEvent, TraceTimeline, BatchNFT
import json
from datetime import datetime

def init_test_data():
    with app.app_context():
        print("Creando tablas...")
        # Crear tablas
        db.create_all()
        print("✅ Tablas creadas")
        
        # Crear compañías de prueba
        companies_data = [
            {'name': 'AgroWeight Cloud', 'company_type': 'technology', 'api_key': 'test_api_key_agroweight'},
            {'name': 'Finca Los Cacaos', 'company_type': 'producer', 'api_key': 'test_api_key_producer'},
            {'name': 'Exportadora del Valle', 'company_type': 'exporter', 'api_key': 'test_api_key_exporter'}
        ]

        companies = []
        for data in companies_data:
            company = Company(
                name=data['name'],
                company_type=data['company_type'],
                api_key=data['api_key'],
                country='Honduras',
                blockchain_address=f'0x{data["api_key"][-16:]}'
            )
            db.session.add(company)
            companies.append(company)

        db.session.commit()
        print(f"✅ Compañías creadas: {len(companies)}")

        # Crear usuarios para las compañías
        for i, company in enumerate(companies):
            user = User(
                email=f'admin@{company.name.lower().replace(" ", "")}.com',
                first_name='Admin',
                last_name=company.name.split()[-1],
                name=f'Admin {company.name.split()[-1]}',
                role='admin' if i == 0 else ('producer' if i == 1 else 'exporter'),
                company_id=company.id,
                active=True
            )
            user.set_password('password123')
            db.session.add(user)

        db.session.commit()
        print(f"✅ Usuarios creados: {len(companies)}")

        # Crear lotes de prueba
        lots_data = [
            {
                'lot_code': 'LOT-001-20251117182859',
                'producer_company_id': companies[1].id,
                'producer_name': 'Juan Pérez',
                'farm_name': 'Finca Los Cacaos',
                'location': 'Choluteca, Honduras',
                'product_type': 'Cacao Fino de Aroma',
                'weight_kg': 5000.0,
                'quality_grade': 'Premium',
                'quality_score': 95.0,
                'moisture_content': 7.2,
                'harvest_date': datetime(2024, 10, 15),
                'purchase_date': datetime(2024, 11, 10),
                'purchase_price_usd': 22000.0,
                'certifications': 'Organic,Fair Trade',
                'status': 'purchased'
            },
            {
                'lot_code': 'LOT-002-20251117182900',
                'producer_company_id': companies[1].id,
                'producer_name': 'María González',
                'farm_name': 'Finca Santa María',
                'location': 'El Paraíso, Honduras',
                'product_type': 'Cacao Trinitario',
                'weight_kg': 3000.0,
                'quality_grade': 'A',
                'quality_score': 88.0,
                'moisture_content': 6.8,
                'harvest_date': datetime(2024, 10, 20),
                'purchase_date': datetime(2024, 11, 12),
                'purchase_price_usd': 12600.0,
                'certifications': 'Organic',
                'status': 'purchased'
            }
        ]

        lots = []
        for data in lots_data:
            lot = ProducerLot(**data)
            db.session.add(lot)
            lots.append(lot)

        db.session.commit()
        print(f"✅ Lotes creados: {len(lots)}")

        print('✅ Datos de prueba creados exitosamente')
        print(f'📊 Compañías: {len(companies)}')
        print(f'👥 Usuarios: {len(companies)}')
        print(f'📦 Lotes: {len(lots)}')
        print()
        print('🔑 API Keys:')
        for company in companies:
            print(f'  {company.name}: {company.api_key}')

if __name__ == '__main__':
    init_test_data()
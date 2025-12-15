#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos de prueba
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models_simple import db
from app_web3 import app
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def populate_test_data():
    """Poblar base de datos con datos de prueba"""
    with app.app_context():
        print("🌱 Poblando base de datos con datos de prueba...")

        # Crear empresas de prueba
        companies_data = [
            {
                'name': 'Café Colombia Export S.A.',
                'company_type': 'exporter',
                'country': 'Colombia',
                'email': 'contacto@cafecolombia.com',
                'blockchain_address': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
            },
            {
                'name': 'Green Bean Trading Ltd.',
                'company_type': 'buyer',
                'country': 'USA',
                'email': 'orders@greenbean.com',
                'blockchain_address': '0x742d35Cc6634C0532925a3b844Bc454e4438f44f'
            },
            {
                'name': 'Finca El Paraíso',
                'company_type': 'producer',
                'country': 'Colombia',
                'email': 'admin@fincaelparaiso.com',
                'blockchain_address': '0x742d35Cc6634C0532925a3b844Bc454e4438f44g'
            },
            {
                'name': 'Café Premium Export',
                'company_type': 'exporter',
                'country': 'Colombia',
                'email': 'ventas@cafepremium.com',
                'blockchain_address': '0x742d35Cc6634C0532925a3b844Bc454e4438f44h'
            },
            {
                'name': 'Organic Coffee Imports',
                'company_type': 'buyer',
                'country': 'Germany',
                'email': 'import@organiccoffee.de',
                'blockchain_address': '0x742d35Cc6634C0532925a3b844Bc454e4438f44i'
            }
        ]

        from models_simple import Company
        companies = []
        for company_data in companies_data:
            company = Company(**company_data)
            db.session.add(company)
            companies.append(company)

        db.session.flush()  # Para obtener IDs
        print("✅ Empresas creadas")

        # Crear usuarios adicionales
        users_data = [
            {
                'email': 'operador@triboka.com',
                'name': 'Operador Sistema',
                'password_hash': generate_password_hash('operador123'),
                'role': 'operator',
                'company_id': companies[0].id,  # Café Colombia Export
                'active': True
            },
            {
                'email': 'productor@triboka.com',
                'name': 'Productor Juan Pérez',
                'password_hash': generate_password_hash('productor123'),
                'role': 'producer',
                'company_id': companies[2].id,  # Finca El Paraíso
                'active': True
            },
            {
                'email': 'exportador@triboka.com',
                'name': 'Exportador María González',
                'password_hash': generate_password_hash('exportador123'),
                'role': 'exporter',
                'company_id': companies[0].id,  # Café Colombia Export
                'active': True
            },
            {
                'email': 'comprador@triboka.com',
                'name': 'Comprador John Smith',
                'password_hash': generate_password_hash('comprador123'),
                'role': 'buyer',
                'company_id': companies[1].id,  # Green Bean Trading
                'active': True
            }
        ]

        from models_simple import User
        for user_data in users_data:
            user = User(**user_data)
            db.session.add(user)

        print("✅ Usuarios adicionales creados")

        # Crear contratos de prueba
        contracts_data = [
            {
                'contract_code': 'EXP-2025-001',
                'buyer_company_id': companies[1].id,  # Green Bean Trading
                'exporter_company_id': companies[0].id,  # Café Colombia Export
                'product_type': 'Café',
                'product_grade': 'Premium',
                'total_volume_mt': 500.0,
                'fixed_volume_mt': 250.0,
                'differential_usd': 0.50,
                'start_date': datetime.now() - timedelta(days=30),
                'end_date': datetime.now() + timedelta(days=180),
                'delivery_date': datetime.now() + timedelta(days=150),
                'status': 'active',
                'created_by_user_id': 1  # Admin
            },
            {
                'contract_code': 'EXP-2025-002',
                'buyer_company_id': companies[4].id,  # Organic Coffee Imports
                'exporter_company_id': companies[3].id,  # Café Premium Export
                'product_type': 'Café',
                'product_grade': 'Orgánico',
                'total_volume_mt': 300.0,
                'fixed_volume_mt': 150.0,
                'differential_usd': 0.75,
                'start_date': datetime.now() - timedelta(days=15),
                'end_date': datetime.now() + timedelta(days=200),
                'delivery_date': datetime.now() + timedelta(days=180),
                'status': 'active',
                'created_by_user_id': 1  # Admin
            },
            {
                'contract_code': 'EXP-2025-003',
                'buyer_company_id': companies[1].id,  # Green Bean Trading
                'exporter_company_id': companies[0].id,  # Café Colombia Export
                'product_type': 'Café',
                'product_grade': 'Especialty',
                'total_volume_mt': 200.0,
                'fixed_volume_mt': 0.0,
                'differential_usd': 1.00,
                'start_date': datetime.now() - timedelta(days=5),
                'end_date': datetime.now() + timedelta(days=120),
                'delivery_date': datetime.now() + timedelta(days=100),
                'status': 'active',
                'created_by_user_id': 1  # Admin
            }
        ]

        from models_simple import ExportContract
        contracts = []
        for contract_data in contracts_data:
            contract = ExportContract(**contract_data)
            db.session.add(contract)
            contracts.append(contract)

        db.session.flush()
        print("✅ Contratos creados")

        # Crear fijaciones para contratos
        fixations_data = [
            {
                'export_contract_id': contracts[0].id,
                'fixed_quantity_mt': 150.0,
                'spot_price_usd': 2.50,
                'total_value_usd': 375.0,
                'fixation_date': datetime.now() - timedelta(days=10),
                'notes': 'Fijación inicial del contrato',
                'created_by_user_id': 1
            },
            {
                'export_contract_id': contracts[0].id,
                'fixed_quantity_mt': 100.0,
                'spot_price_usd': 2.45,
                'total_value_usd': 245.0,
                'fixation_date': datetime.now() - timedelta(days=5),
                'notes': 'Segunda fijación',
                'created_by_user_id': 1
            },
            {
                'export_contract_id': contracts[1].id,
                'fixed_quantity_mt': 150.0,
                'spot_price_usd': 2.60,
                'total_value_usd': 390.0,
                'fixation_date': datetime.now() - timedelta(days=7),
                'notes': 'Fijación orgánica premium',
                'created_by_user_id': 1
            }
        ]

        from models_simple import ContractFixation
        for fixation_data in fixations_data:
            fixation = ContractFixation(**fixation_data)
            db.session.add(fixation)

        print("✅ Fijaciones creadas")

        # Crear lotes de productores
        lots_data = [
            {
                'lot_code': 'LOT-COL-2025-001',
                'producer_company_id': companies[2].id,  # Finca El Paraíso
                'producer_name': 'Finca El Paraíso',
                'farm_name': 'Finca El Paraíso',
                'location': 'Quindío, Colombia',
                'product_type': 'Café',
                'weight_kg': 1250.0,
                'quality_grade': 'Excelente',
                'harvest_date': datetime.now() - timedelta(days=45),
                'purchase_date': datetime.now() - timedelta(days=30),
                'purchase_price_usd': 3.25,
                'certifications': 'Organic,Fair Trade,Rainforest Alliance',
                'status': 'purchased',
                'export_contract_id': contracts[0].id,
                'purchased_by_company_id': companies[0].id,  # Café Colombia Export
                'created_by_user_id': 1
            },
            {
                'lot_code': 'LOT-COL-2025-002',
                'producer_company_id': companies[2].id,  # Finca El Paraíso
                'producer_name': 'Finca El Paraíso',
                'farm_name': 'Finca El Paraíso',
                'location': 'Quindío, Colombia',
                'product_type': 'Café',
                'weight_kg': 980.0,
                'quality_grade': 'Muy Bueno',
                'harvest_date': datetime.now() - timedelta(days=40),
                'purchase_date': datetime.now() - timedelta(days=25),
                'purchase_price_usd': 3.10,
                'certifications': 'Organic,Fair Trade',
                'status': 'purchased',
                'export_contract_id': contracts[0].id,
                'purchased_by_company_id': companies[0].id,  # Café Colombia Export
                'created_by_user_id': 1
            },
            {
                'lot_code': 'LOT-COL-2025-003',
                'producer_company_id': companies[2].id,  # Finca El Paraíso
                'producer_name': 'Finca El Paraíso',
                'farm_name': 'Finca El Paraíso',
                'location': 'Quindío, Colombia',
                'product_type': 'Café',
                'weight_kg': 750.0,
                'quality_grade': 'Premium',
                'harvest_date': datetime.now() - timedelta(days=35),
                'certifications': 'Organic,Fair Trade,Rainforest Alliance',
                'status': 'available',
                'created_by_user_id': 1
            },
            {
                'lot_code': 'LOT-COL-2025-004',
                'producer_company_id': companies[2].id,  # Finca El Paraíso
                'producer_name': 'Finca El Paraíso',
                'farm_name': 'Finca El Paraíso',
                'location': 'Quindío, Colombia',
                'product_type': 'Café',
                'weight_kg': 1100.0,
                'quality_grade': 'Especialty',
                'harvest_date': datetime.now() - timedelta(days=50),
                'certifications': 'Organic,Fair Trade',
                'status': 'available',
                'created_by_user_id': 1
            },
            {
                'lot_code': 'LOT-COL-2025-005',
                'producer_company_id': companies[2].id,  # Finca El Paraíso
                'producer_name': 'Finca El Paraíso',
                'farm_name': 'Finca El Paraíso',
                'location': 'Quindío, Colombia',
                'product_type': 'Café',
                'weight_kg': 650.0,
                'quality_grade': 'Excelente',
                'harvest_date': datetime.now() - timedelta(days=55),
                'purchase_date': datetime.now() - timedelta(days=35),
                'purchase_price_usd': 3.40,
                'certifications': 'Organic,Fair Trade,Rainforest Alliance',
                'status': 'purchased',
                'export_contract_id': contracts[1].id,
                'purchased_by_company_id': companies[3].id,  # Café Premium Export
                'created_by_user_id': 1
            }
        ]

        from models_simple import ProducerLot
        lots = []
        for lot_data in lots_data:
            lot = ProducerLot(**lot_data)
            db.session.add(lot)
            lots.append(lot)

        db.session.flush()
        print("✅ Lotes creados")

        # Crear batches NFT
        batches_data = [
            {
                'batch_code': 'BATCH-COL-2025-001',
                'source_lot_ids': '[1,2]',  # Lotes 1 y 2
                'source_lot_weights': '[1250.0,980.0]',
                'total_weight_kg': 2230.0,
                'batch_type': 'Exportación',
                'location': 'Quindío, Colombia',
                'creator_company_id': companies[0].id,  # Café Colombia Export
                'current_owner_company_id': companies[0].id,
                'status': 'created'
            }
        ]

        from models_simple import BatchNFT
        for batch_data in batches_data:
            batch = BatchNFT(**batch_data)
            db.session.add(batch)

        # Actualizar lotes para que estén en el batch
        lots[0].batch_id = 1
        lots[0].status = 'batched'
        lots[1].batch_id = 1
        lots[1].status = 'batched'

        db.session.commit()
        print("✅ Batches NFT creados")

        print("🎉 ¡Base de datos poblada exitosamente!")
        print("\n📊 Resumen de datos creados:")
        print(f"   • Empresas: {len(companies)}")
        print(f"   • Usuarios: {len(users_data) + 1}")  # +1 por el admin existente
        print(f"   • Contratos: {len(contracts)}")
        print(f"   • Fijaciones: {len(fixations_data)}")
        print(f"   • Lotes: {len(lots)}")
        print(f"   • Batches: {len(batches_data)}")

        print("\n🔑 Credenciales de prueba:")
        print("   Admin: admin@triboka.com / admin123")
        print("   Operador: operador@triboka.com / operador123")
        print("   Productor: productor@triboka.com / productor123")
        print("   Exportador: exportador@triboka.com / exportador123")
        print("   Comprador: comprador@triboka.com / comprador123")

if __name__ == '__main__':
    populate_test_data()
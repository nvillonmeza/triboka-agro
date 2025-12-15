#!/usr/bin/env python3
"""
Script para actualizar la base de datos con las nuevas funcionalidades:
- BatchNFT table
- Nuevos campos en lotes para purchase tracking
- Actualizar permisos de roles
"""

import os
import sys
from datetime import datetime

# Agregar el directorio backend al path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

from models_simple import db, User, Company, ExportContract, ContractFixation, ProducerLot, BatchNFT
from flask import Flask

def create_app():
    """Crear aplicación Flask para migración"""
    app = Flask(__name__)
    
    # Configuración de base de datos
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "triboka_agro.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'triboka-agro-secret-2024'
    
    db.init_app(app)
    return app

def migrate_database():
    """Ejecutar migración de la base de datos"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Iniciando migración de base de datos...")
        
        try:
            # Crear nuevas tablas
            db.create_all()
            print("✅ Tablas creadas/actualizadas exitosamente")
            
            # Verificar si necesitamos agregar campos faltantes a ProducerLot
            if not hasattr(ProducerLot, 'purchased_by_company_id'):
                print("⚠️  Campo 'purchased_by_company_id' no encontrado en ProducerLot")
                print("   Ejecutar ALTER TABLE manualmente si es necesario")
            
            # Verificar usuarios existentes y actualizar permisos si es necesario
            users = User.query.all()
            print(f"📊 Usuarios encontrados: {len(users)}")
            
            for user in users:
                print(f"   - {user.email} (Rol: {user.role})")
                
            # Verificar lotes existentes
            lots = ProducerLot.query.all()
            print(f"📦 Lotes encontrados: {len(lots)}")
            
            # Verificar contratos existentes
            contracts = ExportContract.query.all()
            print(f"📄 Contratos encontrados: {len(contracts)}")
            
            # Verificar batches (debería estar vacío la primera vez)
            batches = BatchNFT.query.all()
            print(f"🔗 Batches encontrados: {len(batches)}")
            
            print("✅ Migración completada exitosamente")
            
        except Exception as e:
            print(f"❌ Error en migración: {e}")
            return False
    
    return True

def update_lot_fields():
    """Agregar campos faltantes a la tabla producer_lots"""
    app = create_app()
    
    with app.app_context():
        try:
            # Intentar agregar campos faltantes usando SQL raw
            db.engine.execute("""
                ALTER TABLE producer_lots ADD COLUMN purchased_by_company_id INTEGER;
            """)
            print("✅ Campo purchased_by_company_id agregado")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️  Campo purchased_by_company_id ya existe")
            else:
                print(f"⚠️  Error agregando campo: {e}")
        
        try:
            db.engine.execute("""
                ALTER TABLE producer_lots ADD COLUMN batch_id INTEGER;
            """)
            print("✅ Campo batch_id agregado")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️  Campo batch_id ya existe")
            else:
                print(f"⚠️  Error agregando campo: {e}")
        
        try:
            db.engine.execute("""
                ALTER TABLE producer_lots ADD COLUMN purchase_tx_hash VARCHAR(66);
            """)
            print("✅ Campo purchase_tx_hash agregado")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️  Campo purchase_tx_hash ya existe")
            else:
                print(f"⚠️  Error agregando campo: {e}")

def create_sample_batch():
    """Crear un batch de ejemplo para testing"""
    app = create_app()
    
    with app.app_context():
        try:
            # Buscar lotes disponibles
            available_lots = ProducerLot.query.filter_by(status='available').limit(3).all()
            
            if len(available_lots) < 2:
                print("⚠️  No hay suficientes lotes disponibles para crear batch de ejemplo")
                return
            
            # Buscar una empresa exportadora
            exporter = Company.query.filter_by(company_type='exporter').first()
            if not exporter:
                print("⚠️  No hay empresa exportadora para crear batch de ejemplo")
                return
            
            # Simular compra de lotes
            total_weight = 0
            lot_ids = []
            lot_weights = []
            
            for lot in available_lots:
                lot.status = 'purchased'
                lot.purchased_by_company_id = exporter.id
                lot.purchase_date = datetime.utcnow()
                lot.purchase_price_usd = 2500.0  # Precio ejemplo
                
                lot_ids.append(lot.id)
                lot_weights.append(float(lot.weight_kg))
                total_weight += float(lot.weight_kg)
            
            # Crear batch de ejemplo
            import json
            batch = BatchNFT(
                batch_code=f"BATCH-DEMO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                source_lot_ids=json.dumps(lot_ids),
                source_lot_weights=json.dumps(lot_weights),
                total_weight_kg=total_weight,
                batch_type='export',
                location='Puerto Guayaquil',
                creator_company_id=exporter.id,
                current_owner_company_id=exporter.id,
                status='created'
            )
            
            db.session.add(batch)
            
            # Actualizar lotes
            for lot in available_lots:
                lot.status = 'batched'
                lot.batch_id = batch.id
            
            db.session.commit()
            
            print(f"✅ Batch de ejemplo creado: {batch.batch_code}")
            print(f"   - Total weight: {total_weight}kg")
            print(f"   - Lotes incluidos: {len(lot_ids)}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creando batch de ejemplo: {e}")

if __name__ == '__main__':
    print("🚀 Iniciando actualización de base de datos Triboka...")
    print("=" * 50)
    
    # Step 1: Migrar esquema principal
    if migrate_database():
        print("\n🔧 Actualizando campos de tabla...")
        update_lot_fields()
        
        print("\n📦 Creando datos de ejemplo...")
        create_sample_batch()
        
        print("\n🎉 Actualización completada exitosamente!")
        print("\n📋 Próximos pasos:")
        print("   1. Reiniciar servidor backend")
        print("   2. Probar endpoints de roles descentralizados")
        print("   3. Probar creación y gestión de batches")
        print("   4. Implementar frontend para nuevas funcionalidades")
    else:
        print("\n❌ Migración falló. Revisar errores arriba.")
        sys.exit(1)
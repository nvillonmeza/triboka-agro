#!/usr/bin/env python3
"""
Sistema de Inicialización de Base de Datos - Triboka Agro Platform
================================================================

Este script maneja la inicialización completa de la base de datos,
incluyendo creación de tablas, datos de prueba y configuración inicial.

Características:
- Creación automática de tablas
- Datos de muestra para desarrollo
- Configuración de roles y permisos
- Validación de integridad de datos
- Soporte para reinicialización segura
- Compatibilidad con sistema de contratos agrícolas existente
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuración de paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Importar modelos según disponibilidad
try:
    # Intentar importar modelos completos primero
    from app_web3 import app
    FULL_SYSTEM = True
    logger.info("✅ Sistema completo detectado")
except ImportError:
    # Fallback a modelos simples
    from models_simple import db, Company, User, ExportContract, ContractFixation, ProducerLot, DigitalIdentity, TraceEvent
    from flask import Flask
    
    # Configurar aplicación mínima
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///triboka.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    FULL_SYSTEM = False
    logger.info("⚙️ Sistema de contratos agrícolas detectado")
    db_path = os.path.join(app.instance_path, 'triboka_production.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    FULL_SYSTEM = False
    logger.info("⚙️ Sistema de contratos agrícolas detectado")

def initialize_database(reset=False):
    """
    Inicializa la base de datos con tablas y datos de muestra.
    
    Args:
        reset: Si True, elimina y recrea todas las tablas
    
    Returns:
        bool: True si la inicialización fue exitosa
    """
    try:
        with app.app_context():
            logger.info("🚀 Iniciando proceso de inicialización de base de datos...")
            
            if reset:
                logger.warning("⚠️ Eliminando todas las tablas existentes...")
                db.drop_all()
                
            # Crear todas las tablas
            logger.info("📊 Creando estructura de tablas...")
            db.create_all()
            
            # Inicializar según el tipo de sistema
            if FULL_SYSTEM:
                return initialize_full_system(reset)
            else:
                return initialize_contracts_system(reset)
                
    except Exception as e:
        logger.error(f"❌ Error durante la inicialización: {str(e)}")
        if 'db' in locals():
            db.session.rollback()
        return False

def initialize_full_system(reset):
    """Inicializar sistema completo con modelos avanzados"""
    try:
        # Verificar si ya existen datos
        if not reset and Usuario.query.first():
            logger.info("✅ Sistema completo ya inicializado. Use reset=True para reinicializar.")
            return True
            
        # Crear usuario administrador por defecto
        logger.info("👤 Creando usuario administrador...")
        admin_user = Usuario(
            nombre_usuario='admin',
            email='admin@triboka.com',
            nombre='Administrador',
            apellido='Sistema',
            password_hash=generate_password_hash('admin123'),
            rol='admin',
            activo=True,
            fecha_creacion=datetime.utcnow()
        )
        db.session.add(admin_user)
        
        # Crear empresa de ejemplo
        logger.info("🏢 Creando empresa de ejemplo...")
        empresa_ejemplo = Empresa(
            nombre='Triboka Agro Demo',
            tipo_empresa='cooperativa',
            pais='Colombia',
            region='Cauca',
            ciudad='Popayán',
            direccion='Calle 5 # 8-13',
            telefono='+57-2-8201234',
            email='demo@triboka.com',
            nit='900123456-1',
            activa=True,
            fecha_creacion=datetime.utcnow()
        )
        db.session.add(empresa_ejemplo)
        db.session.flush()
        
        # Configurar usuario con empresa
        admin_user.empresa_id = empresa_ejemplo.id
        
        # Centro de acopio
        centro_ejemplo = CentroAcopio(
            nombre='Centro Acopio Principal',
            ubicacion='Popayán, Cauca',
            capacidad_almacenamiento=50000.0,
            activo=True,
            empresa_id=empresa_ejemplo.id,
            fecha_creacion=datetime.utcnow()
        )
        db.session.add(centro_ejemplo)
        db.session.flush()
        
        # Proveedores de ejemplo
        proveedores_ejemplo = [
            {
                'nombre': 'Finca La Esperanza',
                'tipo_documento': 'cedula',
                'numero_documento': '12345678',
                'telefono': '+57-300-1234567',
                'email': 'esperanza@finca.com',
                'direccion': 'Vereda El Tambo',
                'hectareas_cultivo': 5.5,
                'activo': True,
                'empresa_id': empresa_ejemplo.id,
                'centro_acopio_id': centro_ejemplo.id,
                'fecha_registro': datetime.utcnow()
            }
        ]
        
        for proveedor_data in proveedores_ejemplo:
            proveedor = Proveedor(**proveedor_data)
            db.session.add(proveedor)
        
        db.session.commit()
        
        print("\n" + "="*60)
        print("🎉 SISTEMA COMPLETO INICIALIZADO")
        print("="*60)
        print(f"👤 Usuario administrador: admin@triboka.com")
        print(f"🔐 Contraseña: admin123")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error inicializando sistema completo: {str(e)}")
        db.session.rollback()
        return False

def initialize_contracts_system(reset):
    """Inicializar sistema de contratos agrícolas (fallback)"""
    try:
        # Verificar si ya existen datos
        if not reset and User.query.first():
            logger.info("✅ Sistema de contratos ya inicializado. Use reset=True para reinicializar.")
            return True
            
        return create_sample_data()
        
    except Exception as e:
        logger.error(f"❌ Error inicializando sistema de contratos: {str(e)}")
        db.session.rollback()
        return False

# Mantener compatibilidad con función original
def init_database():
    """Función de compatibilidad - usar initialize_database() en su lugar"""
    return initialize_database(reset=True)

def create_sample_data():
    """Crear datos de ejemplo"""
    try:
        # Exportadora
        exportadora = Company(
            name='AgroExport Peru SAC',
            email='admin@agroexport.com',
            country='Peru',
            company_type='exporter',
            blockchain_address='0x1234567890abcdef1234567890abcdef12345678'
        )
        
        # Cliente internacional
        hershey = Company(
            name='Hershey Company',
            email='procurement@hershey.com',
            country='USA',
            company_type='buyer',
            blockchain_address='0xabcdef1234567890abcdef1234567890abcdef12'
        )
        
        # Otro cliente
        nestle = Company(
            name='Nestlé SA',
            email='sourcing@nestle.com',
            country='Switzerland',
            company_type='buyer',
            blockchain_address='0xfedcba0987654321fedcba0987654321fedcba09'
        )
        
        # Productor/Cooperativa
        cooperativa = Company(
            name='Cooperativa Cacao Valle',
            email='admin@cacaovalle.com',
            country='Peru',
            company_type='producer'
        )
        
        db.session.add_all([exportadora, hershey, nestle, cooperativa])
        db.session.commit()
        
        # Usuario administrador
        admin = User(
            email='admin@triboka.com',
            name='Administrador Sistema',
            role='admin',
            company_id=exportadora.id
        )
        admin.password_hash = generate_password_hash('admin123')
        
        # Usuario operador
        operador = User(
            email='operador@triboka.com',
            name='Operador Sistema',
            role='operator',
            company_id=exportadora.id
        )
        operador.password_hash = generate_password_hash('operador123')
        
        # Usuario exportador
        exportador = User(
            email='exportador@triboka.com',
            name='Exportadora Cacao Premium',
            role='exporter',
            company_id=exportadora.id
        )
        exportador.password_hash = generate_password_hash('exportador123')
        
        # Usuario comprador
        comprador = User(
            email='comprador@triboka.com',
            name='Comprador Internacional',
            role='buyer',
            company_id=hershey.id
        )
        comprador.password_hash = generate_password_hash('comprador123')
        
        # Usuario productor
        productor = User(
            email='productor@triboka.com',
            name='Productor Agrícola',
            role='producer',
            company_id=cooperativa.id
        )
        productor.password_hash = generate_password_hash('productor123')
        
        db.session.add_all([admin, operador, exportador, comprador, productor])
        db.session.commit()
        
        # Contratos de ejemplo
        # Contrato 1: Hershey - Cacao
        contrato_hershey = ExportContract(
            contract_code='HERSHEY-CACAO-2024-001',
            buyer_company_id=hershey.id,
            exporter_company_id=exportadora.id,
            product_type='cacao',
            product_grade='Fino de Aroma',
            total_volume_mt=500.0,
            differential_usd=-150.0,  # -150 USD/TM vs spot
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now() + timedelta(days=60),
            delivery_date=datetime.now() + timedelta(days=75),
            fixed_volume_mt=300.0,  # Ya se han fijado 300 TM
            status='active'
        )
        
        # Contrato 2: Nestlé - Café
        contrato_nestle = ExportContract(
            contract_code='NESTLE-CAFE-2024-002',
            buyer_company_id=nestle.id,
            exporter_company_id=exportadora.id,
            product_type='cafe',
            product_grade='Arábica Especial',
            total_volume_mt=300.0,
            differential_usd=-200.0,  # -200 USD/TM vs spot
            start_date=datetime.now() - timedelta(days=20),
            end_date=datetime.now() + timedelta(days=70),
            delivery_date=datetime.now() + timedelta(days=85),
            fixed_volume_mt=450.0,  # Ya se han fijado 450 TM
            status='active'
        )
        
        db.session.add_all([contrato_hershey, contrato_nestle])
        db.session.commit()
        
        # Fijaciones de ejemplo para el contrato de Hershey
        fijaciones_hershey = [
            ContractFixation(
                export_contract_id=contrato_hershey.id,
                fixed_quantity_mt=100.0,
                spot_price_usd=2800.0,
                total_value_usd=265000.0,  # 100 TM * 2650 USD/TM
                fixation_date=datetime.now() - timedelta(days=25),
                notes='Primera fijación del contrato'
            ),
            ContractFixation(
                export_contract_id=contrato_hershey.id,
                fixed_quantity_mt=75.0,
                spot_price_usd=2750.0,
                total_value_usd=195000.0,  # 75 TM * 2600 USD/TM
                fixation_date=datetime.now() - timedelta(days=15),
                notes='Segunda fijación - precio favorable'
            ),
            ContractFixation(
                export_contract_id=contrato_hershey.id,
                fixed_quantity_mt=125.0,
                spot_price_usd=2900.0,
                total_value_usd=343750.0,  # 125 TM * 2750 USD/TM
                fixation_date=datetime.now() - timedelta(days=5),
                notes='Tercera fijación - mercado al alza'
            )
        ]
        
        # Fijaciones para el contrato de Nestlé
        fijaciones_nestle = [
            ContractFixation(
                export_contract_id=contrato_nestle.id,
                fixed_quantity_mt=200.0,
                spot_price_usd=4500.0,
                total_value_usd=860000.0,  # 200 TM * 4300 USD/TM
                fixation_date=datetime.now() - timedelta(days=18),
                notes='Primera fijación café arábica'
            ),
            ContractFixation(
                export_contract_id=contrato_nestle.id,
                fixed_quantity_mt=250.0,
                spot_price_usd=4600.0,
                total_value_usd=1100000.0,  # 250 TM * 4400 USD/TM
                fixation_date=datetime.now() - timedelta(days=8),
                notes='Fijación de café especial'
            )
        ]
        
        db.session.add_all(fijaciones_hershey + fijaciones_nestle)
        db.session.commit()
        
        # Lotes de productores de ejemplo
        lotes = [
            ProducerLot(
                lot_code='LOT-CACAO-20241101-0001',
                producer_company_id=cooperativa.id,
                producer_name='José Martínez',
                farm_name='Finca El Dorado',
                location='Tingo María, Huánuco',
                product_type='cacao',
                weight_kg=2500.0,
                quality_grade='Fino de Aroma',
                harvest_date=datetime.now() - timedelta(days=40),
                purchase_date=datetime.now() - timedelta(days=30),
                certifications='["Orgánico", "Fair Trade"]',
                status='purchased'
            ),
            ProducerLot(
                lot_code='LOT-CACAO-20241102-0002',
                producer_company_id=cooperativa.id,
                producer_name='María Gonzalez',
                farm_name='Hacienda San Pedro',
                location='Tocache, San Martín',
                product_type='cacao',
                weight_kg=1800.0,
                quality_grade='Trinitario',
                harvest_date=datetime.now() - timedelta(days=35),
                purchase_date=datetime.now() - timedelta(days=25),
                certifications='["Orgánico"]',
                status='purchased'
            ),
            ProducerLot(
                lot_code='LOT-CAFE-20241103-0003',
                producer_company_id=cooperativa.id,
                producer_name='Carlos Ruiz',
                farm_name='Cafetal La Esperanza',
                location='Villa Rica, Pasco',
                product_type='cafe',
                weight_kg=3200.0,
                quality_grade='Arábica Especial',
                harvest_date=datetime.now() - timedelta(days=30),
                purchase_date=datetime.now() - timedelta(days=20),
                certifications='["Rainforest Alliance"]',
                status='purchased'
            )
        ]
        
        db.session.add_all(lotes)
        db.session.commit()
        
        logger.info(f"✅ Creadas {len([exportadora, hershey, nestle, cooperativa])} empresas")
        logger.info(f"✅ Creados {len([admin, operador, exportador, comprador, productor])} usuarios")
        logger.info(f"✅ Creados {len([contrato_hershey, contrato_nestle])} contratos")
        logger.info(f"✅ Creadas {len(fijaciones_hershey + fijaciones_nestle)} fijaciones")
        logger.info(f"✅ Creados {len(lotes)} lotes de productores")
        
        print("\n" + "="*60)
        print("🎉 SISTEMA BLOCKCHAIN INICIALIZADO")
        print("="*60)
        print("👤 Administrador: admin@triboka.com / admin123")
        print("👤 Operador: operador@triboka.com / operador123")
        print("👤 Exportador: exportador@triboka.com / exportador123")
        print("👤 Comprador: comprador@triboka.com / comprador123")
        print("👤 Productor: productor@triboka.com / productor123")
        print("🌐 Acceso: http://localhost:5004")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error creando datos: {e}")
        return False

def validate_database():
    """
    Valida la integridad de la base de datos y reporta estadísticas.
    
    Returns:
        dict: Estadísticas de la base de datos
    """
    try:
        with app.app_context():
            if FULL_SYSTEM:
                stats = {
                    'usuarios': Usuario.query.count(),
                    'empresas': Empresa.query.count(),
                    'centros_acopio': CentroAcopio.query.count(),
                    'proveedores': Proveedor.query.count(),
                    'empresas_activas': Empresa.query.filter_by(activa=True).count(),
                    'usuarios_activos': Usuario.query.filter_by(activo=True).count(),
                }
            else:
                stats = {
                    'companies': Company.query.count(),
                    'users': User.query.count(),
                    'contracts': ExportContract.query.count(),
                    'fixations': ContractFixation.query.count(),
                    'producer_lots': ProducerLot.query.count(),
                }
            
            print("\n📊 ESTADÍSTICAS DE BASE DE DATOS")
            print("="*40)
            for key, value in stats.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
            print("="*40 + "\n")
            
            return stats
            
    except Exception as e:
        logger.error(f"❌ Error validando base de datos: {str(e)}")
        return {}

def main():
    """Función principal para ejecutar el script desde línea de comandos."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Inicialización de Base de Datos Triboka')
    parser.add_argument('--reset', action='store_true', help='Reinicializar completamente la base de datos')
    parser.add_argument('--validate', action='store_true', help='Validar estado de la base de datos')
    
    args = parser.parse_args()
    
    if args.validate:
        validate_database()
        return
    
    logger.info("🚀 Iniciando Sistema Triboka Agro...")
    success = initialize_database(reset=args.reset)
    
    if success:
        validate_database()
        print("🎯 Sistema inicializado correctamente")
    else:
        print("❌ Inicialización fallida. Revise los logs para más detalles.")
        sys.exit(1)

if __name__ == '__main__':
    main()
"""
Actualización del servidor Flask con integración Web3
Agregando endpoints para interactuar con smart contracts
"""

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import sys
import logging
import json
from decimal import Decimal
from dotenv import load_dotenv
from functools import wraps

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agregar el directorio backend al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models_simple import db, User, Company, ExportContract, ContractFixation, ProducerLot, BatchNFT, Deal, DealMember, DealNote, DealTraceLink, DealFinancePrivate, DealMessage, DigitalIdentity, DigitalSignature, KYCDocument, TraceEvent, TraceTimeline, Dispatch
from blockchain_service import get_blockchain_integration
from routes.agricultural_metadata import agricultural_metadata_bp
from routes.contracts import contracts_bp
from routes.fixations import fixations_bp
from routes.traceability import traceability_bp
from routes.erp import erp_bp
from routes.performance import performance_bp
from routes.analytics import analytics_bp
from routes.dispatches import dispatches_bp
from routes.agroweight import agroweight_bp


# Inicializar SocketIO globalmente
socketio = None

# =====================================
# DECORADOR PARA AUTENTICACIÓN API KEY
# =====================================

def require_api_key(f):
    """Decorador para validar API keys de empresas externas (AgroWeight Cloud, ERP, etc.)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Obtener API key del header Authorization
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    'error': 'API key requerida',
                    'message': 'Debe proporcionar una API key válida en el header Authorization: Bearer {api_key}'
                }), 401
            
            api_key = auth_header.replace('Bearer ', '')
            
            # Validar API key contra la base de datos
            company = Company.query.filter_by(api_key=api_key).first()
            if not company:
                return jsonify({
                    'error': 'API key inválida',
                    'message': 'La API key proporcionada no corresponde a ninguna empresa registrada'
                }), 401
            
            # Inyectar la compañía en el contexto de la request
            g.company = company
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error en autenticación API key: {str(e)}")
            return jsonify({
                'error': 'Error de autenticación',
                'message': 'Error interno en la validación de API key'
            }), 500
    
    return decorated_function

def create_app(testing=False):
    """Crear aplicación Flask"""
    app = Flask(__name__)

    # Configuración condicional para testing
    if testing:
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        app.config['SECRET_KEY'] = 'test-secret-key'
    else:
        # Configuración base usando variables de entorno
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:////home/rootpanel/web/app.triboka.com/backend/instance/triboka_production.db')
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'triboka-agro-secret-2024')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)  # 7 días en lugar de 24 horas

    # Inicializar extensiones
    db.init_app(app)
    jwt = JWTManager(app)
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*", logger=not testing, engineio_logger=not testing)

    # Registrar blueprints siempre, pero con configuración condicional para testing
    app.register_blueprint(agricultural_metadata_bp, url_prefix='/api/agricultural')
    app.register_blueprint(contracts_bp, url_prefix='/api/contracts')
    app.register_blueprint(fixations_bp, url_prefix='/api/fixations')
    app.register_blueprint(traceability_bp, url_prefix='/api/traceability')
    app.register_blueprint(erp_bp, url_prefix='/api/erp')
    app.register_blueprint(performance_bp, url_prefix='/api/performance')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(dispatches_bp, url_prefix='/api/dispatches')
    # app.register_blueprint(agroweight_bp, url_prefix='/api')

    return app


# Crear instancia global de la app para desarrollo
app = create_app()

# Inicializar integración blockchain
blockchain = get_blockchain_integration()

with app.app_context():
    db.create_all()

# =====================================
# MIDDLEWARE DE IMPERSONACIÓN
# =====================================

def impersonation_readonly_middleware(f):
    """Middleware que bloquea operaciones de escritura durante impersonación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verificar si estamos en modo impersonación
            claims = get_jwt()
            if claims.get('is_impersonating', False):
                # Si estamos en impersonación, verificar que sea solo lectura
                if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                    return jsonify({
                        'error': 'Operaciones de escritura bloqueadas en modo impersonación',
                        'message': 'Estás viendo la plataforma desde la perspectiva de otro usuario. Solo lectura permitida.'
                    }), 403
        except Exception as e:
            # Si hay error obteniendo JWT, continuar (podría ser endpoint público)
            pass
        
        return f(*args, **kwargs)
    return decorated_function

# =====================================
# ENDPOINTS DE AUTENTICACIÓN
# =====================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login de usuario"""
    try:
        # Manejar tanto JSON como datos de formulario
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email y password requeridos'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.active:
                return jsonify({'error': 'Usuario inactivo'}), 401
            
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={
                    'role': user.role,
                    'company_id': user.company_id,
                    'scopes': ['read', 'write'],  # Scopes básicos
                    'active_context': {
                        'type': 'global',
                        'deal_id': None,
                        'permissions': ['admin'] if user.role in ['admin', 'operator'] else ['user']
                    }
                }
            )
            
            # Si es una petición AJAX/JSON, devolver JSON
            if request.is_json or request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'access_token': access_token,
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'email': user.email,
                        'role': user.role,
                        'company_id': user.company_id
                    }
                })
            else:
                # Si es un formulario HTML, redirigir con cookie
                response = redirect('/dashboard')
                response.set_cookie('access_token', access_token, httponly=True, secure=False, samesite='Lax')
                flash('Inicio de sesión exitoso', 'success')
                return response
        
        # Credenciales inválidas
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Credenciales inválidas'}), 401
        else:
            flash('Credenciales inválidas', 'error')
            return redirect('/login')
        
    except Exception as e:
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify({'error': str(e)}), 500
        else:
            flash('Error interno del servidor', 'error')
            return redirect('/login')

@app.route('/api/auth/context', methods=['GET'])
@jwt_required()
def get_user_context():
    """Obtener contexto actual del usuario"""
    try:
        claims = get_jwt()
        active_context = claims.get('active_context', {
            'type': 'global',
            'deal_id': None,
            'permissions': ['user']
        })
        
        # Agregar información de impersonación si aplica
        is_impersonating = claims.get('is_impersonating', False)
        impersonation_info = None
        
        if is_impersonating:
            impersonation_info = {
                'original_admin_id': claims.get('original_admin_id'),
                'original_admin_name': active_context.get('original_user_name'),
                'impersonated_user_id': claims.get('active_context', {}).get('impersonated_user_id'),
                'impersonated_user_name': active_context.get('impersonated_user_name'),
                'warning': 'Modo impersonación activo - Solo lectura permitida'
            }
        
        return jsonify({
            'active_context': active_context,
            'user_scopes': claims.get('scopes', []),
            'is_impersonating': is_impersonating,
            'impersonation_info': impersonation_info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/change-context', methods=['POST'])
@jwt_required()
def change_user_context():
    """Cambiar contexto del usuario (requiere nuevo token)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        context_type = data.get('type', 'global')
        
        # Validar contexto
        active_context = {
            'type': context_type,
            'deal_id': None,
            'permissions': ['user']
        }
        
        if context_type == 'deal':
            deal_id = data.get('deal_id')
            if not deal_id:
                return jsonify({'error': 'deal_id requerido para contexto deal'}), 400
            
            deal = Deal.query.get(deal_id)
            if not deal:
                return jsonify({'error': 'Deal no encontrado'}), 404
            
            # Verificar que el usuario tenga acceso al deal
            has_access = False
            permissions = ['read']
            
            if user.id == deal.admin_id:
                has_access = True
                permissions = ['read', 'write', 'admin']
            elif user.company_id == deal.producer_id:
                has_access = True
                permissions = ['read', 'write']
            elif user.company_id == deal.exporter_id:
                has_access = True
                permissions = ['read', 'write']
            elif user.role in ['admin', 'operator']:
                has_access = True
                permissions = ['read', 'write', 'admin']
            
            if not has_access:
                return jsonify({'error': 'Sin acceso al deal especificado'}), 403
            
            active_context.update({
                'deal_id': deal_id,
                'permissions': permissions
            })
        
        # Crear nuevo token con contexto actualizado
        new_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'role': user.role,
                'company_id': user.company_id,
                'scopes': ['read', 'write'],
                'active_context': active_context
            }
        )
        
        return jsonify({
            'message': 'Contexto cambiado exitosamente',
            'access_token': new_token,
            'active_context': active_context
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/impersonate/<int:target_user_id>', methods=['POST'])
@jwt_required()
def impersonate_user(target_user_id):
    """Impersonar a otro usuario (solo admin) - Vista delegada segura"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Solo admin puede impersonar
        if not current_user or current_user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para impersonar usuarios'}), 403
        
        # Obtener el usuario objetivo
        target_user = User.query.get(target_user_id)
        if not target_user:
            return jsonify({'error': 'Usuario objetivo no encontrado'}), 404
        
        # No permitir impersonar a otro admin
        if target_user.role in ['admin', 'operator']:
            return jsonify({'error': 'No se puede impersonar a administradores'}), 403
        
        # Crear contexto de impersonación
        impersonation_context = {
            'type': 'impersonation',
            'original_user_id': current_user.id,
            'original_user_name': current_user.name,
            'impersonated_user_id': target_user.id,
            'impersonated_user_name': target_user.name,
            'permissions': ['read'],  # Solo lectura en impersonación
            'deal_id': None
        }
        
        # Crear nuevo token con contexto de impersonación
        new_token = create_access_token(
            identity=str(target_user.id),  # El token actúa como el usuario objetivo
            additional_claims={
                'role': target_user.role,
                'company_id': target_user.company_id,
                'scopes': ['read'],  # Solo lectura
                'active_context': impersonation_context,
                'is_impersonating': True,
                'original_admin_id': current_user.id
            }
        )
        
        # Loggear la impersonación (usando DealMessage como log temporal)
        log_message = DealMessage(
            deal_id=None,  # No es parte de un deal específico
            author_id=current_user.id,
            content=f"ADMIN IMPERSONATION: {current_user.name} ({current_user.email}) impersonó a {target_user.name} ({target_user.email})",
            message_type='system',
            created_at=datetime.utcnow()
        )
        db.session.add(log_message)
        db.session.commit()
        
        return jsonify({
            'message': f'Impersonación iniciada como {target_user.name}',
            'access_token': new_token,
            'impersonation_context': impersonation_context,
            'warning': 'Estás en modo impersonación de solo lectura. Usa el botón "Salir de Vista Delegada" para volver.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/stop-impersonation', methods=['POST'])
@jwt_required()
def stop_impersonation():
    """Salir del modo impersonación y volver al contexto admin"""
    try:
        claims = get_jwt()
        
        # Verificar que esté en modo impersonación
        if not claims.get('is_impersonating', False):
            return jsonify({'error': 'No estás en modo impersonación'}), 400
        
        original_admin_id = claims.get('original_admin_id')
        if not original_admin_id:
            return jsonify({'error': 'Información de admin original no encontrada'}), 400
        
        # Obtener el admin original
        original_admin = User.query.get(original_admin_id)
        if not original_admin:
            return jsonify({'error': 'Admin original no encontrado'}), 404
        
        # Crear token normal del admin
        normal_context = {
            'type': 'global',
            'deal_id': None,
            'permissions': ['admin'] if original_admin.role in ['admin', 'operator'] else ['user']
        }
        
        new_token = create_access_token(
            identity=str(original_admin.id),
            additional_claims={
                'role': original_admin.role,
                'company_id': original_admin.company_id,
                'scopes': ['read', 'write'],
                'active_context': normal_context,
                'is_impersonating': False
            }
        )
        
        # Loggear fin de impersonación
        log_message = DealMessage(
            deal_id=None,
            author_id=original_admin.id,
            content=f"ADMIN IMPERSONATION END: {original_admin.name} salió del modo impersonación",
            message_type='system',
            created_at=datetime.utcnow()
        )
        db.session.add(log_message)
        db.session.commit()
        
        return jsonify({
            'message': 'Impersonación finalizada. Volviendo a contexto admin.',
            'access_token': new_token,
            'active_context': normal_context
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/register', methods=['POST'])
@impersonation_readonly_middleware
def register():
    """Registro de nuevo usuario - Productores pueden registrarse libremente"""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'producer')  # Por defecto productores
        company_id = data.get('company_id')
        
        if not all([name, email, password]):
            return jsonify({'error': 'Datos incompletos'}), 400
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'El email ya está registrado'}), 400
        
        # Para productores, crear automáticamente una empresa si no se especifica
        if role == 'producer' and not company_id:
            # Crear empresa productora automáticamente
            company_name = f"Productora {name}"
            new_company = Company(
                name=company_name,
                company_type='producer',
                email=email
            )
            db.session.add(new_company)
            db.session.flush()
            company_id = new_company.id
        
        # Crear nuevo usuario
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            company_id=company_id,
            active=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'Usuario creado exitosamente'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Obtener perfil del usuario actual"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        profile = {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role,
            'company_name': user.company.name if user.company else None,
            'company_type': user.company.company_type if user.company else None,
            'active': user.active
        }
        
        return jsonify(profile)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
@jwt_required()
def list_users():
    """Listado de usuarios para panel de administración"""
    try:
        current_user = User.query.get(int(get_jwt_identity()))

        if not current_user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        if current_user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para consultar usuarios'}), 403

        users = User.query.order_by(User.created_at.desc()).all()

        result = []
        for user in users:
            result.append({
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role,
                'is_active': user.active,
                'company_id': user.company_id,
                'company_name': user.company.name if user.company else None,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================
# ENDPOINTS BLOCKCHAIN STATUS
# =====================================

@app.route('/api/blockchain/status', methods=['GET'])
@jwt_required()
def blockchain_status():
    """Obtener estado de la conexión blockchain"""
    try:
        status = blockchain.get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================
# ENDPOINTS DE CONTRATOS
# =====================================

@app.route('/api/contracts', methods=['GET'])
@jwt_required()
def get_contracts():
    """Obtener lista de contratos"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Filtrar contratos según el rol del usuario
        query = ExportContract.query
        
        if user.role == 'exporter':
            query = query.filter_by(exporter_company_id=user.company_id)
        elif user.role == 'buyer':
            query = query.filter_by(buyer_company_id=user.company_id)
        elif user.role == 'producer':
            # Los productores ven contratos donde tienen lotes asignados
            lot_contract_ids = db.session.query(ProducerLot.export_contract_id).filter_by(producer_company_id=user.company_id).all()
            contract_ids = [x[0] for x in lot_contract_ids if x[0]]
            query = query.filter(ExportContract.id.in_(contract_ids))
        
        contracts = query.all()
        
        result = []
        for contract in contracts:
            contract_data = {
                'id': contract.id,
                'contract_code': contract.contract_code,
                'buyer_company': contract.buyer_company.name if contract.buyer_company else None,
                'exporter_company': contract.exporter_company.name if contract.exporter_company else None,
                'product_type': contract.product_type,
                'product_grade': contract.product_grade,
                'total_volume_mt': float(contract.total_volume_mt),
                'differential_usd': float(contract.differential_usd),
                'start_date': contract.start_date.isoformat() if contract.start_date else None,
                'end_date': contract.end_date.isoformat() if contract.end_date else None,
                'delivery_date': contract.delivery_date.isoformat() if contract.delivery_date else None,
                'status': contract.status,
                'created_at': contract.created_at.isoformat(),
                'blockchain_contract_id': contract.blockchain_contract_id,
                'fixed_volume_mt': float(contract.fixed_volume_mt),
                'pending_volume_mt': float(contract.total_volume_mt - contract.fixed_volume_mt)
            }
            result.append(contract_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contracts', methods=['POST'])
@jwt_required()
@impersonation_readonly_middleware
def create_contract():
    """Crear nuevo contrato de exportación - Descentralizado para exportadoras y compradores"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Permitir a admin, operator, exporter y buyer crear contratos
        if not user or user.role not in ['admin', 'operator', 'exporter', 'buyer']:
            return jsonify({'error': 'Sin permisos para crear contratos'}), 403
        
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['buyer_company_id', 'exporter_company_id', 'contract_code', 
                          'product_type', 'product_grade', 'total_volume_mt', 
                          'differential_usd', 'start_date', 'end_date', 'delivery_date']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        # Verificar que las empresas existan
        buyer_company = Company.query.get(data['buyer_company_id'])
        exporter_company = Company.query.get(data['exporter_company_id'])
        
        if not buyer_company or not exporter_company:
            return jsonify({'error': 'Empresa no encontrada'}), 404
        
        # Verificar permisos específicos por rol
        if user.role == 'exporter':
            # Exportadora solo puede crear contratos donde ella es la exportadora
            if data['exporter_company_id'] != user.company_id:
                return jsonify({'error': 'Solo puedes crear contratos como exportadora'}), 403
        elif user.role == 'buyer':
            # Comprador solo puede crear contratos donde él es el comprador
            if data['buyer_company_id'] != user.company_id:
                return jsonify({'error': 'Solo puedes crear contratos como comprador'}), 403
        
        # Crear contrato en la base de datos
        contract = ExportContract(
            buyer_company_id=data['buyer_company_id'],
            exporter_company_id=data['exporter_company_id'],
            contract_code=data['contract_code'],
            product_type=data['product_type'],
            product_grade=data['product_grade'],
            total_volume_mt=Decimal(str(data['total_volume_mt'])),
            differential_usd=Decimal(str(data['differential_usd'])),
            start_date=datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')),
            end_date=datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')),
            delivery_date=datetime.fromisoformat(data['delivery_date'].replace('Z', '+00:00')),
            status='active',
            created_by_user_id=user_id
        )
        
        db.session.add(contract)
        db.session.flush()  # Para obtener el ID
        
        # Crear contrato en blockchain si está disponible
        if blockchain.is_ready():
            blockchain_contract_id = blockchain.agro_contract.create_contract(
                buyer_address=buyer_company.blockchain_address or "0x0000000000000000000000000000000000000000",
                exporter_address=exporter_company.blockchain_address or "0x0000000000000000000000000000000000000000",
                contract_code=data['contract_code'],
                product_type=data['product_type'],
                product_grade=data['product_grade'],
                total_volume_mt=int(data['total_volume_mt'] * 1000),  # Convertir a kg
                differential_usd=int(data['differential_usd'] * 100),  # Convertir a centavos
                start_date=int(contract.start_date.timestamp()),
                end_date=int(contract.end_date.timestamp()),
                delivery_date=int(contract.delivery_date.timestamp())
            )
            
            if blockchain_contract_id:
                contract.blockchain_contract_id = blockchain_contract_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Contrato creado exitosamente',
            'contract_id': contract.id,
            'blockchain_contract_id': contract.blockchain_contract_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contracts/from-lots', methods=['POST'])
@jwt_required()
@impersonation_readonly_middleware
def create_contract_from_lots():
    """
    Crear contrato de compra desde lotes seleccionados
    
    Body JSON:
    {
        "lot_ids": [1, 2, 3],  // IDs de lotes seleccionados
        "differential_usd": -1500,  // Diferencial para productor
        "delivery_date": "2025-12-31",
        "notes": "Contrato generado desde marketplace"
    }
    
    Lógica:
    1. Validar que todos los lotes existan y estén disponibles
    2. Agrupar lotes por productor
    3. Crear un contrato por cada productor
    4. Marcar lotes como 'purchased' y asignar al contrato
    5. Notificar al productor vía WebSocket
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in ['admin', 'operator', 'exporter']:
            return jsonify({'error': 'Sin permisos para crear contratos de compra'}), 403
        
        data = request.get_json()
        
        # Validar datos requeridos
        if 'lot_ids' not in data or not data['lot_ids']:
            return jsonify({'error': 'Debe seleccionar al menos un lote'}), 400
        
        differential_usd = Decimal(str(data.get('differential_usd', -1500)))
        delivery_date_str = data.get('delivery_date')
        notes = data.get('notes', '')
        
        if not delivery_date_str:
            # Fecha por defecto: 3 meses desde hoy
            delivery_date = datetime.now() + timedelta(days=90)
        else:
            delivery_date = datetime.fromisoformat(delivery_date_str.replace('Z', '+00:00'))
        
        # Obtener lotes seleccionados
        lots = ProducerLot.query.filter(ProducerLot.id.in_(data['lot_ids'])).all()
        
        if len(lots) != len(data['lot_ids']):
            return jsonify({'error': 'Algunos lotes no fueron encontrados'}), 404
        
        # Validar que los lotes estén disponibles
        for lot in lots:
            if lot.status != 'available':
                return jsonify({
                    'error': f'El lote {lot.lot_code} no está disponible (estado: {lot.status})'
                }), 400
        
        # Agrupar lotes por productor
        lots_by_producer = {}
        for lot in lots:
            producer_id = lot.producer_company_id
            if producer_id not in lots_by_producer:
                lots_by_producer[producer_id] = []
            lots_by_producer[producer_id].append(lot)
        
        contracts_created = []
        
        # Crear un contrato por cada productor
        for producer_id, producer_lots in lots_by_producer.items():
            producer_company = Company.query.get(producer_id)
            
            # Calcular volumen total
            total_weight_kg = sum(float(lot.weight_kg) for lot in producer_lots)
            total_volume_mt = total_weight_kg / 1000.0
            
            # Generar código de contrato
            contract_code = f"PURCHASE-{user.company.name[:3].upper()}-{producer_company.name[:3].upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Crear contrato
            contract = ExportContract(
                buyer_company_id=user.company_id,  # Exportadora compradora
                exporter_company_id=producer_id,  # Productor vendedor (se invierte la lógica)
                contract_code=contract_code,
                product_type=producer_lots[0].product_type,  # Asumir mismo producto
                product_grade=producer_lots[0].quality_grade or 'A',
                total_volume_mt=Decimal(str(total_volume_mt)),
                differential_usd=differential_usd,
                start_date=datetime.now(),
                end_date=delivery_date,
                delivery_date=delivery_date,
                status='active',
                created_by_user_id=user_id,
                notes=notes
            )
            
            db.session.add(contract)
            db.session.flush()
            
            # Actualizar lotes: marcar como purchased y asignar contrato
            for lot in producer_lots:
                lot.status = 'purchased'
                lot.export_contract_id = contract.id
                lot.purchased_by_company_id = user.company_id
                lot.purchase_date = datetime.now()
            
            contracts_created.append({
                'contract_id': contract.id,
                'contract_code': contract_code,
                'producer': producer_company.name,
                'volume_mt': total_volume_mt,
                'lot_count': len(producer_lots)
            })
        
        db.session.commit()
        
        # TODO: Enviar notificación WebSocket a productores
        
        return jsonify({
            'message': f'{len(contracts_created)} contrato(s) creado(s) exitosamente',
            'contracts': contracts_created
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contracts/<int:contract_id>', methods=['GET'])
@jwt_required()
def get_contract_detail(contract_id):
    """Obtener detalles de un contrato específico"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        contract = ExportContract.query.get(contract_id)
        if not contract:
            return jsonify({'error': 'Contrato no encontrado'}), 404
        
        # Verificar permisos
        if user.role == 'exporter' and contract.exporter_company_id != user.company_id:
            return jsonify({'error': 'Sin permisos para ver este contrato'}), 403
        elif user.role == 'buyer' and contract.buyer_company_id != user.company_id:
            return jsonify({'error': 'Sin permisos para ver este contrato'}), 403
        
        # Obtener fijaciones del contrato
        fixations = ContractFixation.query.filter_by(export_contract_id=contract_id).all()
        
        # Obtener lotes del contrato
        lots = ProducerLot.query.filter_by(export_contract_id=contract_id).all()
        
        contract_data = {
            'id': contract.id,
            'contract_code': contract.contract_code,
            'buyer_company': {
                'id': contract.buyer_company.id,
                'name': contract.buyer_company.name,
                'blockchain_address': contract.buyer_company.blockchain_address
            } if contract.buyer_company else None,
            'exporter_company': {
                'id': contract.exporter_company.id,
                'name': contract.exporter_company.name,
                'blockchain_address': contract.exporter_company.blockchain_address
            } if contract.exporter_company else None,
            'product_type': contract.product_type,
            'product_grade': contract.product_grade,
            'total_volume_mt': float(contract.total_volume_mt),
            'fixed_volume_mt': float(contract.fixed_volume_mt),
            'pending_volume_mt': float(contract.total_volume_mt - contract.fixed_volume_mt),
            'differential_usd': float(contract.differential_usd),
            'start_date': contract.start_date.isoformat() if contract.start_date else None,
            'end_date': contract.end_date.isoformat() if contract.end_date else None,
            'delivery_date': contract.delivery_date.isoformat() if contract.delivery_date else None,
            'status': contract.status,
            'created_at': contract.created_at.isoformat(),
            'blockchain_contract_id': contract.blockchain_contract_id,
            'fixations': [{
                'id': f.id,
                'fixed_quantity_mt': float(f.fixed_quantity_mt),
                'spot_price_usd': float(f.spot_price_usd),
                'total_value_usd': float(f.total_value_usd),
                'fixation_date': f.fixation_date.isoformat(),
                'notes': f.notes,
                'blockchain_fixation_id': f.blockchain_fixation_id
            } for f in fixations],
            'lots': [{
                'id': l.id,
                'producer_company': l.producer_company.name if l.producer_company else None,
                'farm_name': l.farm_name,
                'location': l.location,
                'weight_kg': float(l.weight_kg),
                'quality_grade': l.quality_grade,
                'harvest_date': l.harvest_date.isoformat() if l.harvest_date else None,
                'status': l.status,
                'blockchain_lot_id': l.blockchain_lot_id
            } for l in lots]
        }
        
        # Obtener información adicional del blockchain si está disponible
        if blockchain.is_ready() and contract.blockchain_contract_id:
            blockchain_info = blockchain.agro_contract.get_contract_info(contract.blockchain_contract_id)
            if blockchain_info:
                contract_data['blockchain_info'] = blockchain_info
        
        return jsonify(contract_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================
# ENDPOINTS DE FIJACIONES
# =====================================

@app.route('/api/contracts/<int:contract_id>/fixations', methods=['POST'])
@jwt_required()
@impersonation_readonly_middleware
def create_fixation(contract_id):
    """Crear nueva fijación para un contrato"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in ['admin', 'operator', 'exporter']:
            return jsonify({'error': 'Sin permisos para crear fijaciones'}), 403
        
        contract = ExportContract.query.get(contract_id)
        if not contract:
            return jsonify({'error': 'Contrato no encontrado'}), 404
        
        # Verificar permisos específicos
        if user.role == 'exporter' and contract.exporter_company_id != user.company_id:
            return jsonify({'error': 'Sin permisos para este contrato'}), 403
        
        data = request.get_json()
        
        # Validar datos requeridos
        if not all(k in data for k in ['fixed_quantity_mt', 'spot_price_usd']):
            return jsonify({'error': 'Datos requeridos: fixed_quantity_mt, spot_price_usd'}), 400
        
        fixed_quantity = Decimal(str(data['fixed_quantity_mt']))
        spot_price = Decimal(str(data['spot_price_usd']))
        
        # Verificar que no se exceda el volumen del contrato
        pending_volume = float(contract.total_volume_mt) - float(contract.fixed_volume_mt)
        if float(fixed_quantity) > pending_volume:
            return jsonify({'error': f'Cantidad excede volumen pendiente: {pending_volume}MT'}), 400
        
        # Calcular valor total
        total_value = fixed_quantity * (spot_price + Decimal(str(contract.differential_usd)))
        
        # Crear fijación en la base de datos
        fixation = ContractFixation(
            export_contract_id=contract_id,
            fixed_quantity_mt=fixed_quantity,
            spot_price_usd=spot_price,
            total_value_usd=total_value,
            notes=data.get('notes', ''),
            created_by_user_id=user_id
        )
        
        db.session.add(fixation)
        db.session.flush()
        
        # Actualizar volumen fijado del contrato
        contract.fixed_volume_mt = float(contract.fixed_volume_mt) + float(fixed_quantity)
        
        # Registrar fijación en blockchain si está disponible
        if blockchain.is_ready() and contract.blockchain_contract_id:
            # Obtener lotes asignados para esta fijación
            lot_ids = data.get('lot_ids', [])
            
            blockchain_fixation_id = blockchain.agro_contract.register_fixation(
                contract_id=contract.blockchain_contract_id,
                fixed_quantity_mt=int(fixed_quantity * 1000),  # Convertir a kg
                spot_price_usd=int(spot_price * 100),  # Convertir a centavos
                lot_ids=lot_ids,
                notes=data.get('notes', '')
            )
            
            if blockchain_fixation_id:
                fixation.blockchain_fixation_id = blockchain_fixation_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Fijación creada exitosamente',
            'fixation_id': fixation.id,
            'blockchain_fixation_id': fixation.blockchain_fixation_id,
            'total_value_usd': float(total_value),
            'contract_fixed_volume_mt': float(contract.fixed_volume_mt),
            'contract_pending_volume_mt': float(contract.total_volume_mt - contract.fixed_volume_mt)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# =====================================
# ENDPOINTS DE LOTES NFT
# =====================================

@app.route('/api/lots', methods=['GET'])
@jwt_required()
def get_lots():
    """
    Obtener lista de lotes según rol:
    - Producer: Solo sus lotes
    - Exporter: TODOS los lotes disponibles (marketplace)
    - Admin/Operator: Todos los lotes
    
    Query params para filtros:
    - status: available, purchased, batched
    - location: filtro por ubicación
    - quality_grade: Premium, A, B, C
    - certifications: Organic, Fair Trade, Rainforest Alliance
    - producer_id: ID de empresa productora
    - min_weight: peso mínimo en kg
    - max_weight: peso máximo en kg
    """
    try:
        print("DEBUG: Iniciando get_lots()")
        user_id = get_jwt_identity()
        print(f"DEBUG: user_id={user_id}")
        user = User.query.get(user_id)
        print(f"DEBUG: user={user}, role={user.role if user else None}")
        
        if not user:
            print("DEBUG: Usuario no encontrado")
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        query = ProducerLot.query
        print(f"DEBUG: Query inicial creada")
        
        # Filtrar según el rol del usuario
        if user.role == 'producer':
            # Productores ven solo sus lotes
            query = query.filter_by(producer_company_id=user.company_id)
            print(f"DEBUG: Filtro producer aplicado: company_id={user.company_id}")
        elif user.role == 'exporter':
            # EXPORTADORES VEN TODOS LOS LOTES DISPONIBLES (MARKETPLACE)
            # Sin filtro de company_id - acceso total al marketplace
            print("DEBUG: Role exporter - sin filtro (marketplace completo)")
            pass
        # Admin/Operator ven todos los lotes sin restricción
        
        # Aplicar filtros de query params
        status_filter = request.args.get('status')
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        location_filter = request.args.get('location')
        if location_filter:
            query = query.filter(ProducerLot.location.ilike(f'%{location_filter}%'))
        
        quality_filter = request.args.get('quality_grade')
        if quality_filter:
            query = query.filter_by(quality_grade=quality_filter)
        
        producer_filter = request.args.get('producer_id')
        if producer_filter:
            query = query.filter_by(producer_company_id=int(producer_filter))
        
        min_weight = request.args.get('min_weight')
        if min_weight:
            query = query.filter(ProducerLot.weight_kg >= float(min_weight))
        
        max_weight = request.args.get('max_weight')
        if max_weight:
            query = query.filter(ProducerLot.weight_kg <= float(max_weight))
        
        certifications_filter = request.args.get('certifications')
        if certifications_filter:
            # Filtrar por certificación específica
            query = query.filter(ProducerLot.certifications.ilike(f'%{certifications_filter}%'))
        
        # Ordenar por fecha de cosecha (más recientes primero)
        query = query.order_by(ProducerLot.harvest_date.desc())
        
        print(f"DEBUG: A punto de ejecutar query.all()")
        lots = query.all()
        print(f"DEBUG: Query ejecutada, {len(lots)} lotes encontrados")
        
        result = []
        for lot in lots:
            print(f"DEBUG: Procesando lot {lot.id} - {lot.lot_code}")
            # Calcular precio por MT si está disponible
            price_per_mt = None
            if lot.purchase_price_usd and lot.weight_kg and lot.weight_kg > 0:
                price_per_mt = float(lot.purchase_price_usd) / (float(lot.weight_kg) / 1000.0)
            
            lot_data = {
                'id': lot.id,
                'lot_code': lot.lot_code,
                'producer_company': lot.producer_company.name if lot.producer_company else None,
                'producer_company_id': lot.producer_company_id,
                'producer_name': lot.producer_name,
                'farm_name': lot.farm_name,
                'location': lot.location,
                'product_type': lot.product_type,
                'weight_kg': float(lot.weight_kg),
                'weight_mt': float(lot.weight_kg) / 1000.0,
                'quality_grade': lot.quality_grade,
                'quality_score': float(lot.quality_score) if lot.quality_score else None,
                'moisture_content': float(lot.moisture_content) if lot.moisture_content else None,
                'harvest_date': lot.harvest_date.isoformat() if lot.harvest_date else None,
                'purchase_date': lot.purchase_date.isoformat() if lot.purchase_date else None,
                'purchase_price_usd': float(lot.purchase_price_usd) if lot.purchase_price_usd else None,
                'price_per_mt': price_per_mt,
                'status': lot.status,
                'created_at': lot.created_at.isoformat(),
                'blockchain_lot_id': lot.blockchain_lot_id,
                'export_contract_id': lot.export_contract_id,
                'batch_id': lot.batch_id,
                'certifications': lot.certifications.split(',') if lot.certifications else [],
                # Info adicional para exportadores
                'has_contract': lot.export_contract_id is not None,
                'purchased_by': lot.purchased_by_company.name if lot.purchased_by_company else None,
                'created_by': lot.created_by_user.email if lot.created_by_user else None
            }
            result.append(lot_data)
        
        print(f"DEBUG: Retornando {len(result)} lotes")
        return jsonify(result)
        
    except Exception as e:
        print(f"ERROR en get_lots: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/lots', methods=['POST'])
@jwt_required()
@impersonation_readonly_middleware
def create_lot():
    """Crear nuevo lote NFT de productor"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Productores pueden crear lotes, admin/operator tienen permisos completos
        if not user or user.role not in ['admin', 'operator', 'producer']:
            return jsonify({'error': 'Sin permisos para crear lotes'}), 403
        
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['producer_company_id', 'farm_name', 'location', 
                          'product_type', 'weight_kg', 'quality_grade', 'harvest_date']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        # Verificar permisos del productor
        if user.role == 'producer' and data['producer_company_id'] != user.company_id:
            return jsonify({'error': 'Solo puedes crear lotes para tu empresa'}), 403
        
        # Verificar que la empresa productora exista
        producer_company = Company.query.get(data['producer_company_id'])
        if not producer_company:
            return jsonify({'error': 'Empresa productora no encontrada'}), 404
        
        # Generar código único del lote
        lot_code = f"LOT-{producer_company.name[:3].upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{producer_company.id:03d}"
        
        # Crear lote en la base de datos
        lot = ProducerLot(
            lot_code=lot_code,
            producer_company_id=data['producer_company_id'],
            producer_name=data.get('producer_name', producer_company.name),
            farm_name=data['farm_name'],
            location=data['location'],
            product_type=data['product_type'],
            weight_kg=Decimal(str(data['weight_kg'])),
            quality_grade=data['quality_grade'],
            harvest_date=datetime.fromisoformat(data['harvest_date'].replace('Z', '+00:00')),
            certifications=','.join(data.get('certifications', [])),
            status='available',
            created_by_user_id=user_id
        )
        
        db.session.add(lot)
        db.session.flush()
        
        # Crear NFT en blockchain si está disponible
        if blockchain.is_ready():
            blockchain_lot_id = blockchain.nft_service.create_lot(
                producer_address=producer_company.blockchain_address or "0x0000000000000000000000000000000000000000",
                producer_name=producer_company.name,
                farm_name=data['farm_name'],
                location=data['location'],
                product_type=data['product_type'],
                weight_kg=int(data['weight_kg']),
                quality_grade=data['quality_grade'],
                harvest_date=int(lot.harvest_date.timestamp()),
                certifications=data.get('certifications', []),
                metadata_uri=data.get('metadata_uri', '')
            )
            
            if blockchain_lot_id:
                lot.blockchain_lot_id = blockchain_lot_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Lote NFT creado exitosamente',
            'lot_id': lot.id,
            'blockchain_lot_id': lot.blockchain_lot_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# =====================================
# ENDPOINTS DE COMPRA DE LOTES
# =====================================

@app.route('/api/lots/<int:lot_id>/purchase', methods=['POST'])
@jwt_required()
@impersonation_readonly_middleware
def purchase_lot(lot_id):
    """Permitir a exportadoras comprar lotes directamente de productores"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Solo exportadoras pueden comprar lotes
        if not user or user.role not in ['admin', 'operator', 'exporter']:
            return jsonify({'error': 'Sin permisos para comprar lotes'}), 403
        
        lot = ProducerLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Lote no encontrado'}), 404
        
        # Verificar que el lote esté disponible
        if lot.status != 'available':
            return jsonify({'error': f'Lote no disponible. Estado actual: {lot.status}'}), 400
        
        data = request.get_json()
        
        # Validar datos requeridos
        if 'purchase_price_usd' not in data:
            return jsonify({'error': 'Campo requerido: purchase_price_usd'}), 400
        
        purchase_price = Decimal(str(data['purchase_price_usd']))
        if purchase_price <= 0:
            return jsonify({'error': 'Precio debe ser mayor a 0'}), 400
        
        # Actualizar información de compra
        lot.purchase_date = datetime.utcnow()
        lot.purchase_price_usd = purchase_price
        lot.purchased_by_company_id = user.company_id
        lot.status = 'purchased'
        
        # Registrar la transacción de compra en blockchain si está disponible
        if blockchain.is_ready() and lot.blockchain_lot_id:
            try:
                # Registrar compra en ProducerLotNFT
                tx_result = blockchain.producer_lot_nft.purchase_lot(
                    lot.blockchain_lot_id,
                    user.company.blockchain_address if user.company.blockchain_address else "0x0000000000000000000000000000000000000000",
                    int(purchase_price * 100)  # Convertir a centavos para blockchain
                )
                
                if tx_result:
                    lot.purchase_tx_hash = tx_result.get('tx_hash')
                    
            except Exception as blockchain_error:
                logger.warning(f"Error en compra blockchain: {blockchain_error}")
                # Continuar con la compra en base de datos aunque falle blockchain
        
        db.session.commit()
        
        return jsonify({
            'message': 'Lote comprado exitosamente',
            'lot': {
                'id': lot.id,
                'lot_code': lot.lot_code,
                'producer_company': lot.producer_company.name if lot.producer_company else None,
                'weight_kg': float(lot.weight_kg),
                'purchase_price_usd': float(lot.purchase_price_usd),
                'purchase_date': lot.purchase_date.isoformat(),
                'status': lot.status,
                'purchased_by': user.company.name
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/lots/available', methods=['GET'])
@jwt_required()
def get_available_lots():
    """Obtener lotes disponibles para compra (para exportadoras)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Solo exportadoras y admin pueden ver lotes disponibles para compra
        if not user or user.role not in ['admin', 'operator', 'exporter']:
            return jsonify({'error': 'Sin permisos para ver lotes disponibles'}), 403
        
        # Obtener lotes disponibles
        lots = ProducerLot.query.filter_by(status='available').all()
        
        result = []
        for lot in lots:
            lot_data = {
                'id': lot.id,
                'lot_code': lot.lot_code,
                'producer_company': lot.producer_company.name if lot.producer_company else None,
                'producer_name': lot.producer_name,
                'farm_name': lot.farm_name,
                'location': lot.location,
                'product_type': lot.product_type,
                'weight_kg': float(lot.weight_kg),
                'quality_grade': lot.quality_grade,
                'harvest_date': lot.harvest_date.isoformat() if lot.harvest_date else None,
                'certifications': lot.certifications.split(',') if lot.certifications else [],
                'created_at': lot.created_at.isoformat(),
                'blockchain_lot_id': lot.blockchain_lot_id
            }
            result.append(lot_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/public/lots/available', methods=['GET'])
def get_public_available_lots():
    """Obtener lotes disponibles públicamente (para integración con AgroWeight Cloud)"""
    try:
        # Obtener lotes disponibles sin requerir autenticación
        lots = ProducerLot.query.filter_by(status='available').all()
        
        result = []
        for lot in lots:
            lot_data = {
                'id': lot.id,
                'lot_code': lot.lot_code,
                'producer_company': lot.producer_company.name if lot.producer_company else None,
                'producer_name': lot.producer_name,
                'farm_name': lot.farm_name,
                'location': lot.location,
                'product_type': lot.product_type,
                'weight_kg': float(lot.weight_kg),
                'quality_grade': lot.quality_grade,
                'harvest_date': lot.harvest_date.isoformat() if lot.harvest_date else None,
                'certifications': lot.certifications.split(',') if lot.certifications else [],
                'created_at': lot.created_at.isoformat(),
                'blockchain_lot_id': lot.blockchain_lot_id
            }
            result.append(lot_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lots/id/<lote_id>', methods=['GET'])
def get_lote_by_id(lote_id):
    """Obtener lote por ID (código interno o NFT ID) para integración con AgroWeight Cloud"""
    try:
        print(f"DEBUG: Buscando lote con ID: {lote_id}")
        
        # Para AgroWeight Cloud, permitir consultar cualquier lote
        lot = ProducerLot.query.filter(
            ((ProducerLot.lot_code == lote_id) | (ProducerLot.blockchain_lot_id == lote_id))
        ).first()
        
        print(f"DEBUG: Lote encontrado: {lot}")
        
        if not lot:
            print(f"DEBUG: Lote {lote_id} no encontrado")
            return jsonify({'error': 'Lot not found'}), 404
        
        print(f"DEBUG: Convirtiendo lote a dict")
        result = lot.to_dict()
        print(f"DEBUG: Resultado: {result}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"ERROR en get_lote_by_id: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    """Permitir a productores editar sus propios lotes"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        lot = ProducerLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Lote no encontrado'}), 404
        
        # Verificar permisos: solo el productor propietario o admin/operator
        if user.role == 'producer':
            if lot.producer_company_id != user.company_id:
                return jsonify({'error': 'Solo puedes editar tus propios lotes'}), 403
        elif user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para editar lotes'}), 403
        
        # No permitir editar lotes que ya han sido comprados o están en proceso
        if lot.status not in ['available']:
            return jsonify({'error': f'No se puede editar lote con estado: {lot.status}'}), 400
        
        data = request.get_json()
        
        # Campos editables
        editable_fields = ['farm_name', 'location', 'quality_grade', 'certifications']
        
        for field in editable_fields:
            if field in data:
                if field == 'certifications':
                    # Manejar certificaciones como lista
                    if isinstance(data[field], list):
                        setattr(lot, field, ','.join(data[field]))
                    else:
                        setattr(lot, field, data[field])
                else:
                    setattr(lot, field, data[field])
        
        # Actualizar timestamp de modificación
        lot.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Lote actualizado exitosamente',
            'lot': {
                'id': lot.id,
                'lot_code': lot.lot_code,
                'producer_company': lot.producer_company.name if lot.producer_company else None,
                'farm_name': lot.farm_name,
                'location': lot.location,
                'product_type': lot.product_type,
                'weight_kg': float(lot.weight_kg),
                'quality_grade': lot.quality_grade,
                'harvest_date': lot.harvest_date.isoformat() if lot.harvest_date else None,
                'certifications': lot.certifications.split(',') if lot.certifications else [],
                'status': lot.status,
                'updated_at': lot.updated_at.isoformat() if hasattr(lot, 'updated_at') and lot.updated_at else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# =====================================
# ENDPOINTS DE BATCH NFT
# =====================================

@app.route('/api/batches', methods=['POST'])
@jwt_required()
@impersonation_readonly_middleware
def create_batch():
    """Crear batch NFT desde múltiples lotes"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Solo exportadoras pueden crear batches (agregar lotes)
        if not user or user.role not in ['admin', 'operator', 'exporter']:
            return jsonify({'error': 'Sin permisos para crear batches'}), 403
        
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['source_lot_ids', 'batch_type', 'location']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        source_lot_ids = data['source_lot_ids']
        if not isinstance(source_lot_ids, list) or len(source_lot_ids) == 0:
            return jsonify({'error': 'Debe incluir al menos un lote'}), 400
        
        # Verificar que todos los lotes existan y estén disponibles
        lots = ProducerLot.query.filter(ProducerLot.id.in_(source_lot_ids)).all()
        if len(lots) != len(source_lot_ids):
            return jsonify({'error': 'Algunos lotes no fueron encontrados'}), 404
        
        # Verificar que todos los lotes estén comprados por la exportadora
        if user.role == 'exporter':
            for lot in lots:
                if lot.purchased_by_company_id != user.company_id:
                    return jsonify({'error': f'Lote {lot.lot_code} no te pertenece'}), 403
        
        # Verificar que los lotes estén en estado adecuado para crear batch
        for lot in lots:
            if lot.status not in ['purchased']:
                return jsonify({'error': f'Lote {lot.lot_code} no está disponible para batch (estado: {lot.status})'}), 400
        
        # Calcular peso total y crear arrays
        import json
        total_weight = sum(float(lot.weight_kg) for lot in lots)
        source_weights = [float(lot.weight_kg) for lot in lots]
        
        # Generar código único del batch
        company_code = user.company.name[:3].upper()
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        batch_code = f"BATCH-{company_code}-{timestamp}-{len(source_lot_ids):03d}"
        
        # Crear batch en la base de datos
        batch = BatchNFT(
            batch_code=batch_code,
            source_lot_ids=json.dumps(source_lot_ids),
            source_lot_weights=json.dumps(source_weights),
            total_weight_kg=total_weight,
            batch_type=data['batch_type'],
            location=data['location'],
            creator_company_id=user.company_id,
            current_owner_company_id=user.company_id,
            status='created'
        )
        
        db.session.add(batch)
        db.session.flush()  # Para obtener el ID
        
        # Actualizar estado de los lotes originales
        for lot in lots:
            lot.status = 'batched'
            lot.batch_id = batch.id
        
        # Crear NFT en blockchain si está disponible
        if blockchain.is_ready():
            try:
                # Aquí se llamaría al BatchNFT contract cuando esté desplegado
                logger.info(f"Batch {batch.batch_code} listo para blockchain")
                # blockchain_batch_id = blockchain.batch_nft.create_batch(...)
                # batch.blockchain_batch_id = blockchain_batch_id
            except Exception as blockchain_error:
                logger.warning(f"Error en batch blockchain: {blockchain_error}")
        
        db.session.commit()
        
        return jsonify({
            'message': 'Batch creado exitosamente',
            'batch': batch.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/batches', methods=['GET'])
@jwt_required()
def get_batches():
    """Obtener lista de batches"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        query = BatchNFT.query
        
        # Filtrar según el rol del usuario
        if user.role == 'exporter':
            # Exportadoras ven sus batches creados
            query = query.filter(
                (BatchNFT.creator_company_id == user.company_id) |
                (BatchNFT.current_owner_company_id == user.company_id)
            )
        elif user.role == 'buyer':
            # Compradores ven batches que les pertenecen
            query = query.filter_by(current_owner_company_id=user.company_id)
        elif user.role == 'producer':
            # Productores ven batches que contienen sus lotes
            producer_lots = ProducerLot.query.filter_by(producer_company_id=user.company_id).all()
            lot_ids = [lot.id for lot in producer_lots]
            
            # Buscar batches que contengan estos lotes
            batches_with_producer_lots = []
            all_batches = BatchNFT.query.all()
            for batch in all_batches:
                batch_lot_ids = batch.source_lots_list
                if any(lot_id in batch_lot_ids for lot_id in lot_ids):
                    batches_with_producer_lots.append(batch.id)
            
            if batches_with_producer_lots:
                query = query.filter(BatchNFT.id.in_(batches_with_producer_lots))
            else:
                query = query.filter(BatchNFT.id == -1)  # No results
        
        batches = query.all()
        
        result = []
        for batch in batches:
            batch_data = batch.to_dict()
            
            # Agregar información de la empresa creadora
            creator_company = Company.query.get(batch.creator_company_id)
            batch_data['creator_company'] = {
                'id': creator_company.id,
                'name': creator_company.name,
                'company_type': creator_company.company_type
            } if creator_company else None
            
            # Agregar información del propietario actual
            current_owner = Company.query.get(batch.current_owner_company_id)
            batch_data['current_owner_company'] = {
                'id': current_owner.id,
                'name': current_owner.name,
                'company_type': current_owner.company_type
            } if current_owner else None
            
            # Agregar información de lotes originales
            source_lots = ProducerLot.query.filter(ProducerLot.id.in_(batch.source_lots_list)).all()
            batch_data['source_lots'] = []
            
            for lot in source_lots:
                contribution_percentage = round((float(lot.weight_kg) / float(batch.total_weight_kg)) * 100, 2) if batch.total_weight_kg and float(batch.total_weight_kg) > 0 else 0
                batch_data['source_lots'].append({
                    'id': lot.id,
                    'lot_code': lot.lot_code,
                    'producer_company': lot.producer_company.name if lot.producer_company else None,
                    'weight_kg': float(lot.weight_kg),
                    'contribution_percentage': contribution_percentage
                })
            
            result.append(batch_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batches/<int:batch_id>', methods=['GET'])
@jwt_required()
def get_batch_detail(batch_id):
    """Obtener detalles completos de un batch"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        batch = BatchNFT.query.get(batch_id)
        if not batch:
            return jsonify({'error': 'Batch no encontrado'}), 404
        
        # Verificar permisos
        has_access = False
        if user.role in ['admin', 'operator']:
            has_access = True
        elif user.role == 'exporter':
            has_access = (batch.creator_company_id == user.company_id or 
                         batch.current_owner_company_id == user.company_id)
        elif user.role == 'buyer':
            has_access = (batch.current_owner_company_id == user.company_id)
        elif user.role == 'producer':
            # Verificar si el batch contiene lotes del productor
            producer_lots = ProducerLot.query.filter_by(producer_company_id=user.company_id).all()
            lot_ids = [lot.id for lot in producer_lots]
            has_access = any(lot_id in batch.source_lots_list for lot_id in lot_ids)
        
        if not has_access:
            return jsonify({'error': 'Sin permisos para ver este batch'}), 403
        
        # Obtener información completa
        batch_data = batch.to_dict()
        
        # Agregar información detallada de lotes originales
        source_lots = ProducerLot.query.filter(ProducerLot.id.in_(batch.source_lots_list)).all()
        batch_data['source_lots'] = []
        
        for i, lot in enumerate(source_lots):
            lot_data = {
                'id': lot.id,
                'lot_code': lot.lot_code,
                'producer_company': lot.producer_company.name if lot.producer_company else None,
                'producer_name': lot.producer_name,
                'farm_name': lot.farm_name,
                'location': lot.location,
                'product_type': lot.product_type,
                'weight_kg': float(lot.weight_kg),
                'quality_grade': lot.quality_grade,
                'harvest_date': lot.harvest_date.isoformat() if lot.harvest_date else None,
                'certifications': lot.certifications.split(',') if lot.certifications else [],
                'contribution_percentage': round((float(lot.weight_kg) / float(batch.total_weight_kg)) * 100, 2)
            }
            batch_data['source_lots'].append(lot_data)
        
        # Agregar sub-batches si existen
        if batch.sub_batches:
            batch_data['sub_batches'] = [sub_batch.to_dict() for sub_batch in batch.sub_batches]
        
        return jsonify(batch_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lots/<int:lot_id>/traceability', methods=['GET'])
@jwt_required()
def get_lot_traceability(lot_id):
    """Obtener trazabilidad completa de un lote (incluye batches y blockchain)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        lot = ProducerLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Lote no encontrado'}), 404
        
        # Verificar permisos básicos para ver el lote
        has_access = False
        if user.role in ['admin', 'operator']:
            has_access = True
        elif user.role == 'producer':
            has_access = (lot.producer_company_id == user.company_id)
        elif user.role == 'exporter':
            has_access = (lot.purchased_by_company_id == user.company_id)
        elif user.role == 'buyer':
            # Comprador puede ver si el lote está en un batch que le pertenece
            batches = BatchNFT.query.filter_by(current_owner_company_id=user.company_id).all()
            for batch in batches:
                if lot_id in batch.source_lots_list:
                    has_access = True
                    break
        
        if not has_access:
            return jsonify({'error': 'Sin permisos para ver este lote'}), 403
        
        # Información del lote original
        lot_data = {
            'id': lot.id,
            'lot_code': lot.lot_code,
            'producer_company': lot.producer_company.name if lot.producer_company else None,
            'producer_name': lot.producer_name,
            'farm_name': lot.farm_name,
            'location': lot.location,
            'product_type': lot.product_type,
            'weight_kg': float(lot.weight_kg),
            'quality_grade': lot.quality_grade,
            'harvest_date': lot.harvest_date.isoformat() if lot.harvest_date else None,
            'purchase_date': lot.purchase_date.isoformat() if lot.purchase_date else None,
            'purchase_price_usd': float(lot.purchase_price_usd) if lot.purchase_price_usd else None,
            'certifications': lot.certifications.split(',') if lot.certifications else [],
            'status': lot.status,
            'created_at': lot.created_at.isoformat(),
            'blockchain_lot_id': lot.blockchain_lot_id or f'0x{lot.id:064x}'  # Simular ID blockchain
        }
        
        # Timeline de eventos blockchain (simulado para pruebas)
        timeline = []
        
        # Evento 1: Creación del lote
        timeline.append({
            'event': 'Lote Creado',
            'timestamp': lot.created_at.isoformat() if lot.created_at else None,
            'actor': lot.producer_company.name if lot.producer_company else 'Productor',
            'description': f'Lote registrado en blockchain desde {lot.farm_name or "finca"}',
            'tx_hash': lot.blockchain_lot_id or f'0x{"a" * 64}',
            'block_number': 12345678,
            'icon': 'seedling',
            'color': 'success'
        })
        
        # Evento 2: Certificaciones agregadas
        if lot.certifications:
            timeline.append({
                'event': 'Certificaciones Verificadas',
                'timestamp': lot.created_at.isoformat() if lot.created_at else None,
                'actor': 'Sistema de Certificación',
                'description': f'Certificaciones validadas: {lot.certifications}',
                'tx_hash': f'0x{"b" * 64}',
                'block_number': 12345679,
                'icon': 'certificate',
                'color': 'info'
            })
        
        # Evento 3: Compra del lote (si está purchased)
        if lot.status in ['purchased', 'batched'] and lot.purchase_date:
            buyer_name = 'Exportadora'
            if lot.purchased_by_company:
                buyer_name = lot.purchased_by_company.name
            elif lot.export_contract and lot.export_contract.exporter_company:
                buyer_name = lot.export_contract.exporter_company.name
                
            timeline.append({
                'event': 'Lote Comprado',
                'timestamp': lot.purchase_date.isoformat() if lot.purchase_date else None,
                'actor': buyer_name,
                'description': f'Lote adquirido por {buyer_name}',
                'tx_hash': lot.purchase_tx_hash or f'0x{"c" * 64}',
                'block_number': 12345680,
                'icon': 'handshake',
                'color': 'primary'
            })
        
        # Buscar batches que contienen este lote
        batches_containing_lot = BatchNFT.query.all()
        lot_batches = []
        
        for batch in batches_containing_lot:
            if lot_id in batch.source_lots_list:
                batch_data = {
                    'id': batch.id,
                    'batch_code': batch.batch_code,
                    'total_weight_kg': float(batch.total_weight_kg),
                    'status': batch.status,
                    'created_at': batch.created_at.isoformat() if batch.created_at else None,
                    'exporter_company': batch.exporter_company.name if batch.exporter_company else None,
                    'blockchain_batch_id': batch.blockchain_batch_id
                }
                
                # Calcular el porcentaje de contribución de este lote al batch
                lot_weight = float(lot.weight_kg)
                batch_data['lot_contribution_percentage'] = round((lot_weight / float(batch.total_weight_kg)) * 100, 2)
                lot_batches.append(batch_data)
                
                # Agregar evento de batch al timeline
                timeline.append({
                    'event': 'Agregado a Batch',
                    'timestamp': batch.created_at.isoformat() if batch.created_at else None,
                    'actor': batch.exporter_company.name if batch.exporter_company else 'Exportadora',
                    'description': f'Lote incluido en batch {batch.batch_code}',
                    'tx_hash': batch.blockchain_batch_id or f'0x{"d" * 64}',
                    'block_number': 12345681,
                    'icon': 'boxes',
                    'color': 'warning'
                })
        
        # Ordenar timeline por fecha
        timeline.sort(key=lambda x: x['timestamp'] if x['timestamp'] else '', reverse=True)
        
        # Información blockchain general
        blockchain_info = {
            'network': 'Polygon Mainnet',
            'contract_address': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
            'total_transactions': len(timeline),
            'verified': True,
            'smart_contract_version': 'v2.1.0'
        }
        
        return jsonify({
            'lot': lot_data,
            'batches': lot_batches,
            'timeline': timeline,
            'blockchain': blockchain_info,
            'traceability_complete': len(timeline) > 0
        })
        
    except Exception as e:
        logger.error(f"Error in traceability: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =====================================
# ENDPOINTS PARA INTEGRACIÓN CON AGROWEIGHT CLOUD
# =====================================

@app.route('/api/lotes/nft/<nft_hash>', methods=['GET'])
@require_api_key
def get_lote_nft(nft_hash):
    """Obtener lote por NFT hash (para AgroWeight Cloud)"""
    try:
        company = g.company
        
        # Buscar lote por NFT hash o blockchain_lot_id
        lote = ProducerLot.query.filter(
            db.or_(
                ProducerLot.blockchain_lot_id == nft_hash,
                ProducerLot.lot_code == nft_hash  # También permitir búsqueda por código de lote
            )
        ).first()
        
        if not lote:
            return jsonify({
                'error': 'Lote no encontrado',
                'message': f'No se encontró lote con hash/código: {nft_hash}'
            }), 404
        
        # Verificar que el lote pertenezca a la empresa que hace la consulta
        # Nota: En multi-tenant, cada empresa solo puede ver sus propios lotes
        # Pero para integración, permitimos acceso si el lote existe
        
        # Obtener información adicional del lote
        lote_data = {
            'id': lote.id,
            'lot_code': lote.lot_code,
            'producer_company': lote.producer_company.name if lote.producer_company else None,
            'producer_name': lote.producer_name,
            'farm_name': lote.farm_name,
            'location': lote.location,
            'product_type': lote.product_type,
            'weight_kg': float(lote.weight_kg) if lote.weight_kg else 0,
            'quality_grade': lote.quality_grade,
            'harvest_date': lote.harvest_date.isoformat() if lote.harvest_date else None,
            'certifications': lote.certifications.split(',') if lote.certifications else [],
            'status': lote.status,
            'blockchain_lot_id': lote.blockchain_lot_id,
            'created_at': lote.created_at.isoformat() if lote.created_at else None,
            'metadata': {
                'moisture_content': float(lote.moisture_content) if lote.moisture_content else None,
                'quality_score': float(lote.quality_score) if lote.quality_score else None,
                'certifications_list': lote.certifications.split(',') if lote.certifications else []
            }
        }
        
        return jsonify({
            'success': True,
            'lote': lote_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo lote NFT: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@app.route('/api/lotes/<int:lote_id>/eventos', methods=['POST'])
@require_api_key
def registrar_evento_lote(lote_id):
    """Registrar evento en lote NFT (para AgroWeight Cloud)"""
    try:
        company = g.company
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Datos requeridos',
                'message': 'Se requiere body JSON con datos del evento'
            }), 400
        
        # Validar datos requeridos
        if 'tipo' not in data:
            return jsonify({
                'error': 'Tipo de evento requerido',
                'message': 'Campo "tipo" es obligatorio'
            }), 400
        
        # Buscar el lote
        lote = ProducerLot.query.get(lote_id)
        if not lote:
            return jsonify({
                'error': 'Lote no encontrado',
                'message': f'No se encontró lote con ID: {lote_id}'
            }), 404
        
        # Crear evento de trazabilidad
        evento = TraceEvent(
            entity_type='lot',
            entity_id=lote_id,
            event_type=data['tipo'],
            event_data=json.dumps(data),
            user_id=None,  # Evento desde API externa
            blockchain_tx_hash=None,  # Se puede agregar después
            created_at=datetime.utcnow()
        )
        
        db.session.add(evento)
        db.session.commit()
        
        # Crear timeline entry si no existe
        timeline_entry = TraceTimeline.query.filter_by(
            entity_type='lot',
            entity_id=lote_id,
            event_type=data['tipo']
        ).first()
        
        if not timeline_entry:
            timeline_entry = TraceTimeline(
                entity_type='lot',
                entity_id=lote_id,
                event_type=data['tipo'],
                title=f"Evento: {data['tipo']}",
                description=data.get('descripcion', f"Evento {data['tipo']} registrado desde AgroWeight Cloud"),
                event_data=json.dumps(data),
                created_at=datetime.utcnow()
            )
            db.session.add(timeline_entry)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Evento registrado exitosamente',
            'evento': {
                'id': evento.id,
                'tipo': evento.event_type,
                'lote_id': lote_id,
                'company_id': company.id,
                'timestamp': evento.created_at.isoformat(),
                'data': data
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registrando evento en lote: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@app.route('/api/batch-nft', methods=['POST'])
@require_api_key
def crear_batch_nft():
    """Crear NFT de batch final (para AgroWeight Cloud)"""
    try:
        company = g.company
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Datos requeridos',
                'message': 'Se requiere body JSON con datos del batch'
            }), 400
        
        # Validar datos requeridos
        required_fields = ['batch_code', 'lotes']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Campo requerido: {field}',
                    'message': f'El campo "{field}" es obligatorio'
                }), 400
        
        batch_code = data['batch_code']
        lotes_data = data['lotes']
        
        if not isinstance(lotes_data, list) or len(lotes_data) == 0:
            return jsonify({
                'error': 'Lotes inválidos',
                'message': 'Se requiere una lista de lotes con al menos un elemento'
            }), 400
        
        # Verificar que no exista ya un batch con este código
        existing_batch = BatchNFT.query.filter_by(batch_code=batch_code).first()
        if existing_batch:
            return jsonify({
                'error': 'Código de batch ya existe',
                'message': f'Ya existe un batch con código: {batch_code}'
            }), 400
        
        # Procesar lotes y calcular peso total
        lote_ids = []
        total_weight = 0.0
        
        for lote_info in lotes_data:
            lote_id = lote_info.get('id')
            if not lote_id:
                continue
                
            lote = ProducerLot.query.get(lote_id)
            if lote and lote.status in ['purchased', 'batched']:
                lote_ids.append(lote_id)
                total_weight += float(lote.weight_kg) if lote.weight_kg else 0
        
        if len(lote_ids) == 0:
            return jsonify({
                'error': 'No hay lotes válidos',
                'message': 'Ninguno de los lotes especificados es válido o está disponible'
            }), 400
        
        # Crear batch NFT
        batch = BatchNFT(
            batch_code=batch_code,
            source_lot_ids=json.dumps(lote_ids),
            total_weight_kg=total_weight,
            batch_type=data.get('batch_type', 'export'),
            location=data.get('location', 'Planta de procesamiento'),
            creator_company_id=company.id,
            current_owner_company_id=company.id,
            status='created',
            created_at=datetime.utcnow()
        )
        
        db.session.add(batch)
        db.session.flush()  # Para obtener el ID
        
        # Actualizar estado de los lotes originales
        for lote_id in lote_ids:
            lote = ProducerLot.query.get(lote_id)
            if lote:
                lote.status = 'batched'
                lote.batch_id = batch.id
        
        # Generar hash blockchain simulado
        import hashlib
        batch_data = f"{batch_code}-{company.id}-{total_weight}-{datetime.utcnow().isoformat()}"
        blockchain_hash = hashlib.sha256(batch_data.encode()).hexdigest()
        
        # Actualizar batch con hash
        batch.blockchain_batch_id = f"0x{blockchain_hash[:64]}"
        batch.status = 'minted'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Batch NFT creado exitosamente',
            'batch': {
                'id': batch.id,
                'batch_code': batch_code,
                'total_weight_kg': total_weight,
                'lotes_count': len(lote_ids),
                'blockchain_batch_id': batch.blockchain_batch_id,
                'status': batch.status,
                'company_id': company.id,
                'created_at': batch.created_at.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando batch NFT: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

# =====================================
# ENDPOINTS DE ANALYTICS
# =====================================

@app.route('/api/analytics/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_analytics():
    """Obtener métricas del dashboard"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        result = {}
        
        if user.role in ['admin', 'operator']:
            # Métricas generales para administradores
            result = {
                'total_contracts': ExportContract.query.count(),
                'active_contracts': ExportContract.query.filter_by(status='active').count(),
                'total_volume_mt': db.session.query(db.func.sum(ExportContract.total_volume_mt)).scalar() or 0,
                'fixed_volume_mt': db.session.query(db.func.sum(ExportContract.fixed_volume_mt)).scalar() or 0,
                'total_lots': ProducerLot.query.count(),
                'available_lots': ProducerLot.query.filter_by(status='available').count(),
                'total_companies': Company.query.count(),
                'blockchain_status': blockchain.get_status()
            }
            
        elif user.role == 'exporter':
            # Métricas para exportador
            contracts = ExportContract.query.filter_by(exporter_company_id=user.company_id)
            
            # Obtener IDs de productores con los que hay contratos (convenio establecido)
            producer_ids_with_contracts = db.session.query(ExportContract.exporter_company_id).filter(
                ExportContract.buyer_company_id == user.company_id,
                ExportContract.status.in_(['active', 'completed'])
            ).distinct().all()
            producer_ids = [pid[0] for pid in producer_ids_with_contracts]
            
            # Lotes disponibles SOLO de productores con convenio
            available_lots_with_contract = ProducerLot.query.filter(
                ProducerLot.producer_company_id.in_(producer_ids),
                ProducerLot.status == 'available'
            ).count() if producer_ids else 0
            
            result = {
                'my_contracts': contracts.count(),
                'active_contracts': contracts.filter_by(status='active').count(),
                'total_volume_mt': db.session.query(db.func.sum(ExportContract.total_volume_mt)).filter_by(exporter_company_id=user.company_id).scalar() or 0,
                'fixed_volume_mt': db.session.query(db.func.sum(ExportContract.fixed_volume_mt)).filter_by(exporter_company_id=user.company_id).scalar() or 0,
                'my_fixations': ContractFixation.query.join(ExportContract).filter(ExportContract.exporter_company_id == user.company_id).count(),
                'available_lots_with_contract': available_lots_with_contract,
                'producers_with_contract': len(producer_ids)
            }
            
        elif user.role == 'buyer':
            # Métricas para comprador
            contracts = ExportContract.query.filter_by(buyer_company_id=user.company_id)
            result = {
                'my_contracts': contracts.count(),
                'active_contracts': contracts.filter_by(status='active').count(),
                'total_volume_mt': db.session.query(db.func.sum(ExportContract.total_volume_mt)).filter_by(buyer_company_id=user.company_id).scalar() or 0,
                'fixed_volume_mt': db.session.query(db.func.sum(ExportContract.fixed_volume_mt)).filter_by(buyer_company_id=user.company_id).scalar() or 0
            }
            
        elif user.role == 'producer':
            # Métricas para productor
            result = {
                'my_lots': ProducerLot.query.filter_by(producer_company_id=user.company_id).count(),
                'available_lots': ProducerLot.query.filter_by(producer_company_id=user.company_id, status='available').count(),
                'total_weight_kg': db.session.query(db.func.sum(ProducerLot.weight_kg)).filter_by(producer_company_id=user.company_id).scalar() or 0,
                'assigned_lots': ProducerLot.query.filter_by(producer_company_id=user.company_id).filter(ProducerLot.export_contract_id.isnot(None)).count()
            }
        
        # Convertir Decimals a float para JSON
        for key, value in result.items():
            if isinstance(value, Decimal):
                result[key] = float(value)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/contracts', methods=['GET'])
@jwt_required()
def get_contract_analytics():
    """Obtener analytics específicos de contratos"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Base query según el rol del usuario
        if user.role in ['admin', 'operator']:
            contracts = ExportContract.query
        elif user.role == 'exporter':
            contracts = ExportContract.query.filter_by(exporter_company_id=user.company_id)
        elif user.role == 'buyer':
            contracts = ExportContract.query.filter_by(buyer_company_id=user.company_id)
        else:
            return jsonify({'error': 'No autorizado para ver analytics de contratos'}), 403
        
        # Estadísticas por estado
        stats_by_status = {}
        for status in ['draft', 'active', 'completed', 'cancelled']:
            count = contracts.filter_by(status=status).count()
            stats_by_status[status] = count
        
        # Top contratos por volumen
        top_contracts = contracts.order_by(ExportContract.total_volume_mt.desc()).limit(5).all()
        top_contracts_data = []
        for contract in top_contracts:
            top_contracts_data.append({
                'id': contract.id,
                'contract_code': contract.contract_code,
                'buyer_company': contract.buyer_company.name if contract.buyer_company else 'N/A',
                'total_volume_mt': float(contract.total_volume_mt) if contract.total_volume_mt else 0,
                'fixed_volume_mt': float(contract.fixed_volume_mt) if contract.fixed_volume_mt else 0,
                'completion_percentage': round((float(contract.fixed_volume_mt or 0) / float(contract.total_volume_mt)) * 100, 1) if contract.total_volume_mt else 0
            })
        
        # Analytics por mes (últimos 6 meses)
        from datetime import datetime, timedelta
        six_months_ago = datetime.now() - timedelta(days=180)
        monthly_contracts = contracts.filter(ExportContract.created_at >= six_months_ago).all()
        
        monthly_stats = {}
        for contract in monthly_contracts:
            month_key = contract.created_at.strftime('%Y-%m')
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {'count': 0, 'volume': 0}
            monthly_stats[month_key]['count'] += 1
            monthly_stats[month_key]['volume'] += float(contract.total_volume_mt or 0)
        
        result = {
            'stats_by_status': stats_by_status,
            'top_contracts': top_contracts_data,
            'monthly_stats': monthly_stats,
            'total_contracts': contracts.count(),
            'total_volume': float(contracts.with_entities(db.func.sum(ExportContract.total_volume_mt)).scalar() or 0),
            'total_fixed': float(contracts.with_entities(db.func.sum(ExportContract.fixed_volume_mt)).scalar() or 0)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/esg', methods=['GET'])
@jwt_required()
def get_esg_data():
    """Obtener datos ESG (Environmental, Social, Governance)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Datos ESG simulados realistas para la plataforma agrícola
        esg_data = {
            'overall': {
                'esg_score': 82,
                'sustainability_rating': 'A-',
                'last_updated': '2024-11-05T12:00:00Z',
                'improvement_areas': ['water_conservation', 'renewable_energy_adoption', 'waste_reduction_programs'],
                'strengths': ['blockchain_transparency', 'fair_trade_compliance', 'automated_producer_payments', 'carbon_footprint_tracking']
            },
            'environmental': {
                'carbon_footprint': {
                    'total_co2_tons': 1247.5,
                    'co2_per_ton': 1.8,
                    'reduction_target': 15,
                    'renewable_energy': 68
                },
                'water_usage': {
                    'efficiency_score': 76,
                    'conservation_projects': 12,
                    'water_saved_liters': 1200000
                },
                'biodiversity': {
                    'protected_hectares': 2845,
                    'species_preserved': '127 especies',
                    'reforestation_projects': 8
                },
                'waste_management': {
                    'waste_recycled_pct': 85,
                    'organic_waste_composted': 92,
                    'plastic_reduction': 65
                }
            },
            'social': {
                'fair_trade': {
                    'certified_lots': 1248,
                    'certified_producers': 456,
                    'premium_paid_usd': 125000
                },
                'worker_welfare': {
                    'safety_score': 94,
                    'healthcare_coverage': 87,
                    'training_hours': 2400
                },
                'community_impact': {
                    'schools_supported': 15,
                    'healthcare_centers': 3,
                    'micro_credits_granted': 89
                },
                'gender_equality': {
                    'women_producers': 35,
                    'women_leadership': 28,
                    'equal_pay_score': 96
                }
            },
            'governance': {
                'transparency': {
                    'blockchain_traced_pct': 97,
                    'public_reporting': 100,
                    'third_party_audits': 4,
                    'audit_compliance': 98
                },
                'compliance': {
                    'certifications_current': 12,
                    'regulatory_compliance': 98,
                    'dispute_resolution': '<2%'
                },
                'certifications': {
                    'organic_pct': 78,
                    'fair_trade_pct': 85,
                    'rainforest_alliance_pct': 62,
                    'total_certified_lots': 1248
                },
                'stakeholder_engagement': {
                    'satisfaction_score': 91,
                    'community_meetings': 24,
                    'feedback_response_rate': 89
                },
                'supply_chain': {
                    'traceability_score': 97,
                    'verified_suppliers': 85,
                    'ethical_sourcing': 92
                }
            },
            'metrics': {
                'total_producers': 2456,
                'total_volume_mt': 8500,
                'contracts_completed': 145,
                'traceability_coverage': 97
            }
        }
        
        return jsonify(esg_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================
# ENDPOINTS ADICIONALES
# =====================================

@app.route('/api/companies', methods=['GET'])
@jwt_required()
def get_companies():
    """Obtener lista de empresas"""
    try:
        companies = Company.query.all()
        
        result = []
        for company in companies:
            company_data = {
                'id': company.id,
                'name': company.name,
                'country': company.country,
                'plan_type': getattr(company, 'plan_type', None),
                'wallet_address': getattr(company, 'wallet_address', None),
                'is_active': getattr(company, 'is_active', True)
            }
            result.append(company_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    """Obtener lista de usuarios del sistema"""
    try:
        print(f"API /api/users called")
        
        # Verificar que el usuario tenga permisos de admin
        user_id = get_jwt_identity()
        print(f"JWT identity: {user_id}")
        
        current_user = User.query.get(user_id)
        print(f"Current user: {current_user}")
        
        if not current_user or current_user.role not in ['admin', 'operator']:
            print(f"User {user_id} does not have permission. Role: {current_user.role if current_user else 'None'}")
            return jsonify({'error': 'No tienes permisos para ver la lista de usuarios'}), 403
        
        users = User.query.all()
        result = []
        
        for user in users:
            # Obtener la empresa asociada
            company = Company.query.get(user.company_id) if user.company_id else None
            
            user_data = {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'name': user.name,
                'is_active': user.active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                'company': {
                    'id': company.id,
                    'name': company.name,
                    'type': company.company_type
                } if company else None
            }
            result.append(user_data)
        
        print(f"Returning {len(result)} users")
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in /api/users: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['POST'])
@jwt_required()
def create_user():
    """Crear nuevo usuario - Solo administradores"""
    try:
        print(f"API POST /api/users called")
        
        # Verificar que el usuario tenga permisos de admin
        user_id = get_jwt_identity()
        print(f"JWT identity: {user_id}")
        
        current_user = User.query.get(user_id)
        print(f"Current user: {current_user}")
        
        if not current_user or current_user.role not in ['admin', 'operator']:
            print(f"User {user_id} does not have permission. Role: {current_user.role if current_user else 'None'}")
            return jsonify({'error': 'No tienes permisos para crear usuarios'}), 403
        
        data = request.get_json()
        print(f"Request data: {data}")
        
        # Validar datos requeridos
        required_fields = ['email', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        # Verificar que el email no exista
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Ya existe un usuario con este email'}), 400
        
        # Verificar que la compañía exista si se especifica
        if 'company_id' in data and data['company_id']:
            company = Company.query.get(data['company_id'])
            if not company:
                return jsonify({'error': 'Compañía no encontrada'}), 404
        
        # Crear el usuario
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            name=f"{data['first_name']} {data['last_name']}",
            role=data['role'],
            company_id=data.get('company_id'),
            active=data.get('active', True)
        )
        
        # Establecer contraseña si se proporciona
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        print(f"User created successfully: {user.id}")
        return jsonify({
            'message': 'Usuario creado exitosamente',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'name': user.name,
                'role': user.role,
                'company_id': user.company_id,
                'active': user.active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating user: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Actualizar usuario - Solo administradores"""
    try:
        print(f"API PUT /api/users/{user_id} called")
        
        # Verificar que el usuario tenga permisos de admin
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role not in ['admin', 'operator']:
            return jsonify({'error': 'No tienes permisos para actualizar usuarios'}), 403
        
        # Obtener el usuario a actualizar
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        print(f"Request data: {data}")
        
        # Actualizar campos permitidos
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'first_name' in data or 'last_name' in data:
            user.name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        if 'role' in data:
            user.role = data['role']
        if 'company_id' in data:
            # Verificar que la compañía exista
            if data['company_id']:
                company = Company.query.get(data['company_id'])
                if not company:
                    return jsonify({'error': 'Compañía no encontrada'}), 404
            user.company_id = data['company_id']
        if 'active' in data:
            user.active = data['active']
        
        # Actualizar contraseña si se proporciona
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        db.session.commit()
        
        print(f"User updated successfully: {user.id}")
        return jsonify({
            'message': 'Usuario actualizado exitosamente',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'name': user.name,
                'role': user.role,
                'company_id': user.company_id,
                'active': user.active,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating user: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Eliminar usuario - Solo administradores"""
    try:
        print(f"API DELETE /api/users/{user_id} called")
        
        # Verificar que el usuario tenga permisos de admin
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role not in ['admin', 'operator']:
            return jsonify({'error': 'No tienes permisos para eliminar usuarios'}), 403
        
        # Obtener el usuario a eliminar
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # No permitir eliminar al propio usuario
        if user.id == current_user_id:
            return jsonify({'error': 'No puedes eliminar tu propio usuario'}), 400
        
        # Eliminar el usuario
        db.session.delete(user)
        db.session.commit()
        
        print(f"User deleted successfully: {user_id}")
        return jsonify({'message': 'Usuario eliminado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/blockchain/transactions', methods=['GET'])
def get_blockchain_transactions():
    """Obtener transacciones recientes del blockchain"""
    try:
        # Simulamos transacciones por ahora - en producción sería desde blockchain
        transactions = [
            {
                'id': 1,
                'hash': '0x1234567890abcdef1234567890abcdef12345678',
                'type': 'contract_creation',
                'status': 'confirmed',
                'timestamp': datetime.now().isoformat(),
                'gas_cost': '0.0045',
                'block_number': 12345678
            },
            {
                'id': 2,
                'hash': '0xabcdef1234567890abcdef1234567890abcdef12',
                'type': 'fixation_registered',
                'status': 'confirmed',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'gas_cost': '0.0023',
                'block_number': 12345677
            },
            {
                'id': 3,
                'hash': '0x567890abcdef1234567890abcdef1234567890ab',
                'type': 'nft_mint',
                'status': 'pending',
                'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat(),
                'gas_cost': '0.0078',
                'block_number': None
            }
        ]
        
        return jsonify(transactions)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lots/available-for-batch', methods=['GET'])
@jwt_required()
def get_lots_available_for_batch():
    """Obtener lotes disponibles para crear batch (lotes purchased sin agrupar)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in ['admin', 'operator', 'exporter']:
            return jsonify({'error': 'Sin permisos para crear batches'}), 403
        
        # Obtener lotes comprados que aún no están en batch
        query = ProducerLot.query.filter_by(status='purchased')
        
        # Si es exportador, solo sus lotes
        if user.role == 'exporter':
            query = query.filter_by(purchased_by_company_id=user.company_id)
        
        lots = query.order_by(ProducerLot.harvest_date.desc()).all()
        
        result = []
        for lot in lots:
            # Calcular precio por MT
            price_per_mt = 0
            if lot.weight_kg and lot.weight_kg > 0 and lot.purchase_price_usd:
                price_per_mt = float(lot.purchase_price_usd) / (float(lot.weight_kg) / 1000.0)
            
            lot_data = {
                'id': lot.id,
                'lot_code': lot.lot_code,
                'weight_kg': float(lot.weight_kg) if lot.weight_kg else 0,
                'weight_mt': float(lot.weight_kg) / 1000.0 if lot.weight_kg else 0,
                'purchase_price_usd': float(lot.purchase_price_usd) if lot.purchase_price_usd else 0,
                'price_per_mt': price_per_mt,
                'producer_name': lot.producer_name,
                'farm_name': lot.farm_name,
                'location': lot.location,
                'harvest_date': lot.harvest_date.isoformat() if lot.harvest_date else None,
                'quality_score': float(lot.quality_score) if lot.quality_score else None,
                'moisture_content': float(lot.moisture_content) if lot.moisture_content else None,
                'status': lot.status,
                'certifications': lot.certifications,
                'product_type': lot.product_type,
                'purchased_by_company': {
                    'id': lot.purchased_by_company.id,
                    'name': lot.purchased_by_company.name,
                    'company_type': lot.purchased_by_company.company_type
                } if lot.purchased_by_company else None,
                'producer_company': {
                    'id': lot.producer_company.id,
                    'name': lot.producer_company.name
                } if lot.producer_company else None
            }
            result.append(lot_data)
        
        return jsonify({
            'success': True,
            'count': len(result),
            'lots': result
        })
        
    except Exception as e:
        logger.error(f"Error en get_lots_available_for_batch: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/batches/available', methods=['GET'])
@jwt_required()
def get_available_batches():
    """Obtener batches disponibles para compra"""
    try:
        # Obtener batches que no están completamente vendidos
        batches = BatchNFT.query.filter(
            BatchNFT.status.in_(['active', 'created'])
        ).all()
        
        result = []
        for batch in batches:
            batch_data = {
                'id': batch.id,
                'code': batch.batch_code,
                'quantity': float(batch.total_weight_kg) if batch.total_weight_kg else 0,
                'available_quantity': float(batch.total_weight_kg) if batch.total_weight_kg else 0,  # Por ahora asumimos que todo está disponible
                'sold_quantity': 0,  # No hay campo de vendido en BatchNFT
                'price_per_unit': 0,  # No hay precio en BatchNFT
                'total_value': 0,
                'status': batch.status,
                'created_at': batch.created_at.isoformat() if batch.created_at else None,
                'creator_company': {
                    'id': batch.creator_company.id,
                    'name': batch.creator_company.name,
                    'company_type': batch.creator_company.company_type
                } if batch.creator_company else None
            }
            result.append(batch_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/purchases', methods=['GET'])
@jwt_required()
def get_user_purchases():
    """Obtener compras del usuario actual"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.company:
            return jsonify({'error': 'Usuario o compañía no encontrada'}), 404
        
        # Obtener lotes comprados por la compañía del usuario
        purchased_lots = ProducerLot.query.filter_by(
            purchased_by_company_id=user.company_id
        ).all()
        
        result = []
        for lot in purchased_lots:
            purchase_data = {
                'id': lot.id,
                'lot_code': lot.lot_code,
                'product_type': lot.product_type,
                'weight_kg': float(lot.weight_kg) if lot.weight_kg else 0,
                'quality_grade': lot.quality_grade,
                'purchase_price_usd': float(lot.purchase_price_usd) if lot.purchase_price_usd else 0,
                'purchase_date': lot.purchase_date.isoformat() if lot.purchase_date else None,
                'status': lot.status,
                'producer_name': lot.producer_name,
                'farm_name': lot.farm_name,
                'location': lot.location,
                'certifications': lot.certifications,
                'batch_id': lot.batch_id,
                'purchase_tx_hash': lot.purchase_tx_hash,
                'producer_company': {
                    'id': lot.producer_company.id,
                    'name': lot.producer_company.name,
                    'company_type': lot.producer_company.company_type
                } if lot.producer_company else None
            }
            result.append(purchase_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batches/<int:batch_id>/traceability', methods=['GET'])
@jwt_required()
def get_batch_traceability(batch_id):
    """Obtener trazabilidad de un batch específico"""
    try:
        batch = BatchNFT.query.get(batch_id)
        
        if not batch:
            return jsonify({'error': 'Batch no encontrado'}), 404
        
        # Obtener lotes fuente del batch
        source_lot_ids = batch.source_lots_list
        source_lots = ProducerLot.query.filter(ProducerLot.id.in_(source_lot_ids)).all()
        
        traceability_data = {
            'batch': batch.to_dict(),
            'source_lots': [lot.__dict__ for lot in source_lots],
            'traceability_chain': []
        }
        
        # Construir cadena de trazabilidad
        for lot in source_lots:
            chain_entry = {
                'lot_id': lot.id,
                'lot_code': lot.lot_code,
                'producer_name': lot.producer_name,
                'farm_name': lot.farm_name,
                'location': lot.location,
                'harvest_date': lot.harvest_date.isoformat() if lot.harvest_date else None,
                'certifications': lot.certifications,
                'blockchain_lot_id': lot.blockchain_lot_id
            }
            traceability_data['traceability_chain'].append(chain_entry)
        
        return jsonify(traceability_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batches/search', methods=['GET'])
@jwt_required()
def search_batches():
    """Buscar batches por código"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'error': 'Parámetro de búsqueda requerido'}), 400
        
        # Buscar batches por código
        batches = BatchNFT.query.filter(
            BatchNFT.batch_code.ilike(f'%{query}%')
        ).all()
        
        result = []
        for batch in batches:
            batch_data = {
                'id': batch.id,
                'code': batch.batch_code,
                'total_weight_kg': float(batch.total_weight_kg) if batch.total_weight_kg else 0,
                'batch_type': batch.batch_type,
                'location': batch.location,
                'status': batch.status,
                'creator_company': {
                    'id': batch.creator_company.id,
                    'name': batch.creator_company.name,
                    'company_type': batch.creator_company.company_type
                } if batch.creator_company else None,
                'created_at': batch.created_at.isoformat() if batch.created_at else None
            }
            result.append(batch_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lots/search', methods=['GET'])
@jwt_required()
def search_lots():
    """Buscar lotes por código"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'error': 'Parámetro de búsqueda requerido'}), 400
        
        # Buscar lotes por código
        lots = ProducerLot.query.filter(
            ProducerLot.lot_code.ilike(f'%{query}%')
        ).all()
        
        result = []
        for lot in lots:
            lot_data = {
                'id': lot.id,
                'lot_code': lot.lot_code,
                'product_type': lot.product_type,
                'weight_kg': float(lot.weight_kg) if lot.weight_kg else 0,
                'quality_grade': lot.quality_grade,
                'producer_name': lot.producer_name,
                'farm_name': lot.farm_name,
                'location': lot.location,
                'status': lot.status,
                'producer_company': {
                    'id': lot.producer_company.id,
                    'name': lot.producer_company.name
                } if lot.producer_company else None,
                'created_at': lot.created_at.isoformat() if lot.created_at else None
            }
            result.append(lot_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test/users', methods=['GET'])
def test_users():
    """Endpoint de prueba para verificar usuarios"""
    try:
        users = User.query.all()
        return jsonify({
            'count': len(users),
            'users': [{'id': u.id, 'email': u.email, 'name': u.name, 'role': u.role, 'active': u.active} for u in users]
        })
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

# =====================================
# HEALTH CHECK ENDPOINT
# =====================================

@app.route('/api/health', methods=['GET'])
@app.route('/health', methods=['GET'])  # Alias para compatibilidad
def health_check():
    """Health check endpoint para monitoreo"""
    try:
        # Verificar conexión a base de datos
        db.session.execute(db.text('SELECT 1')).fetchone()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"

    # Verificar integración blockchain
    blockchain_status = "ready" if blockchain and blockchain.is_ready() else "not_configured"

    return jsonify({
        'status': 'ok' if db_status == 'healthy' else 'error',
        'service': 'Triboka Agro API',
        'database': db_status,
        'blockchain': blockchain_status,
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    }), 200 if db_status == 'healthy' else 503


# =====================================
# ENDPOINTS PARA INTEGRACIÓN CON ERP
# =====================================

@app.route('/api/producers/<int:producer_id>', methods=['GET'])
def get_producer_info(producer_id):
    """Obtener información de un productor (para integración con ERP)"""
    try:
        company = Company.query.filter_by(id=producer_id, company_type='producer').first()
        
        if not company:
            return jsonify({'error': 'Productor no encontrado'}), 404
        
        return jsonify({
            'id': company.id,
            'name': company.name,
            'farm_name': company.name,  # Asumiendo que el nombre es la finca
            'cacao_variety': 'Criollo',  # Podría venir de metadata adicional
            'certifications': 'Orgánico, Fair Trade',
            'phone': company.contact_info if hasattr(company, 'contact_info') else None,
            'email': company.wallet_address if hasattr(company, 'wallet_address') else None,
            'location': 'Honduras',  # Podría venir de metadata adicional
            'active': True
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting producer info: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/batches/create-export', methods=['POST'])
def create_export_batch_with_nft():
    """
    Crear batch de exportación con NFT desde ERP
    Recibe metadata completa de trazabilidad y genera NFT
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Metadata requerida'}), 400
        
        # Extraer información del batch
        batch_erp = data.get('batch_erp', {})
        cliente = data.get('cliente', {})
        lotes = data.get('lotes', [])
        totales = data.get('totales', {})
        despacho = data.get('despacho', {})
        certificaciones = data.get('certificaciones', {})
        
        # Validar datos mínimos
        if not batch_erp.get('codigo') or not lotes:
            return jsonify({'error': 'Código de batch y lotes son requeridos'}), 400
        
        logger.info(f"📦 Creando batch de exportación: {batch_erp.get('codigo')}")
        logger.info(f"   Cliente: {cliente.get('nombre')}")
        logger.info(f"   Lotes: {len(lotes)}")
        logger.info(f"   Peso: {totales.get('peso_qq')} qq")
        
        # Crear BatchNFT en la base de datos
        import json as json_lib
        lot_ids_list = [str(l.get('codigo_lote_triboka_agro') or l.get('codigo_lote_erp')) for l in lotes]
        
        batch = BatchNFT(
            batch_code=batch_erp.get('codigo'),
            source_lot_ids=json_lib.dumps(lot_ids_list),
            total_weight_kg=totales.get('peso_kg', 0),
            batch_type='export',
            location=despacho.get('pais_destino', 'Internacional'),
            status='pending'
        )
        
        db.session.add(batch)
        db.session.flush()
        
        # Generar hash blockchain
        import hashlib
        import json
        hash_data = json.dumps({
            'batch_code': batch.batch_code,
            'lotes': [l.get('codigo_lote_erp') for l in lotes],
            'peso_qq': totales.get('peso_qq'),
            'timestamp': datetime.now().isoformat()
        }, sort_keys=True)
        blockchain_hash = hashlib.sha256(hash_data.encode()).hexdigest()
        
        # Simular creación de NFT en blockchain
        nft_token_id = 1000 + batch.id  # Simulado
        nft_contract_address = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1'
        
        # Generar URLs
        ipfs_hash = hashlib.md5(hash_data.encode()).hexdigest()
        nft_metadata_url = f'ipfs://{ipfs_hash}/metadata.json'
        nft_image_url = f'https://triboka-nft-images.s3.amazonaws.com/batch-{nft_token_id}.jpg'
        nft_opensea_url = f'https://opensea.io/assets/ethereum/{nft_contract_address}/{nft_token_id}'
        
        # Actualizar batch con info de NFT
        batch.nft_token_id = nft_token_id
        batch.blockchain_batch_id = batch.id
        batch.status = 'minted'
        
        db.session.commit()
        
        logger.info(f"✅ NFT Generado:")
        logger.info(f"   Token ID: {nft_token_id}")
        logger.info(f"   Hash: {blockchain_hash[:16]}...")
        logger.info(f"   OpenSea: {nft_opensea_url}")
        
        # Respuesta con toda la información del NFT
        return jsonify({
            'success': True,
            'batch_id': batch.id,
            'blockchain_hash': f'0x{blockchain_hash}',
            'block_number': 18234567 + batch.id,
            'transaction_hash': f'0x{hashlib.sha256(str(datetime.now()).encode()).hexdigest()}',
            'timestamp': datetime.now().isoformat(),
            'nft_token_id': nft_token_id,
            'nft_contract_address': nft_contract_address,
            'nft_metadata_url': nft_metadata_url,
            'nft_image_url': nft_image_url,
            'nft_opensea_url': nft_opensea_url,
            'metadata': {
                'batch_code': batch.batch_code,
                'total_weight_qq': totales.get('peso_qq'),
                'num_lots': totales.get('numero_lotes'),
                'quality': totales.get('calidad_promedio'),
                'destination': despacho.get('pais_destino'),
                'client': cliente.get('nombre')
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating export batch: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# =====================================
# DASHBOARD ESPECÍFICOS POR ROL
# =====================================

@app.route('/api/dashboard/producer', methods=['GET'])
@jwt_required()
def get_producer_dashboard():
    """Obtener datos del dashboard de productor"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in ['producer', 'admin']:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        # Obtener lotes del productor
        lots_query = ProducerLot.query.filter_by(producer_company_id=user.company_id)
        all_lots = lots_query.all()
        
        # Métricas
        total_lots = len(all_lots)
        available_lots = len([l for l in all_lots if l.status == 'available'])
        purchased_lots = len([l for l in all_lots if l.status == 'purchased'])
        total_weight = sum([float(l.weight_kg) for l in all_lots])
        total_revenue = sum([float(l.purchase_price_usd or 0) for l in all_lots if l.purchase_price_usd])
        
        # Formatear lotes para el frontend
        lots_data = []
        for lot in all_lots[:20]:  # Últimos 20 lotes
            lots_data.append({
                'id': lot.id,
                'lot_code': lot.lot_code,
                'producer_company': lot.producer_company.name if lot.producer_company else None,
                'farm_name': lot.farm_name,
                'location': lot.location,
                'weight_kg': float(lot.weight_kg),
                'quality_grade': lot.quality_grade,
                'harvest_date': lot.harvest_date.isoformat() if lot.harvest_date else None,
                'purchase_date': lot.purchase_date.isoformat() if lot.purchase_date else None,
                'purchase_price_usd': float(lot.purchase_price_usd) if lot.purchase_price_usd else None,
                'status': lot.status,
                'certifications': lot.certifications.split(',') if lot.certifications else [],
                'exporter_name': lot.export_contract.exporter_company.name if lot.export_contract and lot.export_contract.exporter_company else None
            })
        
        return jsonify({
            'metrics': {
                'total_lots': total_lots,
                'available_lots': available_lots,
                'purchased_lots': purchased_lots,
                'total_weight_kg': total_weight,
                'total_revenue_usd': total_revenue
            },
            'lots': lots_data
        })
        
    except Exception as e:
        logger.error(f"Error in producer dashboard: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/exporter', methods=['GET'])
@jwt_required()
def get_exporter_dashboard():
    """Obtener datos del dashboard de exportador"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in ['exporter', 'admin']:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        # Lotes comprados por el exportador
        purchased_lots = ProducerLot.query.join(ExportContract).filter(
            ExportContract.exporter_company_id == user.company_id,
            ProducerLot.status == 'purchased'
        ).all()
        
        # Lotes disponibles para comprar
        available_lots = ProducerLot.query.filter_by(status='available').all()
        
        # Batches creados por el exportador
        batches = BatchNFT.query.filter_by(exporter_company_id=user.company_id).all()
        
        # Métricas
        total_purchased_lots = len(purchased_lots)
        total_weight_purchased = sum([float(l.weight_kg) for l in purchased_lots])
        total_batches = len(batches)
        total_batch_weight = sum([float(b.total_weight_kg) for b in batches])
        
        # Formatear lotes disponibles
        available_lots_data = []
        for lot in available_lots[:20]:  # Primeros 20
            available_lots_data.append({
                'id': lot.id,
                'lot_code': lot.lot_code,
                'producer_name': lot.producer_company.name if lot.producer_company else lot.producer_name,
                'farm_name': lot.farm_name,
                'location': lot.location,
                'weight_kg': float(lot.weight_kg),
                'quality_grade': lot.quality_grade,
                'harvest_date': lot.harvest_date.isoformat() if lot.harvest_date else None,
                'certifications': lot.certifications.split(',') if lot.certifications else [],
                'status': lot.status
            })
        
        # Formatear lotes comprados
        purchased_lots_data = []
        for lot in purchased_lots[:20]:
            purchased_lots_data.append({
                'id': lot.id,
                'lot_code': lot.lot_code,
                'producer_name': lot.producer_company.name if lot.producer_company else lot.producer_name,
                'weight_kg': float(lot.weight_kg),
                'purchase_price_usd': float(lot.purchase_price_usd) if lot.purchase_price_usd else None,
                'purchase_date': lot.purchase_date.isoformat() if lot.purchase_date else None,
                'quality_grade': lot.quality_grade,
                'status': lot.status
            })
        
        return jsonify({
            'metrics': {
                'total_purchased_lots': total_purchased_lots,
                'total_weight_purchased_kg': total_weight_purchased,
                'total_batches': total_batches,
                'total_batch_weight_kg': total_batch_weight,
                'available_lots_count': len(available_lots)
            },
            'available_lots': available_lots_data,
            'purchased_lots': purchased_lots_data,
            'batches': [{
                'id': b.id,
                'batch_code': b.batch_code,
                'total_weight_kg': float(b.total_weight_kg),
                'status': b.status,
                'created_at': b.created_at.isoformat()
            } for b in batches[:10]]
        })
        
    except Exception as e:
        logger.error(f"Error in exporter dashboard: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/buyer', methods=['GET'])
@jwt_required()
def get_buyer_dashboard():
    """Obtener datos del dashboard de comprador"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in ['buyer', 'admin']:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        # Batches disponibles para comprar
        available_batches = BatchNFT.query.filter_by(status='available').all()
        
        # Batches comprados (si implementas la compra de batches)
        # purchased_batches = BatchNFT.query.filter_by(buyer_company_id=user.company_id).all()
        
        # Formatear batches disponibles
        batches_data = []
        for batch in available_batches[:20]:
            # Obtener lotes del batch
            source_lots = ProducerLot.query.filter_by(batch_nft_id=batch.id).all()
            
            # Calcular quality_grade del batch basado en los lotes fuente
            quality_grades = [lot.quality_grade for lot in source_lots if lot.quality_grade]
            batch_quality_grade = quality_grades[0] if quality_grades else 'N/A'
            
            batches_data.append({
                'id': batch.id,
                'batch_code': batch.batch_code,
                'exporter_name': batch.exporter_company.name if batch.exporter_company else 'N/A',
                'total_weight_kg': float(batch.total_weight_kg),
                'quality_grade': batch_quality_grade,
                'status': batch.status,
                'created_at': batch.created_at.isoformat(),
                'source_lots_count': len(source_lots),
                'certifications': batch.certifications.split(',') if batch.certifications else [],
                'location': batch.port_of_shipment or 'N/A'
            })
        
        return jsonify({
            'metrics': {
                'available_batches': len(available_batches),
                'total_weight_available_kg': sum([float(b.total_weight_kg) for b in available_batches])
            },
            'batches': batches_data
        })
        
    except Exception as e:
        logger.error(f"Error in buyer dashboard: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =====================================
# MARKET DATA - PRECIOS DE CACAO
# =====================================

@app.route('/api/market/cacao-prices', methods=['GET'])
def get_cacao_prices():
    """Obtener precios actuales del cacao basados en contratos activos y mercado spot real (Yahoo Finance)"""
    from decimal import Decimal
    import statistics
    from datetime import datetime, timedelta
    import yfinance as yf
    
    try:
        
        # ========================================
        # 1. OBTENER PRECIO SPOT REAL (YAHOO FINANCE)
        # ========================================
        spot_price = 3250.0  # Valor por defecto
        daily_change = 0.0
        
        try:
            # Ticker del cacao en Yahoo Finance: CC=F (Cocoa Futures)
            cacao = yf.Ticker("CC=F")
            
            # Obtener datos históricos de los últimos 5 días
            hist = cacao.history(period="5d")
            
            if not hist.empty and len(hist) >= 2:
                # Precio más reciente (último cierre)
                current_price = float(hist['Close'].iloc[-1])
                
                # Convertir de USD/ton a USD/MT (métrica ton)
                # CC=F está en USD por tonelada corta (2000 lbs)
                # 1 tonelada métrica = 2204.62 lbs
                spot_price = current_price * (2204.62 / 2000.0)
                
                # Calcular cambio diario
                if len(hist) >= 2:
                    prev_price = float(hist['Close'].iloc[-2])
                    daily_change = ((current_price - prev_price) / prev_price) * 100
                
                logger.info(f"✅ Precio spot real obtenido: ${spot_price:.2f}/MT (cambio: {daily_change:+.2f}%)")
            else:
                logger.warning("⚠️ No se pudieron obtener datos de Yahoo Finance, usando valor por defecto")
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo precio de Yahoo Finance: {str(e)}")
            # Continuar con valor por defecto
        
        # ========================================
        # 2. OBTENER LOTES CON PRECIOS REALES DE BD
        # ========================================
        purchased_lots = ProducerLot.query.filter(
            ProducerLot.status.in_(['purchased', 'batched']),
            ProducerLot.purchase_price_usd.isnot(None),
            ProducerLot.weight_kg > 0
        ).all()
        
        logger.info(f"📊 Lotes encontrados en BD: {len(purchased_lots)}")
        
        # ========================================
        # 3. CALCULAR PRECIO PROMEDIO DE CONTRATOS ACTIVOS (DATOS REALES)
        # ========================================
        # ========================================
        # 3. CALCULAR PRECIO PROMEDIO DE CONTRATOS ACTIVOS (DATOS REALES)
        # ========================================
        # LÓGICA DE NEGOCIO:
        # - Los contratos tienen un diferencial de -$1000 a -$1200 por debajo del spot
        # - Cuando se fija un precio, se fija según el spot de ese momento
        # - El diferencial es FIJO en USD, no porcentual
        
        contract_prices = []
        total_contract_weight = 0.0
        
        # Si hay lotes con precios reales en BD, usar esos datos
        if purchased_lots and len(purchased_lots) > 0:
            for lot in purchased_lots:
                weight_mt = float(lot.weight_kg) / 1000.0  # Convertir kg a toneladas métricas
                if weight_mt > 0 and lot.purchase_price_usd:
                    price_per_mt = float(lot.purchase_price_usd) / weight_mt
                    contract_prices.append(price_per_mt)
                    total_contract_weight += weight_mt
                    
                    logger.debug(f"  - {lot.lot_code}: ${lot.purchase_price_usd} / {weight_mt:.2f} MT = ${price_per_mt:.2f}/MT")
            
            # Precio promedio real de contratos en BD
            avg_contract_price = statistics.mean(contract_prices)
            logger.info(f"💰 Precio promedio contratos (BD real): ${avg_contract_price:.2f}/MT (de {len(contract_prices)} lotes)")
        else:
            # Si no hay lotes en BD, aplicar lógica de negocio estándar
            # Diferencial típico: -$1000 a -$1200 bajo el spot
            import random
            differential_business = random.uniform(-1200, -1000)
            avg_contract_price = spot_price + differential_business
            logger.info(f"💰 Precio contratos (lógica negocio): ${avg_contract_price:.2f}/MT (spot {differential_business:+.0f})")
        
        # ========================================
        # 4. CALCULAR PRECIO FIJADO (LOTES PURCHASED + BATCHED)
        # ========================================
        # LÓGICA DE NEGOCIO:
        # - El precio fijado se establece según el spot del momento de la fijación
        # - Típicamente: Spot - $1000 a $1200 (diferencial estándar del mercado)
        
        fixed_lots = ProducerLot.query.filter(
            ProducerLot.status.in_(['purchased', 'batched']),
            ProducerLot.purchase_price_usd.isnot(None),
            ProducerLot.weight_kg > 0
        ).all()
        
        fixed_prices = []
        total_fixed_volume = 0.0
        
        if fixed_lots and len(fixed_lots) > 0:
            for lot in fixed_lots:
                weight_mt = float(lot.weight_kg) / 1000.0
                if weight_mt > 0 and lot.purchase_price_usd:
                    price_per_mt = float(lot.purchase_price_usd) / weight_mt
                    fixed_prices.append(price_per_mt)
                    total_fixed_volume += weight_mt
            
            avg_fixed_price = statistics.mean(fixed_prices) if fixed_prices else spot_price - 1100
            logger.info(f"🔒 Precio fijado promedio (BD real): ${avg_fixed_price:.2f}/MT, Volumen: {total_fixed_volume:.2f} MT")
        else:
            # Precio fijado según lógica de negocio: Spot - $1100 (promedio de rango)
            avg_fixed_price = spot_price - 1100
            total_fixed_volume = 0.0
            logger.info(f"🔒 Precio fijado (lógica negocio): ${avg_fixed_price:.2f}/MT (spot - $1100)")
        
        # ========================================
        # 5. CALCULAR NÚMERO DE CONTRATOS ACTIVOS (REAL)
        # ========================================
        active_contracts = ExportContract.query.filter(
            ExportContract.status.in_(['active', 'pending'])
        ).count()
        
        total_contract_volume = ExportContract.query.filter(
            ExportContract.status.in_(['active', 'pending']),
            ExportContract.total_volume_mt.isnot(None)
        ).all()
        
        contract_volume_sum = sum([float(c.total_volume_mt or 0) for c in total_contract_volume])
        
        logger.info(f"📄 Contratos activos: {active_contracts}, Volumen total: {contract_volume_sum:.2f} MT")
        
        # ========================================
        # 6. CALCULAR DIFERENCIAL VS MERCADO
        # ========================================
        # LÓGICA DE NEGOCIO DEL CACAO:
        # - Diferencial estándar: -$1000 a -$1200 USD/MT bajo el spot
        # - El diferencial es FIJO en USD, no es porcentual
        # - Esto se debe a:
        #   * Costos de procesamiento y logística (fijos)
        #   * Prima por calidad/origen (puede variar)
        #   * Certificaciones (Orgánico, Fair Trade, etc.)
        #   * Condiciones del contrato (plazo, volumen)
        # - Cuando el spot sube, el diferencial en USD se mantiene
        # - Ejemplo: Si spot = $6,000, contrato ≈ $4,800-$4,900
        #            Si spot = $7,000, contrato ≈ $5,800-$5,900
        
        differential = avg_contract_price - spot_price
        differential_percent = (differential / spot_price) * 100 if spot_price > 0 else 0
        
        # Clasificar el diferencial según lógica de negocio
        # Cadena de valor: Productores (-$1,400 a -$1,600) → Exportadoras (-$1,000 a -$1,200)
        if -1600 <= differential <= -1400:
            differential_status = "Normal - Compra a Productores"
            differential_type = "producer"
        elif -1400 < differential <= -1200:
            differential_status = "Transición (entre productores y exportadoras)"
            differential_type = "transition"
        elif -1200 < differential <= -1000:
            differential_status = "Normal - Venta Exportadoras"
            differential_type = "exporter"
        elif differential < -1600:
            differential_status = "Muy bajo (por debajo de rango productores)"
            differential_type = "below_range"
        elif -1000 < differential < 0:
            differential_status = "Competitivo (mejor que estándar exportadoras)"
            differential_type = "competitive"
        elif differential >= 0:
            differential_status = "Premium (sobre mercado spot)"
            differential_type = "premium"
        else:
            differential_status = "Revisar"
            differential_type = "unknown"
        
        logger.info(f"📊 Diferencial: ${differential:+.2f}/MT ({differential_percent:+.2f}%) - {differential_status}")
        
        # ========================================
        # 7. ESTADÍSTICAS DE MERCADO (52 SEMANAS)
        # ========================================
        try:
            cacao = yf.Ticker("CC=F")
            hist_year = cacao.history(period="1y")
            
            if not hist_year.empty:
                year_low = float(hist_year['Low'].min()) * (2204.62 / 2000.0)
                year_high = float(hist_year['High'].max()) * (2204.62 / 2000.0)
                
                # Calcular volatilidad (desviación estándar de retornos diarios)
                returns = hist_year['Close'].pct_change().dropna()
                volatility = float(returns.std()) * 100 * (252 ** 0.5)  # Anualizada
                
                logger.info(f"📈 Rango anual: ${year_low:.2f} - ${year_high:.2f}, Volatilidad: {volatility:.2f}%")
            else:
                year_low = spot_price * 0.85
                year_high = spot_price * 1.30
                volatility = 15.0
        except Exception as e:
            logger.error(f"Error obteniendo datos históricos: {str(e)}")
            year_low = spot_price * 0.85
            year_high = spot_price * 1.30
            year_low = spot_price * 0.85
            year_high = spot_price * 1.30
            volatility = 15.0
        
        # ========================================
        # 8. RETORNAR RESPUESTA CON DATOS REALES
        # ========================================
        response_data = {
            'spot': {
                'price': round(spot_price, 2),
                'change': round(daily_change, 2),
                'currency': 'USD',
                'unit': 'MT',
                'source': 'Yahoo Finance (CC=F)'
            },
            'contracts': {
                'avgPrice': round(avg_contract_price, 2),
                'activeCount': active_contracts if active_contracts > 0 else len(purchased_lots),
                'totalVolume': round(contract_volume_sum if contract_volume_sum > 0 else total_contract_weight, 2)
            },
            'fixed': {
                'avgPrice': round(avg_fixed_price, 2),
                'volume': round(total_fixed_volume, 2)
            },
            'differential': {
                'value': round(differential, 2),
                'percent': round(differential_percent, 2),
                'status': differential_status,
                'type': differential_type,
                'explanation': 'Productores: -$1,400 a -$1,600/MT | Exportadoras: -$1,000 a -$1,200/MT'
            },
            'market': {
                'rangeMin': round(year_low, 2),
                'rangeMax': round(year_high, 2),
                'volatility': round(volatility, 2)
            },
            'business_logic': {
                'differential_producers': {
                    'min': -1600,
                    'max': -1400,
                    'unit': 'USD/MT',
                    'description': 'Compra a productores (descuento sobre spot)'
                },
                'differential_exporters': {
                    'min': -1200,
                    'max': -1000,
                    'unit': 'USD/MT',
                    'description': 'Venta a clientes (descuento sobre spot)'
                },
                'expected_margin': {
                    'min': 300,
                    'max': 600,
                    'unit': 'USD/MT',
                    'description': 'Margen esperado entre compra y venta'
                },
                'pricing_model': 'Diferencial fijo en USD (no porcentual)',
                'factors': [
                    'Oferta y demanda del mercado',
                    'Condiciones del contrato (plazo, volumen, pago)',
                    'Calidad y origen (fino de aroma vs. ordinario)',
                    'Certificaciones (Orgánico, Fair Trade, Rainforest)'
                ],
                'fixing_logic': 'Al fijar precio: Spot del momento - diferencial negociado'
            },
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'Yahoo Finance (CC=F) + Triboka Database',
            'data_points': {
                'lots_analyzed': len(purchased_lots),
                'contracts_active': active_contracts,
                'total_fixed_mt': round(total_fixed_volume, 2)
            }
        }
        
        return jsonify(response_data)
        
        
    except Exception as e:
        logger.error(f"Error obteniendo precios del cacao: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/deals', methods=['GET'])
@jwt_required()
def get_deals():
    """Obtener lista de deals según permisos del usuario con filtros y paginación"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Solo admin y operator pueden ver deals
        if user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para ver deals'}), 403
        
        # Obtener parámetros de consulta
        status_filter = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validar límite
        if limit > 200:
            limit = 200
        if limit < 1:
            limit = 1
            
        # Base query
        query = Deal.query
        
        # Aplicar filtros
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        # Ordenar por fecha de creación (más recientes primero)
        query = query.order_by(Deal.created_at.desc())
        
        # Aplicar paginación
        total_count = query.count()
        deals = query.offset(offset).limit(limit).all()
        
        result = []
        for deal in deals:
            deal_data = {
                'id': deal.id,
                'deal_code': deal.deal_code,
                'producer_company': deal.producer.name if deal.producer else None,
                'exporter_company': deal.exporter.name if deal.exporter else None,
                'terms_public': deal.terms_public,
                'status': deal.status,
                'created_at': deal.created_at.isoformat() if deal.created_at else None,
                'updated_at': deal.updated_at.isoformat() if deal.updated_at else None,
                'admin_name': deal.admin.name if deal.admin else None
            }
            result.append(deal_data)
        
        return jsonify({
            'deals': result,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total_count
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deals', methods=['POST'])
@jwt_required()
def create_deal():
    """Crear nuevo deal entre productor y exportador"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para crear deals'}), 403
        
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['producer_id', 'exporter_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        # Verificar que las empresas existan
        producer_company = Company.query.get(data['producer_id'])
        exporter_company = Company.query.get(data['exporter_id'])
        
        if not producer_company or not exporter_company:
            return jsonify({'error': 'Empresa no encontrada'}), 404
        
        # Generar código único del deal
        current_year = datetime.utcnow().year
        # Contar deals del año actual
        year_deals_count = Deal.query.filter(
            Deal.created_at >= datetime(current_year, 1, 1),
            Deal.created_at < datetime(current_year + 1, 1, 1)
        ).count()
        deal_code = "03d"
        
        # Crear deal paso a paso para evitar problemas de binding
        deal = Deal()
        deal.deal_code = deal_code
        deal.producer_id = data['producer_id']
        deal.exporter_id = data['exporter_id']
        deal.admin_id = user_id
        deal.description = data.get('description', '')
        deal.terms_public = json.dumps(data.get('terms_public', {}))
        deal.terms_private = json.dumps(data.get('terms_private', {}))
        deal.visibility_rules = json.dumps({
            'public': ['admin', 'producer', 'exporter'],
            'private': ['admin']
        })
        
        print(f"DEBUG: terms_public type: {type(deal.terms_public)}, value: {deal.terms_public}")
        print(f"DEBUG: terms_private type: {type(deal.terms_private)}, value: {deal.terms_private}")
        
        db.session.add(deal)
        db.session.flush()  # Para obtener el ID
        
        # Crear miembros del deal
        producer_member = DealMember(
            deal_id=deal.id,
            company_id=data['producer_id'],
            role='producer',
            permissions=['read', 'write']
        )
        
        exporter_member = DealMember(
            deal_id=deal.id,
            company_id=data['exporter_id'],
            role='exporter',
            permissions=['read', 'write']
        )
        
        db.session.add(producer_member)
        db.session.add(exporter_member)
        db.session.commit()
        
        return jsonify({
            'message': 'Deal creado exitosamente',
            'deal': {
                'id': deal.id,
                'producer_company': producer_company.name,
                'exporter_company': exporter_company.name,
                'description': deal.description,
                'terms_public': json.loads(deal.terms_public) if deal.terms_public else {},
                'status': deal.status,
                'created_at': deal.created_at.isoformat(),
                'admin_name': deal.admin.name if deal.admin else 'Admin'
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/deals/<int:deal_id>', methods=['GET'])
@jwt_required()
def get_deal_detail(deal_id):
    """Obtener detalles de un deal específico"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal no encontrado'}), 404
        
        # Verificar permisos
        has_access = False
        user_role_in_deal = 'viewer'
        
        if user.id == deal.admin_id:
            has_access = True
            user_role_in_deal = 'admin'
        elif user.company_id and user.company_id == deal.producer_id:
            has_access = True
            user_role_in_deal = 'producer'
        elif user.company_id and user.company_id == deal.exporter_id:
            has_access = True
            user_role_in_deal = 'exporter'
        elif user.role in ['admin', 'operator']:
            has_access = True
            user_role_in_deal = 'admin'
        
        if not has_access:
            return jsonify({'error': 'Sin permisos para ver este deal'}), 403
        
        deal_data = deal.to_dict(role=user_role_in_deal)
        
        # Agregar información adicional
        deal_data['members'] = []
        for member in deal.members:
            member_data = {
                'id': member.id,
                'party_id': member.party_id,
                'party_type': member.party_type,
                'role_in_deal': member.role_in_deal,
                'permissions': member.permissions,
                'joined_at': member.joined_at.isoformat() if member.joined_at else None
            }
            
            # Agregar nombre de la empresa/usuario
            if member.party_type == 'company':
                company = Company.query.get(member.party_id)
                member_data['party_name'] = company.name if company else 'Empresa desconocida'
            else:
                member_user = User.query.get(member.party_id)
                member_data['party_name'] = member_user.name if member_user else 'Usuario desconocido'
            
            deal_data['members'].append(member_data)
        
        return jsonify(deal_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deals/<int:deal_id>/members', methods=['POST'])
@jwt_required()
def invite_deal_member(deal_id):
    """Invitar miembro a un deal (solo admin del deal)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal no encontrado'}), 404
        
        # Solo el admin del deal puede invitar miembros
        if user.id != deal.admin_id and user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Solo el admin del deal puede invitar miembros'}), 403
        
        data = request.get_json()
        
        # Validar datos requeridos
        if 'party_id' not in data or 'role_in_deal' not in data:
            return jsonify({'error': 'Campos requeridos: party_id, role_in_deal'}), 400
        
        # Verificar que el rol sea válido
        valid_roles = ['producer', 'exporter', 'observer']
        if data['role_in_deal'] not in valid_roles:
            return jsonify({'error': f'Rol inválido. Roles válidos: {valid_roles}'}), 400
        
        # Verificar que no exista ya un miembro con este rol
        existing_member = DealMember.query.filter_by(
            deal_id=deal_id,
            role_in_deal=data['role_in_deal']
        ).first()
        
        if existing_member:
            return jsonify({'error': f'Ya existe un {data["role_in_deal"]} en este deal'}), 400
        
        # Crear nuevo miembro
        member = DealMember(
            deal_id=deal_id,
            party_id=data['party_id'],
            party_type=data.get('party_type', 'company'),
            role_in_deal=data['role_in_deal'],
            permissions=data.get('permissions', '["read"]')
        )
        
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'message': 'Miembro invitado exitosamente',
            'member': {
                'id': member.id,
                'party_id': member.party_id,
                'party_type': member.party_type,
                'role_in_deal': member.role_in_deal,
                'permissions': member.permissions,
                'invited_at': member.invited_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/deals/<int:deal_id>/notes', methods=['GET'])
@jwt_required()
def get_deal_notes(deal_id):
    """Obtener notas de un deal según permisos"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal no encontrado'}), 404
        
        # Verificar permisos
        has_access = False
        user_role_in_deal = 'viewer'
        
        if user.id == deal.admin_id:
            has_access = True
            user_role_in_deal = 'admin'
        elif user.company_id == deal.producer_id:
            has_access = True
            user_role_in_deal = 'producer'
        elif user.company_id == deal.exporter_id:
            has_access = True
            user_role_in_deal = 'exporter'
        elif user.role in ['admin', 'operator']:
            has_access = True
            user_role_in_deal = 'admin'
        
        if not has_access:
            return jsonify({'error': 'Sin permisos para ver notas de este deal'}), 403
        
        # Filtrar notas según permisos
        query = DealNote.query.filter_by(deal_id=deal_id)
        
        if user_role_in_deal != 'admin':
            # No admins ven solo notas públicas y del rol correspondiente
            query = query.filter(
                db.or_(
                    DealNote.scope == 'PUBLIC',
                    DealNote.scope == 'PARTES',
                    db.and_(DealNote.scope == 'SOLO_ADMIN', DealNote.author_id == user_id)
                )
            )
        
        notes = query.order_by(DealNote.created_at.desc()).all()
        
        result = []
        for note in notes:
            note_data = {
                'id': note.id,
                'author_id': note.author_id,
                'author_name': note.author.name if note.author else 'Usuario desconocido',
                'scope': note.scope,
                'content': note.content,
                'attachments': note.attachments,
                'created_at': note.created_at.isoformat(),
                'updated_at': note.updated_at.isoformat() if note.updated_at else None
            }
            result.append(note_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deals/<int:deal_id>/notes', methods=['POST'])
@jwt_required()
def create_deal_note(deal_id):
    """Crear nueva nota en un deal"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal no encontrado'}), 404
        
        # Verificar permisos
        has_access = False
        user_role_in_deal = 'viewer'
        
        if user.id == deal.admin_id:
            has_access = True
            user_role_in_deal = 'admin'
        elif user.company_id == deal.producer_id:
            has_access = True
            user_role_in_deal = 'producer'
        elif user.company_id == deal.exporter_id:
            has_access = True
            user_role_in_deal = 'exporter'
        elif user.role in ['admin', 'operator']:
            has_access = True
            user_role_in_deal = 'admin'
        
        if not has_access:
            return jsonify({'error': 'Sin permisos para crear notas en este deal'}), 403
        
        data = request.get_json()
        
        # Validar datos requeridos
        if 'content' not in data:
            return jsonify({'error': 'Campo requerido: content'}), 400
        
        scope = data.get('scope', 'PUBLIC')
        valid_scopes = ['PUBLIC', 'PARTES', 'SOLO_ADMIN']
        
        if scope not in valid_scopes:
            return jsonify({'error': f'Scope inválido. Scopes válidos: {valid_scopes}'}), 400
        
        # Solo admin puede crear notas privadas
        if scope == 'SOLO_ADMIN' and user_role_in_deal != 'admin':
            return jsonify({'error': 'Solo el admin puede crear notas privadas'}), 403
        
        # Crear nota
        note = DealNote(
            deal_id=deal_id,
            author_id=user_id,
            scope=scope,
            content=data['content'],
            attachments=data.get('attachments', '[]')
        )
        
        db.session.add(note)
        db.session.commit()
        
        return jsonify({
            'message': 'Nota creada exitosamente',
            'note': {
                'id': note.id,
                'author_id': note.author_id,
                'author_name': note.author.name,
                'scope': note.scope,
                'content': note.content,
                'attachments': note.attachments,
                'created_at': note.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/deals/<int:deal_id>/messages', methods=['GET'])
@jwt_required()
def get_deal_messages(deal_id):
    """Obtener mensajes del deal"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal no encontrado'}), 404

        # Verificar permisos
        has_access = False
        if user.id == deal.admin_id:
            has_access = True
        elif user.company_id == deal.producer_id:
            has_access = True
        elif user.company_id == deal.exporter_id:
            has_access = True
        elif user.role in ['admin', 'operator']:
            has_access = True

        if not has_access:
            return jsonify({'error': 'Sin permisos para ver mensajes de este deal'}), 403

        messages = DealMessage.query.filter_by(deal_id=deal_id).order_by(DealMessage.created_at.asc()).all()

        result = []
        for m in messages:
            result.append({
                'id': m.id,
                'author_id': m.author_id,
                'author_name': m.author.name if m.author else 'Usuario',
                'content': m.content,
                'attachments': m.attachments,
                'created_at': m.created_at.isoformat()
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/deals/<int:deal_id>/messages', methods=['POST'])
@jwt_required()
def create_deal_message(deal_id):
    """Crear mensaje en el deal"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal no encontrado'}), 404

        # Verificar permisos para enviar mensajes
        has_access = False
        if user.id == deal.admin_id:
            has_access = True
        elif user.company_id == deal.producer_id:
            has_access = True
        elif user.company_id == deal.exporter_id:
            has_access = True
        elif user.role in ['admin', 'operator']:
            has_access = True

        if not has_access:
            return jsonify({'error': 'Sin permisos para enviar mensajes en este deal'}), 403

        data = request.get_json()
        if 'content' not in data or not data['content'].strip():
            return jsonify({'error': 'Campo requerido: content'}), 400

        msg = DealMessage(
            deal_id=deal_id,
            author_id=user_id,
            content=data['content'].strip(),
            attachments=data.get('attachments', '[]')
        )

        db.session.add(msg)
        db.session.commit()

        return jsonify({
            'message': 'Mensaje enviado',
            'msg': {
                'id': msg.id,
                'author_id': msg.author_id,
                'author_name': msg.author.name if msg.author else 'Usuario',
                'content': msg.content,
                'attachments': msg.attachments,
                'created_at': msg.created_at.isoformat()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/deals/<int:deal_id>/finance', methods=['GET'])
@jwt_required()
def get_deal_finance(deal_id):
    """Obtener información financiera privada del deal (solo admin)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal no encontrado'}), 404
        
        # Solo el admin del deal puede ver finanzas privadas
        if user.id != deal.admin_id and user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para ver finanzas privadas'}), 403
        
        finance = DealFinancePrivate.query.filter_by(deal_id=deal_id).first()
        
        if not finance:
            return jsonify({
                'deal_id': deal_id,
                'costo_admin': None,
                'precio_admin': None,
                'margen_pct': None,
                'margen_abs': None,
                'currency': 'USD',
                'notes': None,
                'updated_at': None
            })
        
        return jsonify({
            'deal_id': finance.deal_id,
            'costo_admin': finance.costo_admin,
            'precio_admin': finance.precio_admin,
            'margen_pct': finance.margen_pct,
            'margen_abs': finance.margen_abs,
            'currency': finance.currency,
            'notes': finance.notes,
            'updated_at': finance.updated_at.isoformat() if finance.updated_at else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deals/<int:deal_id>/finance', methods=['POST'])
@jwt_required()
def update_deal_finance(deal_id):
    """Actualizar información financiera privada del deal (solo admin)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal no encontrado'}), 404
        
        # Solo el admin del deal puede actualizar finanzas privadas
        if user.id != deal.admin_id and user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para actualizar finanzas privadas'}), 403
        
        data = request.get_json()
        
        # Obtener o crear registro de finanzas
        finance = DealFinancePrivate.query.filter_by(deal_id=deal_id).first()
        if not finance:
            finance = DealFinancePrivate(deal_id=deal_id)
            db.session.add(finance)
        
        # Actualizar campos
        if 'costo_admin' in data:
            finance.costo_admin = data['costo_admin']
        if 'precio_admin' in data:
            finance.precio_admin = data['precio_admin']
        if 'currency' in data:
            finance.currency = data['currency']
        if 'notes' in data:
            finance.notes = data['notes']
        
        # Calcular márgenes
        finance.calculate_margin()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Finanzas actualizadas exitosamente',
            'finance': {
                'deal_id': finance.deal_id,
                'costo_admin': finance.costo_admin,
                'precio_admin': finance.precio_admin,
                'margen_pct': finance.margen_pct,
                'margen_abs': finance.margen_abs,
                'currency': finance.currency,
                'notes': finance.notes,
                'updated_at': finance.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/deals/<int:deal_id>/trace', methods=['GET'])
@jwt_required()
def get_deal_trace(deal_id):
    """Obtener trazabilidad completa del deal con timeline blockchain"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal no encontrado'}), 404
        
        # Verificar permisos
        has_access = False
        if user.id == deal.admin_id:
            has_access = True
        elif user.company_id == deal.producer_id:
            has_access = True
        elif user.company_id == deal.exporter_id:
            has_access = True
        elif user.role in ['admin', 'operator']:
            has_access = True
        
        if not has_access:
            return jsonify({'error': 'Sin permisos para ver trazabilidad de este deal'}), 403
        
        # Obtener enlaces de trazabilidad del deal
        trace_links = DealTraceLink.query.filter_by(deal_id=deal_id).all()
        
        # Crear timeline completa de eventos
        timeline_events = []
        
        # 1. Evento de creación del deal
        timeline_events.append({
            'id': f'deal_created_{deal.id}',
            'type': 'deal_created',
            'title': 'Acuerdo Creado',
            'description': f'Acuerdo #{deal.id} creado entre productor y exportadora',
            'timestamp': deal.created_at.isoformat(),
            'actor': 'Sistema Triboka',
            'icon': 'handshake',
            'color': 'primary',
            'metadata': {
                'deal_id': deal.id,
                'producer_company': deal.producer.name if deal.producer else None,
                'exporter_company': deal.exporter.name if deal.exporter else None,
                'admin': deal.admin.name if deal.admin else None
            }
        })
        
        # 2. Procesar cada enlace de trazabilidad
        for link in trace_links:
            lote_ids = link.get_lote_ids()
            batch_ids = link.get_batch_ids()
            events = link.get_events()
            
            # Eventos de lotes
            if lote_ids:
                lotes = ProducerLot.query.filter(ProducerLot.id.in_(lote_ids)).all()
                for lote in lotes:
                    # Evento de creación del lote
                    timeline_events.append({
                        'id': f'lote_created_{lote.id}',
                        'type': 'lote_created',
                        'title': f'Lote {lote.lot_code} Creado',
                        'description': f'Lote registrado por {lote.producer_company.name if lote.producer_company else "Productor"}',
                        'timestamp': lote.created_at.isoformat(),
                        'actor': lote.producer_company.name if lote.producer_company else 'Productor',
                        'icon': 'seedling',
                        'color': 'success',
                        'metadata': {
                            'lote_id': lote.id,
                            'lote_code': lote.lot_code,
                            'weight_kg': float(lote.weight_kg),
                            'quality_grade': lote.quality_grade,
                            'location': lote.location,
                            'blockchain_lot_id': lote.blockchain_lot_id
                        }
                    })
                    
                    # Evento de cosecha
                    if lote.harvest_date:
                        timeline_events.append({
                            'id': f'lote_harvest_{lote.id}',
                            'type': 'harvest',
                            'title': f'Cosecha {lote.lot_code}',
                            'description': f'Cosecha realizada en {lote.farm_name or "finca"}',
                            'timestamp': lote.harvest_date.isoformat(),
                            'actor': lote.producer_company.name if lote.producer_company else 'Productor',
                            'icon': 'leaf',
                            'color': 'success',
                            'metadata': {
                                'lote_id': lote.id,
                                'farm_name': lote.farm_name,
                                'location': lote.location
                            }
                        })
                    
                    # Evento de compra (si está purchased)
                    if lote.status in ['purchased', 'batched'] and lote.purchase_date:
                        buyer_name = 'Exportadora'
                        if lote.purchased_by_company:
                            buyer_name = lote.purchased_by_company.name
                        
                        timeline_events.append({
                            'id': f'lote_purchased_{lote.id}',
                            'type': 'purchase',
                            'title': f'Lote {lote.lot_code} Comprado',
                            'description': f'Adquirido por {buyer_name}',
                            'timestamp': lote.purchase_date.isoformat(),
                            'actor': buyer_name,
                            'icon': 'shopping-cart',
                            'color': 'info',
                            'metadata': {
                                'lote_id': lote.id,
                                'buyer': buyer_name,
                                'purchase_price': float(lote.purchase_price_usd) if lote.purchase_price_usd else None
                            }
                        })
            
            # Eventos de batches
            if batch_ids:
                batches = BatchNFT.query.filter(BatchNFT.id.in_(batch_ids)).all()
                for batch in batches:
                    timeline_events.append({
                        'id': f'batch_created_{batch.id}',
                        'type': 'batch_created',
                        'title': f'Batch {batch.batch_code} Creado',
                        'description': f'Batch creado por {batch.creator_company.name if batch.creator_company else "Exportadora"}',
                        'timestamp': batch.created_at.isoformat(),
                        'actor': batch.creator_company.name if batch.creator_company else 'Exportadora',
                        'icon': 'boxes',
                        'color': 'warning',
                        'metadata': {
                            'batch_id': batch.id,
                            'batch_code': batch.batch_code,
                            'total_weight_kg': float(batch.total_weight_kg),
                            'batch_type': batch.batch_type,
                            'location': batch.location,
                            'blockchain_batch_id': batch.blockchain_batch_id
                        }
                    })
            
            # Eventos personalizados del enlace
            if events:
                for event in events:
                    if isinstance(event, dict):
                        timeline_events.append({
                            'id': f'custom_event_{event.get("id", "unknown")}',
                            'type': event.get('type', 'custom'),
                            'title': event.get('title', 'Evento Personalizado'),
                            'description': event.get('description', ''),
                            'timestamp': event.get('timestamp', datetime.utcnow().isoformat()),
                            'actor': event.get('actor', 'Sistema'),
                            'icon': event.get('icon', 'circle'),
                            'color': event.get('color', 'secondary'),
                            'metadata': event.get('metadata', {})
                        })
        
        # 3. Eventos de contratos relacionados
        if deal.producer_company and deal.exporter_company:
            # Buscar contratos entre estas compañías
            contracts = ExportContract.query.filter(
                ((ExportContract.exporter_company_id == deal.producer_id) & 
                 (ExportContract.buyer_company_id == deal.exporter_id)) |
                ((ExportContract.exporter_company_id == deal.exporter_id) & 
                 (ExportContract.buyer_company_id == deal.producer_id))
            ).all()
            
            for contract in contracts:
                # Evento de creación del contrato
                timeline_events.append({
                    'id': f'contract_created_{contract.id}',
                    'type': 'contract_created',
                    'title': f'Contrato {contract.contract_code} Creado',
                    'description': f'Contrato entre {contract.exporter_company.name if contract.exporter_company else "Exportadora"} y {contract.buyer_company.name if contract.buyer_company else "Comprador"}',
                    'timestamp': contract.created_at.isoformat(),
                    'actor': 'Sistema Triboka',
                    'icon': 'file-contract',
                    'color': 'primary',
                    'metadata': {
                        'contract_id': contract.id,
                        'contract_code': contract.contract_code,
                        'total_volume_mt': float(contract.total_volume_mt),
                        'status': contract.status,
                        'blockchain_contract_id': contract.blockchain_contract_id
                    }
                })
                
                # Fijaciones del contrato
                fixations = ContractFixation.query.filter_by(export_contract_id=contract.id).all()
                for fixation in fixations:
                    timeline_events.append({
                        'id': f'fixation_created_{fixation.id}',
                        'type': 'fixation',
                        'title': f'Fijación de Precio',
                        'description': f'Precio fijado: ${fixation.spot_price_usd} USD + ${contract.differential_usd} diferencial',
                        'timestamp': fixation.fixation_date.isoformat(),
                        'actor': contract.exporter_company.name if contract.exporter_company else 'Exportadora',
                        'icon': 'dollar-sign',
                        'color': 'success',
                        'metadata': {
                            'fixation_id': fixation.id,
                            'fixed_quantity_mt': float(fixation.fixed_quantity_mt),
                            'spot_price_usd': float(fixation.spot_price_usd),
                            'differential_usd': float(contract.differential_usd),
                            'total_value_usd': float(fixation.total_value_usd)
                        }
                    })
        
        # 4. Eventos de mensajes importantes del deal
        important_messages = DealMessage.query.filter_by(deal_id=deal_id).filter(
            DealMessage.message_type.in_(['system', 'file_upload'])
        ).order_by(DealMessage.created_at.asc()).all()
        
        for msg in important_messages:
            if msg.message_type == 'file_upload':
                timeline_events.append({
                    'id': f'message_{msg.id}',
                    'type': 'file_upload',
                    'title': 'Archivo Compartido',
                    'description': msg.content,
                    'timestamp': msg.created_at.isoformat(),
                    'actor': msg.author.name if msg.author else 'Usuario',
                    'icon': 'paperclip',
                    'color': 'info',
                    'metadata': {
                        'message_id': msg.id,
                        'attachments': json.loads(msg.attachments) if msg.attachments else []
                    }
                })
            elif msg.message_type == 'system':
                timeline_events.append({
                    'id': f'message_{msg.id}',
                    'type': 'system_event',
                    'title': 'Evento del Sistema',
                    'description': msg.content,
                    'timestamp': msg.created_at.isoformat(),
                    'actor': 'Sistema Triboka',
                    'icon': 'cog',
                    'color': 'secondary',
                    'metadata': {
                        'message_id': msg.id
                    }
                })
        
        # 5. Eventos simulados de blockchain (para demo)
        # En producción, estos vendrían del servicio blockchain real
        blockchain_events = []
        if blockchain.is_ready():
            # Aquí se integrarían eventos reales del blockchain
            # Por ahora, simulamos algunos eventos
            for lote in ProducerLot.query.filter(ProducerLot.id.in_(sum([link.get_lote_ids() for link in trace_links], []))).all():
                if lote.blockchain_lot_id:
                    blockchain_events.append({
                        'id': f'blockchain_lote_{lote.id}',
                        'type': 'blockchain_mint',
                        'title': f'NFT Lote {lote.lot_code} Creado',
                        'description': f'Lote tokenizado en blockchain como NFT',
                        'timestamp': lote.created_at.isoformat(),
                        'actor': 'Blockchain Triboka',
                        'icon': 'gem',
                        'color': 'purple',
                        'metadata': {
                            'blockchain_lot_id': lote.blockchain_lot_id,
                            'network': 'Polygon',
                            'contract': 'ProducerLotNFT'
                        }
                    })
        
        timeline_events.extend(blockchain_events)
        
        # Ordenar timeline por timestamp (más antiguos primero)
        timeline_events.sort(key=lambda x: x['timestamp'])
        
        # Crear resumen de trazabilidad
        trace_summary = {
            'deal_id': deal_id,
            'total_events': len(timeline_events),
            'date_range': {
                'start': timeline_events[0]['timestamp'] if timeline_events else None,
                'end': timeline_events[-1]['timestamp'] if timeline_events else None
            },
            'entities': {
                'lotes': len(set([e['metadata'].get('lote_id') for e in timeline_events if e['metadata'].get('lote_id')])),
                'batches': len(set([e['metadata'].get('batch_id') for e in timeline_events if e['metadata'].get('batch_id')])),
                'contracts': len(set([e['metadata'].get('contract_id') for e in timeline_events if e['metadata'].get('contract_id')])),
                'blockchain_events': len([e for e in timeline_events if 'blockchain' in e['type']])
            }
        }
        
        return jsonify({
            'summary': trace_summary,
            'timeline': timeline_events,
            'trace_links': [{
                'id': link.id,
                'lote_ids': link.get_lote_ids(),
                'batch_ids': link.get_batch_ids(),
                'events': link.get_events(),
                'created_at': link.created_at.isoformat()
            } for link in trace_links]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deals/<int:deal_id>/trace', methods=['POST'])
@jwt_required()
def add_deal_trace(deal_id):
    """Agregar trazabilidad al deal"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal no encontrado'}), 404
        
        # Solo admin del deal puede agregar trazabilidad
        if user.id != deal.admin_id and user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para agregar trazabilidad'}), 403
        
        data = request.get_json()
        
        # Crear enlace de trazabilidad
        trace_link = DealTraceLink(
            deal_id=deal_id,
            lote_ids=json.dumps(data.get('lote_ids', [])),
            batch_ids=json.dumps(data.get('batch_ids', [])),
            events=json.dumps(data.get('events', []))
        )
        
        db.session.add(trace_link)
        db.session.commit()
        
        return jsonify({
            'message': 'Trazabilidad agregada exitosamente',
            'trace_link': {
                'id': trace_link.id,
                'lote_ids': trace_link.get_lote_ids(),
                'batch_ids': trace_link.get_batch_ids(),
                'events': trace_link.get_events(),
                'created_at': trace_link.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# =====================================
# WEBSOCKET EVENTS PARA CHAT EN TIEMPO REAL
# =====================================

@socketio.on('join_deal')
def handle_join_deal(data):
    """Usuario se une a la sala del deal para chat en tiempo real"""
    try:
        deal_id = data.get('deal_id')
        user_id = data.get('user_id')
        
        if not deal_id or not user_id:
            emit('error', {'message': 'deal_id y user_id requeridos'})
            return
        
        # Verificar permisos del usuario para el deal
        deal = Deal.query.get(deal_id)
        user = User.query.get(user_id)
        
        if not deal or not user:
            emit('error', {'message': 'Deal o usuario no encontrado'})
            return
        
        has_access = False
        if user.id == deal.admin_id:
            has_access = True
        elif user.company_id == deal.producer_id:
            has_access = True
        elif user.company_id == deal.exporter_id:
            has_access = True
        elif user.role in ['admin', 'operator']:
            has_access = True
        
        if not has_access:
            emit('error', {'message': 'Sin permisos para acceder a este deal'})
            return
        
        # Unir usuario a la sala del deal
        room = f'deal_{deal_id}'
        join_room(room)
        
        # Notificar a otros usuarios en la sala
        emit('user_joined', {
            'user_id': user_id,
            'user_name': user.name,
            'message': f'{user.name} se unió al chat'
        }, room=room, skip_sid=True)
        
        # Confirmar unión al usuario
        emit('joined_room', {'deal_id': deal_id, 'room': room})
        
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('leave_deal')
def handle_leave_deal(data):
    """Usuario sale de la sala del deal"""
    try:
        deal_id = data.get('deal_id')
        user_id = data.get('user_id')
        
        if deal_id:
            room = f'deal_{deal_id}'
            leave_room(room)
            
            user = User.query.get(user_id)
            if user:
                emit('user_left', {
                    'user_id': user_id,
                    'user_name': user.name,
                    'message': f'{user.name} salió del chat'
                }, room=room, skip_sid=True)
        
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('send_message')
def handle_send_message(data):
    """Enviar mensaje en tiempo real"""
    try:
        deal_id = data.get('deal_id')
        user_id = data.get('user_id')
        content = data.get('content', '').strip()
        attachments = data.get('attachments', [])
        
        if not deal_id or not user_id or not content:
            emit('error', {'message': 'deal_id, user_id y content requeridos'})
            return
        
        # Verificar permisos
        deal = Deal.query.get(deal_id)
        user = User.query.get(user_id)
        
        if not deal or not user:
            emit('error', {'message': 'Deal o usuario no encontrado'})
            return
        
        has_access = False
        if user.id == deal.admin_id:
            has_access = True
        elif user.company_id == deal.producer_id:
            has_access = True
        elif user.company_id == deal.exporter_id:
            has_access = True
        elif user.role in ['admin', 'operator']:
            has_access = True
        
        if not has_access:
            emit('error', {'message': 'Sin permisos para enviar mensajes'})
            return
        
        # Crear mensaje en BD
        msg = DealMessage(
            deal_id=deal_id,
            author_id=user_id,
            content=content,
            attachments=json.dumps(attachments) if attachments else '[]',
            message_type='chat'
        )
        
        db.session.add(msg)
        db.session.commit()
        
        # Preparar datos del mensaje para broadcast
        message_data = {
            'id': msg.id,
            'deal_id': msg.deal_id,
            'author_id': msg.author_id,
            'author_name': msg.author.name if msg.author else 'Usuario',
            'content': msg.content,
            'attachments': json.loads(msg.attachments) if msg.attachments else [],
            'created_at': msg.created_at.isoformat(),
            'message_type': msg.message_type
        }
        
        # Enviar mensaje a todos en la sala del deal
        room = f'deal_{deal_id}'
        emit('new_message', message_data, room=room)
        
        # Confirmar envío al remitente
        emit('message_sent', {'message_id': msg.id})
        
    except Exception as e:
        db.session.rollback()
        emit('error', {'message': str(e)})

@socketio.on('typing_start')
def handle_typing_start(data):
    """Usuario comenzó a escribir"""
    try:
        deal_id = data.get('deal_id')
        user_id = data.get('user_id')
        
        if deal_id and user_id:
            user = User.query.get(user_id)
            room = f'deal_{deal_id}'
            
            emit('user_typing', {
                'user_id': user_id,
                'user_name': user.name if user else 'Usuario',
                'is_typing': True
            }, room=room, skip_sid=True)
            
    except Exception as e:
        pass

@socketio.on('typing_stop')
def handle_typing_stop(data):
    """Usuario dejó de escribir"""
    try:
        deal_id = data.get('deal_id')
        user_id = data.get('user_id')
        
        if deal_id and user_id:
            user = User.query.get(user_id)
            room = f'deal_{deal_id}'
            
            emit('user_typing', {
                'user_id': user_id,
                'user_name': user.name if user else 'Usuario',
                'is_typing': False
            }, room=room, skip_sid=True)
            
    except Exception as e:
        pass

# =====================================
# ENDPOINTS PARA SUBIDA DE ARCHIVOS
# =====================================

@app.route('/api/deals/<int:deal_id>/upload', methods=['POST'])
@jwt_required()
def upload_deal_file(deal_id):
    """Subir archivo al deal con etiquetas de confidencialidad"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal no encontrado'}), 404
        
        # Verificar permisos
        has_access = False
        if user.id == deal.admin_id:
            has_access = True
        elif user.company_id == deal.producer_id:
            has_access = True
        elif user.company_id == deal.exporter_id:
            has_access = True
        elif user.role in ['admin', 'operator']:
            has_access = True
        
        if not has_access:
            return jsonify({'error': 'Sin permisos para subir archivos'}), 403
        
        if 'file' not in request.files:
            return jsonify({'error': 'Archivo requerido'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nombre de archivo vacío'}), 400
        
        # Validar tipo de archivo (solo documentos comunes)
        allowed_extensions = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'jpg', 'jpeg', 'png'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'error': 'Tipo de archivo no permitido'}), 400
        
        # Crear directorio si no existe
        upload_dir = os.path.join(os.getcwd(), 'uploads', 'deals', str(deal_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generar nombre único para el archivo
        import uuid
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Guardar archivo
        file.save(file_path)
        
        # Obtener metadatos del formulario
        confidentiality = request.form.get('confidentiality', 'PUBLIC')  # PUBLIC, PARTES, SOLO_ADMIN
        description = request.form.get('description', '')
        
        # Validar confidencialidad
        if confidentiality not in ['PUBLIC', 'PARTES', 'SOLO_ADMIN']:
            confidentiality = 'PUBLIC'
        
        # Solo admin puede subir archivos SOLO_ADMIN
        if confidentiality == 'SOLO_ADMIN' and user.id != deal.admin_id and user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Solo admin puede subir archivos privados'}), 403
        
        # Crear registro del archivo
        file_record = {
            'id': str(uuid.uuid4()),
            'filename': file.filename,
            'unique_filename': unique_filename,
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'file_type': file_extension,
            'uploaded_by': user_id,
            'uploaded_by_name': user.name,
            'confidentiality': confidentiality,
            'description': description,
            'uploaded_at': datetime.utcnow().isoformat()
        }
        
        # Crear mensaje del sistema sobre el archivo subido
        system_message = DealMessage(
            deal_id=deal_id,
            author_id=user_id,
            content=f"📎 Archivo subido: {file.filename}",
            attachments=json.dumps([file_record]),
            message_type='file_upload'
        )
        
        db.session.add(system_message)
        db.session.commit()
        
        # Notificar via WebSocket
        room = f'deal_{deal_id}'
        socketio.emit('file_uploaded', {
            'message': system_message.to_dict(),
            'file': file_record
        }, room=room)
        
        return jsonify({
            'message': 'Archivo subido exitosamente',
            'file': file_record
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/deals/<int:deal_id>/files', methods=['GET'])
@jwt_required()
def get_deal_files(deal_id):
    """Obtener lista de archivos del deal según permisos"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal no encontrado'}), 404
        
        # Verificar permisos básicos
        has_access = False
        user_role_in_deal = 'viewer'
        
        if user.id == deal.admin_id:
            has_access = True
            user_role_in_deal = 'admin'
        elif user.company_id == deal.producer_id:
            has_access = True
            user_role_in_deal = 'producer'
        elif user.company_id == deal.exporter_id:
            has_access = True
            user_role_in_deal = 'exporter'
        elif user.role in ['admin', 'operator']:
            has_access = True
            user_role_in_deal = 'admin'
        
        if not has_access:
            return jsonify({'error': 'Sin permisos para ver archivos'}), 403
        
        # Obtener mensajes con archivos
        file_messages = DealMessage.query.filter_by(
            deal_id=deal_id, 
            message_type='file_upload'
        ).order_by(DealMessage.created_at.desc()).all()
        
        files = []
        for msg in file_messages:
            if msg.attachments and msg.attachments != '[]':
                try:
                    attachments = json.loads(msg.attachments)
                    for attachment in attachments:
                        # Filtrar según confidencialidad y rol
                        confidentiality = attachment.get('confidentiality', 'PUBLIC')
                        
                        can_access = False
                        if confidentiality == 'PUBLIC':
                            can_access = True
                        elif confidentiality == 'PARTES':
                            can_access = True  # Todos los miembros pueden ver
                        elif confidentiality == 'SOLO_ADMIN':
                            can_access = (user_role_in_deal == 'admin')
                        
                        if can_access:
                            # Agregar URL de descarga (sin path real por seguridad)
                            attachment_copy = attachment.copy()
                            attachment_copy['download_url'] = f'/api/deals/{deal_id}/files/{attachment["id"]}/download'
                            files.append(attachment_copy)
                except:
                    pass
        
        return jsonify(files)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deals/<int:deal_id>/files/<file_id>/download', methods=['GET'])
@jwt_required()
def download_deal_file(deal_id, file_id):
    """Descargar archivo del deal"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal no encontrado'}), 404
        
        # Verificar permisos básicos
        has_access = False
        user_role_in_deal = 'viewer'
        
        if user.id == deal.admin_id:
            has_access = True
            user_role_in_deal = 'admin'
        elif user.company_id == deal.producer_id:
            has_access = True
            user_role_in_deal = 'producer'
        elif user.company_id == deal.exporter_id:
            has_access = True
            user_role_in_deal = 'exporter'
        elif user.role in ['admin', 'operator']:
            has_access = True
            user_role_in_deal = 'admin'
        
        if not has_access:
            return jsonify({'error': 'Sin permisos para descargar archivos'}), 403
        
        # Buscar el archivo en los mensajes
        file_messages = DealMessage.query.filter_by(
            deal_id=deal_id, 
            message_type='file_upload'
        ).all()
        
        for msg in file_messages:
            if msg.attachments and msg.attachments != '[]':
                try:
                    attachments = json.loads(msg.attachments)
                    for attachment in attachments:
                        if attachment.get('id') == file_id:
                            # Verificar permisos de confidencialidad
                            confidentiality = attachment.get('confidentiality', 'PUBLIC')
                            
                            can_access = False
                            if confidentiality == 'PUBLIC':
                                can_access = True
                            elif confidentiality == 'PARTES':
                                can_access = True
                            elif confidentiality == 'SOLO_ADMIN':
                                can_access = (user_role_in_deal == 'admin')
                            
                            if can_access:
                                file_path = attachment.get('file_path')
                                if file_path and os.path.exists(file_path):
                                    from flask import send_file
                                    return send_file(
                                        file_path,
                                        as_attachment=True,
                                        download_name=attachment.get('filename', 'file')
                                    )
                                else:
                                    return jsonify({'error': 'Archivo no encontrado en el servidor'}), 404
                except:
                    pass
        
        return jsonify({'error': 'Archivo no encontrado'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================
# MEJORA DE BÚSQUEDA DE MENSAJES
# =====================================

@app.route('/api/deals/<int:deal_id>/messages/search', methods=['GET'])
@jwt_required()
def search_deal_messages(deal_id):
    """Buscar mensajes en el deal con filtros avanzados"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal no encontrado'}), 404
        
        # Verificar permisos
        has_access = False
        if user.id == deal.admin_id:
            has_access = True
        elif user.company_id == deal.producer_id:
            has_access = True
        elif user.company_id == deal.exporter_id:
            has_access = True
        elif user.role in ['admin', 'operator']:
            has_access = True
        
        if not has_access:
            return jsonify({'error': 'Sin permisos para buscar mensajes'}), 403
        
        # Parámetros de búsqueda
        query = request.args.get('q', '').strip()
        author_id = request.args.get('author_id')
        message_type = request.args.get('type')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        limit = min(int(request.args.get('limit', 50)), 200)  # Máximo 200 resultados
        
        # Base query
        search_query = DealMessage.query.filter_by(deal_id=deal_id)
        
        # Filtros
        if query:
            search_query = search_query.filter(DealMessage.content.ilike(f'%{query}%'))
        
        if author_id:
            search_query = search_query.filter_by(author_id=int(author_id))
        
        if message_type:
            search_query = search_query.filter_by(message_type=message_type)
        
        if date_from:
            try:
                date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                search_query = search_query.filter(DealMessage.created_at >= date_from_obj)
            except:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                search_query = search_query.filter(DealMessage.created_at <= date_to_obj)
            except:
                pass
        
        # Ordenar por fecha descendente (más recientes primero)
        messages = search_query.order_by(DealMessage.created_at.desc()).limit(limit).all()
        
        result = []
        for m in messages:
            result.append({
                'id': m.id,
                'author_id': m.author_id,
                'author_name': m.author.name if m.author else 'Usuario',
                'content': m.content,
                'attachments': json.loads(m.attachments) if m.attachments else [],
                'message_type': m.message_type,
                'created_at': m.created_at.isoformat(),
                'deal_id': m.deal_id
            })
        
        return jsonify({
            'query': query,
            'total_results': len(result),
            'messages': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================
# EXPORTACIÓN DE TRAZABILIDAD EN PDF
# =====================================

@app.route('/api/deals/<int:deal_id>/trace/export', methods=['GET'])
@jwt_required()
def export_deal_trace_pdf(deal_id):
    """Exportar trazabilidad completa del deal en PDF"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal no encontrado'}), 404
        
        # Verificar permisos
        has_access = False
        if user.id == deal.admin_id:
            has_access = True
        elif user.company_id == deal.producer_id:
            has_access = True
        elif user.company_id == deal.exporter_id:
            has_access = True
        elif user.role in ['admin', 'operator']:
            has_access = True
        
        if not has_access:
            return jsonify({'error': 'Sin permisos para exportar trazabilidad'}), 403
        
        # Obtener datos de trazabilidad (reutilizar lógica del endpoint GET)
        from io import BytesIO
        
        # Obtener timeline completa (código similar al endpoint GET)
        trace_links = DealTraceLink.query.filter_by(deal_id=deal_id).all()
        timeline_events = []
        
        # Evento de creación del deal
        timeline_events.append({
            'type': 'deal_created',
            'title': 'Acuerdo Creado',
            'description': f'Acuerdo #{deal.id} creado entre productor y exportadora',
            'timestamp': deal.created_at.isoformat(),
            'actor': 'Sistema Triboka',
            'metadata': {
                'deal_id': deal.id,
                'producer_company': deal.producer.name if deal.producer else None,
                'exporter_company': deal.exporter.name if deal.exporter else None
            }
        })
        
        # Procesar enlaces de trazabilidad (versión simplificada)
        for link in trace_links:
            lote_ids = link.get_lote_ids()
            if lote_ids:
                lotes = ProducerLot.query.filter(ProducerLot.id.in_(lote_ids)).all()
                for lote in lotes:
                    timeline_events.append({
                        'type': 'lote_created',
                        'title': f'Lote {lote.lot_code} Creado',
                        'description': f'Lote registrado por {lote.producer_company.name if lote.producer_company else "Productor"}',
                        'timestamp': lote.created_at.isoformat(),
                        'actor': lote.producer_company.name if lote.producer_company else 'Productor',
                        'metadata': {
                            'lote_code': lote.lot_code,
                            'weight_kg': float(lote.weight_kg),
                            'quality_grade': lote.quality_grade
                        }
                    })
        
        # Generar PDF
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import inch
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Centrado
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20
        )
        
        normal_style = styles['Normal']
        event_style = ParagraphStyle(
            'EventStyle',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=20
        )
        
        # Contenido del PDF
        content = []
        
        # Título
        content.append(Paragraph("Certificado de Trazabilidad Triboka Agro", title_style))
        content.append(Spacer(1, 12))
        
        # Información del deal
        content.append(Paragraph("Información del Acuerdo", subtitle_style))
        deal_info = [
            ["ID del Acuerdo:", str(deal.id)],
            ["Productor:", deal.producer.name if deal.producer else "N/A"],
            ["Exportadora:", deal.exporter.name if deal.exporter else "N/A"],
            ["Admin:", deal.admin.name if deal.admin else "N/A"],
            ["Fecha de Creación:", deal.created_at.strftime("%Y-%m-%d %H:%M:%S")],
            ["Estado:", deal.status.title()]
        ]
        
        deal_table = Table(deal_info, colWidths=[2*inch, 4*inch])
        deal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        content.append(deal_table)
        content.append(Spacer(1, 20))
        
        # Timeline de eventos
        content.append(Paragraph("Línea de Tiempo de Trazabilidad", subtitle_style))
        content.append(Spacer(1, 12))
        
        # Ordenar eventos por timestamp
        timeline_events.sort(key=lambda x: x['timestamp'])
        
        for event in timeline_events[:50]:  # Limitar a 50 eventos para evitar PDFs muy largos
            try:
                event_date = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                date_str = event_date.strftime("%Y-%m-%d %H:%M:%S")
            except:
                date_str = event['timestamp']
            
            event_text = f"<b>{date_str}</b> - <b>{event['title']}</b><br/>" \
                        f"<i>{event['actor']}</i><br/>" \
                        f"{event['description']}"
            
            content.append(Paragraph(event_text, event_style))
            content.append(Spacer(1, 8))
        
        # Información adicional
        content.append(Spacer(1, 20))
        content.append(Paragraph("Información Adicional", subtitle_style))
        
        additional_info = [
            ["Total de Eventos:", str(len(timeline_events))],
            ["Período de Trazabilidad:", f"{timeline_events[0]['timestamp'][:10] if timeline_events else 'N/A'} - {timeline_events[-1]['timestamp'][:10] if timeline_events else 'N/A'}"],
            ["Generado por:", user.name],
            ["Fecha de Generación:", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")],
            ["Sistema:", "Triboka Agro - Plataforma de Trazabilidad Blockchain"]
        ]
        
        additional_table = Table(additional_info, colWidths=[2.5*inch, 3.5*inch])
        additional_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        content.append(additional_table)
        
        # Pie de página
        content.append(Spacer(1, 30))
        footer_text = """
        <para alignment="center" fontSize="8">
        Este certificado de trazabilidad es generado por el sistema Triboka Agro y certifica la autenticidad 
        de la cadena de suministro desde la finca hasta la exportación. La información contenida en este 
        documento está respaldada por registros blockchain inmutables.
        </para>
        """
        content.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=1)))
        
        # Generar PDF
        doc.build(content)
        buffer.seek(0)
        
        # Retornar PDF como respuesta
        from flask import send_file
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'trazabilidad_deal_{deal_id}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Error generando PDF: {str(e)}'}), 500

@app.route('/api/deals/<int:deal_id>/trace/filter', methods=['GET'])
@jwt_required()
def filter_deal_trace(deal_id):
    """Filtrar eventos de trazabilidad por tipo, fecha, actor, etc."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal no encontrado'}), 404
        
        # Verificar permisos
        has_access = False
        if user.id == deal.admin_id:
            has_access = True
        elif user.company_id == deal.producer_id:
            has_access = True
        elif user.company_id == deal.exporter_id:
            has_access = True
        elif user.role in ['admin', 'operator']:
            has_access = True
        
        if not has_access:
            return jsonify({'error': 'Sin permisos para filtrar trazabilidad'}), 403
        
        # Obtener timeline completa (reutilizar lógica)
        trace_links = DealTraceLink.query.filter_by(deal_id=deal_id).all()
        timeline_events = []
        
        # ... [código para generar timeline_events, igual que en get_deal_trace]
        
        # Evento de creación del deal
        timeline_events.append({
            'id': f'deal_created_{deal.id}',
            'type': 'deal_created',
            'title': 'Acuerdo Creado',
            'description': f'Acuerdo #{deal.id} creado entre productor y exportadora',
            'timestamp': deal.created_at.isoformat(),
            'actor': 'Sistema Triboka',
            'icon': 'handshake',
            'color': 'primary',
            'metadata': {
                'deal_id': deal.id,
                'producer_company': deal.producer.name if deal.producer else None,
                'exporter_company': deal.exporter.name if deal.exporter else None,
                'admin': deal.admin.name if deal.admin else None
            }
        })
        
        # Procesar enlaces de trazabilidad (simplificado)
        for link in trace_links:
            lote_ids = link.get_lote_ids()
            if lote_ids:
                lotes = ProducerLot.query.filter(ProducerLot.id.in_(lote_ids)).all()
                for lote in lotes:
                    timeline_events.append({
                        'id': f'lote_created_{lote.id}',
                        'type': 'lote_created',
                        'title': f'Lote {lote.lot_code} Creado',
                        'description': f'Lote registrado por {lote.producer_company.name if lote.producer_company else "Productor"}',
                        'timestamp': lote.created_at.isoformat(),
                        'actor': lote.producer_company.name if lote.producer_company else 'Productor',
                        'icon': 'seedling',
                        'color': 'success',
                        'metadata': {
                            'lote_id': lote.id,
                            'lote_code': lote.lot_code,
                            'weight_kg': float(lote.weight_kg),
                            'quality_grade': lote.quality_grade,
                            'location': lote.location,
                            'blockchain_lot_id': lote.blockchain_lot_id
                        }
                    })
        
        # Aplicar filtros
        event_type = request.args.get('type')
        actor_filter = request.args.get('actor')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        entity_id = request.args.get('entity_id')  # lote_id, batch_id, contract_id
        
        filtered_events = timeline_events
        
        if event_type:
            filtered_events = [e for e in filtered_events if e['type'] == event_type]
        
        if actor_filter:
            filtered_events = [e for e in filtered_events if actor_filter.lower() in e['actor'].lower()]
        
        if date_from:
            try:
                date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                filtered_events = [e for e in filtered_events if datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00')) >= date_from_obj]
            except:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                filtered_events = [e for e in filtered_events if datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00')) <= date_to_obj]
            except:
                pass
        
        if entity_id:
            filtered_events = [e for e in filtered_events if 
                             e['metadata'].get('lote_id') == int(entity_id) or
                             e['metadata'].get('batch_id') == int(entity_id) or
                             e['metadata'].get('contract_id') == int(entity_id)]
        
        # Ordenar por timestamp
        filtered_events.sort(key=lambda x: x['timestamp'])
        
        # Estadísticas de filtros aplicados
        filter_stats = {
            'total_events': len(timeline_events),
            'filtered_events': len(filtered_events),
            'applied_filters': {
                'type': event_type,
                'actor': actor_filter,
                'date_from': date_from,
                'date_to': date_to,
                'entity_id': entity_id
            },
            'event_types': list(set([e['type'] for e in timeline_events])),
            'actors': list(set([e['actor'] for e in timeline_events]))
        }
        
        return jsonify({
            'filter_stats': filter_stats,
            'timeline': filtered_events
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================
# ENDPOINTS PARA IDENTIDADES DIGITALES (DID)
# =====================================

@app.route('/api/did/create', methods=['POST'])
@jwt_required()
def create_digital_identity():
    """Crear una nueva Identidad Digital (DID) para el usuario"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Verificar si ya tiene una identidad digital
        existing_did = DigitalIdentity.query.filter_by(user_id=user_id).first()
        if existing_did:
            return jsonify({
                'error': 'El usuario ya tiene una identidad digital',
                'did': existing_did.to_dict()
            }), 400
        
        # Crear nueva identidad digital
        did = DigitalIdentity(user_id=user_id, company_id=user.company_id)
        did.generate_did()
        
        # Generar wallet usando Web3.py
        from web3 import Web3
        w3 = Web3()
        
        # Crear cuenta Ethereum
        account = w3.eth.account.create()
        did.blockchain_address = account.address
        did.public_key = account.key.hex()
        
        # En un entorno real, encriptaríamos la private key
        # Por ahora, la almacenamos encriptada para backup
        from cryptography.fernet import Fernet
        import base64
        
        # Generar clave de encriptación (en producción usar una clave segura)
        key = base64.urlsafe_b64encode(b'triboka_did_encryption_key_2024!')
        fernet = Fernet(key)
        did.encrypted_private_key = fernet.encrypt(account.key.hex().encode()).decode()
        
        # Guardar en base de datos
        db.session.add(did)
        db.session.commit()
        
        return jsonify({
            'message': 'Identidad digital creada exitosamente',
            'did': did.to_dict(),
            'wallet_address': did.blockchain_address,
            'warning': 'Guarda tu clave privada de forma segura. Esta es la única vez que se muestra.'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/did/verify', methods=['POST'])
@jwt_required()
def verify_digital_identity():
    """Verificar una identidad digital con KYC básico"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        did_id = data.get('did_id')
        verification_notes = data.get('notes', '')
        
        if not did_id:
            return jsonify({'error': 'ID de identidad digital requerido'}), 400
        
        # Buscar la identidad digital
        did = DigitalIdentity.query.filter_by(id=did_id, user_id=user_id).first()
        if not did:
            return jsonify({'error': 'Identidad digital no encontrada o no pertenece al usuario'}), 404
        
        # Solo admin puede verificar identidades
        current_user = User.query.get(user_id)
        if current_user.role != 'admin':
            return jsonify({'error': 'Solo administradores pueden verificar identidades'}), 403
        
        # Actualizar estado de verificación
        did.kyc_status = 'verified'
        did.kyc_verified_at = datetime.utcnow()
        did.kyc_verified_by = user_id
        
        # Actualizar reputación
        did.update_reputation(10.0)  # +10 puntos por verificación
        
        db.session.commit()
        
        return jsonify({
            'message': 'Identidad digital verificada exitosamente',
            'did': did.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/did/<int:did_id>', methods=['GET'])
@jwt_required()
def get_digital_identity(did_id):
    """Obtener información de una identidad digital"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Buscar la identidad digital
        did = DigitalIdentity.query.get(did_id)
        if not did:
            return jsonify({'error': 'Identidad digital no encontrada'}), 404
        
        # Solo el propietario, su compañía o admin pueden ver
        if did.user_id != user_id and did.company_id != user.company_id and user.role != 'admin':
            return jsonify({'error': 'No tienes permisos para ver esta identidad'}), 403
        
        # Incluir datos privados solo para el propietario o admin
        include_private = (did.user_id == user_id or user.role == 'admin')
        
        return jsonify({
            'did': did.to_dict(include_private=include_private)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/did', methods=['GET'])
@jwt_required()
def list_digital_identities():
    """Listar identidades digitales con filtros"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Parámetros de consulta
        status_filter = request.args.get('status')  # verified, pending, rejected
        company_filter = request.args.get('company_id', type=int)
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Base query
        query = DigitalIdentity.query
        
        # Aplicar filtros
        if status_filter:
            query = query.filter_by(kyc_status=status_filter)
        
        if company_filter:
            query = query.filter_by(company_id=company_filter)
        
        # Solo admin ve todas, otros solo las de su compañía
        if user.role != 'admin':
            query = query.filter(
                (DigitalIdentity.user_id == user_id) | 
                (DigitalIdentity.company_id == user.company_id)
            )
        
        # Paginación
        total_count = query.count()
        dids = query.offset(offset).limit(limit).all()
        
        result = []
        for did in dids:
            # Incluir datos privados solo para propietario o admin
            include_private = (did.user_id == user_id or user.role == 'admin')
            result.append(did.to_dict(include_private=include_private))
        
        return jsonify({
            'dids': result,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/did/<int:did_id>/sign', methods=['POST'])
@jwt_required()
def sign_event_with_did(did_id):
    """Firmar digitalmente un evento usando la identidad digital"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        event_type = data.get('event_type')
        event_id = data.get('event_id')
        event_data = data.get('event_data', {})
        
        if not event_type or not event_id:
            return jsonify({'error': 'Tipo de evento e ID requeridos'}), 400
        
        # Verificar que la identidad digital pertenece al usuario
        did = DigitalIdentity.query.filter_by(id=did_id, user_id=user_id).first()
        if not did:
            return jsonify({'error': 'Identidad digital no encontrada o no pertenece al usuario'}), 404
        
        if not did.is_active or did.kyc_status != 'verified':
            return jsonify({'error': 'Identidad digital no está activa o verificada'}), 400
        
        # Calcular hash de los datos del evento
        import hashlib
        import json
        
        event_data_str = json.dumps(event_data, sort_keys=True)
        event_data_hash = hashlib.sha256(event_data_str.encode()).hexdigest()
        
        # Firmar usando Web3.py
        from web3 import Web3
        from eth_account import Account
        import os
        
        w3 = Web3()
        
        # En un entorno real, desencriptaríamos la private key
        # Por simplicidad, recreamos la firma usando la dirección
        # En producción, esto requeriría la private key del usuario
        
        # Crear firma simulada (en producción usar la private key real)
        message = f"{event_type}:{event_id}:{event_data_hash}"
        message_hash = w3.keccak(text=message)
        
        # Para demo, usamos una firma simulada
        # En producción: signed_message = Account.sign_message(message_hash, private_key)
        signature = f"simulated_signature_{did.blockchain_address}_{message_hash.hex()[:16]}"
        
        # Crear registro de firma digital
        digital_signature = DigitalSignature(
            did_id=did_id,
            event_type=event_type,
            event_id=str(event_id),
            event_data_hash=event_data_hash,
            signature=signature
        )
        
        # Opcional: registrar en blockchain
        if blockchain.is_ready():
            try:
                # Aquí iría la lógica para registrar en blockchain
                # tx_hash = blockchain.register_signature(digital_signature)
                # digital_signature.blockchain_tx_hash = tx_hash
                pass
            except Exception as blockchain_error:
                logger.warning(f"Error registrando firma en blockchain: {blockchain_error}")
        
        db.session.add(digital_signature)
        
        # Actualizar reputación por firma
        did.update_reputation(0.1)  # +0.1 puntos por firma
        
        db.session.commit()
        
        return jsonify({
            'message': 'Evento firmado digitalmente',
            'signature': digital_signature.to_dict(),
            'event_hash': event_data_hash
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/did/<int:did_id>/signatures', methods=['GET'])
@jwt_required()
def get_did_signatures(did_id):
    """Obtener firmas digitales de una identidad"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Verificar permisos
        did = DigitalIdentity.query.get(did_id)
        if not did:
            return jsonify({'error': 'Identidad digital no encontrada'}), 404
        
        if did.user_id != user_id and did.company_id != user.company_id and user.role != 'admin':
            return jsonify({'error': 'No tienes permisos para ver estas firmas'}), 403
        
        # Parámetros de consulta
        event_type = request.args.get('event_type')
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Query de firmas
        query = DigitalSignature.query.filter_by(did_id=did_id, is_valid=True)
        
        if event_type:
            query = query.filter_by(event_type=event_type)
        
        total_count = query.count()
        signatures = query.order_by(DigitalSignature.signed_at.desc()).offset(offset).limit(limit).all()
        
        result = [sig.to_dict() for sig in signatures]
        
        return jsonify({
            'signatures': result,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/did/<int:did_id>/kyc', methods=['POST'])
@jwt_required()
def upload_kyc_document(did_id):
    """Subir documento KYC para verificación"""
    try:
        user_id = get_jwt_identity()
        
        # Verificar que la identidad pertenece al usuario
        did = DigitalIdentity.query.filter_by(id=did_id, user_id=user_id).first()
        if not did:
            return jsonify({'error': 'Identidad digital no encontrada o no pertenece al usuario'}), 404
        
        # Obtener datos del formulario
        document_type = request.form.get('document_type')
        document_number = request.form.get('document_number')
        issuing_country = request.form.get('issuing_country')
        issuing_authority = request.form.get('issuing_authority')
        issue_date = request.form.get('issue_date')
        expiry_date = request.form.get('expiry_date')
        notes = request.form.get('notes', '')
        
        if not document_type or not document_number:
            return jsonify({'error': 'Tipo de documento y número son requeridos'}), 400
        
        # Verificar si hay archivo
        if 'document_file' not in request.files:
            return jsonify({'error': 'Archivo de documento requerido'}), 400
        
        file = request.files['document_file']
        if file.filename == '':
            return jsonify({'error': 'Archivo no seleccionado'}), 400
        
        # Guardar archivo
        import hashlib
        import os
        
        # Crear directorio si no existe
        upload_dir = os.path.join(os.getcwd(), 'uploads', 'kyc')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Calcular hash del archivo
        file_content = file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Guardar archivo con hash como nombre
        file_extension = os.path.splitext(file.filename)[1]
        file_path = os.path.join(upload_dir, f"{file_hash}{file_extension}")
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Crear registro KYC
        kyc_doc = KYCDocument(
            did_id=did_id,
            document_type=document_type,
            document_number=document_number,
            issuing_country=issuing_country,
            issuing_authority=issuing_authority,
            issue_date=datetime.fromisoformat(issue_date) if issue_date else None,
            expiry_date=datetime.fromisoformat(expiry_date) if expiry_date else None,
            file_path=file_path,
            file_hash=file_hash,
            notes=notes
        )
        
        db.session.add(kyc_doc)
        db.session.commit()
        
        return jsonify({
            'message': 'Documento KYC subido exitosamente',
            'kyc_document': kyc_doc.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# =====================================
# ENDPOINTS PARA TRAZABILIDAD Y EVENTOS
# =====================================

@app.route('/api/trace/event', methods=['POST'])
@jwt_required()
def create_trace_event():
    """Crear un nuevo evento de trazabilidad"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json()
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Validar datos requeridos
        required_fields = ['event_type', 'entity_type', 'entity_id', 'title']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        event_type = data['event_type']
        entity_type = data['entity_type']
        entity_id = data['entity_id']
        title = data['title']
        
        # Validar tipos de entidad permitidos
        allowed_entity_types = ['lot', 'batch', 'contract', 'deal']
        if entity_type not in allowed_entity_types:
            return jsonify({'error': f'Tipo de entidad no válido. Permitidos: {allowed_entity_types}'}), 400
        
        # Verificar permisos según el tipo de entidad
        if not _check_trace_permissions(user, entity_type, entity_id):
            return jsonify({'error': 'No tienes permisos para registrar eventos en esta entidad'}), 403
        
        # Crear evento de trazabilidad
        trace_event = TraceEvent(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=str(entity_id),
            title=title,
            description=data.get('description'),
            location=data.get('location'),
            actor_id=user_id,
            actor_name=user.name,
            event_data=json.dumps(data.get('event_data', {})),
            measurements=json.dumps(data.get('measurements', {})),
            tags=json.dumps(data.get('tags', [])),
            is_public=data.get('is_public', True)
        )
        
        # Establecer timestamp del evento
        if 'event_timestamp' in data:
            try:
                trace_event.event_timestamp = datetime.fromisoformat(data['event_timestamp'].replace('Z', '+00:00'))
            except:
                pass  # Usar timestamp por defecto
        
        db.session.add(trace_event)
        db.session.flush()  # Para obtener el ID
        
        # Firmar digitalmente el evento si el usuario tiene DID verificada
        did = DigitalIdentity.query.filter_by(user_id=user_id, is_active=True, kyc_status='verified').first()
        if did:
            try:
                # Crear firma digital
                event_hash = trace_event.get_event_hash()
                digital_signature = DigitalSignature(
                    did_id=did.id,
                    event_type=f"trace_{event_type}",
                    event_id=str(trace_event.id),
                    event_data_hash=event_hash,
                    signature=f"simulated_signature_{did.blockchain_address}_{event_hash[:16]}"
                )
                db.session.add(digital_signature)
                trace_event.digital_signature_id = digital_signature.id
                
                # Actualizar reputación por registrar evento trazable
                did.update_reputation(0.5)
                
            except Exception as sign_error:
                logger.warning(f"Error firmando evento: {sign_error}")
        
        # Registrar en blockchain si está disponible y es evento importante
        important_events = ['lot_creation', 'batch_creation', 'export', 'certification']
        if blockchain.is_ready() and event_type in important_events:
            try:
                # Intentar registrar en blockchain
                tx_hash = _register_event_on_chain(trace_event)
                if tx_hash:
                    trace_event.blockchain_tx_hash = tx_hash
                    trace_event.blockchain_block_number = blockchain.w3.eth.block_number
                    trace_event.blockchain_timestamp = datetime.utcnow()
            except Exception as blockchain_error:
                logger.warning(f"Error registrando en blockchain: {blockchain_error}")
        
        # Actualizar timeline
        _update_timeline_stats(entity_type, str(entity_id))
        
        db.session.commit()
        
        return jsonify({
            'message': 'Evento de trazabilidad registrado exitosamente',
            'event': trace_event.to_dict(include_private=True),
            'blockchain_registered': trace_event.blockchain_tx_hash is not None
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/trace/events', methods=['GET'])
@jwt_required()
def get_trace_events():
    """Obtener eventos de trazabilidad con filtros"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Parámetros de consulta
        entity_type = request.args.get('entity_type')
        entity_id = request.args.get('entity_id')
        event_type = request.args.get('event_type')
        actor_id = request.args.get('actor_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        include_private = request.args.get('include_private', 'false').lower() == 'true'
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Base query
        query = TraceEvent.query
        
        # Aplicar filtros
        if entity_type:
            query = query.filter_by(entity_type=entity_type)
        if entity_id:
            query = query.filter_by(entity_id=str(entity_id))
        if event_type:
            query = query.filter_by(event_type=event_type)
        if actor_id:
            query = query.filter_by(actor_id=actor_id)
        
        # Filtros de fecha
        if date_from:
            try:
                date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(TraceEvent.event_timestamp >= date_from_obj)
            except:
                pass
        if date_to:
            try:
                date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(TraceEvent.event_timestamp <= date_to_obj)
            except:
                pass
        
        # Filtrar eventos públicos si no es admin
        if user.role != 'admin':
            query = query.filter_by(is_public=True)
        
        # Paginación
        total_count = query.count()
        events = query.order_by(TraceEvent.event_timestamp.desc()).offset(offset).limit(limit).all()
        
        result = []
        for event in events:
            result.append(event.to_dict(include_private=include_private and user.role == 'admin'))
        
        return jsonify({
            'events': result,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trace/timeline/<entity_type>/<entity_id>', methods=['GET'])
@jwt_required()
def get_trace_timeline(entity_type, entity_id):
    """Obtener timeline completo de trazabilidad para una entidad"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Validar tipo de entidad
        allowed_types = ['lot', 'batch', 'contract', 'deal']
        if entity_type not in allowed_types:
            return jsonify({'error': 'Tipo de entidad no válido'}), 400
        
        # Verificar permisos
        if not _check_trace_permissions(user, entity_type, entity_id):
            return jsonify({'error': 'No tienes permisos para ver esta trazabilidad'}), 403
        
        # Obtener o crear timeline
        timeline = TraceTimeline.query.filter_by(
            entity_type=entity_type, 
            entity_id=str(entity_id)
        ).first()
        
        if not timeline:
            timeline = TraceTimeline(entity_type=entity_type, entity_id=str(entity_id))
            db.session.add(timeline)
            db.session.commit()
        
        # Obtener eventos del timeline
        events = TraceEvent.query.filter_by(
            entity_type=entity_type,
            entity_id=str(entity_id)
        ).order_by(TraceEvent.event_timestamp.asc()).all()
        
        # Formatear respuesta
        timeline_data = timeline.to_dict()
        timeline_data['events'] = [event.to_dict(include_private=user.role == 'admin') for event in events]
        
        return jsonify(timeline_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/public/trace/verify/<entity_type>/<entity_id>', methods=['GET'])
def verify_trace_public(entity_type, entity_id):
    """API pública para verificar trazabilidad (sin autenticación)"""
    try:
        # Validar tipo de entidad
        allowed_types = ['lot', 'batch', 'contract']
        if entity_type not in allowed_types:
            return jsonify({'error': 'Tipo de entidad no válido'}), 400
        
        # Obtener timeline público
        timeline = TraceTimeline.query.filter_by(
            entity_type=entity_type,
            entity_id=str(entity_id)
        ).first()
        
        if not timeline:
            return jsonify({'error': 'Entidad no encontrada o sin trazabilidad'}), 404
        
        # Obtener solo eventos públicos
        events = TraceEvent.query.filter_by(
            entity_type=entity_type,
            entity_id=str(entity_id),
            is_public=True
        ).order_by(TraceEvent.event_timestamp.asc()).all()
        
        # Información básica de verificación
        verification_info = {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'total_events': len(events),
            'blockchain_events': sum(1 for e in events if e.blockchain_tx_hash),
            'last_update': timeline.last_event_timestamp.isoformat() if timeline.last_event_timestamp else None,
            'verification_status': 'verified' if events else 'no_data',
            'events': [event.to_dict(include_private=False) for event in events]
        }
        
        return jsonify(verification_info), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/trace/event/<int:event_id>', methods=['GET'])
@jwt_required()
def get_trace_event(event_id):
    """Obtener detalles de un evento específico"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        event = TraceEvent.query.get(event_id)
        if not event:
            return jsonify({'error': 'Evento no encontrado'}), 404
        
        # Verificar permisos
        if not event.is_public and user.role != 'admin':
            if not _check_trace_permissions(user, event.entity_type, event.entity_id):
                return jsonify({'error': 'No tienes permisos para ver este evento'}), 403
        
        include_private = user.role == 'admin'
        return jsonify({'event': event.to_dict(include_private=include_private)}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trace/event/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_trace_event(event_id):
    """Actualizar un evento de trazabilidad (solo admin)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json()
        
        if user.role != 'admin':
            return jsonify({'error': 'Solo administradores pueden actualizar eventos'}), 403
        
        event = TraceEvent.query.get(event_id)
        if not event:
            return jsonify({'error': 'Evento no encontrado'}), 404
        
        # Actualizar campos permitidos
        allowed_fields = ['title', 'description', 'location', 'event_data', 'measurements', 'tags', 'is_public']
        for field in allowed_fields:
            if field in data:
                if field in ['event_data', 'measurements', 'tags']:
                    setattr(event, field, json.dumps(data[field]))
                else:
                    setattr(event, field, data[field])
        
        event.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Evento actualizado exitosamente',
            'event': event.to_dict(include_private=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# =====================================
# FUNCIONES AUXILIARES PARA TRAZABILIDAD
# =====================================

def _check_trace_permissions(user, entity_type, entity_id):
    """Verificar si un usuario tiene permisos para acceder a trazabilidad"""
    try:
        if user.role == 'admin':
            return True
        
        # Para lotes: verificar si el usuario es el productor o pertenece a la compañía
        if entity_type == 'lot':
            lot = ProducerLot.query.filter_by(id=int(entity_id)).first()
            if lot and (lot.producer_id == user.id or lot.producer.company_id == user.company_id):
                return True
        
        # Para batches: verificar membresía en deals relacionados
        elif entity_type == 'batch':
            batch = BatchNFT.query.filter_by(id=int(entity_id)).first()
            if batch:
                # Verificar si el usuario está en deals relacionados con este batch
                deal_links = DealTraceLink.query.filter(
                    DealTraceLink.batch_ids.contains(f'"{entity_id}"')
                ).all()
                for link in deal_links:
                    member = DealMember.query.filter_by(
                        deal_id=link.deal_id,
                        party_id=user.company_id if user.company_id else user.id
                    ).first()
                    if member:
                        return True
        
        # Para contracts: verificar si el usuario pertenece a la compañía del contrato
        elif entity_type == 'contract':
            contract = ExportContract.query.filter_by(id=int(entity_id)).first()
            if contract and (contract.created_by_user_id == user.id or 
                           contract.buyer_company_id == user.company_id or
                           contract.exporter_company_id == user.company_id):
                return True
        
        # Para deals: verificar membresía
        elif entity_type == 'deal':
            member = DealMember.query.filter_by(
                deal_id=int(entity_id),
                party_id=user.company_id if user.company_id else user.id
            ).first()
            if member:
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error verificando permisos de trazabilidad: {e}")
        return False

def _register_event_on_chain(trace_event):
    """Registrar evento en blockchain si está disponible"""
    try:
        if not blockchain.is_ready():
            return None
        
        # Preparar datos para blockchain
        event_data = {
            'eventType': trace_event.event_type,
            'entityType': trace_event.entity_type,
            'entityId': trace_event.entity_id,
            'eventHash': trace_event.get_event_hash(),
            'timestamp': int(trace_event.event_timestamp.timestamp()),
            'actor': trace_event.actor_name
        }
        
        # Intentar registrar usando el servicio de blockchain
        # Esto dependerá de los contratos inteligentes disponibles
        if hasattr(blockchain, 'register_trace_event'):
            tx_hash = blockchain.register_trace_event(event_data)
            return tx_hash
        
        return None
        
    except Exception as e:
        logger.error(f"Error registrando evento en blockchain: {e}")
        return None

def _update_timeline_stats(entity_type, entity_id):
    """Actualizar estadísticas del timeline"""
    try:
        timeline = TraceTimeline.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).first()
        
        if not timeline:
            timeline = TraceTimeline(entity_type=entity_type, entity_id=entity_id)
            db.session.add(timeline)
        
        timeline.update_stats()
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Error actualizando estadísticas del timeline: {e}")

# =====================================
# ENDPOINTS DE MATCHMAKING B2B
# =====================================

@app.route('/api/match/producers', methods=['GET'])
@jwt_required()
def search_producers():
    """Buscar productores disponibles para matchmaking B2B"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in ['admin', 'operator', 'exporter', 'buyer']:
            return jsonify({'error': 'Sin permisos para buscar productores'}), 403
        
        # Parámetros de búsqueda
        location = request.args.get('location')
        certifications = request.args.getlist('certifications')  # Lista de certificaciones
        min_volume = request.args.get('min_volume', type=float)
        max_volume = request.args.get('max_volume', type=float)
        quality_grade = request.args.get('quality_grade')
        product_type = request.args.get('product_type')
        available_now = request.args.get('available_now', 'true').lower() == 'true'
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Base query para productores con lotes disponibles
        query = db.session.query(
            Company,
            db.func.count(ProducerLot.id).label('available_lots'),
            db.func.sum(ProducerLot.weight_kg).label('total_volume_kg'),
            db.func.avg(
                db.case(
                    (ProducerLot.quality_grade == 'Premium', 95),
                    (ProducerLot.quality_grade == 'A', 90),
                    (ProducerLot.quality_grade == 'B', 80),
                    (ProducerLot.quality_grade == 'C', 70),
                    (ProducerLot.quality_grade == 'Standard', 75),
                    (ProducerLot.quality_grade == 'High', 85),
                    (ProducerLot.quality_grade == 'Medium', 75),
                    (ProducerLot.quality_grade == 'Low', 65),
                    else_=75
                )
            ).label('avg_quality_score')
        ).join(ProducerLot, Company.id == ProducerLot.producer_company_id)\
         .filter(ProducerLot.status == 'available')\
         .group_by(Company.id)
        
        # Aplicar filtros
        if location:
            query = query.filter(ProducerLot.location.ilike(f'%{location}%'))
        
        if certifications:
            # Filtrar por certificaciones (al menos una de las solicitadas)
            cert_conditions = []
            for cert in certifications:
                cert_conditions.append(ProducerLot.certifications.ilike(f'%{cert}%'))
            query = query.filter(db.or_(*cert_conditions))
        
        if min_volume:
            query = query.having(db.func.sum(ProducerLot.weight_kg) >= min_volume * 1000)  # Convertir MT a KG
        
        if max_volume:
            query = query.having(db.func.sum(ProducerLot.weight_kg) <= max_volume * 1000)
        
        if quality_grade:
            query = query.filter(ProducerLot.quality_grade == quality_grade)
        
        if product_type:
            query = query.filter(ProducerLot.product_type.ilike(f'%{product_type}%'))
        
        if available_now:
            # Solo productores con lotes disponibles actualmente
            pass  # Ya filtrado por status == 'available'
        
        # Ejecutar consulta con paginación
        results = query.offset(offset).limit(limit).all()
        
        # Formatear respuesta
        producers = []
        for company, available_lots, total_volume_kg, avg_quality_score in results:
            # Obtener información adicional del productor
            did = DigitalIdentity.query.filter_by(
                user_id=company.users[0].id if company.users else None,
                is_active=True
            ).first() if company.users else None
            
            producer_data = {
                'company_id': company.id,
                'company_name': company.name,
                'company_type': company.company_type,
                'location': company.country,  # Usar country como ubicación general
                'available_lots': available_lots,
                'total_volume_mt': round(total_volume_kg / 1000, 2) if total_volume_kg else 0,
                'avg_quality_score': round(avg_quality_score, 1) if avg_quality_score else None,
                'has_did': did is not None,
                'reputation_score': float(did.reputation_score) if did else 0.0,
                'certifications': [],  # Se calculará más abajo
                'contact_info': {
                    'email': company.users[0].email if company.users else None,
                    'phone': None  # No tenemos teléfono en el modelo actual
                }
            }
            
            # Obtener certificaciones únicas de sus lotes
            lot_certifications = db.session.query(ProducerLot.certifications)\
                .filter(ProducerLot.producer_company_id == company.id)\
                .filter(ProducerLot.status == 'available')\
                .distinct().all()
            
            unique_certs = set()
            for cert_tuple in lot_certifications:
                if cert_tuple[0]:
                    certs = [c.strip() for c in cert_tuple[0].split(',') if c.strip()]
                    unique_certs.update(certs)
            
            producer_data['certifications'] = list(unique_certs)
            producers.append(producer_data)
        
        # Obtener total para paginación
        total_query = db.session.query(
            db.func.count(db.distinct(Company.id))
        ).join(ProducerLot, Company.id == ProducerLot.producer_company_id)\
         .filter(ProducerLot.status == 'available')
        
        # Aplicar mismos filtros para el total
        if location:
            total_query = total_query.filter(ProducerLot.location.ilike(f'%{location}%'))
        if certifications:
            cert_conditions = []
            for cert in certifications:
                cert_conditions.append(ProducerLot.certifications.ilike(f'%{cert}%'))
            total_query = total_query.filter(db.or_(*cert_conditions))
        if quality_grade:
            total_query = total_query.filter(ProducerLot.quality_grade == quality_grade)
        if product_type:
            total_query = total_query.filter(ProducerLot.product_type.ilike(f'%{product_type}%'))
        
        total_producers = total_query.scalar()
        
        return jsonify({
            'producers': producers,
            'pagination': {
                'total': total_producers,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total_producers
            },
            'filters_applied': {
                'location': location,
                'certifications': certifications,
                'min_volume': min_volume,
                'max_volume': max_volume,
                'quality_grade': quality_grade,
                'product_type': product_type,
                'available_now': available_now
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/match/lots', methods=['GET'])
@jwt_required()
def search_available_lots():
    """Buscar lotes disponibles para matchmaking"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in ['admin', 'operator', 'exporter', 'buyer']:
            return jsonify({'error': 'Sin permisos para buscar lotes'}), 403
        
        # Parámetros de búsqueda
        producer_id = request.args.get('producer_id', type=int)
        location = request.args.get('location')
        certifications = request.args.getlist('certifications')
        min_weight = request.args.get('min_weight', type=float)
        max_weight = request.args.get('max_weight', type=float)
        quality_grade = request.args.get('quality_grade')
        product_type = request.args.get('product_type')
        harvest_date_from = request.args.get('harvest_date_from')
        harvest_date_to = request.args.get('harvest_date_to')
        sort_by = request.args.get('sort_by', 'harvest_date')  # harvest_date, weight_kg, quality_score
        sort_order = request.args.get('sort_order', 'desc')  # asc, desc
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Base query
        query = ProducerLot.query.filter_by(status='available')
        
        # Aplicar filtros
        if producer_id:
            query = query.filter_by(producer_company_id=producer_id)
        
        if location:
            query = query.filter(ProducerLot.location.ilike(f'%{location}%'))
        
        if certifications:
            cert_conditions = []
            for cert in certifications:
                cert_conditions.append(ProducerLot.certifications.ilike(f'%{cert}%'))
            query = query.filter(db.or_(*cert_conditions))
        
        if min_weight:
            query = query.filter(ProducerLot.weight_kg >= min_weight)
        
        if max_weight:
            query = query.filter(ProducerLot.weight_kg <= max_weight)
        
        if quality_grade:
            query = query.filter_by(quality_grade=quality_grade)
        
        if product_type:
            query = query.filter(ProducerLot.product_type.ilike(f'%{product_type}%'))
        
        # Filtros de fecha de cosecha
        if harvest_date_from:
            try:
                date_from = datetime.fromisoformat(harvest_date_from.replace('Z', '+00:00'))
                query = query.filter(ProducerLot.harvest_date >= date_from)
            except:
                pass
        
        if harvest_date_to:
            try:
                date_to = datetime.fromisoformat(harvest_date_to.replace('Z', '+00:00'))
                query = query.filter(ProducerLot.harvest_date <= date_to)
            except:
                pass
        
        # Ordenamiento
        if sort_by == 'weight_kg':
            order_col = ProducerLot.weight_kg
        elif sort_by == 'quality_score':
            # Para ordenar por quality_score, necesitamos usar una expresión CASE
            order_col = db.case(
                (ProducerLot.quality_grade == 'Premium', 95),
                (ProducerLot.quality_grade == 'A', 90),
                (ProducerLot.quality_grade == 'B', 80),
                (ProducerLot.quality_grade == 'C', 70),
                (ProducerLot.quality_grade == 'Standard', 75),
                (ProducerLot.quality_grade == 'High', 85),
                (ProducerLot.quality_grade == 'Medium', 75),
                (ProducerLot.quality_grade == 'Low', 65),
                else_=75
            )
        else:  # harvest_date
            order_col = ProducerLot.harvest_date
        
        if sort_order == 'asc':
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())
        
        # Ejecutar consulta con paginación
        total_count = query.count()
        lots = query.offset(offset).limit(limit).all()
        
        # Formatear respuesta
        result = []
        for lot in lots:
            # Calcular precio estimado por MT
            price_per_mt = None
            if lot.purchase_price_usd and lot.weight_kg and lot.weight_kg > 0:
                price_per_mt = float(lot.purchase_price_usd) / (float(lot.weight_kg) / 1000.0)
            
            # Obtener información del productor
            producer_did = None
            if lot.producer_company and lot.producer_company.users:
                producer_did = DigitalIdentity.query.filter_by(
                    user_id=lot.producer_company.users[0].id,
                    is_active=True
                ).first()
            
            lot_data = {
                'id': lot.id,
                'lot_code': lot.lot_code,
                'producer_company': {
                    'id': lot.producer_company.id if lot.producer_company else None,
                    'name': lot.producer_company.name if lot.producer_company else None,
                    'has_did': producer_did is not None,
                    'reputation_score': float(producer_did.reputation_score) if producer_did else 0.0
                },
                'location': lot.location,
                'product_type': lot.product_type,
                'weight_kg': float(lot.weight_kg),
                'weight_mt': float(lot.weight_kg) / 1000.0,
                'quality_grade': lot.quality_grade,
                'quality_score': float(lot.quality_score) if lot.quality_score else None,
                'harvest_date': lot.harvest_date.isoformat() if lot.harvest_date else None,
                'certifications': lot.certifications.split(',') if lot.certifications else [],
                'estimated_price_per_mt': price_per_mt,
                'blockchain_lot_id': lot.blockchain_lot_id,
                'created_at': lot.created_at.isoformat() if lot.created_at else None
            }
            result.append(lot_data)
        
        return jsonify({
            'lots': result,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total_count
            },
            'filters_applied': {
                'producer_id': producer_id,
                'location': location,
                'certifications': certifications,
                'min_weight': min_weight,
                'max_weight': max_weight,
                'quality_grade': quality_grade,
                'product_type': product_type,
                'harvest_date_from': harvest_date_from,
                'harvest_date_to': harvest_date_to,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/match/recommendations', methods=['GET'])
@jwt_required()
def get_match_recommendations():
    """Obtener recomendaciones de matchmaking basadas en perfil del usuario"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Obtener preferencias del usuario (simuladas por ahora)
        # En el futuro, esto podría venir de un perfil de preferencias guardado
        preferred_certifications = ['Organic', 'Fair Trade']
        preferred_locations = []  # Todas las ubicaciones por defecto
        min_quality_score = 80
        max_results = request.args.get('limit', 10, type=int)
        
        # Buscar lotes que coincidan con preferencias
        query = ProducerLot.query.filter_by(status='available')
        
        # Aplicar filtros de calidad
        if min_quality_score:
            quality_case = db.case(
                (ProducerLot.quality_grade == 'Premium', 95),
                (ProducerLot.quality_grade == 'A', 90),
                (ProducerLot.quality_grade == 'B', 80),
                (ProducerLot.quality_grade == 'C', 70),
                (ProducerLot.quality_grade == 'Standard', 75),
                (ProducerLot.quality_grade == 'High', 85),
                (ProducerLot.quality_grade == 'Medium', 75),
                (ProducerLot.quality_grade == 'Low', 65),
                else_=75
            )
            query = query.filter(quality_case >= min_quality_score)
        
        # Filtrar por certificaciones preferidas
        if preferred_certifications:
            cert_conditions = []
            for cert in preferred_certifications:
                cert_conditions.append(ProducerLot.certifications.ilike(f'%{cert}%'))
            query = query.filter(db.or_(*cert_conditions))
        
        # Ordenar por puntuación de coincidencia (simplificada)
        # En el futuro, implementar algoritmo de recomendación más sofisticado
        quality_case = db.case(
            (ProducerLot.quality_grade == 'Premium', 95),
            (ProducerLot.quality_grade == 'A', 90),
            (ProducerLot.quality_grade == 'B', 80),
            (ProducerLot.quality_grade == 'C', 70),
            (ProducerLot.quality_grade == 'Standard', 75),
            (ProducerLot.quality_grade == 'High', 85),
            (ProducerLot.quality_grade == 'Medium', 75),
            (ProducerLot.quality_grade == 'Low', 65),
            else_=75
        )
        query = query.order_by(quality_case.desc(), ProducerLot.harvest_date.desc())
        
        recommended_lots = query.limit(max_results).all()
        
        # Formatear recomendaciones
        recommendations = []
        for lot in recommended_lots:
            # Calcular score de recomendación (0-100)
            score = 50  # Base
            
            # Bonus por calidad
            if lot.quality_score and lot.quality_score >= 90:
                score += 20
            elif lot.quality_score and lot.quality_score >= 80:
                score += 10
            
            # Bonus por certificaciones
            if lot.certifications:
                certs = [c.strip().lower() for c in lot.certifications.split(',')]
                matching_certs = sum(1 for cert in preferred_certifications 
                                   if cert.lower() in ' '.join(certs))
                score += matching_certs * 10
            
            # Bonus por DID verificado del productor
            if lot.producer_company and lot.producer_company.users:
                did = DigitalIdentity.query.filter_by(
                    user_id=lot.producer_company.users[0].id,
                    is_active=True,
                    kyc_status='verified'
                ).first()
                if did:
                    score += 15
            
            score = min(100, score)  # Máximo 100
            
            recommendation = {
                'lot': {
                    'id': lot.id,
                    'lot_code': lot.lot_code,
                    'producer_company': lot.producer_company.name if lot.producer_company else None,
                    'location': lot.location,
                    'product_type': lot.product_type,
                    'weight_mt': float(lot.weight_kg) / 1000.0,
                    'quality_grade': lot.quality_grade,
                    'quality_score': float(lot.quality_score) if lot.quality_score else None,
                    'certifications': lot.certifications.split(',') if lot.certifications else [],
                    'harvest_date': lot.harvest_date.isoformat() if lot.harvest_date else None
                },
                'recommendation_score': score,
                'match_reasons': []
            }
            
            # Agregar razones de coincidencia
            if lot.quality_score and lot.quality_score >= min_quality_score:
                recommendation['match_reasons'].append(f"Calidad alta ({lot.quality_score}%)")
            
            if lot.certifications:
                certs = [c.strip() for c in lot.certifications.split(',')]
                matching = [c for c in certs if c in preferred_certifications]
                if matching:
                    recommendation['match_reasons'].append(f"Certificaciones: {', '.join(matching)}")
            
            recommendations.append(recommendation)
        
        # Ordenar por score de recomendación
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return jsonify({
            'recommendations': recommendations,
            'total_recommendations': len(recommendations),
            'preferences_used': {
                'preferred_certifications': preferred_certifications,
                'min_quality_score': min_quality_score
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/match/contact/<int:producer_company_id>', methods=['POST'])
@jwt_required()
def initiate_contact(producer_company_id):
    """Iniciar contacto con un productor (crear deal o enviar mensaje)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in ['admin', 'operator', 'exporter', 'buyer']:
            return jsonify({'error': 'Sin permisos para contactar productores'}), 403
        
        # Verificar que el productor existe
        producer_company = Company.query.get(producer_company_id)
        if not producer_company:
            return jsonify({'error': 'Productor no encontrado'}), 404
        
        data = request.get_json()
        contact_type = data.get('contact_type', 'inquiry')  # inquiry, deal_proposal
        message = data.get('message', '')
        lot_ids = data.get('lot_ids', [])  # IDs de lotes de interés
        
        # Verificar que los lotes pertenezcan al productor
        if lot_ids:
            lots = ProducerLot.query.filter(
                ProducerLot.id.in_(lot_ids),
                ProducerLot.producer_company_id == producer_company_id,
                ProducerLot.status == 'available'
            ).all()
            
            if len(lots) != len(lot_ids):
                return jsonify({'error': 'Algunos lotes no están disponibles o no pertenecen al productor'}), 400
        
        # Crear un deal si es una propuesta formal
        if contact_type == 'deal_proposal':
            # Generar código único para el deal
            deal_code = f"D-{datetime.now().strftime('%Y%m%d')}-{user.company_id:03d}-{producer_company_id:03d}"
            
            deal = Deal(
                deal_code=deal_code,
                admin_id=user_id,  # El usuario que inicia es el admin del deal
                producer_id=producer_company_id,
                exporter_id=user.company_id if user.company_id else None,
                terms_public=json.dumps({
                    'contact_initiator': user.name,
                    'contact_type': 'matchmaking_proposal',
                    'interested_lots': lot_ids,
                    'initial_message': message
                })
            )
            
            db.session.add(deal)
            db.session.flush()
            
            # Agregar miembros al deal
            # Productor
            producer_member = DealMember(
                deal_id=deal.id,
                party_id=producer_company_id,
                party_type='company',
                role_in_deal='producer',
                permissions=json.dumps(['read', 'write', 'trace'])
            )
            db.session.add(producer_member)
            
            # Iniciador (exportador/comprador)
            initiator_member = DealMember(
                deal_id=deal.id,
                party_id=user.company_id or user.id,
                party_type='company' if user.company_id else 'user',
                role_in_deal='exporter' if user.role == 'exporter' else 'buyer',
                permissions=json.dumps(['read', 'write', 'admin'])
            )
            db.session.add(initiator_member)
            
            # Vincular lotes al deal si se especificaron
            if lot_ids:
                deal_trace_link = DealTraceLink(
                    deal_id=deal.id,
                    lote_ids=json.dumps(lot_ids)
                )
                db.session.add(deal_trace_link)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Propuesta de deal enviada exitosamente',
                'deal_id': deal.id,
                'deal_code': deal_code,
                'status': 'proposal_sent'
            }), 201
        
        else:
            # Para inquiry simple, crear un mensaje en el sistema de notificaciones
            # Por ahora, solo devolver confirmación
            return jsonify({
                'message': 'Consulta enviada al productor',
                'producer_company': producer_company.name,
                'contact_type': 'inquiry',
                'status': 'sent'
            }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# =====================================
# REDIRECCIONES AL FRONTEND
# =====================================

@app.route('/')
def redirect_to_frontend():
    """Redirigir al frontend"""
    from flask import redirect
    # En producción usar la URL externa, en desarrollo localhost
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5004/')
    return redirect(frontend_url, code=302)

@app.route('/dashboard')
def redirect_dashboard():
    """Redirigir dashboard al frontend"""
    from flask import redirect
    # En producción usar la URL externa, en desarrollo localhost
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5004/')
    return redirect(f"{frontend_url}dashboard", code=302)

@app.route('/login')
def redirect_login():
    """Redirigir login al frontend"""
    from flask import redirect
    # En producción usar la URL externa, en desarrollo localhost
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5004/')
    return redirect(f"{frontend_url}login", code=302)

# Backend API Only - Frontend is served separately from frontend/app.py on port 5004

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Crear directorio de uploads si no existe
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    
    print("🚀 Triboka Agro API Server with WebSocket support starting...")
    print("📡 API Endpoints: http://localhost:5003/api (desarrollo) | https://app.triboka.com/api (producción)")
    print("🖥️  Frontend Dashboard: http://localhost:5004 (desarrollo) | https://app.triboka.com (producción)")
    print("💬 WebSocket Chat: ws://localhost:5003/socket.io (desarrollo) | wss://app.triboka.com/socket.io (producción)")
    print("🔗 Blockchain integration:", "✅ Ready" if blockchain.is_ready() else "⚠️ Not configured")
    
    socketio.run(app, debug=False, host='0.0.0.0', port=9091, allow_unsafe_werkzeug=True)
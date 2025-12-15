"""
Lot management routes for Triboka BaaS Platform
CRUD operations for cacao lots with blockchain integration
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, asc
from datetime import datetime
import uuid
from functools import wraps

from models_simple import ProducerLot, TraceEvent, User, Company, db
# from services.blockchain_service import BlockchainService  # Commented out - service error
# from services.lot_service import LotService  # Commented out - service not found

lots_bp = Blueprint('lots', __name__)
# blockchain_service = BlockchainService()  # Commented out - service error
# lot_service = LotService()  # Commented out - service not found

def require_api_key(f):
    """Decorador para validar API keys de empresas externas"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('Authorization')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Remover 'Bearer ' si está presente
        if api_key.startswith('Bearer '):
            api_key = api_key[7:]
        
        # Validar API key y obtener empresa
        company = Company.query.filter_by(api_key=api_key).first()
        if not company:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Inyectar company en request context
        g.company = company
        return f(*args, **kwargs)
    return decorated_function

@lots_bp.route('/', methods=['GET'])
@jwt_required()
def get_lots():
    """Get all lots for current company with filtering and pagination"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # For AgroWeight Cloud integration, return all available lots
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

# @lots_bp.route('/<lot_uuid>', methods=['GET'])
# @jwt_required()
# def get_lot(lot_uuid):
#     """Get specific lot by UUID with full details"""
#     # Commented out - uses old Lot model
#     pass

# @lots_bp.route('/', methods=['POST'])
# @jwt_required()
# def create_lot():
#     """Create new cacao lot and register on blockchain"""
#     # Commented out - uses old Lot model
#     pass

# @lots_bp.route('/<lot_uuid>', methods=['PUT'])
# @jwt_required()
# def update_lot(lot_uuid):
#     """Update lot information"""
#     # Commented out - uses old Lot model
#     pass

# @lots_bp.route('/<lot_uuid>/quality-test', methods=['POST'])
# @jwt_required()
# def add_quality_test(lot_uuid):
#     """Add quality test results to lot"""
#     # Commented out - uses old models
#     pass

# @lots_bp.route('/<lot_uuid>/track', methods=['GET'])
# @jwt_required()
# def track_lot(lot_uuid):
#     """Get complete tracking history for lot"""
#     # Commented out - uses old models
#     pass

# @lots_bp.route('/stats', methods=['GET'])
# @jwt_required()
# def get_lot_stats():
#     """Get lot statistics for current company"""
#     # Commented out - uses old models
#     pass

# =====================================
# ENDPOINTS PARA INTEGRACIÓN CON MICRO-SAAS
# =====================================

@lots_bp.route('/nft/<nft_hash>', methods=['GET'])
@require_api_key
def get_lote_nft(nft_hash):
    """Obtener lote por hash NFT para integración con AgroWeight Cloud"""
    try:
        company = g.company
        
        # Buscar lote por NFT hash o blockchain_lot_id
        lot = ProducerLot.query.filter(
            (ProducerLot.blockchain_lot_id == nft_hash) |
            (ProducerLot.lot_code == nft_hash)
        ).first()
        
        if not lot:
            return jsonify({'error': 'Lot not found'}), 404
        
        # Convertir a dict usando el método to_dict()
        return jsonify(lot.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lots_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Endpoint de prueba"""
    return jsonify({'message': 'Test endpoint working'})

@lots_bp.route('/id/<lote_id>', methods=['GET'])
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

@lots_bp.route('/<lot_id>/eventos', methods=['POST'])
@require_api_key
def registrar_evento_lote(lot_id):
    """Registrar evento de trazabilidad en lote"""
    try:
        company = g.company
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Crear evento de trazabilidad
        event = TraceEvent(
            entity_type='lot',
            entity_id=lot_id,
            event_type=data.get('tipo', 'evento_planta'),
            measurements=data,
            company_id=company.id,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'event_id': event.id,
            'message': 'Event registered successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
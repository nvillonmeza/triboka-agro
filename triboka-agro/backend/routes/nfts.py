"""
NFT Certificate routes for Triboka BaaS Platform
Create and manage NFT certificates for lot authenticity
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import secrets
from functools import wraps

from models.models import NFTCertificate, User, Lot, BatchNFT, Company, db
from services.blockchain_service import BlockchainService
from services.nft_service import NFTService

nfts_bp = Blueprint('nfts', __name__)
blockchain_service = BlockchainService()
nft_service = NFTService()

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

@nfts_bp.route('/', methods=['GET'])
@jwt_required()
def get_nfts():
    """Get all NFT certificates for current company"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        certificate_type = request.args.get('type')
        is_minted = request.args.get('is_minted')
        
        # Base query
        query = NFTCertificate.query.filter_by(company_id=user.company_id)
        
        # Apply filters
        if certificate_type:
            query = query.filter(NFTCertificate.certificate_type == certificate_type)
        
        if is_minted is not None:
            query = query.filter(NFTCertificate.is_minted == (is_minted.lower() == 'true'))
        
        # Order by creation date
        query = query.order_by(NFTCertificate.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        nfts = []
        for nft in pagination.items:
            nft_data = nft.to_dict()
            nft_data['lot'] = nft.lot.to_dict() if nft.lot else None
            nfts.append(nft_data)
        
        return jsonify({
            'nfts': nfts,
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nfts_bp.route('/<nft_uuid>', methods=['GET'])
@jwt_required()
def get_nft(nft_uuid):
    """Get specific NFT certificate by UUID"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        nft = NFTCertificate.query.filter_by(
            uuid=nft_uuid,
            company_id=user.company_id
        ).first()
        
        if not nft:
            return jsonify({'error': 'NFT certificate not found'}), 404
        
        nft_data = nft.to_dict()
        nft_data['lot'] = nft.lot.to_dict() if nft.lot else None
        
        # Get blockchain status if minted
        if nft.is_minted and nft.blockchain_tx_hash:
            blockchain_status = blockchain_service.get_transaction_status(nft.blockchain_tx_hash)
            nft_data['blockchain_status'] = blockchain_status
        
        return jsonify({'nft': nft_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nfts_bp.route('/create', methods=['POST'])
@jwt_required()
def create_nft():
    """Create new NFT certificate for a lot"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['lot_uuid', 'certificate_type', 'title']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Verify lot exists and belongs to company
        lot = Lot.query.filter_by(
            uuid=data['lot_uuid'],
            company_id=user.company_id
        ).first()
        
        if not lot:
            return jsonify({'error': 'Lot not found'}), 404
        
        # Check if NFT of this type already exists for this lot
        existing_nft = NFTCertificate.query.filter_by(
            lot_id=lot.id,
            certificate_type=data['certificate_type']
        ).first()
        
        if existing_nft:
            return jsonify({'error': f'NFT certificate of type {data["certificate_type"]} already exists for this lot'}), 409
        
        # Generate unique token ID
        token_id = f"TRIBOKA-{lot.lot_number}-{data['certificate_type'].upper()}-{secrets.token_hex(4)}"
        
        # Create NFT certificate
        nft = NFTCertificate(
            token_id=token_id,
            certificate_type=data['certificate_type'],
            title=data['title'],
            description=data.get('description', ''),
            image_url=data.get('image_url'),
            lot_id=lot.id,
            company_id=user.company_id
        )
        
        db.session.add(nft)
        db.session.flush()  # Get NFT ID
        
        # Generate metadata
        metadata = nft_service.generate_metadata(nft)
        nft.metadata_uri = metadata['uri']
        
        db.session.commit()
        
        return jsonify({
            'message': 'NFT certificate created successfully',
            'nft': nft.to_dict(),
            'metadata': metadata
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@nfts_bp.route('/<nft_uuid>/mint', methods=['POST'])
@jwt_required()
def mint_nft(nft_uuid):
    """Mint NFT certificate on blockchain"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        nft = NFTCertificate.query.filter_by(
            uuid=nft_uuid,
            company_id=user.company_id
        ).first()
        
        if not nft:
            return jsonify({'error': 'NFT certificate not found'}), 404
        
        if nft.is_minted:
            return jsonify({'error': 'NFT already minted'}), 400
        
        # Check company plan limits
        if not nft_service.can_mint_nft(user.company):
            return jsonify({'error': 'NFT minting limit reached for your plan'}), 403
        
        # Mint on blockchain
        mint_result = blockchain_service.mint_nft(nft)
        
        if mint_result and mint_result.get('success'):
            nft.is_minted = True
            nft.mint_date = datetime.utcnow()
            nft.blockchain_tx_hash = mint_result.get('tx_hash')
            nft.block_number = mint_result.get('block_number')
            nft.contract_address = mint_result.get('contract_address')
            
            db.session.commit()
            
            # Charge commission
            nft_service.charge_nft_commission(user.company, nft)
            
            return jsonify({
                'message': 'NFT minted successfully',
                'nft': nft.to_dict(),
                'transaction': mint_result
            })
        else:
            return jsonify({'error': 'Failed to mint NFT on blockchain'}), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@nfts_bp.route('/<nft_uuid>/verify', methods=['GET'])
def verify_nft(nft_uuid):
    """Public endpoint to verify NFT authenticity"""
    try:
        nft = NFTCertificate.query.filter_by(uuid=nft_uuid).first()
        
        if not nft:
            return jsonify({'error': 'NFT certificate not found'}), 404
        
        if not nft.is_minted:
            return jsonify({'error': 'NFT not yet minted'}), 400
        
        # Verify on blockchain
        verification_result = blockchain_service.verify_nft(nft)
        
        return jsonify({
            'verified': verification_result.get('verified', False),
            'nft': {
                'token_id': nft.token_id,
                'certificate_type': nft.certificate_type,
                'title': nft.title,
                'description': nft.description,
                'mint_date': nft.mint_date.isoformat() if nft.mint_date else None,
                'contract_address': nft.contract_address,
                'blockchain_tx_hash': nft.blockchain_tx_hash
            },
            'lot': {
                'lot_number': nft.lot.lot_number,
                'origin_location': nft.lot.origin_location,
                'quantity_kg': nft.lot.quantity_kg,
                'quality_grade': nft.lot.quality_grade
            },
            'company': {
                'name': nft.company.name
            },
            'blockchain_data': verification_result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nfts_bp.route('/<nft_uuid>/metadata', methods=['GET'])
def get_nft_metadata(nft_uuid):
    """Get NFT metadata (public endpoint for OpenSea compatibility)"""
    try:
        nft = NFTCertificate.query.filter_by(uuid=nft_uuid).first()
        
        if not nft:
            return jsonify({'error': 'NFT certificate not found'}), 404
        
        metadata = nft_service.get_nft_metadata(nft)
        
        return jsonify(metadata)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nfts_bp.route('/types', methods=['GET'])
@jwt_required()
def get_certificate_types():
    """Get available certificate types"""
    return jsonify({
        'certificate_types': [
            {
                'id': 'origin',
                'name': 'Certificate of Origin',
                'description': 'Certifies the geographical origin of the cacao lot',
                'price': 10
            },
            {
                'id': 'quality',
                'name': 'Quality Certificate',
                'description': 'Certifies quality test results and grade',
                'price': 15
            },
            {
                'id': 'organic',
                'name': 'Organic Certificate',
                'description': 'Certifies organic farming practices',
                'price': 20
            },
            {
                'id': 'fairtrade',
                'name': 'Fair Trade Certificate',
                'description': 'Certifies fair trade compliance',
                'price': 20
            },
            {
                'id': 'export',
                'name': 'Export Certificate',
                'description': 'Certifies lot readiness for export',
                'price': 12
            },
            {
                'id': 'delivery',
                'name': 'Delivery Certificate',
                'description': 'Certifies successful delivery to destination',
                'price': 10
            }
        ]
    })

@nfts_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_nft_stats():
    """Get NFT statistics for current company"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        stats = nft_service.get_company_nft_stats(user.company_id)
        
        return jsonify({'stats': stats})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================
# ENDPOINTS PARA INTEGRACIÓN CON MICRO-SAAS
# =====================================

@nfts_bp.route('/batch-nft', methods=['POST'])
@require_api_key
def crear_batch_nft():
    """Crear NFT de batch final para integración con AgroWeight Cloud"""
    try:
        company = g.company
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Crear batch NFT para esta empresa
        batch = BatchNFT(
            batch_code=data.get('batch_code'),
            company_id=company.id,
            lotes_nft_ids=data.get('lotes_nft_ids', []),
            peso_total_kg=data.get('peso_total_kg'),
            destino=data.get('destino'),
            timestamp=datetime.utcnow()
        )
        
        db.session.add(batch)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'batch_id': batch.id,
            'batch_code': batch.batch_code,
            'message': 'Batch NFT created successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
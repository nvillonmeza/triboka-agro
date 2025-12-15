"""
Routes for Export Contracts Management
Advanced contract management with fixations, workflow, and business logic
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models_simple import db, ExportContract, ContractFixation, User, Company
from datetime import datetime
import logging

contracts_bp = Blueprint('contracts', __name__)
logger = logging.getLogger(__name__)

# Contract status workflow
CONTRACT_STATUSES = ['draft', 'active', 'suspended', 'completed', 'cancelled']
VALID_TRANSITIONS = {
    'draft': ['active', 'cancelled'],
    'active': ['suspended', 'completed'],
    'suspended': ['active', 'cancelled'],
    'completed': [],
    'cancelled': []
}

@contracts_bp.route('', methods=['GET'])
@jwt_required()
def get_contracts():
    """Get contracts with filtering and pagination"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Build query based on user role
        query = ExportContract.query

        # Filter by company if not admin
        if user.role not in ['admin', 'broker']:
            if user.company_id:
                query = query.filter(
                    db.or_(
                        ExportContract.buyer_company_id == user.company_id,
                        ExportContract.exporter_company_id == user.company_id
                    )
                )

        # Apply filters
        status = request.args.get('status')
        if status:
            query = query.filter(ExportContract.status == status)

        product_type = request.args.get('product_type')
        if product_type:
            query = query.filter(ExportContract.product_type == product_type)

        buyer_id = request.args.get('buyer_id')
        if buyer_id:
            query = query.filter(ExportContract.buyer_company_id == int(buyer_id))

        exporter_id = request.args.get('exporter_id')
        if exporter_id:
            query = query.filter(ExportContract.exporter_company_id == int(exporter_id))

        # Pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        pagination = query.order_by(ExportContract.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        contracts = []
        for contract in pagination.items:
            contract_data = contract.to_dict()
            contract_data['buyer_company'] = contract.buyer_company.to_dict() if contract.buyer_company else None
            contract_data['exporter_company'] = contract.exporter_company.to_dict() if contract.exporter_company else None
            contract_data['created_by'] = contract.created_by_user.to_dict() if contract.created_by_user else None
            contracts.append(contract_data)

        return jsonify({
            'contracts': contracts,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })

    except Exception as e:
        logger.error(f"Error getting contracts: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@contracts_bp.route('', methods=['POST'])
@jwt_required()
def create_contract():
    """Create new export contract"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        # Validate required fields
        required_fields = ['contract_code', 'buyer_company_id', 'exporter_company_id',
                          'product_type', 'product_grade', 'total_volume_mt',
                          'differential_usd', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate companies exist
        buyer = Company.query.get(data['buyer_company_id'])
        exporter = Company.query.get(data['exporter_company_id'])

        if not buyer or not exporter:
            return jsonify({'error': 'Invalid buyer or exporter company'}), 400

        # Validate date logic
        start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))

        if end_date <= start_date:
            return jsonify({'error': 'End date must be after start date'}), 400

        # Generate contract code if not provided
        contract_code = data.get('contract_code')
        if not contract_code:
            contract_code = f"CTR-{datetime.now().strftime('%Y%m%d')}-{user.company_id}-{ExportContract.query.count() + 1:04d}"

        # Check for duplicate contract code
        existing = ExportContract.query.filter_by(contract_code=contract_code).first()
        if existing:
            return jsonify({'error': 'Contract code already exists'}), 400

        # Create contract
        contract = ExportContract(
            contract_code=contract_code,
            buyer_company_id=data['buyer_company_id'],
            exporter_company_id=data['exporter_company_id'],
            product_type=data['product_type'],
            product_grade=data['product_grade'],
            total_volume_mt=data['total_volume_mt'],
            differential_usd=data['differential_usd'],
            start_date=start_date,
            end_date=end_date,
            delivery_date=datetime.fromisoformat(data.get('delivery_date').replace('Z', '+00:00')) if data.get('delivery_date') else None,
            status='draft',
            created_by_user_id=user_id
        )

        db.session.add(contract)
        db.session.commit()

        # Log contract creation
        logger.info(f"Contract {contract_code} created by user {user_id}")

        return jsonify({
            'message': 'Contract created successfully',
            'contract': contract.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating contract: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@contracts_bp.route('/<int:contract_id>', methods=['GET'])
@jwt_required()
def get_contract(contract_id):
    """Get specific contract with full details"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        contract = ExportContract.query.get(contract_id)
        if not contract:
            return jsonify({'error': 'Contract not found'}), 404

        # Check permissions
        if user.role not in ['admin', 'broker']:
            if user.company_id not in [contract.buyer_company_id, contract.exporter_company_id]:
                return jsonify({'error': 'Access denied'}), 403

        # Get contract data
        contract_data = contract.to_dict()
        contract_data['buyer_company'] = contract.buyer_company.to_dict() if contract.buyer_company else None
        contract_data['exporter_company'] = contract.exporter_company.to_dict() if contract.exporter_company else None
        contract_data['created_by'] = contract.created_by_user.to_dict() if contract.created_by_user else None

        # Get fixations
        fixations = []
        for fixation in contract.fixations:
            fixation_data = fixation.to_dict()
            fixation_data['created_by'] = fixation.created_by_user.to_dict() if fixation.created_by_user else None
            fixations.append(fixation_data)

        contract_data['fixations'] = fixations
        contract_data['total_fixed_volume'] = sum(f['fixed_quantity_mt'] for f in fixations)
        contract_data['remaining_volume'] = contract.total_volume_mt - contract_data['total_fixed_volume']

        return jsonify({'contract': contract_data})

    except Exception as e:
        logger.error(f"Error getting contract {contract_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@contracts_bp.route('/<int:contract_id>', methods=['PUT'])
@jwt_required()
def update_contract(contract_id):
    """Update contract (only if in draft status)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        contract = ExportContract.query.get(contract_id)
        if not contract:
            return jsonify({'error': 'Contract not found'}), 404

        # Check permissions
        if user.role not in ['admin']:
            if contract.created_by_user_id != user_id:
                return jsonify({'error': 'Only contract creator or admin can update'}), 403

        # Only allow updates if contract is in draft status
        if contract.status != 'draft':
            return jsonify({'error': 'Can only update contracts in draft status'}), 400

        data = request.get_json()

        # Update allowed fields
        updatable_fields = ['product_type', 'product_grade', 'total_volume_mt',
                          'differential_usd', 'start_date', 'end_date', 'delivery_date']

        for field in updatable_fields:
            if field in data:
                if field in ['start_date', 'end_date', 'delivery_date']:
                    if data[field]:
                        setattr(contract, field, datetime.fromisoformat(data[field].replace('Z', '+00:00')))
                else:
                    setattr(contract, field, data[field])

        # Validate dates if updated
        if contract.end_date and contract.start_date:
            if contract.end_date <= contract.start_date:
                return jsonify({'error': 'End date must be after start date'}), 400

        contract.updated_at = datetime.utcnow()

        db.session.commit()

        logger.info(f"Contract {contract_id} updated by user {user_id}")

        return jsonify({
            'message': 'Contract updated successfully',
            'contract': contract.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating contract {contract_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@contracts_bp.route('/<int:contract_id>/status', methods=['PUT'])
@jwt_required()
def update_contract_status(contract_id):
    """Update contract status with workflow validation"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        contract = ExportContract.query.get(contract_id)
        if not contract:
            return jsonify({'error': 'Contract not found'}), 404

        # Check permissions
        if user.role not in ['admin']:
            if user.company_id not in [contract.buyer_company_id, contract.exporter_company_id]:
                return jsonify({'error': 'Access denied'}), 403

        data = request.get_json()
        new_status = data.get('status')

        if not new_status:
            return jsonify({'error': 'New status is required'}), 400

        if new_status not in CONTRACT_STATUSES:
            return jsonify({'error': 'Invalid status'}), 400

        # Validate status transition
        if new_status not in VALID_TRANSITIONS.get(contract.status, []):
            return jsonify({
                'error': f'Cannot change status from {contract.status} to {new_status}'
            }), 400

        # Business logic validations
        if new_status == 'active':
            # Validate required data for activation
            if not contract.total_volume_mt or contract.total_volume_mt <= 0:
                return jsonify({'error': 'Contract must have a valid volume to activate'}), 400

            if not contract.start_date or not contract.end_date:
                return jsonify({'error': 'Contract must have valid dates to activate'}), 400

        old_status = contract.status
        contract.status = new_status
        contract.updated_at = datetime.utcnow()

        db.session.commit()

        logger.info(f"Contract {contract_id} status changed from {old_status} to {new_status} by user {user_id}")

        return jsonify({
            'message': f'Contract status updated to {new_status}',
            'contract': contract.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating contract status {contract_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@contracts_bp.route('/<int:contract_id>', methods=['DELETE'])
@jwt_required()
def delete_contract(contract_id):
    """Delete contract (only if in draft status)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        contract = ExportContract.query.get(contract_id)
        if not contract:
            return jsonify({'error': 'Contract not found'}), 404

        # Check permissions
        if user.role not in ['admin']:
            if contract.created_by_user_id != user_id:
                return jsonify({'error': 'Only contract creator or admin can delete'}), 403

        # Only allow deletion if contract is in draft status
        if contract.status != 'draft':
            return jsonify({'error': 'Can only delete contracts in draft status'}), 400

        # Check if contract has fixations
        if contract.fixations:
            return jsonify({'error': 'Cannot delete contract with existing fixations'}), 400

        db.session.delete(contract)
        db.session.commit()

        logger.info(f"Contract {contract_id} deleted by user {user_id}")

        return jsonify({'message': 'Contract deleted successfully'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting contract {contract_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
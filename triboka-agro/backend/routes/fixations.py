"""
Routes for Contract Fixations Management
Price fixations, volume allocations, and financial calculations
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models_simple import db, ExportContract, ContractFixation, User
from datetime import datetime
import logging

fixations_bp = Blueprint('fixations', __name__)
logger = logging.getLogger(__name__)

@fixations_bp.route('', methods=['GET'])
@jwt_required()
def get_fixations():
    """Get fixations with filtering"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Build query
        query = ContractFixation.query.join(ExportContract)

        # Filter by company if not admin/broker
        if user.role not in ['admin', 'broker']:
            if user.company_id:
                query = query.filter(
                    db.or_(
                        ExportContract.buyer_company_id == user.company_id,
                        ExportContract.exporter_company_id == user.company_id
                    )
                )

        # Apply filters
        contract_id = request.args.get('contract_id')
        if contract_id:
            query = query.filter(ContractFixation.export_contract_id == int(contract_id))

        start_date = request.args.get('start_date')
        if start_date:
            query = query.filter(ContractFixation.fixation_date >= datetime.fromisoformat(start_date))

        end_date = request.args.get('end_date')
        if end_date:
            query = query.filter(ContractFixation.fixation_date <= datetime.fromisoformat(end_date))

        # Pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        pagination = query.order_by(ContractFixation.fixation_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        fixations = []
        for fixation in pagination.items:
            fixation_data = fixation.to_dict()
            fixation_data['contract'] = {
                'id': fixation.export_contract.id,
                'contract_code': fixation.export_contract.contract_code,
                'buyer_company': fixation.export_contract.buyer_company.name if fixation.export_contract.buyer_company else None,
                'exporter_company': fixation.export_contract.exporter_company.name if fixation.export_contract.exporter_company else None
            }
            fixation_data['created_by'] = fixation.created_by_user.to_dict() if fixation.created_by_user else None
            fixations.append(fixation_data)

        return jsonify({
            'fixations': fixations,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })

    except Exception as e:
        logger.error(f"Error getting fixations: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@fixations_bp.route('/contract/<int:contract_id>', methods=['POST'])
@jwt_required()
def create_fixation(contract_id):
    """Create new fixation for a contract"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get contract
        contract = ExportContract.query.get(contract_id)
        if not contract:
            return jsonify({'error': 'Contract not found'}), 404

        # Check permissions
        if user.role not in ['admin', 'broker']:
            if user.company_id not in [contract.buyer_company_id, contract.exporter_company_id]:
                return jsonify({'error': 'Access denied'}), 403

        # Check contract status
        if contract.status not in ['active']:
            return jsonify({'error': 'Contract must be active to create fixations'}), 400

        data = request.get_json()

        # Validate required fields
        required_fields = ['fixed_quantity_mt', 'spot_price_usd']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        fixed_quantity = float(data['fixed_quantity_mt'])
        spot_price = float(data['spot_price_usd'])

        # Validate positive values
        if fixed_quantity <= 0 or spot_price <= 0:
            return jsonify({'error': 'Quantity and price must be positive'}), 400

        # Calculate total value
        total_value = fixed_quantity * spot_price

        # Check available volume
        current_fixed = db.session.query(db.func.sum(ContractFixation.fixed_quantity_mt))\
            .filter(ContractFixation.export_contract_id == contract_id)\
            .scalar() or 0

        available_volume = contract.total_volume_mt - current_fixed

        if fixed_quantity > available_volume:
            return jsonify({
                'error': f'Insufficient available volume. Available: {available_volume} MT'
            }), 400

        # Create fixation
        fixation = ContractFixation(
            export_contract_id=contract_id,
            fixed_quantity_mt=fixed_quantity,
            spot_price_usd=spot_price,
            total_value_usd=total_value,
            fixation_date=datetime.fromisoformat(data.get('fixation_date', datetime.utcnow().isoformat())),
            notes=data.get('notes'),
            created_by_user_id=user_id
        )

        db.session.add(fixation)
        db.session.commit()

        # Update contract fixed volume
        contract.fixed_volume_mt = (contract.fixed_volume_mt or 0) + fixed_quantity
        db.session.commit()

        logger.info(f"Fixation created for contract {contract_id} by user {user_id}")

        return jsonify({
            'message': 'Fixation created successfully',
            'fixation': fixation.to_dict(),
            'contract_summary': {
                'total_volume': contract.total_volume_mt,
                'fixed_volume': contract.fixed_volume_mt,
                'available_volume': contract.total_volume_mt - contract.fixed_volume_mt
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating fixation: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@fixations_bp.route('/<int:fixation_id>', methods=['GET'])
@jwt_required()
def get_fixation(fixation_id):
    """Get specific fixation"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        fixation = ContractFixation.query.get(fixation_id)
        if not fixation:
            return jsonify({'error': 'Fixation not found'}), 404

        # Check permissions
        contract = fixation.export_contract
        if user.role not in ['admin', 'broker']:
            if user.company_id not in [contract.buyer_company_id, contract.exporter_company_id]:
                return jsonify({'error': 'Access denied'}), 403

        fixation_data = fixation.to_dict()
        fixation_data['contract'] = contract.to_dict()
        fixation_data['created_by'] = fixation.created_by_user.to_dict() if fixation.created_by_user else None

        return jsonify({'fixation': fixation_data})

    except Exception as e:
        logger.error(f"Error getting fixation {fixation_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@fixations_bp.route('/<int:fixation_id>', methods=['PUT'])
@jwt_required()
def update_fixation(fixation_id):
    """Update fixation (limited fields)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        fixation = ContractFixation.query.get(fixation_id)
        if not fixation:
            return jsonify({'error': 'Fixation not found'}), 404

        # Check permissions
        contract = fixation.export_contract
        if user.role not in ['admin']:
            if fixation.created_by_user_id != user_id:
                return jsonify({'error': 'Only fixation creator or admin can update'}), 403

        data = request.get_json()

        # Only allow updating notes
        if 'notes' in data:
            fixation.notes = data['notes']

        fixation.updated_at = datetime.utcnow()

        db.session.commit()

        logger.info(f"Fixation {fixation_id} updated by user {user_id}")

        return jsonify({
            'message': 'Fixation updated successfully',
            'fixation': fixation.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating fixation {fixation_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@fixations_bp.route('/<int:fixation_id>', methods=['DELETE'])
@jwt_required()
def delete_fixation(fixation_id):
    """Delete fixation"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        fixation = ContractFixation.query.get(fixation_id)
        if not fixation:
            return jsonify({'error': 'Fixation not found'}), 404

        # Check permissions
        if user.role not in ['admin']:
            if fixation.created_by_user_id != user_id:
                return jsonify({'error': 'Only fixation creator or admin can delete'}), 403

        # Get contract for volume update
        contract = fixation.export_contract

        # Remove fixation volume from contract
        contract.fixed_volume_mt = (contract.fixed_volume_mt or 0) - fixation.fixed_quantity_mt

        db.session.delete(fixation)
        db.session.commit()

        logger.info(f"Fixation {fixation_id} deleted by user {user_id}")

        return jsonify({
            'message': 'Fixation deleted successfully',
            'contract_summary': {
                'total_volume': contract.total_volume_mt,
                'fixed_volume': contract.fixed_volume_mt,
                'available_volume': contract.total_volume_mt - contract.fixed_volume_mt
            }
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting fixation {fixation_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@fixations_bp.route('/contract/<int:contract_id>/summary', methods=['GET'])
@jwt_required()
def get_contract_fixation_summary(contract_id):
    """Get fixation summary for a contract"""
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

        # Calculate summary
        fixations = ContractFixation.query.filter_by(export_contract_id=contract_id)\
            .order_by(ContractFixation.fixation_date).all()

        total_fixed_quantity = sum(f.fixed_quantity_mt for f in fixations)
        total_value = sum(f.total_value_usd for f in fixations)
        avg_price = total_value / total_fixed_quantity if total_fixed_quantity > 0 else 0

        # Group by month
        monthly_summary = {}
        for fixation in fixations:
            month_key = fixation.fixation_date.strftime('%Y-%m')
            if month_key not in monthly_summary:
                monthly_summary[month_key] = {
                    'quantity': 0,
                    'value': 0,
                    'count': 0
                }
            monthly_summary[month_key]['quantity'] += fixation.fixed_quantity_mt
            monthly_summary[month_key]['value'] += fixation.total_value_usd
            monthly_summary[month_key]['count'] += 1

        return jsonify({
            'contract_id': contract_id,
            'contract_code': contract.contract_code,
            'total_volume': contract.total_volume_mt,
            'fixed_volume': total_fixed_quantity,
            'available_volume': contract.total_volume_mt - total_fixed_quantity,
            'total_value_usd': total_value,
            'average_price_usd': avg_price,
            'fixation_count': len(fixations),
            'monthly_summary': monthly_summary,
            'fixations': [f.to_dict() for f in fixations]
        })

    except Exception as e:
        logger.error(f"Error getting fixation summary for contract {contract_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
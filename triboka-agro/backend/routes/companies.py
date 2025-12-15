"""
Company routes for Triboka BaaS Platform
Manage company information and settings
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from models.models import Company, User, db
from services.blockchain_service import BlockchainService

companies_bp = Blueprint('companies', __name__)
blockchain_service = BlockchainService()

@companies_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_company_profile():
    """Get current company profile"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        company = user.company
        company_data = company.to_dict()
        
        # Add subscription info
        company_data['subscription_info'] = {
            'plan': company.subscription_plan,
            'status': company.subscription_status,
            'expires_at': company.subscription_expires_at.isoformat() if company.subscription_expires_at else None,
            'auto_renew': company.auto_renew_subscription
        }
        
        # Add usage statistics
        from services.nft_service import NFTService
        nft_service = NFTService()
        company_data['usage_stats'] = nft_service.get_monthly_nft_usage(company.id)
        
        return jsonify({'company': company_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@companies_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_company_profile():
    """Update company profile"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        company = user.company
        
        # Update allowed fields
        updateable_fields = [
            'name', 'description', 'country', 'address', 'phone', 
            'website', 'contact_email', 'business_type'
        ]
        
        for field in updateable_fields:
            if field in data:
                setattr(company, field, data[field])
        
        company.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Company profile updated successfully',
            'company': company.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@companies_bp.route('/wallet', methods=['GET'])
@jwt_required()
def get_wallet_info():
    """Get company blockchain wallet information"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        company = user.company
        wallet_info = {
            'wallet_address': company.wallet_address,
            'has_wallet': bool(company.wallet_address),
            'blockchain_stats': None
        }
        
        # Get blockchain balance if wallet exists
        if company.wallet_address:
            balance = blockchain_service.get_balance(company.wallet_address)
            wallet_info['blockchain_stats'] = {
                'balance_eth': balance,
                'network_connected': blockchain_service.is_connected()
            }
        
        return jsonify({'wallet': wallet_info})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@companies_bp.route('/wallet', methods=['POST'])
@jwt_required()
def set_wallet_address():
    """Set company blockchain wallet address"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        if 'wallet_address' not in data:
            return jsonify({'error': 'Wallet address is required'}), 400
        
        wallet_address = data['wallet_address']
        
        # Basic validation
        if not wallet_address.startswith('0x') or len(wallet_address) != 42:
            return jsonify({'error': 'Invalid wallet address format'}), 400
        
        company = user.company
        company.wallet_address = wallet_address
        company.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Wallet address updated successfully',
            'wallet_address': wallet_address
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@companies_bp.route('/subscription', methods=['GET'])
@jwt_required()
def get_subscription_info():
    """Get detailed subscription information"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        company = user.company
        
        # Get plan details
        from config.config import Config
        config = Config.get_instance()
        
        plan_details = {
            'starter': {
                'name': 'Starter',
                'price_monthly': 99,
                'nft_limit': 50,
                'features': ['Basic lot tracking', 'NFT certificates', 'API access']
            },
            'professional': {
                'name': 'Professional', 
                'price_monthly': 299,
                'nft_limit': 200,
                'features': ['Advanced analytics', 'Custom branding', 'Priority support']
            },
            'enterprise': {
                'name': 'Enterprise',
                'price_monthly': 499,
                'nft_limit': -1,  # Unlimited
                'features': ['Unlimited NFTs', 'Custom integration', 'Dedicated support']
            }
        }
        
        current_plan = plan_details.get(company.subscription_plan, plan_details['starter'])
        
        # Calculate usage
        from services.nft_service import NFTService
        nft_service = NFTService()
        usage_stats = nft_service.get_monthly_nft_usage(company.id)
        
        subscription_info = {
            'current_plan': company.subscription_plan,
            'plan_details': current_plan,
            'status': company.subscription_status,
            'expires_at': company.subscription_expires_at.isoformat() if company.subscription_expires_at else None,
            'auto_renew': company.auto_renew_subscription,
            'usage': usage_stats,
            'available_plans': plan_details
        }
        
        return jsonify({'subscription': subscription_info})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@companies_bp.route('/subscription/upgrade', methods=['POST'])
@jwt_required()
def upgrade_subscription():
    """Upgrade subscription plan"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        if 'plan' not in data:
            return jsonify({'error': 'Plan is required'}), 400
        
        new_plan = data['plan']
        valid_plans = ['starter', 'professional', 'enterprise']
        
        if new_plan not in valid_plans:
            return jsonify({'error': 'Invalid plan'}), 400
        
        company = user.company
        
        # In a real implementation, this would integrate with payment processor
        # For now, we'll just update the plan
        company.subscription_plan = new_plan
        company.subscription_status = 'active'
        company.updated_at = datetime.utcnow()
        
        # Extend subscription by 30 days
        from datetime import timedelta
        if company.subscription_expires_at:
            company.subscription_expires_at += timedelta(days=30)
        else:
            company.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Subscription upgraded to {new_plan}',
            'plan': new_plan,
            'expires_at': company.subscription_expires_at.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@companies_bp.route('/users', methods=['GET'])
@jwt_required()
def get_company_users():
    """Get all users in the company"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        users = User.query.filter_by(company_id=user.company_id).all()
        
        users_data = []
        for u in users:
            user_data = u.to_dict()
            # Remove sensitive information
            user_data.pop('password_hash', None)
            users_data.append(user_data)
        
        return jsonify({'users': users_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@companies_bp.route('/users', methods=['POST'])
@jwt_required()
def invite_user():
    """Invite new user to company"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'name', 'role']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Create new user
        from werkzeug.security import generate_password_hash
        import secrets
        
        temp_password = secrets.token_urlsafe(12)
        
        new_user = User(
            email=data['email'],
            name=data['name'],
            role=data['role'],
            company_id=user.company_id,
            password_hash=generate_password_hash(temp_password),
            is_active=True,
            must_change_password=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # In a real implementation, send invitation email with temp password
        
        return jsonify({
            'message': 'User invited successfully',
            'user': new_user.to_dict(),
            'temporary_password': temp_password  # In production, don't return this
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@companies_bp.route('/users/<user_uuid>', methods=['PUT'])
@jwt_required()
def update_user():
    """Update user information"""
    try:
        current_user_uuid = get_jwt_identity()
        current_user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        user_uuid = request.view_args['user_uuid']
        data = request.get_json()
        
        # Find user to update
        user_to_update = User.query.filter_by(
            uuid=user_uuid,
            company_id=current_user.company_id
        ).first()
        
        if not user_to_update:
            return jsonify({'error': 'User not found'}), 404
        
        # Update allowed fields
        updateable_fields = ['name', 'role', 'is_active']
        
        for field in updateable_fields:
            if field in data:
                setattr(user_to_update, field, data[field])
        
        user_to_update.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user_to_update.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@companies_bp.route('/users/<user_uuid>', methods=['DELETE'])
@jwt_required()
def deactivate_user(user_uuid):
    """Deactivate user (soft delete)"""
    try:
        current_user_uuid = get_jwt_identity()
        current_user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Find user to deactivate
        user_to_deactivate = User.query.filter_by(
            uuid=user_uuid,
            company_id=current_user.company_id
        ).first()
        
        if not user_to_deactivate:
            return jsonify({'error': 'User not found'}), 404
        
        if user_to_deactivate.uuid == current_user.uuid:
            return jsonify({'error': 'Cannot deactivate yourself'}), 400
        
        user_to_deactivate.is_active = False
        user_to_deactivate.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'User deactivated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@companies_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_company_stats():
    """Get comprehensive company statistics"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        company_id = user.company_id
        
        # Get NFT statistics
        from services.nft_service import NFTService
        nft_service = NFTService()
        nft_stats = nft_service.get_company_nft_stats(company_id)
        
        # Get lot statistics
        from models.models import Lot
        from sqlalchemy import func
        
        total_lots = Lot.query.filter_by(company_id=company_id).count()
        total_quantity = db.session.query(func.sum(Lot.quantity_kg)).filter_by(company_id=company_id).scalar() or 0
        
        # Get user count
        user_count = User.query.filter_by(company_id=company_id, is_active=True).count()
        
        stats = {
            'company': {
                'total_lots': total_lots,
                'total_quantity_kg': float(total_quantity),
                'active_users': user_count
            },
            'nfts': nft_stats,
            'blockchain': blockchain_service.get_network_stats() if blockchain_service.is_connected() else None
        }
        
        return jsonify({'stats': stats})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
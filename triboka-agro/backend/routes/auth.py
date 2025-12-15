"""
Authentication routes for Triboka BaaS Platform
JWT-based authentication with company management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, verify_jwt_in_request
)
from werkzeug.exceptions import BadRequest
from datetime import datetime
import secrets

from models.models import User, Company, db
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_bp.route('/register', methods=['POST'])
def register_company():
    """Register a new company and admin user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['company_name', 'admin_email', 'admin_password', 'admin_first_name', 'admin_last_name']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if company email already exists
        if Company.query.filter_by(email=data['admin_email']).first():
            return jsonify({'error': 'Company email already registered'}), 409
        
        # Check if admin email already exists
        if User.query.filter_by(email=data['admin_email']).first():
            return jsonify({'error': 'Admin email already registered'}), 409
        
        # Create company
        company = Company(
            name=data['company_name'],
            email=data['admin_email'],
            phone=data.get('phone'),
            address=data.get('address'),
            country=data.get('country'),
            plan_type=data.get('plan_type', 'basic'),
            api_key=secrets.token_urlsafe(32)
        )
        
        db.session.add(company)
        db.session.flush()  # Get company ID
        
        # Create admin user
        admin_user = User(
            email=data['admin_email'],
            first_name=data['admin_first_name'],
            last_name=data['admin_last_name'],
            role='admin',
            company_id=company.id
        )
        admin_user.set_password(data['admin_password'])
        
        db.session.add(admin_user)
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(identity=admin_user.uuid)
        refresh_token = create_refresh_token(identity=admin_user.uuid)
        
        return jsonify({
            'message': 'Company registered successfully',
            'company': company.to_dict(),
            'user': admin_user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login with email and password"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Check company status
        if not user.company.is_active:
            return jsonify({'error': 'Company account is suspended'}), 401
        
        # Update login info
        user.last_login = datetime.utcnow()
        user.login_count += 1
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(identity=user.uuid)
        refresh_token = create_refresh_token(identity=user.uuid)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'company': user.company.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 404
        
        new_token = create_access_token(identity=current_user_uuid)
        
        return jsonify({
            'access_token': new_token
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict(),
            'company': user.company.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current and new password required'}), 400
        
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password incorrect'}), 401
        
        if len(data['new_password']) < 8:
            return jsonify({'error': 'New password must be at least 8 characters'}), 400
        
        user.set_password(data['new_password'])
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/company/api-key/regenerate', methods=['POST'])
@jwt_required()
def regenerate_api_key():
    """Regenerate company API key"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Generate new API key
        user.company.api_key = secrets.token_urlsafe(32)
        user.company.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'API key regenerated successfully',
            'api_key': user.company.api_key
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/validate-token', methods=['GET'])
@jwt_required()
def validate_token():
    """Validate current JWT token"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        
        if not user or not user.is_active:
            return jsonify({'valid': False, 'error': 'Invalid user'}), 401
        
        return jsonify({
            'valid': True,
            'user_uuid': current_user_uuid,
            'company_id': user.company_id,
            'role': user.role
        })
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 401
"""
User management routes for Triboka BaaS Platform
CRUD operations for users within companies
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from datetime import datetime

from models.models import User, Company, db

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users for the current user's company"""
    try:
        current_user_uuid = get_jwt_identity()
        current_user = User.query.filter_by(uuid=current_user_uuid).first()

        if not current_user:
            return jsonify({'error': 'User not found'}), 404

        # Get all users for the company
        users = User.query.filter_by(company_id=current_user.company_id).all()

        return jsonify({
            'users': [user.to_dict() for user in users]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('', methods=['POST'])
@jwt_required()
def create_user():
    """Create a new user for the current user's company"""
    try:
        current_user_uuid = get_jwt_identity()
        current_user = User.query.filter_by(uuid=current_user_uuid).first()

        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'first_name', 'last_name', 'password', 'role']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409

        # Validate role
        if data['role'] not in ['admin', 'manager', 'user']:
            return jsonify({'error': 'Invalid role'}), 400

        # Create user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role'],
            company_id=current_user.company_id
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<user_uuid>', methods=['PUT'])
@jwt_required()
def update_user(user_uuid):
    """Update a user"""
    try:
        current_user_uuid = get_jwt_identity()
        current_user = User.query.filter_by(uuid=current_user_uuid).first()

        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        user = User.query.filter_by(uuid=user_uuid, company_id=current_user.company_id).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'role' in data and data['role'] in ['admin', 'manager', 'user']:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']

        user.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<user_uuid>', methods=['DELETE'])
@jwt_required()
def delete_user(user_uuid):
    """Delete a user (soft delete by deactivating)"""
    try:
        current_user_uuid = get_jwt_identity()
        current_user = User.query.filter_by(uuid=current_user_uuid).first()

        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        user = User.query.filter_by(uuid=user_uuid, company_id=current_user.company_id).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Prevent deleting the last admin
        if user.role == 'admin':
            admin_count = User.query.filter_by(
                company_id=current_user.company_id,
                role='admin',
                is_active=True
            ).count()
            if admin_count <= 1:
                return jsonify({'error': 'Cannot delete the last admin user'}), 400

        # Soft delete by deactivating
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'User deactivated successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
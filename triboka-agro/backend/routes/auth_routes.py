from flask import Blueprint, request, jsonify
import os
from keycloak import KeycloakAdmin
from models_simple import db, User, Company

auth_routes_bp = Blueprint('auth_routes', __name__)

# Keycloak Configuration for Admin Access
KEYCLOAK_SERVER_URL = os.getenv('KEYCLOAK_SERVER_URL', 'https://auth.triboka.com')
KEYCLOAK_REALM_NAME = os.getenv('KEYCLOAK_REALM_NAME', 'triboka')
KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID', 'triboka-mobile')
KEYCLOAK_ADMIN_USER = os.getenv('KEYCLOAK_ADMIN_USER', 'admin') # Needs to be set in env
KEYCLOAK_ADMIN_PASSWORD = os.getenv('KEYCLOAK_ADMIN_PASSWORD', 'admin') # Needs to be set in env

@auth_routes_bp.route('/auth/register', methods=['POST'])
def register_user_natively():
    """
    Native registration endpoint for Mobile App.
    Creates user in Keycloak and syncs to local DB.
    """
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        role = data.get('role', 'user') # Default to user

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # 1. Initialize Keycloak Admin Client
        # Note: In production, you might want to reuse this connection or handle token expiration
        keycloak_admin = KeycloakAdmin(
            server_url=KEYCLOAK_SERVER_URL + '/' if not KEYCLOAK_SERVER_URL.endswith('/') else KEYCLOAK_SERVER_URL,
            username=KEYCLOAK_ADMIN_USER,
            password=KEYCLOAK_ADMIN_PASSWORD,
            realm_name=KEYCLOAK_REALM_NAME,
            user_realm_name='master', # Admin usually lives in master
            verify=True
        )

        # 2. Check if user exists in Keycloak
        # keycloak_admin.get_user_id(email) could fail if not found, safer to create and catch conflict
        
        # 3. Create User in Keycloak
        new_user_payload = {
            "email": email,
            "username": email,
            "enabled": True,
            "firstName": first_name,
            "lastName": last_name,
            "credentials": [{"value": password, "type": "password", "temporary": False}],
            "emailVerified": False # Or True if you trust this source
        }
        
        try:
            user_id = keycloak_admin.create_user(new_user_payload)
        except Exception as e:
            if "409" in str(e):
                return jsonify({'error': 'User already exists in Keycloak'}), 409
            raise e

        # 4. Create/Sync User in Local DB (models_simple.User)
        # Check if local user exists
        from models_simple import UserProfile # Import locally to avoid circular issues if any

        local_user = User.query.filter_by(email=email).first()
        if not local_user:
            local_user = User(
                keycloak_id=user_id, # Save the UUID from Keycloak
                email=email,
                name=f"{first_name} {last_name}".strip(),
                first_name=first_name,
                last_name=last_name,
                role=role,
                active=True
            )
            db.session.add(local_user)
            db.session.flush() # Flush to get local_user.id for profile

            # Create UserProfile with business data
            location = data.get('location', '')
            product_type = data.get('productType', '')
            
            new_profile = UserProfile(
                user_id=local_user.id,
                location=location,
                product_type=product_type,
                business_type=role # Initially sync business type with role
            )
            db.session.add(new_profile)
            
            db.session.commit()
        else:
            # If user exists locally (rare race condition but possible), ensure keycloak_id is linked
            if not local_user.keycloak_id:
                local_user.keycloak_id = user_id
                db.session.commit()

        return jsonify({
            'message': 'User registered successfully',
            'userId': user_id
        }), 201

    except Exception as e:
        print(f"Registration Error: {e}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

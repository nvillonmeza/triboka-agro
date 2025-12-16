import os
import jwt
from functools import wraps
from flask import request, jsonify, g
from keycloak import KeycloakOpenID

# Configuración de Keycloak desde variables de entorno
KEYCLOAK_SERVER_URL = os.getenv('KEYCLOAK_SERVER_URL', 'https://auth.triboka.com/')
KEYCLOAK_REALM_NAME = os.getenv('KEYCLOAK_REALM_NAME', 'triboka')
KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID', 'triboka-mobile')
KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET', '') # Opcional si es cliente público

# Instancia de KeycloakOpenID para interactuar con Keycloak
keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_SERVER_URL,
    client_id=KEYCLOAK_CLIENT_ID,
    realm_name=KEYCLOAK_REALM_NAME,
    client_secret_key=KEYCLOAK_CLIENT_SECRET,
    verify=True
)

def require_auth(roles=None):
    """
    Decorador para proteger endpoints verificando el token de Keycloak.
    :param roles: Lista de roles permitidos (opcional). Si se pasa, el usuario debe tener al menos uno.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'message': 'Authorization header is missing'}), 401
            
            try:
                # El formato debe ser "Bearer <token>"
                parts = auth_header.split()
                if parts[0].lower() != 'bearer':
                    raise ValueError('Authorization header must start with Bearer')
                elif len(parts) == 1:
                    raise ValueError('Token not found')
                elif len(parts) > 2:
                    raise ValueError('Authorization header must be Bearer token')
                
                token = parts[1]
                
                # Opciones de decodificación
                options = {
                    'verify_signature': True,
                    'verify_aud': False, # A veces la audiencia puede variar, ajustar según necesidad
                    'verify_exp': True
                }
                
                # Obtener la clave pública de Keycloak se hace automáticamente con keycloak_openid.decode_token
                # o userinfo, pero para validación local rápida usamos la public key del realm.
                # keycloak_openid.public_key() nos da la clave pública formato PEM
                
                # Validar el token contra Keycloak (introspección offline usando la clave pública)
                # Nota: decode_token de python-keycloak ya maneja la validación de firma si se le pasa la key.
                KEYCLOAK_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n" + keycloak_openid.public_key() + "\n-----END PUBLIC KEY-----"
                
                decoded_token = keycloak_openid.decode_token(
                    token,
                    key=KEYCLOAK_PUBLIC_KEY,
                    options=options
                )
                
                # Inyectar datos del usuario en el contexto global de Flask
                g.user = decoded_token
                g.user_id = decoded_token.get('sub')
                g.user_roles = decoded_token.get('realm_access', {}).get('roles', [])
                
                # Verificación de roles (si se requieren)
                if roles:
                    has_role = any(role in g.user_roles for role in roles)
                    if not has_role:
                        return jsonify({'message': 'Insufficient permissions'}), 403
                        
            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'Token has expired'}), 401
            except jwt.InvalidTokenError as e:
                return jsonify({'message': f'Invalid token: {str(e)}'}), 401
            except Exception as e:
                return jsonify({'message': f'Authentication error: {str(e)}'}), 401

            return f(*args, **kwargs)
        return decorated_function
    return decorator

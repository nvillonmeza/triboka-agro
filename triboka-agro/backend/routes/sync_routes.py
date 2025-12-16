from flask import Blueprint, request, jsonify, g
from middleware.auth_middleware import require_auth
import time

sync_bp = Blueprint('sync', __name__)

@sync_bp.route('/sync/delta', methods=['GET'])
@require_auth(roles=['proveedor', 'admin', 'vendedor'])
def get_delta_updates():
    """
    Retorna los cambios ocurridos desde `last_sync`.
    """
    last_sync_timestamp = request.args.get('last_sync', type=int, default=0)
    
    # Convertir timestamp a datetime si es necesario
    # last_sync_dt = datetime.fromtimestamp(last_sync_timestamp / 1000.0)
    
    # Aquí consultarías tu base de datos buscando registros con updated_at > last_sync_dt
    # Ejemplo simulado:
    
    response_data = {
        'server_timestamp': int(time.time() * 1000),
        'categories': [], # Fetch from DB where updated_at > last_sync
        'products': [],
        # ... otras entidades
    }
    
    # Lógica real de DB (pseudo-código):
    # categories = Category.query.filter(Category.updated_at > last_sync_dt).all()
    # response_data['categories'] = [cat.to_dict() for cat in categories]
    
    return jsonify(response_data)

@sync_bp.route('/sync/push', methods=['POST'])
@require_auth()
def receive_offline_transaction():
    """
    Endpoint genérico si se prefiere un solo punto de entrada para transacciones offline.
    Alternativamente, el cliente llama a los endpoints REST normales.
    """
    data = request.json
    # Procesar data...
    return jsonify({'status': 'success', 'synced_at': int(time.time() * 1000)})

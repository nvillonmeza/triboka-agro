"""
Routes for AgroWeight Cloud integration
Minimal blueprint with lot search functionality
"""

from flask import Blueprint, jsonify
from models_simple import ProducerLot

agroweight_bp = Blueprint('agroweight', __name__)

@agroweight_bp.route('/lots/id/<lote_id>', methods=['GET'])
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
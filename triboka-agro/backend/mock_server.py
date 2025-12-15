from flask import Flask, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Datos de ejemplo de lotes para testing
mock_lotes = {
    "NFT12345": {
        "id": 1,
        "lot_code": "NFT12345",
        "producer_company": "Finca El Paraíso",
        "producer_name": "Juan Pérez",
        "farm_name": "Finca El Paraíso",
        "location": "Chiriquí, Panamá",
        "product_type": "Cacao Fino",
        "weight_kg": 250.5,
        "quality_grade": "Premium",
        "harvest_date": "2024-10-15",
        "certifications": "Orgánico,Fair Trade,Rainforest Alliance",
        "status": "available",
        "blockchain_lot_id": "NFT12345",
        "metadata": {
            "moisture_content": 6.8,
            "quality_score": 95,
            "certifications_list": ["Orgánico", "Fair Trade", "Rainforest Alliance"]
        }
    },
    "LOT67890": {
        "id": 2,
        "lot_code": "LOT67890",
        "producer_company": "Cooperativa Los Cacaos",
        "producer_name": "María González",
        "farm_name": "Finca La Esperanza",
        "location": "Bocas del Toro, Panamá",
        "product_type": "Cacao Criollo",
        "weight_kg": 180.0,
        "quality_grade": "Excelente",
        "harvest_date": "2024-11-01",
        "certifications": "Orgánico,Fair Trade",
        "status": "available",
        "blockchain_lot_id": "LOT67890",
        "metadata": {
            "moisture_content": 7.2,
            "quality_score": 92,
            "certifications_list": ["Orgánico", "Fair Trade"]
        }
    }
}

@app.route('/api/lots/id/<lote_id>', methods=['GET'])
def get_lote_by_id(lote_id):
    """Buscar lote por ID (simulado para testing)"""
    if lote_id in mock_lotes:
        return jsonify({
            'success': True,
            'lote': mock_lotes[lote_id]
        })
    else:
        return jsonify({
            'error': 'Lote no encontrado',
            'message': f'No se encontró lote con ID: {lote_id}'
        }), 404

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Triboka Agro Mock API',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🚀 Triboka Agro Mock API Server starting...")
    print("📡 API Endpoint: http://localhost:9091/api/lots/id/<lote_id>")
    print("🖥️ Health Check: http://localhost:9091/health")
    app.run(host='0.0.0.0', port=9091, debug=False)
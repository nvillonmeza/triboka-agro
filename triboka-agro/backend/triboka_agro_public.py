"""
Servicio mínimo de Triboka Agro para integración con AgroWeight Cloud
Proporciona endpoints públicos sin autenticación para acceso desde la app móvil
"""

from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Configuración de la base de datos
DB_PATH = '/home/rootpanel/web/app.triboka.com/backend/instance/triboka_production.db'

def get_db_connection():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({
        'status': 'ok',
        'service': 'Triboka Agro Public API',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/public/lots/available', methods=['GET'])
def get_public_available_lots():
    """Obtener lotes disponibles públicamente para AgroWeight Cloud"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Consulta para obtener lotes disponibles
        cursor.execute("""
            SELECT
                pl.id,
                pl.lot_code,
                c.name as producer_company,
                pl.producer_name,
                pl.farm_name,
                pl.location,
                pl.product_type,
                pl.weight_kg,
                pl.quality_grade,
                pl.harvest_date,
                pl.certifications,
                pl.created_at,
                pl.blockchain_lot_id
            FROM producer_lot pl
            LEFT JOIN company c ON pl.producer_company_id = c.id
            WHERE pl.status = 'available'
            ORDER BY pl.created_at DESC
        """)

        lots = []
        for row in cursor.fetchall():
            lot_data = {
                'id': row['id'],
                'lot_code': row['lot_code'],
                'producer_company': row['producer_company'],
                'producer_name': row['producer_name'],
                'farm_name': row['farm_name'],
                'location': row['location'],
                'product_type': row['product_type'],
                'weight_kg': float(row['weight_kg']) if row['weight_kg'] else 0,
                'quality_grade': row['quality_grade'],
                'harvest_date': row['harvest_date'],
                'certifications': row['certifications'].split(',') if row['certifications'] else [],
                'created_at': row['created_at'],
                'blockchain_lot_id': row['blockchain_lot_id']
            }
            lots.append(lot_data)

        conn.close()
        return jsonify(lots)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/public/lots/<int:lot_id>', methods=['GET'])
def get_public_lot_detail(lot_id):
    """Obtener detalles de un lote específico públicamente"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                pl.id,
                pl.lot_code,
                c.name as producer_company,
                pl.producer_name,
                pl.farm_name,
                pl.location,
                pl.product_type,
                pl.weight_kg,
                pl.quality_grade,
                pl.harvest_date,
                pl.certifications,
                pl.created_at,
                pl.blockchain_lot_id,
                pl.status
            FROM producer_lot pl
            LEFT JOIN company c ON pl.producer_company_id = c.id
            WHERE pl.id = ?
        """, (lot_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({'error': 'Lote no encontrado'}), 404

        lot_data = {
            'id': row['id'],
            'lot_code': row['lot_code'],
            'producer_company': row['producer_company'],
            'producer_name': row['producer_name'],
            'farm_name': row['farm_name'],
            'location': row['location'],
            'product_type': row['product_type'],
            'weight_kg': float(row['weight_kg']) if row['weight_kg'] else 0,
            'quality_grade': row['quality_grade'],
            'harvest_date': row['harvest_date'],
            'certifications': row['certifications'].split(',') if row['certifications'] else [],
            'created_at': row['created_at'],
            'blockchain_lot_id': row['blockchain_lot_id'],
            'status': row['status']
        }

        return jsonify(lot_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Iniciando Triboka Agro Public API en puerto 5007...")
    app.run(host='0.0.0.0', port=5007, debug=False)
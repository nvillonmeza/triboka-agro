"""
Sistema de trazabilidad blockchain para Triboka
Maneja eventos de trazabilidad desde PRODUCER_INIT hasta CUSTOMS_CLEARANCE
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models_simple import db, User, TraceEvent, TraceTimeline, ProducerLot, BatchNFT, Company
from blockchain_service import get_blockchain_integration
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
traceability_bp = Blueprint('traceability', __name__)

# Inicializar integración blockchain
blockchain = get_blockchain_integration()

# =====================================
# EVENTOS DE TRAZABILIDAD DEFINIDOS
# =====================================

TRACEABILITY_EVENTS = {
    'PRODUCER_INIT': {
        'name': 'Inicio de Producción',
        'description': 'Registro inicial del lote en finca',
        'required_measurements': ['weight_kg', 'location', 'harvest_date'],
        'permissions': ['producer', 'admin', 'operator']
    },
    'RECEPCIÓN': {
        'name': 'Recepción en Centro de Acopio',
        'description': 'Lote recibido en centro de acopio',
        'required_measurements': ['weight_kg', 'quality_score', 'moisture_content'],
        'permissions': ['producer', 'exporter', 'admin', 'operator']
    },
    'CALIDAD': {
        'name': 'Control de Calidad',
        'description': 'Evaluación de calidad del lote',
        'required_measurements': ['quality_score', 'moisture_content', 'defects_pct'],
        'permissions': ['exporter', 'admin', 'operator']
    },
    'DRYING': {
        'name': 'Secado',
        'description': 'Proceso de secado del cacao',
        'required_measurements': ['moisture_content', 'drying_time_hours', 'temperature_c'],
        'permissions': ['exporter', 'admin', 'operator']
    },
    'FERMENTATION': {
        'name': 'Fermentación',
        'description': 'Proceso de fermentación',
        'required_measurements': ['fermentation_time_hours', 'temperature_c', 'ph_level'],
        'permissions': ['exporter', 'admin', 'operator']
    },
    'STORAGE': {
        'name': 'Almacenamiento',
        'description': 'Almacenamiento del lote procesado',
        'required_measurements': ['storage_conditions', 'humidity_pct', 'temperature_c'],
        'permissions': ['exporter', 'admin', 'operator']
    },
    'EXPORT_PREPARATION': {
        'name': 'Preparación para Exportación',
        'description': 'Preparación final del lote para exportación',
        'required_measurements': ['final_weight_kg', 'packaging_type', 'destination_country'],
        'permissions': ['exporter', 'admin', 'operator']
    },
    'CUSTOMS_CLEARANCE': {
        'name': 'Despacho Aduanero',
        'description': 'Tramitación aduanera completada',
        'required_measurements': ['customs_declaration_number', 'export_certificate', 'shipping_date'],
        'permissions': ['exporter', 'admin', 'operator']
    },
    'SHIPMENT': {
        'name': 'Embarque',
        'description': 'Producto embarcado hacia destino',
        'required_measurements': ['shipping_company', 'vessel_name', 'bl_number', 'eta'],
        'permissions': ['exporter', 'admin', 'operator']
    }
}

# =====================================
# ENDPOINTS DE TRAZABILIDAD
# =====================================

@traceability_bp.route('/events', methods=['POST'])
@jwt_required()
def create_traceability_event():
    """Crear un nuevo evento de trazabilidad"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        data = request.get_json()

        # Validar datos requeridos
        required_fields = ['event_type', 'entity_type', 'entity_id', 'measurements']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400

        event_type = data['event_type']
        entity_type = data['entity_type']
        entity_id = data['entity_id']
        measurements = data['measurements']

        # Validar que el evento existe
        if event_type not in TRACEABILITY_EVENTS:
            return jsonify({'error': f'Evento no válido: {event_type}'}), 400

        event_config = TRACEABILITY_EVENTS[event_type]

        # Verificar permisos
        if user.role not in event_config['permissions'] and user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para crear este evento'}), 403

        # Verificar que la entidad existe y el usuario tiene acceso
        if not check_entity_permissions(user, entity_type, entity_id):
            return jsonify({'error': 'Sin acceso a esta entidad'}), 403

        # Validar mediciones requeridas
        for measurement in event_config['required_measurements']:
            if measurement not in measurements:
                return jsonify({'error': f'Medición requerida faltante: {measurement}'}), 400

        # Crear evento de trazabilidad
        trace_event = TraceEvent(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            measurements=json.dumps(measurements),
            notes=data.get('notes', ''),
            location=data.get('location', ''),
            created_by_user_id=user_id
        )

        db.session.add(trace_event)
        db.session.flush()

        # Registrar en blockchain si está disponible
        blockchain_tx_hash = None
        if blockchain.is_ready():
            try:
                # Crear hash de los datos del evento
                event_data = {
                    'event_type': event_type,
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'measurements': measurements,
                    'timestamp': trace_event.created_at.isoformat(),
                    'user_id': user_id
                }

                blockchain_tx_hash = blockchain.traceability_service.register_event(
                    event_data=json.dumps(event_data, sort_keys=True),
                    entity_type=entity_type,
                    entity_id=str(entity_id)
                )

                if blockchain_tx_hash:
                    trace_event.blockchain_tx_hash = blockchain_tx_hash

            except Exception as blockchain_error:
                logger.warning(f"Error registrando evento en blockchain: {blockchain_error}")

        # Actualizar timeline
        update_timeline(entity_type, entity_id, trace_event)

        db.session.commit()

        return jsonify({
            'message': 'Evento de trazabilidad creado exitosamente',
            'event_id': trace_event.id,
            'blockchain_tx_hash': blockchain_tx_hash,
            'event': {
                'id': trace_event.id,
                'event_type': trace_event.event_type,
                'entity_type': trace_event.entity_type,
                'entity_id': trace_event.entity_id,
                'measurements': measurements,
                'location': trace_event.location,
                'notes': trace_event.notes,
                'created_at': trace_event.created_at.isoformat(),
                'created_by': user.name
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando evento de trazabilidad: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@traceability_bp.route('/events', methods=['GET'])
@jwt_required()
def get_traceability_events():
    """Obtener eventos de trazabilidad con filtros"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Parámetros de consulta
        entity_type = request.args.get('entity_type')
        entity_id = request.args.get('entity_id')
        event_type = request.args.get('event_type')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        # Base query
        query = TraceEvent.query

        # Aplicar filtros
        if entity_type:
            query = query.filter_by(entity_type=entity_type)
        if entity_id:
            query = query.filter_by(entity_id=entity_id)
        if event_type:
            query = query.filter_by(event_type=event_type)

        # Filtrar por permisos del usuario
        if user.role not in ['admin', 'operator']:
            # Los usuarios normales solo ven eventos de entidades a las que tienen acceso
            allowed_entity_ids = get_allowed_entity_ids(user)
            if allowed_entity_ids:
                query = query.filter(TraceEvent.entity_id.in_(allowed_entity_ids))
            else:
                return jsonify({'events': [], 'total': 0}), 200

        # Ordenar por fecha de creación (más recientes primero)
        query = query.order_by(TraceEvent.created_at.desc())

        # Paginación
        total_count = query.count()
        events = query.offset(offset).limit(limit).all()

        result = []
        for event in events:
            creator = User.query.get(event.created_by_user_id)
            result.append({
                'id': event.id,
                'event_type': event.event_type,
                'event_name': TRACEABILITY_EVENTS.get(event.event_type, {}).get('name', event.event_type),
                'entity_type': event.entity_type,
                'entity_id': event.entity_id,
                'measurements': json.loads(event.measurements) if event.measurements else {},
                'location': event.location,
                'notes': event.notes,
                'blockchain_tx_hash': event.blockchain_tx_hash,
                'created_at': event.created_at.isoformat(),
                'created_by': creator.name if creator else 'Sistema'
            })

        return jsonify({
            'events': result,
            'total': total_count,
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        logger.error(f"Error obteniendo eventos de trazabilidad: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@traceability_bp.route('/timeline/<entity_type>/<entity_id>', methods=['GET'])
@jwt_required()
def get_entity_timeline(entity_type, entity_id):
    """Obtener timeline completo de trazabilidad para una entidad"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Verificar permisos
        if not check_entity_permissions(user, entity_type, entity_id):
            return jsonify({'error': 'Sin acceso a esta entidad'}), 403

        # Obtener eventos de trazabilidad
        events = TraceEvent.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).order_by(TraceEvent.created_at.asc()).all()

        # Obtener timeline si existe
        timeline = TraceTimeline.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).first()

        timeline_events = []
        if timeline and timeline.events_json:
            timeline_events = json.loads(timeline.events_json)

        # Combinar eventos y timeline
        complete_timeline = []

        # Agregar eventos registrados
        for event in events:
            complete_timeline.append({
                'id': f'event_{event.id}',
                'type': 'traceability_event',
                'title': TRACEABILITY_EVENTS.get(event.event_type, {}).get('name', event.event_type),
                'description': TRACEABILITY_EVENTS.get(event.event_type, {}).get('description', ''),
                'timestamp': event.created_at.isoformat(),
                'measurements': json.loads(event.measurements) if event.measurements else {},
                'location': event.location,
                'notes': event.notes,
                'blockchain_tx_hash': event.blockchain_tx_hash,
                'actor': User.query.get(event.created_by_user_id).name if User.query.get(event.created_by_user_id) else 'Sistema'
            })

        # Agregar eventos del timeline
        for timeline_event in timeline_events:
            if not any(t['id'] == timeline_event.get('id') for t in complete_timeline):
                complete_timeline.append(timeline_event)

        # Ordenar por timestamp
        complete_timeline.sort(key=lambda x: x.get('timestamp', ''), reverse=False)

        return jsonify({
            'entity_type': entity_type,
            'entity_id': entity_id,
            'timeline': complete_timeline,
            'total_events': len(complete_timeline)
        })

    except Exception as e:
        logger.error(f"Error obteniendo timeline: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@traceability_bp.route('/validate-chain/<entity_type>/<entity_id>', methods=['GET'])
@jwt_required()
def validate_traceability_chain(entity_type, entity_id):
    """Validar la cadena de trazabilidad usando blockchain"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Verificar permisos
        if not check_entity_permissions(user, entity_type, entity_id):
            return jsonify({'error': 'Sin acceso a esta entidad'}), 403

        validation_result = {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'is_valid': True,
            'validation_details': [],
            'blockchain_verification': False
        }

        # Obtener eventos
        events = TraceEvent.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).order_by(TraceEvent.created_at.asc()).all()

        # Validar secuencia lógica de eventos
        expected_sequence = list(TRACEABILITY_EVENTS.keys())
        event_sequence = [event.event_type for event in events]

        for i, event_type in enumerate(event_sequence):
            if event_type not in expected_sequence:
                validation_result['is_valid'] = False
                validation_result['validation_details'].append({
                    'type': 'invalid_event',
                    'message': f'Evento no válido en la cadena: {event_type}',
                    'event_index': i
                })

        # Verificar integridad de datos
        for event in events:
            measurements = json.loads(event.measurements) if event.measurements else {}
            event_config = TRACEABILITY_EVENTS.get(event.event_type, {})

            for required_measurement in event_config.get('required_measurements', []):
                if required_measurement not in measurements:
                    validation_result['is_valid'] = False
                    validation_result['validation_details'].append({
                        'type': 'missing_measurement',
                        'message': f'Medición requerida faltante: {required_measurement}',
                        'event_type': event.event_type
                    })

        # Verificar blockchain si está disponible
        if blockchain.is_ready():
            try:
                blockchain_valid = blockchain.traceability_service.verify_chain(
                    entity_type=entity_type,
                    entity_id=str(entity_id)
                )
                validation_result['blockchain_verification'] = blockchain_valid

                if not blockchain_valid:
                    validation_result['is_valid'] = False
                    validation_result['validation_details'].append({
                        'type': 'blockchain_verification_failed',
                        'message': 'La verificación blockchain falló'
                    })

            except Exception as blockchain_error:
                logger.warning(f"Error verificando blockchain: {blockchain_error}")

        return jsonify(validation_result)

    except Exception as e:
        logger.error(f"Error validando cadena de trazabilidad: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# =====================================
# FUNCIONES AUXILIARES
# =====================================

def check_entity_permissions(user, entity_type, entity_id):
    """Verificar si el usuario tiene permisos para acceder a una entidad"""
    try:
        if user.role in ['admin', 'operator']:
            return True

        if entity_type == 'lot':
            lot = ProducerLot.query.get(int(entity_id))
            if not lot:
                return False

            if user.role == 'producer' and lot.producer_company_id == user.company_id:
                return True
            elif user.role == 'exporter' and lot.purchased_by_company_id == user.company_id:
                return True

        elif entity_type == 'batch':
            batch = BatchNFT.query.get(int(entity_id))
            if not batch:
                return False

            if user.role == 'exporter' and batch.creator_company_id == user.company_id:
                return True

        return False

    except Exception as e:
        logger.error(f"Error checking entity permissions: {str(e)}")
        return False

def get_allowed_entity_ids(user):
    """Obtener IDs de entidades a las que el usuario tiene acceso"""
    try:
        allowed_ids = []

        if user.role == 'producer':
            # Lotes del productor
            lots = ProducerLot.query.filter_by(producer_company_id=user.company_id).all()
            allowed_ids.extend([str(lot.id) for lot in lots])

        elif user.role == 'exporter':
            # Lotes comprados por el exportador
            purchased_lots = ProducerLot.query.filter_by(purchased_by_company_id=user.company_id).all()
            allowed_ids.extend([str(lot.id) for lot in purchased_lots])

            # Batches creados por el exportador
            batches = BatchNFT.query.filter_by(creator_company_id=user.company_id).all()
            allowed_ids.extend([f"batch_{batch.id}" for batch in batches])

        return allowed_ids

    except Exception as e:
        logger.error(f"Error getting allowed entity IDs: {str(e)}")
        return []

def update_timeline(entity_type, entity_id, trace_event):
    """Actualizar el timeline de trazabilidad para una entidad"""
    try:
        # Obtener o crear timeline
        timeline = TraceTimeline.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).first()

        if not timeline:
            timeline = TraceTimeline(
                entity_type=entity_type,
                entity_id=entity_id,
                events_json=json.dumps([])
            )
            db.session.add(timeline)

        # Obtener eventos existentes
        events = json.loads(timeline.events_json) if timeline.events_json else []

        # Agregar nuevo evento
        new_event = {
            'id': f'event_{trace_event.id}',
            'type': 'traceability_event',
            'event_type': trace_event.event_type,
            'title': TRACEABILITY_EVENTS.get(trace_event.event_type, {}).get('name', trace_event.event_type),
            'description': TRACEABILITY_EVENTS.get(trace_event.event_type, {}).get('description', ''),
            'timestamp': trace_event.created_at.isoformat(),
            'measurements': json.loads(trace_event.measurements) if trace_event.measurements else {},
            'location': trace_event.location,
            'notes': trace_event.notes,
            'blockchain_tx_hash': trace_event.blockchain_tx_hash,
            'actor': User.query.get(trace_event.created_by_user_id).name if User.query.get(trace_event.created_by_user_id) else 'Sistema'
        }

        events.append(new_event)

        # Actualizar timeline
        timeline.events_json = json.dumps(events)
        timeline.updated_at = datetime.utcnow()

    except Exception as e:
        logger.error(f"Error updating timeline: {str(e)}")


class TraceabilityManager:
    """Gestor de trazabilidad para operaciones avanzadas"""

    def __init__(self):
        self.blockchain = blockchain

    def record_event(self, event_type: str, entity_type: str, entity_id: int,
                    measurements: dict, user_id: int, location: str = None,
                    notes: str = None) -> dict:
        """Registrar un evento de trazabilidad"""
        try:
            # Validar evento
            if event_type not in TRACEABILITY_EVENTS:
                raise ValueError(f"Tipo de evento no válido: {event_type}")

            # Crear evento
            event = TraceEvent(
                event_type=event_type,
                entity_type=entity_type,
                entity_id=entity_id,
                measurements=json.dumps(measurements),
                created_by_user_id=user_id,
                location=location,
                notes=notes
            )

            db.session.add(event)
            db.session.commit()

            # Registrar en blockchain si está disponible
            if self.blockchain:
                try:
                    tx_hash = self.blockchain.record_traceability_event(
                        event_type=event_type,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        measurements=measurements,
                        user_id=user_id
                    )
                    event.blockchain_tx_hash = tx_hash
                    db.session.commit()
                except Exception as e:
                    logger.warning(f"Error registrando en blockchain: {str(e)}")

            return {
                'event_id': event.id,
                'blockchain_tx_hash': event.blockchain_tx_hash,
                'status': 'recorded'
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error recording traceability event: {str(e)}")
            raise

    def get_entity_events(self, entity_type: str, entity_id: int) -> list:
        """Obtener eventos de una entidad"""
        events = TraceEvent.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).order_by(TraceEvent.created_at).all()

        return [{
            'id': event.id,
            'event_type': event.event_type,
            'timestamp': event.created_at.isoformat(),
            'measurements': json.loads(event.measurements) if event.measurements else {},
            'location': event.location,
            'notes': event.notes,
            'blockchain_tx_hash': event.blockchain_tx_hash,
            'user': User.query.get(event.created_by_user_id).name if User.query.get(event.created_by_user_id) else 'Sistema'
        } for event in events]

    def validate_chain(self, entity_type: str, entity_id: int) -> dict:
        """Validar la cadena de trazabilidad"""
        events = self.get_entity_events(entity_type, entity_id)

        if not events:
            return {'valid': False, 'reason': 'No events found'}

        # Validar secuencia lógica de eventos
        expected_sequence = ['PRODUCER_INIT', 'RECEPCIÓN', 'CALIDAD', 'DRYING',
                           'FERMENTATION', 'STORAGE', 'EXPORT_PREPARATION',
                           'CUSTOMS_CLEARANCE', 'SHIPMENT']

        event_types = [e['event_type'] for e in events]
        current_index = 0

        for event_type in event_types:
            if event_type in expected_sequence:
                expected_index = expected_sequence.index(event_type)
                if expected_index < current_index:
                    return {
                        'valid': False,
                        'reason': f'Event {event_type} out of sequence',
                        'expected_order': expected_sequence
                    }
                current_index = expected_index

        # Validar integridad blockchain
        if self.blockchain:
            blockchain_valid = True
            for event in events:
                if event.get('blockchain_tx_hash'):
                    try:
                        is_valid = self.blockchain.verify_transaction(event['blockchain_tx_hash'])
                        if not is_valid:
                            blockchain_valid = False
                            break
                    except Exception as e:
                        logger.warning(f"Error verifying blockchain transaction: {str(e)}")
                        blockchain_valid = False

            if not blockchain_valid:
                return {'valid': False, 'reason': 'Blockchain verification failed'}

        return {
            'valid': True,
            'events_count': len(events),
            'last_event': events[-1]['event_type'] if events else None,
            'blockchain_verified': self.blockchain is not None
        }

    def get_chain_summary(self, entity_type: str, entity_id: int) -> dict:
        """Obtener resumen de la cadena de trazabilidad"""
        events = self.get_entity_events(entity_type, entity_id)

        if not events:
            return {'status': 'empty', 'events': []}

        # Calcular estadísticas
        event_types = [e['event_type'] for e in events]
        timestamps = [datetime.fromisoformat(e['timestamp']) for e in events]

        return {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'total_events': len(events),
            'event_types': list(set(event_types)),
            'first_event': min(timestamps).isoformat() if timestamps else None,
            'last_event': max(timestamps).isoformat() if timestamps else None,
            'blockchain_integrity': self.validate_chain(entity_type, entity_id)['valid'],
            'events': events
        }


# Instancia global del gestor de trazabilidad
traceability_manager = TraceabilityManager()
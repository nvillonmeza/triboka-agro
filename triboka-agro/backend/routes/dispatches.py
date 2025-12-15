"""
Routes for Dispatch Management - ERP Module
Gestión completa de despachos de cacao con integración logística
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models_simple import db, Dispatch, ExportContract, BatchNFT, User, Company
from datetime import datetime
import logging
import json

dispatches_bp = Blueprint('dispatches', __name__)
logger = logging.getLogger(__name__)

# Estados válidos para despachos
DISPATCH_STATUSES = ['planned', 'in_transit', 'delivered', 'cancelled']
VALID_STATUS_TRANSITIONS = {
    'planned': ['in_transit', 'cancelled'],
    'in_transit': ['delivered', 'cancelled'],
    'delivered': [],
    'cancelled': []
}

@dispatches_bp.route('', methods=['GET'])
@jwt_required()
def get_dispatches():
    """Obtener despachos con filtros y paginación"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Build query based on user role
        query = Dispatch.query

        # Filter by company if not admin
        if user.role not in ['admin', 'broker']:
            if user.company_id:
                # Filtrar por contratos donde la compañía es buyer o exporter
                query = query.join(ExportContract).filter(
                    db.or_(
                        ExportContract.buyer_company_id == user.company_id,
                        ExportContract.exporter_company_id == user.company_id
                    )
                )

        # Apply filters
        status = request.args.get('status')
        if status:
            query = query.filter(Dispatch.status == status)

        contract_id = request.args.get('contract_id')
        if contract_id:
            query = query.filter(Dispatch.contract_id == int(contract_id))

        batch_id = request.args.get('batch_id')
        if batch_id:
            query = query.filter(Dispatch.batch_id == int(batch_id))

        destination_country = request.args.get('destination_country')
        if destination_country:
            query = query.filter(Dispatch.destination_country.ilike(f'%{destination_country}%'))

        # Date filters
        shipping_from = request.args.get('shipping_from')
        if shipping_from:
            query = query.filter(Dispatch.shipping_date >= datetime.fromisoformat(shipping_from).date())

        shipping_to = request.args.get('shipping_to')
        if shipping_to:
            query = query.filter(Dispatch.shipping_date <= datetime.fromisoformat(shipping_to).date())

        # Pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        pagination = query.order_by(Dispatch.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        dispatches = []
        for dispatch in pagination.items:
            dispatch_data = dispatch.to_dict()
            dispatch_data['contract'] = dispatch.contract.to_dict() if dispatch.contract else None
            dispatch_data['batch'] = dispatch.batch.to_dict() if dispatch.batch else None
            dispatch_data['created_by'] = dispatch.created_by.to_dict() if dispatch.created_by else None
            dispatches.append(dispatch_data)

        return jsonify({
            'dispatches': dispatches,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })

    except Exception as e:
        logger.error(f"Error getting dispatches: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@dispatches_bp.route('', methods=['POST'])
@jwt_required()
def create_dispatch():
    """Crear nuevo despacho"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Validar permisos (solo admin, operator o usuarios de compañías exportadoras)
        if user.role not in ['admin', 'operator'] and (not user.company_id or user.role not in ['admin', 'manager', 'operator']):
            return jsonify({'error': 'Sin permisos para crear despachos'}), 403

        data = request.get_json()

        required_fields = ['contract_id', 'batch_id', 'quantity_mt', 'destination_country', 'shipping_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400

        # Validar que el contrato existe y pertenece a la compañía del usuario
        contract = ExportContract.query.get(data['contract_id'])
        if not contract:
            return jsonify({'error': 'Contrato no encontrado'}), 404

        if user.role not in ['admin', 'broker'] and user.company_id not in [contract.buyer_company_id, contract.exporter_company_id]:
            return jsonify({'error': 'Sin permisos para este contrato'}), 403

        # Validar que el batch existe
        batch = BatchNFT.query.get(data['batch_id'])
        if not batch:
            return jsonify({'error': 'Batch no encontrado'}), 404

        # Validar cantidad disponible en el batch
        total_dispatched = db.session.query(db.func.sum(Dispatch.quantity_mt)).filter(
            Dispatch.batch_id == data['batch_id'],
            Dispatch.status != 'cancelled'
        ).scalar() or 0

        available_quantity = float(batch.total_weight_kg) / 1000 - float(total_dispatched)
        if data['quantity_mt'] > available_quantity:
            return jsonify({
                'error': f'Cantidad excede lo disponible. Disponible: {available_quantity:.3f} MT'
            }), 400

        # Crear el despacho
        dispatch = Dispatch(
            contract_id=data['contract_id'],
            batch_id=data['batch_id'],
            quantity_mt=data['quantity_mt'],
            destination_country=data['destination_country'],
            destination_port=data.get('destination_port'),
            destination_company=data.get('destination_company'),
            shipping_date=datetime.fromisoformat(data['shipping_date']).date(),
            estimated_delivery_date=datetime.fromisoformat(data.get('estimated_delivery_date')).date() if data.get('estimated_delivery_date') else None,
            carrier_name=data.get('carrier_name'),
            vessel_name=data.get('vessel_name'),
            tracking_number=data.get('tracking_number'),
            bill_of_lading=data.get('bill_of_lading'),
            freight_cost_usd=data.get('freight_cost_usd'),
            insurance_cost_usd=data.get('insurance_cost_usd'),
            other_costs_usd=data.get('other_costs_usd'),
            notes=data.get('notes'),
            created_by_id=user_id
        )

        # Generar código único
        dispatch.generate_dispatch_code()

        db.session.add(dispatch)
        db.session.commit()

        return jsonify({
            'message': 'Despacho creado exitosamente',
            'dispatch': dispatch.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating dispatch: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@dispatches_bp.route('/<int:dispatch_id>', methods=['GET'])
@jwt_required()
def get_dispatch(dispatch_id):
    """Obtener detalles de un despacho específico"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        dispatch = Dispatch.query.get(dispatch_id)
        if not dispatch:
            return jsonify({'error': 'Despacho no encontrado'}), 404

        # Validar permisos
        if user.role not in ['admin', 'broker']:
            contract = dispatch.contract
            if not contract or user.company_id not in [contract.buyer_company_id, contract.exporter_company_id]:
                return jsonify({'error': 'Sin permisos para ver este despacho'}), 403

        dispatch_data = dispatch.to_dict()
        dispatch_data['contract'] = dispatch.contract.to_dict() if dispatch.contract else None
        dispatch_data['batch'] = dispatch.batch.to_dict() if dispatch.batch else None
        dispatch_data['created_by'] = dispatch.created_by.to_dict() if dispatch.created_by else None

        return jsonify({'dispatch': dispatch_data})

    except Exception as e:
        logger.error(f"Error getting dispatch: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@dispatches_bp.route('/<int:dispatch_id>', methods=['PUT'])
@jwt_required()
def update_dispatch(dispatch_id):
    """Actualizar despacho"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        dispatch = Dispatch.query.get(dispatch_id)
        if not dispatch:
            return jsonify({'error': 'Despacho no encontrado'}), 404

        # Validar permisos
        if user.role not in ['admin', 'broker']:
            contract = dispatch.contract
            if not contract or user.company_id not in [contract.buyer_company_id, contract.exporter_company_id]:
                return jsonify({'error': 'Sin permisos para modificar este despacho'}), 403

        data = request.get_json()

        # Validar transición de estado si se incluye
        if 'status' in data:
            new_status = data['status']
            if new_status not in DISPATCH_STATUSES:
                return jsonify({'error': f'Estado inválido: {new_status}'}), 400

            if dispatch.status not in VALID_STATUS_TRANSITIONS or new_status not in VALID_STATUS_TRANSITIONS[dispatch.status]:
                return jsonify({
                    'error': f'Transición de estado inválida: {dispatch.status} -> {new_status}'
                }), 400

            # Si se marca como delivered, actualizar fecha de entrega real
            if new_status == 'delivered' and not dispatch.actual_delivery_date:
                dispatch.actual_delivery_date = datetime.now().date()

        # Actualizar campos permitidos
        updatable_fields = [
            'destination_port', 'destination_company', 'estimated_delivery_date',
            'carrier_name', 'vessel_name', 'tracking_number', 'bill_of_lading',
            'freight_cost_usd', 'insurance_cost_usd', 'other_costs_usd',
            'documents', 'notes', 'status'
        ]

        for field in updatable_fields:
            if field in data:
                if field.endswith('_date') and data[field]:
                    setattr(dispatch, field, datetime.fromisoformat(data[field]).date())
                else:
                    setattr(dispatch, field, data[field])

        dispatch.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Despacho actualizado exitosamente',
            'dispatch': dispatch.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating dispatch: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@dispatches_bp.route('/<int:dispatch_id>', methods=['DELETE'])
@jwt_required()
def delete_dispatch(dispatch_id):
    """Eliminar despacho (solo si está en estado planned)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        dispatch = Dispatch.query.get(dispatch_id)
        if not dispatch:
            return jsonify({'error': 'Despacho no encontrado'}), 404

        # Solo permitir eliminación si está planned
        if dispatch.status != 'planned':
            return jsonify({'error': 'Solo se pueden eliminar despachos en estado planned'}), 400

        # Validar permisos
        if user.role not in ['admin', 'broker']:
            contract = dispatch.contract
            if not contract or user.company_id not in [contract.buyer_company_id, contract.exporter_company_id]:
                return jsonify({'error': 'Sin permisos para eliminar este despacho'}), 403

        db.session.delete(dispatch)
        db.session.commit()

        return jsonify({'message': 'Despacho eliminado exitosamente'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting dispatch: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@dispatches_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dispatch_stats():
    """Obtener estadísticas de despachos"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Base query con filtros de compañía
        base_query = Dispatch.query
        if user.role not in ['admin', 'broker'] and user.company_id:
            base_query = base_query.join(ExportContract).filter(
                db.or_(
                    ExportContract.buyer_company_id == user.company_id,
                    ExportContract.exporter_company_id == user.company_id
                )
            )

        # Estadísticas generales
        total_dispatches = base_query.count()
        by_status = db.session.query(
            Dispatch.status,
            db.func.count(Dispatch.id)
        ).filter(Dispatch.id.in_([d.id for d in base_query.all()])).group_by(Dispatch.status).all()

        status_counts = {status: count for status, count in by_status}

        # Estadísticas por mes (últimos 12 meses)
        from sqlalchemy import func, extract
        monthly_stats = db.session.query(
            extract('year', Dispatch.created_at).label('year'),
            extract('month', Dispatch.created_at).label('month'),
            db.func.count(Dispatch.id).label('count'),
            db.func.sum(Dispatch.quantity_mt).label('total_quantity')
        ).filter(Dispatch.id.in_([d.id for d in base_query.all()])).group_by(
            extract('year', Dispatch.created_at),
            extract('month', Dispatch.created_at)
        ).order_by(
            extract('year', Dispatch.created_at).desc(),
            extract('month', Dispatch.created_at).desc()
        ).limit(12).all()

        # Estadísticas por destino
        destination_stats = db.session.query(
            Dispatch.destination_country,
            db.func.count(Dispatch.id),
            db.func.sum(Dispatch.quantity_mt)
        ).filter(Dispatch.id.in_([d.id for d in base_query.all()])).group_by(
            Dispatch.destination_country
        ).order_by(db.func.sum(Dispatch.quantity_mt).desc()).limit(10).all()

        return jsonify({
            'total_dispatches': total_dispatches,
            'status_distribution': status_counts,
            'monthly_stats': [
                {
                    'year': int(stat.year),
                    'month': int(stat.month),
                    'count': stat.count,
                    'total_quantity_mt': float(stat.total_quantity or 0)
                } for stat in monthly_stats
            ],
            'top_destinations': [
                {
                    'country': stat[0],
                    'count': stat[1],
                    'total_quantity_mt': float(stat[2] or 0)
                } for stat in destination_stats
            ]
        })

    except Exception as e:
        logger.error(f"Error getting dispatch stats: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
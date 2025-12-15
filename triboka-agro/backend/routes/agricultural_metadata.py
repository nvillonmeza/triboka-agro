"""
API Endpoints para Sistema de Metadatos Agrícolas Avanzados
Permite construcción progresiva de información de trazabilidad
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
import json
from models_simple import db, ProducerLot, User, Company
from models.agricultural_metadata import (
    AgriculturalMetadata, MetadataUpdateLog, ThirdPartyVerification,
    CultivationMethod, DryingMethod, FermentationType, CertificationStatus
)

agricultural_metadata_bp = Blueprint('agricultural_metadata', __name__)

def require_auth():
    """Verificar que el usuario esté autenticado"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    return None

def get_current_user():
    """Obtener usuario actual de la sesión"""
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

def log_metadata_update(metadata_id, field_name, old_value, new_value, user_id, reason=None):
    """Registrar actualización de metadatos para auditoría"""
    log = MetadataUpdateLog(
        metadata_id=metadata_id,
        field_name=field_name,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        updated_by=user_id,
        update_reason=reason
    )
    db.session.add(log)

@agricultural_metadata_bp.route('/api/agricultural-metadata/<int:lot_id>', methods=['GET'])
def get_agricultural_metadata(lot_id):
    """Obtener metadatos agrícolas de un lote"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        # Verificar que el lote existe
        lot = ProducerLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Lote no encontrado'}), 404
        
        # Obtener metadatos
        metadata = AgriculturalMetadata.query.filter_by(lot_id=lot_id).first()
        
        if not metadata:
            # Crear metadatos vacíos si no existen
            metadata = AgriculturalMetadata(lot_id=lot_id)
            db.session.add(metadata)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'metadata': metadata.to_dict(),
            'lot_info': lot.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agricultural_metadata_bp.route('/api/agricultural-metadata/<int:lot_id>/harvest', methods=['POST'])
def update_harvest_info(lot_id):
    """Actualizar información de cosecha"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Verificar que el lote existe y pertenece al productor
        lot = ProducerLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Lote no encontrado'}), 404
        
        if user.company.company_type != 'producer' or lot.producer_company_id != user.company_id:
            return jsonify({'error': 'No tienes permisos para editar este lote'}), 403
        
        # Obtener o crear metadatos
        metadata = AgriculturalMetadata.query.filter_by(lot_id=lot_id).first()
        if not metadata:
            metadata = AgriculturalMetadata(lot_id=lot_id)
            db.session.add(metadata)
        
        # Actualizar campos de cosecha
        update_fields = {
            'harvest_date': 'harvest_date',
            'harvest_season': 'harvest_season',
            'harvest_method': 'harvest_method',
            'days_from_flowering': 'days_from_flowering'
        }
        
        updates_made = []
        for api_field, db_field in update_fields.items():
            if api_field in data:
                old_value = getattr(metadata, db_field)
                new_value = data[api_field]
                
                if api_field == 'harvest_date' and new_value:
                    new_value = datetime.fromisoformat(new_value.replace('Z', '+00:00'))
                
                if old_value != new_value:
                    setattr(metadata, db_field, new_value)
                    log_metadata_update(metadata.id, db_field, old_value, new_value, user.id, 
                                      f"Actualización de información de cosecha")
                    updates_made.append(api_field)
        
        # Actualizar condiciones climáticas (JSON)
        if 'weather_conditions' in data:
            old_weather = metadata.get_weather_conditions()
            metadata.set_weather_conditions(data['weather_conditions'])
            if old_weather != data['weather_conditions']:
                log_metadata_update(metadata.id, 'weather_conditions', 
                                  json.dumps(old_weather), json.dumps(data['weather_conditions']), 
                                  user.id, "Actualización de condiciones climáticas")
                updates_made.append('weather_conditions')
        
        metadata.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Información de cosecha actualizada. Campos: {", ".join(updates_made)}',
            'metadata': metadata.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@agricultural_metadata_bp.route('/api/agricultural-metadata/<int:lot_id>/cultivation', methods=['POST'])
def update_cultivation_info(lot_id):
    """Actualizar información de cultivo"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Verificar permisos
        lot = ProducerLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Lote no encontrado'}), 404
        
        if user.company.company_type != 'producer' or lot.producer_company_id != user.company_id:
            return jsonify({'error': 'No tienes permisos para editar este lote'}), 403
        
        # Obtener metadatos
        metadata = AgriculturalMetadata.query.filter_by(lot_id=lot_id).first()
        if not metadata:
            metadata = AgriculturalMetadata(lot_id=lot_id)
            db.session.add(metadata)
        
        # Actualizar campos de cultivo
        update_fields = {
            'cultivation_method': 'cultivation_method',
            'seed_variety': 'seed_variety',
            'irrigation_method': 'irrigation_method',
            'planting_date': 'planting_date'
        }
        
        updates_made = []
        for api_field, db_field in update_fields.items():
            if api_field in data:
                old_value = getattr(metadata, db_field)
                new_value = data[api_field]
                
                if api_field == 'planting_date' and new_value:
                    new_value = datetime.fromisoformat(new_value.replace('Z', '+00:00'))
                
                if old_value != new_value:
                    setattr(metadata, db_field, new_value)
                    log_metadata_update(metadata.id, db_field, old_value, new_value, user.id)
                    updates_made.append(api_field)
        
        # Actualizar técnicas de cultivo (JSON array)
        if 'cultivation_techniques' in data:
            old_techniques = metadata.get_cultivation_techniques()
            metadata.set_cultivation_techniques(data['cultivation_techniques'])
            if old_techniques != data['cultivation_techniques']:
                log_metadata_update(metadata.id, 'cultivation_techniques', 
                                  json.dumps(old_techniques), json.dumps(data['cultivation_techniques']), 
                                  user.id)
                updates_made.append('cultivation_techniques')
        
        metadata.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Información de cultivo actualizada. Campos: {", ".join(updates_made)}',
            'metadata': metadata.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@agricultural_metadata_bp.route('/api/agricultural-metadata/<int:lot_id>/processing', methods=['POST'])
def update_processing_info(lot_id):
    """Actualizar información de procesamiento (fermentación y secado)"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Verificar permisos
        lot = ProducerLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Lote no encontrado'}), 404
        
        if user.company.company_type != 'producer' or lot.producer_company_id != user.company_id:
            return jsonify({'error': 'No tienes permisos para editar este lote'}), 403
        
        # Obtener metadatos
        metadata = AgriculturalMetadata.query.filter_by(lot_id=lot_id).first()
        if not metadata:
            metadata = AgriculturalMetadata(lot_id=lot_id)
            db.session.add(metadata)
        
        updates_made = []
        
        # Actualizar información de fermentación
        fermentation_fields = {
            'fermentation_type': 'fermentation_type',
            'fermentation_duration_hours': 'fermentation_duration_hours',
            'fermentation_temperature_avg': 'fermentation_temperature_avg',
            'fermentation_humidity_avg': 'fermentation_humidity_avg',
            'fermentation_notes': 'fermentation_notes'
        }
        
        for api_field, db_field in fermentation_fields.items():
            if api_field in data:
                old_value = getattr(metadata, db_field)
                new_value = data[api_field]
                
                if old_value != new_value:
                    setattr(metadata, db_field, new_value)
                    log_metadata_update(metadata.id, db_field, old_value, new_value, user.id,
                                      "Actualización de procesamiento")
                    updates_made.append(api_field)
        
        # Actualizar información de secado
        drying_fields = {
            'drying_method': 'drying_method',
            'drying_duration_days': 'drying_duration_days',
            'drying_temperature_avg': 'drying_temperature_avg',
            'initial_moisture_percentage': 'initial_moisture_percentage',
            'final_moisture_percentage': 'final_moisture_percentage',
            'drying_notes': 'drying_notes'
        }
        
        for api_field, db_field in drying_fields.items():
            if api_field in data:
                old_value = getattr(metadata, db_field)
                new_value = data[api_field]
                
                if old_value != new_value:
                    setattr(metadata, db_field, new_value)
                    log_metadata_update(metadata.id, db_field, old_value, new_value, user.id,
                                      "Actualización de procesamiento")
                    updates_made.append(api_field)
        
        metadata.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Información de procesamiento actualizada. Campos: {", ".join(updates_made)}',
            'metadata': metadata.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@agricultural_metadata_bp.route('/api/agricultural-metadata/<int:lot_id>/certifications', methods=['POST'])
def update_certifications(lot_id):
    """Actualizar certificaciones del lote"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Verificar permisos
        lot = ProducerLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Lote no encontrado'}), 404
        
        if user.company.company_type != 'producer' or lot.producer_company_id != user.company_id:
            return jsonify({'error': 'No tienes permisos para editar este lote'}), 403
        
        # Obtener metadatos
        metadata = AgriculturalMetadata.query.filter_by(lot_id=lot_id).first()
        if not metadata:
            metadata = AgriculturalMetadata(lot_id=lot_id)
            db.session.add(metadata)
        
        updates_made = []
        
        # Actualizar certificaciones específicas
        certification_types = ['organic', 'fair_trade', 'rainforest_alliance', 'utz']
        
        for cert_type in certification_types:
            if cert_type in data:
                old_cert = metadata.get_certifications().get(cert_type, {})
                metadata.add_certification(cert_type, data[cert_type])
                log_metadata_update(metadata.id, f'{cert_type}_certification', 
                                  json.dumps(old_cert), json.dumps(data[cert_type]), user.id,
                                  f"Actualización de certificación {cert_type}")
                updates_made.append(cert_type)
        
        # Certificaciones custom
        if 'custom_certifications' in data:
            old_custom = metadata.get_custom_certifications()
            for cert_name, cert_data in data['custom_certifications'].items():
                metadata.add_certification(cert_name, cert_data)
                updates_made.append(f'custom_{cert_name}')
        
        metadata.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Certificaciones actualizadas: {", ".join(updates_made)}',
            'metadata': metadata.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@agricultural_metadata_bp.route('/api/agricultural-metadata/<int:lot_id>/sustainability', methods=['POST'])
def update_sustainability_metrics(lot_id):
    """Actualizar métricas de sostenibilidad"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Verificar permisos
        lot = ProducerLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Lote no encontrado'}), 404
        
        if user.company.company_type != 'producer' or lot.producer_company_id != user.company_id:
            return jsonify({'error': 'No tienes permisos para editar este lote'}), 403
        
        # Obtener metadatos
        metadata = AgriculturalMetadata.query.filter_by(lot_id=lot_id).first()
        if not metadata:
            metadata = AgriculturalMetadata(lot_id=lot_id)
            db.session.add(metadata)
        
        # Actualizar métricas de sostenibilidad
        sustainability_fields = {
            'water_usage_liters_per_kg': 'water_usage_liters_per_kg',
            'carbon_footprint_kg_co2': 'carbon_footprint_kg_co2',
            'biodiversity_score': 'biodiversity_score',
            'soil_health_score': 'soil_health_score'
        }
        
        updates_made = []
        for api_field, db_field in sustainability_fields.items():
            if api_field in data:
                old_value = getattr(metadata, db_field)
                new_value = data[api_field]
                
                if old_value != new_value:
                    setattr(metadata, db_field, new_value)
                    log_metadata_update(metadata.id, db_field, old_value, new_value, user.id,
                                      "Actualización de métricas de sostenibilidad")
                    updates_made.append(api_field)
        
        # Actualizar prácticas de sostenibilidad (JSON)
        if 'sustainability_practices' in data:
            old_practices = metadata.get_sustainability_practices()
            metadata.set_sustainability_practices(data['sustainability_practices'])
            if old_practices != data['sustainability_practices']:
                log_metadata_update(metadata.id, 'sustainability_practices', 
                                  json.dumps(old_practices), json.dumps(data['sustainability_practices']), 
                                  user.id, "Actualización de prácticas de sostenibilidad")
                updates_made.append('sustainability_practices')
        
        metadata.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Métricas de sostenibilidad actualizadas: {", ".join(updates_made)}',
            'metadata': metadata.to_dict(),
            'sustainability_score': metadata.calculate_sustainability_score()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@agricultural_metadata_bp.route('/api/agricultural-metadata/<int:lot_id>/quality', methods=['POST'])
def update_quality_analysis(lot_id):
    """Actualizar análisis de calidad"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Verificar permisos (productores y exportadores pueden actualizar calidad)
        lot = ProducerLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Lote no encontrado'}), 404
        
        if user.company.company_type not in ['producer', 'exporter']:
            return jsonify({'error': 'No tienes permisos para actualizar calidad'}), 403
        
        if (user.company.company_type == 'producer' and lot.producer_company_id != user.company_id) or \
           (user.company.company_type == 'exporter' and lot.purchased_by_company_id != user.company_id):
            return jsonify({'error': 'No tienes permisos para editar este lote'}), 403
        
        # Obtener metadatos
        metadata = AgriculturalMetadata.query.filter_by(lot_id=lot_id).first()
        if not metadata:
            metadata = AgriculturalMetadata(lot_id=lot_id)
            db.session.add(metadata)
        
        # Actualizar campos de calidad
        quality_fields = {
            'defect_percentage': 'defect_percentage',
            'protein_content_percentage': 'protein_content_percentage',
            'fat_content_percentage': 'fat_content_percentage',
            'ph_level': 'ph_level'
        }
        
        updates_made = []
        for api_field, db_field in quality_fields.items():
            if api_field in data:
                old_value = getattr(metadata, db_field)
                new_value = data[api_field]
                
                if old_value != new_value:
                    setattr(metadata, db_field, new_value)
                    log_metadata_update(metadata.id, db_field, old_value, new_value, user.id,
                                      "Actualización de análisis de calidad")
                    updates_made.append(api_field)
        
        # Actualizar análisis de calidad (JSON)
        if 'quality_analysis' in data:
            old_analysis = metadata.get_quality_analysis()
            metadata.set_quality_analysis(data['quality_analysis'])
            if old_analysis != data['quality_analysis']:
                log_metadata_update(metadata.id, 'quality_analysis', 
                                  json.dumps(old_analysis), json.dumps(data['quality_analysis']), 
                                  user.id, "Actualización de análisis de calidad")
                updates_made.append('quality_analysis')
        
        # Actualizar perfil de sabor (JSON)
        if 'flavor_profile' in data:
            old_flavor = metadata.get_flavor_profile()
            metadata.set_flavor_profile(data['flavor_profile'])
            if old_flavor != data['flavor_profile']:
                log_metadata_update(metadata.id, 'flavor_profile', 
                                  json.dumps(old_flavor), json.dumps(data['flavor_profile']), 
                                  user.id, "Actualización de perfil de sabor")
                updates_made.append('flavor_profile')
        
        metadata.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Análisis de calidad actualizado: {", ".join(updates_made)}',
            'metadata': metadata.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@agricultural_metadata_bp.route('/api/agricultural-metadata/<int:lot_id>/verification', methods=['POST'])
def add_third_party_verification(lot_id):
    """Agregar verificación de terceros"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Verificar que el lote existe
        lot = ProducerLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Lote no encontrado'}), 404
        
        # Obtener metadatos
        metadata = AgriculturalMetadata.query.filter_by(lot_id=lot_id).first()
        if not metadata:
            metadata = AgriculturalMetadata(lot_id=lot_id)
            db.session.add(metadata)
            db.session.flush()  # Para obtener el ID
        
        # Crear verificación
        verification = ThirdPartyVerification(
            metadata_id=metadata.id,
            verifier_name=data.get('verifier_name'),
            verifier_organization=data.get('verifier_organization'),
            verifier_license=data.get('verifier_license'),
            verification_type=data.get('verification_type'),
            fields_verified=json.dumps(data.get('fields_verified', [])),
            verification_result=data.get('verification_result'),
            confidence_score=data.get('confidence_score'),
            verification_date=datetime.fromisoformat(data.get('verification_date').replace('Z', '+00:00')) if data.get('verification_date') else datetime.utcnow(),
            report_url=data.get('report_url'),
            certificate_url=data.get('certificate_url'),
            notes=data.get('notes'),
            cost_usd=data.get('cost_usd')
        )
        
        db.session.add(verification)
        
        # Actualizar también en metadatos (para búsquedas rápidas)
        verification_data = {
            'verifier': data.get('verifier_name'),
            'organization': data.get('verifier_organization'),
            'type': data.get('verification_type'),
            'result': data.get('verification_result'),
            'date': verification.verification_date.isoformat(),
            'confidence': data.get('confidence_score')
        }
        metadata.add_third_party_verification(verification_data)
        
        # Si la verificación es exitosa, actualizar estado
        if data.get('verification_result') == 'passed':
            metadata.verification_status = 'verified'
        
        metadata.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Verificación de terceros agregada exitosamente',
            'verification_id': verification.id,
            'metadata': metadata.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@agricultural_metadata_bp.route('/api/agricultural-metadata/<int:lot_id>/photos', methods=['POST'])
def add_photographic_evidence(lot_id):
    """Agregar evidencia fotográfica"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Verificar permisos
        lot = ProducerLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Lote no encontrado'}), 404
        
        # Obtener metadatos
        metadata = AgriculturalMetadata.query.filter_by(lot_id=lot_id).first()
        if not metadata:
            metadata = AgriculturalMetadata(lot_id=lot_id)
            db.session.add(metadata)
        
        # Agregar foto
        photo_data = {
            'url': data.get('url'),
            'caption': data.get('caption'),
            'stage': data.get('stage'),  # 'planting', 'harvest', 'fermentation', 'drying', 'storage'
            'uploaded_by': user.name,
            'gps_coordinates': data.get('gps_coordinates'),
            'date_taken': data.get('date_taken', datetime.utcnow().isoformat())
        }
        
        metadata.add_photographic_evidence(photo_data)
        metadata.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Evidencia fotográfica agregada exitosamente',
            'photo_count': len(metadata.get_photographic_evidence()),
            'metadata': metadata.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@agricultural_metadata_bp.route('/api/agricultural-metadata/<int:lot_id>/nft-metadata', methods=['GET'])
def get_nft_metadata(lot_id):
    """Obtener metadatos formateados para NFT"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        # Verificar que el lote existe
        lot = ProducerLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Lote no encontrado'}), 404
        
        # Obtener metadatos
        metadata = AgriculturalMetadata.query.filter_by(lot_id=lot_id).first()
        if not metadata:
            return jsonify({'error': 'Metadatos no encontrados'}), 404
        
        # Generar metadatos NFT
        nft_metadata = metadata.to_nft_metadata()
        
        return jsonify({
            'success': True,
            'nft_metadata': nft_metadata,
            'is_complete': metadata.is_metadata_complete(),
            'missing_fields': metadata.get_missing_fields(),
            'sustainability_score': metadata.calculate_sustainability_score()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agricultural_metadata_bp.route('/api/agricultural-metadata/<int:lot_id>/lock', methods=['POST'])
def lock_metadata(lot_id):
    """Bloquear metadatos para mint del NFT"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        user = get_current_user()
        
        # Verificar permisos
        lot = ProducerLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Lote no encontrado'}), 404
        
        if user.company.company_type != 'producer' or lot.producer_company_id != user.company_id:
            return jsonify({'error': 'No tienes permisos para bloquear metadatos'}), 403
        
        # Obtener metadatos
        metadata = AgriculturalMetadata.query.filter_by(lot_id=lot_id).first()
        if not metadata:
            return jsonify({'error': 'Metadatos no encontrados'}), 404
        
        # Verificar que están completos
        if not metadata.is_metadata_complete():
            return jsonify({
                'error': 'Metadatos incompletos',
                'missing_fields': metadata.get_missing_fields()
            }), 400
        
        # Bloquear metadatos
        metadata.lock_metadata()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Metadatos bloqueados exitosamente',
            'locked_at': metadata.metadata_locked_at.isoformat(),
            'metadata': metadata.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@agricultural_metadata_bp.route('/api/agricultural-metadata/<int:lot_id>/completeness', methods=['GET'])
def check_metadata_completeness(lot_id):
    """Verificar completitud de metadatos"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        # Obtener metadatos
        metadata = AgriculturalMetadata.query.filter_by(lot_id=lot_id).first()
        if not metadata:
            return jsonify({
                'is_complete': False,
                'completion_percentage': 0,
                'missing_fields': [
                    'Fecha de cosecha', 'Método de cultivo', 'Tipo de fermentación',
                    'Duración de fermentación', 'Método de secado', 
                    'Duración de secado', 'Porcentaje de humedad final'
                ]
            })
        
        missing_fields = metadata.get_missing_fields()
        total_required_fields = 7  # Campos requeridos mínimos
        completed_fields = total_required_fields - len(missing_fields)
        completion_percentage = (completed_fields / total_required_fields) * 100
        
        return jsonify({
            'is_complete': metadata.is_metadata_complete(),
            'completion_percentage': round(completion_percentage, 2),
            'missing_fields': missing_fields,
            'completed_fields': completed_fields,
            'total_required_fields': total_required_fields,
            'sustainability_score': metadata.calculate_sustainability_score(),
            'verification_status': metadata.verification_status,
            'certifications_count': len([c for c in metadata.get_certifications().values() if c]),
            'photos_count': len(metadata.get_photographic_evidence()),
            'verifications_count': len(metadata.get_third_party_verifications())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agricultural_metadata_bp.route('/api/agricultural-metadata/<int:lot_id>/audit-log', methods=['GET'])
def get_metadata_audit_log(lot_id):
    """Obtener log de auditoría de metadatos"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        # Obtener metadatos
        metadata = AgriculturalMetadata.query.filter_by(lot_id=lot_id).first()
        if not metadata:
            return jsonify({'error': 'Metadatos no encontrados'}), 404
        
        # Obtener logs de actualización
        logs = MetadataUpdateLog.query.filter_by(metadata_id=metadata.id)\
                                      .order_by(MetadataUpdateLog.created_at.desc())\
                                      .all()
        
        return jsonify({
            'success': True,
            'audit_log': [log.to_dict() for log in logs],
            'total_updates': len(logs)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rutas adicionales para obtener enums y ayuda
@agricultural_metadata_bp.route('/api/agricultural-metadata/enums', methods=['GET'])
def get_metadata_enums():
    """Obtener enumeraciones disponibles para metadatos"""
    return jsonify({
        'cultivation_methods': [method.value for method in CultivationMethod],
        'drying_methods': [method.value for method in DryingMethod],
        'fermentation_types': [ftype.value for ftype in FermentationType],
        'certification_statuses': [status.value for status in CertificationStatus],
        'harvest_methods': ['manual', 'mechanical', 'selective'],
        'irrigation_methods': ['drip', 'sprinkler', 'flood', 'rain-fed'],
        'verification_types': ['field_inspection', 'lab_test', 'document_review'],
        'verification_results': ['passed', 'failed', 'partial'],
        'photo_stages': ['planting', 'growth', 'harvest', 'fermentation', 'drying', 'storage', 'transport']
    })
"""
Sistema de Metadatos Agrícolas Avanzados para Trazabilidad NFT
Información detallada que se va construyendo progresivamente durante la vida del lote
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class CultivationMethod(Enum):
    ORGANIC = "organic"
    CONVENTIONAL = "conventional"
    BIODYNAMIC = "biodynamic"
    REGENERATIVE = "regenerative"
    PERMACULTURE = "permaculture"

class DryingMethod(Enum):
    SUN_DRIED = "sun_dried"
    INDUSTRIAL_DRYER = "industrial_dryer"
    MIXED = "mixed"
    NATURAL_SHADE = "natural_shade"
    GREENHOUSE = "greenhouse"

class FermentationType(Enum):
    TRADITIONAL = "traditional"
    CONTROLLED = "controlled"
    NO_FERMENTATION = "no_fermentation"
    EXTENDED = "extended"
    RAPID = "rapid"

class CertificationStatus(Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    EXPIRED = "expired"
    REJECTED = "rejected"

class AgriculturalMetadata(db.Model):
    """
    Metadatos agrícolas detallados que se van construyendo progresivamente
    Esta información se agrega al NFT del lote como metadata inmutable
    """
    __tablename__ = 'agricultural_metadata'
    
    id = Column(Integer, primary_key=True)
    lot_id = Column(Integer, ForeignKey('producer_lots.id'), nullable=False, unique=True)
    
    # === INFORMACIÓN DE COSECHA ===
    harvest_date = Column(DateTime)
    harvest_season = Column(String(50))  # "main", "secondary", "off-season"
    harvest_method = Column(String(50))  # "manual", "mechanical", "selective"
    days_from_flowering = Column(Integer)  # Días desde floración hasta cosecha
    weather_conditions = Column(Text)  # JSON con condiciones climáticas durante cosecha
    
    # === MÉTODOS DE CULTIVO ===
    cultivation_method = Column(String(50))  # organic, conventional, etc.
    cultivation_techniques = Column(Text)  # JSON array con técnicas específicas
    seed_variety = Column(String(100))  # Variedad específica de la semilla
    planting_date = Column(DateTime)
    irrigation_method = Column(String(50))  # "drip", "sprinkler", "flood", "rain-fed"
    
    # === SOSTENIBILIDAD Y CERTIFICACIONES ===
    sustainability_practices = Column(Text)  # JSON con prácticas sostenibles
    water_usage_liters_per_kg = Column(Float)  # Uso de agua por kg producido
    carbon_footprint_kg_co2 = Column(Float)  # Huella de carbono
    biodiversity_score = Column(Float)  # Puntuación de biodiversidad (0-100)
    soil_health_score = Column(Float)  # Puntuación de salud del suelo (0-100)
    
    # === CERTIFICACIONES ORGÁNICAS Y DE CALIDAD ===
    organic_certification = Column(Text)  # JSON con detalles de certificación orgánica
    fair_trade_certification = Column(Text)  # JSON con detalles Fair Trade
    rainforest_alliance_certification = Column(Text)  # JSON con detalles Rainforest Alliance
    utz_certification = Column(Text)  # JSON con detalles UTZ
    custom_certifications = Column(Text)  # JSON con otras certificaciones
    
    # === PROCESAMIENTO POST-COSECHA ===
    # Fermentación
    fermentation_type = Column(String(50))
    fermentation_duration_hours = Column(Integer)
    fermentation_temperature_avg = Column(Float)
    fermentation_humidity_avg = Column(Float)
    fermentation_notes = Column(Text)
    
    # Secado
    drying_method = Column(String(50))
    drying_duration_days = Column(Integer)
    drying_temperature_avg = Column(Float)
    initial_moisture_percentage = Column(Float)
    final_moisture_percentage = Column(Float)
    drying_notes = Column(Text)
    
    # === CALIDAD Y ANÁLISIS ===
    quality_analysis = Column(Text)  # JSON con análisis detallado de calidad
    defect_percentage = Column(Float)
    protein_content_percentage = Column(Float)
    fat_content_percentage = Column(Float)
    ph_level = Column(Float)
    flavor_profile = Column(Text)  # JSON con perfil de sabor
    aroma_profile = Column(Text)  # JSON con perfil aromático
    
    # === TRAZABILIDAD DE INSUMOS ===
    fertilizers_used = Column(Text)  # JSON con fertilizantes utilizados
    pesticides_used = Column(Text)  # JSON con pesticidas utilizados
    organic_inputs = Column(Text)  # JSON con insumos orgánicos
    input_suppliers = Column(Text)  # JSON con proveedores de insumos
    
    # === INFORMACIÓN ECONÓMICA ===
    production_cost_per_kg = Column(Float)
    labor_cost_per_kg = Column(Float)
    input_cost_per_kg = Column(Float)
    yield_per_hectare = Column(Float)
    
    # === VERIFICACIÓN Y AUDITORÍA ===
    third_party_verifications = Column(Text)  # JSON con verificaciones de terceros
    audit_reports = Column(Text)  # JSON con reportes de auditoría
    photographic_evidence = Column(Text)  # JSON con URLs de evidencia fotográfica
    gps_verification = Column(Text)  # JSON con verificación GPS de ubicación
    
    # === CADENA DE CUSTODIA ===
    custody_chain = Column(Text)  # JSON con cadena de custodia detallada
    handling_instructions = Column(Text)  # Instrucciones especiales de manejo
    storage_conditions = Column(Text)  # JSON con condiciones de almacenamiento
    transport_conditions = Column(Text)  # JSON con condiciones de transporte
    
    # === METADATA DEL NFT ===
    nft_metadata_hash = Column(String(66))  # Hash IPFS de metadatos completos
    metadata_version = Column(String(10), default="1.0")
    last_updated_by = Column(Integer, ForeignKey('users.id'))
    verification_status = Column(String(20), default="pending")  # pending, verified, disputed
    
    # === TIMESTAMPS ===
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_locked_at = Column(DateTime)  # Cuando se bloquean los metadatos para mint
    
    # === RELATIONSHIPS ===
    lot = relationship("ProducerLot", backref="agricultural_metadata")
    updated_by = relationship("User", backref="metadata_updates")
    
    def __init__(self, **kwargs):
        super(AgriculturalMetadata, self).__init__(**kwargs)
        # Inicializar JSON fields como diccionarios vacíos si no se proporcionan
        json_fields = [
            'weather_conditions', 'cultivation_techniques', 'sustainability_practices',
            'organic_certification', 'fair_trade_certification', 'rainforest_alliance_certification',
            'utz_certification', 'custom_certifications', 'quality_analysis', 'flavor_profile',
            'aroma_profile', 'fertilizers_used', 'pesticides_used', 'organic_inputs',
            'input_suppliers', 'third_party_verifications', 'audit_reports',
            'photographic_evidence', 'gps_verification', 'custody_chain',
            'storage_conditions', 'transport_conditions'
        ]
        
        for field in json_fields:
            if not getattr(self, field):
                setattr(self, field, '{}')
    
    # === HELPER METHODS PARA JSON FIELDS ===
    
    def get_weather_conditions(self):
        return json.loads(self.weather_conditions) if self.weather_conditions else {}
    
    def set_weather_conditions(self, data):
        self.weather_conditions = json.dumps(data)
    
    def get_cultivation_techniques(self):
        return json.loads(self.cultivation_techniques) if self.cultivation_techniques else []
    
    def set_cultivation_techniques(self, data):
        self.cultivation_techniques = json.dumps(data)
    
    def get_sustainability_practices(self):
        return json.loads(self.sustainability_practices) if self.sustainability_practices else {}
    
    def set_sustainability_practices(self, data):
        self.sustainability_practices = json.dumps(data)
    
    def get_certifications(self):
        """Obtener todas las certificaciones en un solo objeto"""
        return {
            'organic': json.loads(self.organic_certification) if self.organic_certification else {},
            'fair_trade': json.loads(self.fair_trade_certification) if self.fair_trade_certification else {},
            'rainforest_alliance': json.loads(self.rainforest_alliance_certification) if self.rainforest_alliance_certification else {},
            'utz': json.loads(self.utz_certification) if self.utz_certification else {},
            'custom': json.loads(self.custom_certifications) if self.custom_certifications else {}
        }
    
    def add_certification(self, cert_type, cert_data):
        """Agregar o actualizar una certificación"""
        if cert_type == 'organic':
            self.organic_certification = json.dumps(cert_data)
        elif cert_type == 'fair_trade':
            self.fair_trade_certification = json.dumps(cert_data)
        elif cert_type == 'rainforest_alliance':
            self.rainforest_alliance_certification = json.dumps(cert_data)
        elif cert_type == 'utz':
            self.utz_certification = json.dumps(cert_data)
        else:
            # Certificación custom
            custom_certs = self.get_custom_certifications()
            custom_certs[cert_type] = cert_data
            self.custom_certifications = json.dumps(custom_certs)
    
    def get_custom_certifications(self):
        return json.loads(self.custom_certifications) if self.custom_certifications else {}
    
    def get_quality_analysis(self):
        return json.loads(self.quality_analysis) if self.quality_analysis else {}
    
    def set_quality_analysis(self, data):
        self.quality_analysis = json.dumps(data)
    
    def get_flavor_profile(self):
        return json.loads(self.flavor_profile) if self.flavor_profile else {}
    
    def set_flavor_profile(self, data):
        self.flavor_profile = json.dumps(data)
    
    def get_third_party_verifications(self):
        return json.loads(self.third_party_verifications) if self.third_party_verifications else []
    
    def add_third_party_verification(self, verification_data):
        """Agregar una nueva verificación de terceros"""
        verifications = self.get_third_party_verifications()
        verification_data['timestamp'] = datetime.utcnow().isoformat()
        verifications.append(verification_data)
        self.third_party_verifications = json.dumps(verifications)
    
    def get_photographic_evidence(self):
        return json.loads(self.photographic_evidence) if self.photographic_evidence else []
    
    def add_photographic_evidence(self, photo_data):
        """Agregar evidencia fotográfica"""
        photos = self.get_photographic_evidence()
        photo_data['timestamp'] = datetime.utcnow().isoformat()
        photos.append(photo_data)
        self.photographic_evidence = json.dumps(photos)
    
    def calculate_sustainability_score(self):
        """Calcular puntuación de sostenibilidad general (0-100)"""
        scores = []
        
        # Biodiversidad (25% del score)
        if self.biodiversity_score:
            scores.append(self.biodiversity_score * 0.25)
        
        # Salud del suelo (25% del score)
        if self.soil_health_score:
            scores.append(self.soil_health_score * 0.25)
        
        # Certificaciones (25% del score)
        cert_score = 0
        certifications = self.get_certifications()
        if certifications['organic']:
            cert_score += 30
        if certifications['fair_trade']:
            cert_score += 25
        if certifications['rainforest_alliance']:
            cert_score += 25
        if certifications['utz']:
            cert_score += 20
        scores.append(min(cert_score, 100) * 0.25)
        
        # Eficiencia de agua (25% del score)
        if self.water_usage_liters_per_kg:
            # Asumiendo que menos de 1000L/kg es excelente (100 puntos)
            # y más de 5000L/kg es deficiente (0 puntos)
            water_score = max(0, min(100, 100 - (self.water_usage_liters_per_kg - 1000) / 40))
            scores.append(water_score * 0.25)
        
        return sum(scores) if scores else 0
    
    def lock_metadata(self):
        """Bloquear metadatos para prevenir cambios antes del mint del NFT"""
        self.metadata_locked_at = datetime.utcnow()
        self.verification_status = "locked"
    
    def is_metadata_complete(self):
        """Verificar si los metadatos están completos para el mint del NFT"""
        required_fields = [
            'harvest_date', 'cultivation_method', 'fermentation_type',
            'drying_method', 'final_moisture_percentage'
        ]
        
        for field in required_fields:
            if not getattr(self, field):
                return False
        return True
    
    def get_missing_fields(self):
        """Obtener lista de campos faltantes para completar metadatos"""
        required_fields = {
            'harvest_date': 'Fecha de cosecha',
            'cultivation_method': 'Método de cultivo',
            'fermentation_type': 'Tipo de fermentación',
            'fermentation_duration_hours': 'Duración de fermentación',
            'drying_method': 'Método de secado',
            'drying_duration_days': 'Duración de secado',
            'final_moisture_percentage': 'Porcentaje de humedad final'
        }
        
        missing = []
        for field, label in required_fields.items():
            if not getattr(self, field):
                missing.append(label)
        
        return missing
    
    def to_nft_metadata(self):
        """Generar metadatos completos para el NFT"""
        return {
            'name': f"Lote Agrícola #{self.lot.lot_code}",
            'description': f"Lote de {self.lot.product_type} con trazabilidad completa desde la finca hasta el consumidor",
            'image': self.get_photographic_evidence()[0]['url'] if self.get_photographic_evidence() else None,
            'attributes': [
                # Información básica
                {'trait_type': 'Producto', 'value': self.lot.product_type},
                {'trait_type': 'Peso (kg)', 'value': self.lot.weight_kg},
                {'trait_type': 'Variedad', 'value': self.seed_variety or 'No especificada'},
                
                # Fechas importantes
                {'trait_type': 'Fecha de Cosecha', 'value': self.harvest_date.isoformat() if self.harvest_date else None},
                {'trait_type': 'Fecha de Siembra', 'value': self.planting_date.isoformat() if self.planting_date else None},
                
                # Métodos de cultivo
                {'trait_type': 'Método de Cultivo', 'value': self.cultivation_method},
                {'trait_type': 'Método de Riego', 'value': self.irrigation_method or 'No especificado'},
                
                # Procesamiento
                {'trait_type': 'Tipo de Fermentación', 'value': self.fermentation_type},
                {'trait_type': 'Duración Fermentación (horas)', 'value': self.fermentation_duration_hours},
                {'trait_type': 'Método de Secado', 'value': self.drying_method},
                {'trait_type': 'Duración Secado (días)', 'value': self.drying_duration_days},
                {'trait_type': 'Humedad Final (%)', 'value': self.final_moisture_percentage},
                
                # Calidad
                {'trait_type': 'Grado de Calidad', 'value': self.lot.quality_grade},
                {'trait_type': 'Defectos (%)', 'value': self.defect_percentage},
                {'trait_type': 'pH', 'value': self.ph_level},
                
                # Sostenibilidad
                {'trait_type': 'Puntuación Sostenibilidad', 'value': round(self.calculate_sustainability_score(), 2)},
                {'trait_type': 'Huella de Carbono (kg CO2)', 'value': self.carbon_footprint_kg_co2},
                {'trait_type': 'Uso de Agua (L/kg)', 'value': self.water_usage_liters_per_kg},
                {'trait_type': 'Biodiversidad (0-100)', 'value': self.biodiversity_score},
                {'trait_type': 'Salud del Suelo (0-100)', 'value': self.soil_health_score},
                
                # Certificaciones
                {'trait_type': 'Orgánico Certificado', 'value': bool(self.get_certifications()['organic'])},
                {'trait_type': 'Fair Trade', 'value': bool(self.get_certifications()['fair_trade'])},
                {'trait_type': 'Rainforest Alliance', 'value': bool(self.get_certifications()['rainforest_alliance'])},
                
                # Ubicación
                {'trait_type': 'Finca', 'value': self.lot.farm_name},
                {'trait_type': 'Ubicación', 'value': self.lot.location},
                {'trait_type': 'Coordenadas', 'value': self.lot.coordinates},
                
                # Trazabilidad
                {'trait_type': 'Verificaciones de Terceros', 'value': len(self.get_third_party_verifications())},
                {'trait_type': 'Evidencia Fotográfica', 'value': len(self.get_photographic_evidence())},
                {'trait_type': 'Estado de Verificación', 'value': self.verification_status}
            ],
            'harvest_details': {
                'date': self.harvest_date.isoformat() if self.harvest_date else None,
                'method': self.harvest_method,
                'season': self.harvest_season,
                'weather': self.get_weather_conditions()
            },
            'processing_details': {
                'fermentation': {
                    'type': self.fermentation_type,
                    'duration_hours': self.fermentation_duration_hours,
                    'temperature_avg': self.fermentation_temperature_avg,
                    'humidity_avg': self.fermentation_humidity_avg,
                    'notes': self.fermentation_notes
                },
                'drying': {
                    'method': self.drying_method,
                    'duration_days': self.drying_duration_days,
                    'temperature_avg': self.drying_temperature_avg,
                    'initial_moisture': self.initial_moisture_percentage,
                    'final_moisture': self.final_moisture_percentage,
                    'notes': self.drying_notes
                }
            },
            'sustainability': {
                'score': self.calculate_sustainability_score(),
                'practices': self.get_sustainability_practices(),
                'certifications': self.get_certifications(),
                'carbon_footprint': self.carbon_footprint_kg_co2,
                'water_usage': self.water_usage_liters_per_kg,
                'biodiversity_score': self.biodiversity_score,
                'soil_health_score': self.soil_health_score
            },
            'quality': {
                'grade': self.lot.quality_grade,
                'analysis': self.get_quality_analysis(),
                'flavor_profile': self.get_flavor_profile(),
                'defect_percentage': self.defect_percentage,
                'protein_content': self.protein_content_percentage,
                'fat_content': self.fat_content_percentage,
                'ph_level': self.ph_level
            },
            'traceability': {
                'custody_chain': json.loads(self.custody_chain) if self.custody_chain else [],
                'verifications': self.get_third_party_verifications(),
                'photographic_evidence': self.get_photographic_evidence(),
                'gps_verification': json.loads(self.gps_verification) if self.gps_verification else {}
            },
            'metadata_info': {
                'version': self.metadata_version,
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat(),
                'locked_at': self.metadata_locked_at.isoformat() if self.metadata_locked_at else None,
                'verification_status': self.verification_status,
                'completeness': self.is_metadata_complete()
            }
        }
    
    def to_dict(self):
        """Representación completa del objeto como diccionario"""
        return {
            'id': self.id,
            'lot_id': self.lot_id,
            
            # Información de cosecha
            'harvest_date': self.harvest_date.isoformat() if self.harvest_date else None,
            'harvest_season': self.harvest_season,
            'harvest_method': self.harvest_method,
            'days_from_flowering': self.days_from_flowering,
            'weather_conditions': self.get_weather_conditions(),
            
            # Métodos de cultivo
            'cultivation_method': self.cultivation_method,
            'cultivation_techniques': self.get_cultivation_techniques(),
            'seed_variety': self.seed_variety,
            'planting_date': self.planting_date.isoformat() if self.planting_date else None,
            'irrigation_method': self.irrigation_method,
            
            # Sostenibilidad
            'sustainability_practices': self.get_sustainability_practices(),
            'water_usage_liters_per_kg': self.water_usage_liters_per_kg,
            'carbon_footprint_kg_co2': self.carbon_footprint_kg_co2,
            'biodiversity_score': self.biodiversity_score,
            'soil_health_score': self.soil_health_score,
            'sustainability_score': self.calculate_sustainability_score(),
            
            # Certificaciones
            'certifications': self.get_certifications(),
            
            # Procesamiento
            'fermentation': {
                'type': self.fermentation_type,
                'duration_hours': self.fermentation_duration_hours,
                'temperature_avg': self.fermentation_temperature_avg,
                'humidity_avg': self.fermentation_humidity_avg,
                'notes': self.fermentation_notes
            },
            'drying': {
                'method': self.drying_method,
                'duration_days': self.drying_duration_days,
                'temperature_avg': self.drying_temperature_avg,
                'initial_moisture_percentage': self.initial_moisture_percentage,
                'final_moisture_percentage': self.final_moisture_percentage,
                'notes': self.drying_notes
            },
            
            # Calidad
            'quality_analysis': self.get_quality_analysis(),
            'defect_percentage': self.defect_percentage,
            'protein_content_percentage': self.protein_content_percentage,
            'fat_content_percentage': self.fat_content_percentage,
            'ph_level': self.ph_level,
            'flavor_profile': self.get_flavor_profile(),
            
            # Verificación
            'third_party_verifications': self.get_third_party_verifications(),
            'photographic_evidence': self.get_photographic_evidence(),
            'verification_status': self.verification_status,
            'metadata_complete': self.is_metadata_complete(),
            'missing_fields': self.get_missing_fields(),
            
            # Metadata
            'nft_metadata_hash': self.nft_metadata_hash,
            'metadata_version': self.metadata_version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'metadata_locked_at': self.metadata_locked_at.isoformat() if self.metadata_locked_at else None
        }


class MetadataUpdateLog(db.Model):
    """Log de actualizaciones de metadatos para auditoría"""
    __tablename__ = 'metadata_update_logs'
    
    id = Column(Integer, primary_key=True)
    metadata_id = Column(Integer, ForeignKey('agricultural_metadata.id'), nullable=False)
    field_name = Column(String(100), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    update_reason = Column(String(255))
    verification_required = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    verified_by = Column(Integer, ForeignKey('users.id'))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agricultural_metadata = relationship("AgriculturalMetadata", backref="update_logs")
    user = relationship("User", foreign_keys=[updated_by], backref="metadata_updates")
    verifier = relationship("User", foreign_keys=[verified_by], backref="metadata_verifications")
    
    def to_dict(self):
        return {
            'id': self.id,
            'metadata_id': self.metadata_id,
            'field_name': self.field_name,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'updated_by': self.user.name if self.user else None,
            'update_reason': self.update_reason,
            'verification_required': self.verification_required,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'verified_by': self.verifier.name if self.verifier else None,
            'created_at': self.created_at.isoformat()
        }


class ThirdPartyVerification(db.Model):
    """Verificaciones de terceros para metadatos"""
    __tablename__ = 'third_party_verifications'
    
    id = Column(Integer, primary_key=True)
    metadata_id = Column(Integer, ForeignKey('agricultural_metadata.id'), nullable=False)
    verifier_name = Column(String(255), nullable=False)
    verifier_organization = Column(String(255))
    verifier_license = Column(String(100))
    verification_type = Column(String(100), nullable=False)  # 'field_inspection', 'lab_test', 'document_review'
    
    fields_verified = Column(Text)  # JSON array con campos verificados
    verification_result = Column(String(50), nullable=False)  # 'passed', 'failed', 'partial'
    confidence_score = Column(Float)  # 0-100
    
    verification_date = Column(DateTime, nullable=False)
    report_url = Column(String(500))
    certificate_url = Column(String(500))
    
    notes = Column(Text)
    cost_usd = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agricultural_metadata = relationship("AgriculturalMetadata", backref="verifications")
    
    def to_dict(self):
        return {
            'id': self.id,
            'verifier_name': self.verifier_name,
            'verifier_organization': self.verifier_organization,
            'verification_type': self.verification_type,
            'fields_verified': json.loads(self.fields_verified) if self.fields_verified else [],
            'verification_result': self.verification_result,
            'confidence_score': self.confidence_score,
            'verification_date': self.verification_date.isoformat(),
            'report_url': self.report_url,
            'certificate_url': self.certificate_url,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }
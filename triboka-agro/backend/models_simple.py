"""
Modelos para el sistema Triboka
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    keycloak_id = db.Column(db.String(36), unique=True) # UUID from Keycloak
    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(50), default='user')
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with Profile
    profile = db.relationship('UserProfile', uselist=False, backref='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'keycloak_id': self.keycloak_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'name': self.name,
            'role': self.role,
            'company_id': self.company_id,
            'active': self.active,
            'profile': self.profile.to_dict() if self.profile else None
        }

class UserProfile(db.Model):
    """
    Business Profile for Ecosystem Identity.
    Captures critical data for Web3 traceability (Location, Product, Capacity).
    """
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Business Data
    location = db.Column(db.String(255)) # City, Region e.g., "Chone, Manabí"
    product_type = db.Column(db.String(100)) # e.g., "Cacao CCN51", "Cacao Nacional"
    business_type = db.Column(db.String(50)) # e.g., "Producer", "Exporter" (Explicit override of role)
    
    # Extensible Metadata (JSON)
    additional_data = db.Column(db.Text) # JSON for flexible expansion (GPS, Certifications)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'location': self.location,
            'product_type': self.product_type,
            'business_type': self.business_type,
            'additional_data': self.additional_data
        }

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    company_type = db.Column(db.String(50))  # producer, exporter, buyer
    country = db.Column(db.String(100))
    api_key = db.Column(db.String(100), unique=True)  # API key for external integrations
    blockchain_address = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='company')

class ExportContract(db.Model):
    __tablename__ = 'export_contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_code = db.Column(db.String(100), unique=True)
    buyer_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    exporter_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    product_type = db.Column(db.String(100))
    product_grade = db.Column(db.String(50))
    total_volume_mt = db.Column(db.Numeric(10, 2), default=0)
    fixed_volume_mt = db.Column(db.Numeric(10, 2), default=0)
    differential_usd = db.Column(db.Numeric(10, 2), default=0)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    delivery_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='active')
    blockchain_contract_id = db.Column(db.String(100))
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    buyer_company = db.relationship('Company', foreign_keys=[buyer_company_id], backref='bought_contracts')
    exporter_company = db.relationship('Company', foreign_keys=[exporter_company_id], backref='exported_contracts')
    created_by_user = db.relationship('User', backref='created_contracts')

    def to_dict(self):
        """Convertir contrato a diccionario"""
        return {
            'id': self.id,
            'contract_code': self.contract_code,
            'buyer_company_id': self.buyer_company_id,
            'exporter_company_id': self.exporter_company_id,
            'product_type': self.product_type,
            'product_grade': self.product_grade,
            'total_volume_mt': float(self.total_volume_mt) if self.total_volume_mt else 0,
            'fixed_volume_mt': float(self.fixed_volume_mt) if self.fixed_volume_mt else 0,
            'differential_usd': float(self.differential_usd) if self.differential_usd else 0,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'status': self.status,
            'blockchain_contract_id': self.blockchain_contract_id,
            'created_by_user_id': self.created_by_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ContractFixation(db.Model):
    __tablename__ = 'contract_fixations'
    
    id = db.Column(db.Integer, primary_key=True)
    export_contract_id = db.Column(db.Integer, db.ForeignKey('export_contracts.id'))
    fixed_quantity_mt = db.Column(db.Numeric(10, 2))
    spot_price_usd = db.Column(db.Numeric(10, 2))
    total_value_usd = db.Column(db.Numeric(10, 2))
    fixation_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    blockchain_fixation_id = db.Column(db.String(100))
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    export_contract = db.relationship('ExportContract', backref='fixations')
    created_by_user = db.relationship('User', backref='created_fixations')

    def to_dict(self):
        """Convertir fijación a diccionario"""
        return {
            'id': self.id,
            'export_contract_id': self.export_contract_id,
            'fixed_quantity_mt': float(self.fixed_quantity_mt) if self.fixed_quantity_mt else 0,
            'spot_price_usd': float(self.spot_price_usd) if self.spot_price_usd else 0,
            'total_value_usd': float(self.total_value_usd) if self.total_value_usd else 0,
            'fixation_date': self.fixation_date.isoformat() if self.fixation_date else None,
            'notes': self.notes,
            'blockchain_fixation_id': self.blockchain_fixation_id,
            'created_by_user_id': self.created_by_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ProducerLot(db.Model):
    __tablename__ = 'producer_lots'
    
    id = db.Column(db.Integer, primary_key=True)
    lot_code = db.Column(db.String(100), unique=True)
    producer_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    producer_name = db.Column(db.String(255))
    farm_name = db.Column(db.String(255))
    location = db.Column(db.String(255))
    product_type = db.Column(db.String(100))
    weight_kg = db.Column(db.Numeric(10, 2))
    quality_grade = db.Column(db.String(50))
    moisture_content = db.Column(db.Numeric(5, 2))  # Contenido de humedad en porcentaje
    quality_score = db.Column(db.Numeric(5, 2))  # Puntaje de calidad 0-100
    harvest_date = db.Column(db.DateTime)
    purchase_date = db.Column(db.DateTime)
    purchase_price_usd = db.Column(db.Numeric(10, 2))
    certifications = db.Column(db.Text)
    status = db.Column(db.String(50), default='available')
    blockchain_lot_id = db.Column(db.String(100))
    export_contract_id = db.Column(db.Integer, db.ForeignKey('export_contracts.id'))
    purchased_by_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    batch_id = db.Column(db.Integer)
    purchase_tx_hash = db.Column(db.String(100))
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    producer_company = db.relationship('Company', foreign_keys=[producer_company_id], backref='produced_lots')
    purchased_by_company = db.relationship('Company', foreign_keys=[purchased_by_company_id], backref='purchased_lots')
    export_contract = db.relationship('ExportContract', backref='lots')
    created_by_user = db.relationship('User', backref='created_lots')
    
    @property
    def source_lots_list(self):
        """Para compatibilidad con BatchNFT"""
        return [self.id]
    
    @property
    def source_lots_weights(self):
        """Para compatibilidad con BatchNFT"""
        return [float(self.weight_kg)]
    
    @property
    def quality_score(self):
        """Convertir quality_grade a score numérico para compatibilidad"""
        if not self.quality_grade:
            return None
        
        grade_map = {
            'Premium': 95,
            'A': 90,
            'B': 80,
            'C': 70,
            'Standard': 75,
            'High': 85,
            'Medium': 75,
            'Low': 65
        }
        
        return grade_map.get(self.quality_grade, 75)  # Default a 75 si no está mapeado
    
    def to_dict(self):
        """Convertir lote a diccionario para API"""
        return {
            'id': str(self.id),
            'lote_nft_id': self.blockchain_lot_id,
            'nft_id': self.blockchain_lot_id,  # Para compatibilidad
            'productor_id': 'P001',  # Valor fijo según la simulación
            'productor_nombre': self.producer_name or 'Productor desconocido',
            'finca': self.farm_name or 'Finca desconocida',
            'producto': self.product_type or 'Cacao Seco',
            'peso_estimado_kg': float(self.weight_kg) if self.weight_kg else None,
            'tipo_cacao': self.quality_grade or 'Standard',
            'humedad_estimada': float(self.moisture_content) if self.moisture_content else None,
            'empresa_erp_id': self.producer_company.name if self.producer_company else 'AGROCROP',
            'contrato_id': self.export_contract.contract_code if self.export_contract else 'CTR-2025-001',
            'estado': self.status or 'available',
            'fecha_creacion': self.created_at.isoformat() if self.created_at else None,
            'metadata': {
                'moisture_content': float(self.moisture_content) if self.moisture_content else None,
                'quality_score': float(self.quality_score) if self.quality_score else None,
                'certifications_list': self.certifications.split(',') if self.certifications else []
            }
        }

class BatchNFT(db.Model):
    __tablename__ = 'batch_nfts'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_code = db.Column(db.String(100), unique=True)
    source_lot_ids = db.Column(db.Text)  # JSON string
    source_lot_weights = db.Column(db.Text)  # JSON string
    total_weight_kg = db.Column(db.Numeric(10, 2))
    batch_type = db.Column(db.String(50))
    location = db.Column(db.String(255))
    creator_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    current_owner_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    blockchain_batch_id = db.Column(db.String(100))
    status = db.Column(db.String(50), default='created')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    creator_company = db.relationship('Company', foreign_keys=[creator_company_id], backref='created_batches')
    current_owner_company = db.relationship('Company', foreign_keys=[current_owner_company_id], backref='owned_batches')
    
    @property
    def source_lots_list(self):
        """Retorna lista de IDs de lotes fuente"""
        import json
        try:
            return json.loads(self.source_lot_ids) if self.source_lot_ids else []
        except:
            return []
    
    @property
    def source_lots_weights_list(self):
        """Retorna lista de pesos de lotes fuente"""
        import json
        try:
            return json.loads(self.source_lot_weights) if self.source_lot_weights else []
        except:
            return []
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'batch_code': self.batch_code,
            'source_lot_ids': self.source_lots_list,
            'source_lot_weights': self.source_lots_weights_list,
            'total_weight_kg': float(self.total_weight_kg) if self.total_weight_kg else 0,
            'batch_type': self.batch_type,
            'location': self.location,
            'creator_company_id': self.creator_company_id,
            'current_owner_company_id': self.current_owner_company_id,
            'blockchain_batch_id': self.blockchain_batch_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ========================================
# DEAL ROOMS - Admin Broker Mode
# ========================================

class Deal(db.Model):
    __tablename__ = 'deals'
    
    id = db.Column(db.Integer, primary_key=True)
    deal_code = db.Column(db.String(50), unique=True, nullable=False)  # e.g., D-2025-001
    status = db.Column(db.String(20), default='draft')  # draft, active, closed
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    producer_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    exporter_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    terms_public = db.Column(db.Text)  # JSON string for public terms
    terms_private = db.Column(db.Text)  # JSON string for private terms (admin only)
    visibility_rules = db.Column(db.Text)  # JSON string for field visibility rules
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    admin = db.relationship('User', backref='admin_deals')
    producer = db.relationship('Company', foreign_keys=[producer_id], backref='producer_deals')
    exporter = db.relationship('Company', foreign_keys=[exporter_id], backref='exporter_deals')
    
    def to_dict(self, role='admin'):
        """Convert to dict with role-based filtering"""
        base = {
            'id': self.id,
            'deal_code': self.deal_code,
            'status': self.status,
            'admin_id': self.admin_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if role in ['admin', 'producer', 'exporter']:
            base['producer_id'] = self.producer_id
            base['exporter_id'] = self.exporter_id
            
        if role == 'admin':
            base['terms_private'] = self.terms_private
            
        # Public terms visible to all
        base['terms_public'] = self.terms_public
        
        return base

class DealMember(db.Model):
    __tablename__ = 'deal_members'
    
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    party_id = db.Column(db.Integer, nullable=False)  # user or company id
    party_type = db.Column(db.String(20), default='company')  # user or company
    role_in_deal = db.Column(db.String(20), nullable=False)  # producer, exporter, admin
    permissions = db.Column(db.Text)  # JSON string for specific permissions
    invited_at = db.Column(db.DateTime, default=datetime.utcnow)
    joined_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='invited')  # invited, active, inactive
    
    # Relationship
    deal = db.relationship('Deal', backref='members')

class DealNote(db.Model):
    __tablename__ = 'deal_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scope = db.Column(db.String(20), default='PUBLIC')  # PUBLIC, PARTES, SOLO_ADMIN
    content = db.Column(db.Text, nullable=False)
    attachments = db.Column(db.Text)  # JSON string for file attachments
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deal = db.relationship('Deal', backref='notes')
    author = db.relationship('User', backref='deal_notes')

class DealFinancePrivate(db.Model):
    __tablename__ = 'deal_finance_private'
    
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    costo_admin = db.Column(db.Float)  # Cost agreed with producer
    precio_admin = db.Column(db.Float)  # Price agreed with exporter
    margen_pct = db.Column(db.Float)  # Calculated margin percentage
    margen_abs = db.Column(db.Float)  # Calculated absolute margin
    currency = db.Column(db.String(10), default='USD')
    notes = db.Column(db.Text)  # Private notes
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    deal = db.relationship('Deal', backref='finance_private')
    
    def calculate_margin(self):
        """Calculate margin based on cost and price"""
        if self.costo_admin and self.precio_admin and self.costo_admin > 0:
            self.margen_abs = self.precio_admin - self.costo_admin
            self.margen_pct = (self.margen_abs / self.costo_admin) * 100
        else:
            self.margen_abs = 0
            self.margen_pct = 0

class DealTraceLink(db.Model):
    __tablename__ = 'deal_trace_links'
    
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    lote_ids = db.Column(db.Text)  # JSON array of lot IDs
    batch_ids = db.Column(db.Text)  # JSON array of batch IDs
    events = db.Column(db.Text)  # JSON array of trace events
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    deal = db.relationship('Deal', backref='trace_links')
    
    def get_lote_ids(self):
        import json
        return json.loads(self.lote_ids) if self.lote_ids else []
    
    def get_batch_ids(self):
        import json
        return json.loads(self.batch_ids) if self.batch_ids else []
    
    def get_events(self):
        import json
        return json.loads(self.events) if self.events else []

class DealMessage(db.Model):
    __tablename__ = 'deal_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, file, system
    attachments = db.Column(db.Text)  # JSON string for file attachments
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    deal = db.relationship('Deal', backref='messages')
    author = db.relationship('User', backref='deal_messages')
    
    def to_dict(self):
        return {
            'id': self.id,
            'deal_id': self.deal_id,
            'author_id': self.author_id,
            'author_name': self.author.name if self.author else 'Usuario desconocido',
            'content': self.content,
            'message_type': self.message_type,
            'attachments': self.attachments,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# =====================================
# MODELOS PARA IDENTIDADES DIGITALES (DID)
# =====================================

class DigitalIdentity(db.Model):
    """Modelo para Identidades Digitales (DID) - Perfiles verificados de usuarios/empresas"""
    __tablename__ = 'digital_identities'
    
    id = db.Column(db.Integer, primary_key=True)
    did = db.Column(db.String(255), unique=True, nullable=False, index=True)  # DID único (e.g., did:triboka:123)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), index=True)
    
    # Información de verificación KYC
    kyc_status = db.Column(db.String(50), default='pending', index=True)  # pending, verified, rejected
    kyc_verified_at = db.Column(db.DateTime, index=True)
    kyc_verified_by = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    
    # Información blockchain
    blockchain_address = db.Column(db.String(100), unique=True, index=True)  # Dirección de wallet
    public_key = db.Column(db.Text)  # Clave pública para verificación
    encrypted_private_key = db.Column(db.Text)  # Clave privada encriptada (solo para backup)
    
    # Metadatos del perfil
    profile_data = db.Column(db.Text)  # JSON con información adicional (certificaciones, etc.)
    reputation_score = db.Column(db.Numeric(5, 2), default=0.0, index=True)  # Puntaje de reputación 0-100
    
    # Estado y timestamps
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='digital_identity')
    company = db.relationship('Company', foreign_keys=[company_id], backref='digital_identity')
    kyc_verifier = db.relationship('User', foreign_keys=[kyc_verified_by], backref='verified_identities')
    
    def to_dict(self, include_private=False):
        """Serializar identidad digital con opción de incluir datos privados"""
        base_data = {
            'id': self.id,
            'did': self.did,
            'user_id': self.user_id,
            'company_id': self.company_id,
            'kyc_status': self.kyc_status,
            'kyc_verified_at': self.kyc_verified_at.isoformat() if self.kyc_verified_at else None,
            'blockchain_address': self.blockchain_address,
            'reputation_score': float(self.reputation_score) if self.reputation_score else 0.0,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_private and self.profile_data:
            import json
            base_data['profile_data'] = json.loads(self.profile_data)
        
        return base_data
    
    def generate_did(self):
        """Generar DID único basado en el ID de usuario"""
        self.did = f"did:triboka:{self.user_id}"
    
    def update_reputation(self, score_change):
        """Actualizar puntaje de reputación"""
        current_score = float(self.reputation_score) if self.reputation_score else 0.0
        self.reputation_score = max(0, min(100, current_score + score_change))

class DigitalSignature(db.Model):
    """Modelo para firmas digitales de documentos y eventos"""
    __tablename__ = 'digital_signatures'
    
    id = db.Column(db.Integer, primary_key=True)
    signer_did = db.Column(db.String(100), nullable=False, index=True)  # DID del firmante
    signer_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)  # Usuario firmante
    signer_name = db.Column(db.String(255))  # Nombre del firmante (cache)
    
    # Documento o evento firmado
    document_type = db.Column(db.String(50), nullable=False, index=True)  # 'contract', 'event', 'kyc', 'deal'
    document_id = db.Column(db.String(100), nullable=False, index=True)  # ID del documento
    document_hash = db.Column(db.String(128), nullable=False, index=True)  # Hash SHA-256 del documento
    
    # Firma digital
    signature = db.Column(db.Text, nullable=False)  # Firma digital en formato base64
    signature_algorithm = db.Column(db.String(50), default='RSA-SHA256')  # Algoritmo usado
    public_key = db.Column(db.Text)  # Clave pública usada para verificar
    
    # Blockchain
    blockchain_tx_hash = db.Column(db.String(100), index=True)  # Hash de transacción si se registra on-chain
    blockchain_timestamp = db.Column(db.DateTime, index=True)
    
    # Estado
    status = db.Column(db.String(50), default='valid', index=True)  # valid, revoked, expired
    revocation_reason = db.Column(db.Text)
    
    # Timestamps
    signed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    expires_at = db.Column(db.DateTime, index=True)  # Fecha de expiración opcional
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class KYCDocument(db.Model):
    """Modelo para documentos KYC de identidades digitales"""
    __tablename__ = 'kyc_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    did_id = db.Column(db.Integer, db.ForeignKey('digital_identities.id'), nullable=False, index=True)
    
    # Información del documento
    document_type = db.Column(db.String(50), nullable=False, index=True)  # 'passport', 'id_card', 'license', 'certificate'
    document_number = db.Column(db.String(100), nullable=False, index=True)
    issuing_country = db.Column(db.String(100), index=True)
    issuing_authority = db.Column(db.String(255))
    
    # Archivos y hashes
    document_hash = db.Column(db.String(128), nullable=False, index=True)  # Hash del documento original
    verification_hash = db.Column(db.String(128), index=True)  # Hash de verificación adicional
    file_path = db.Column(db.String(500))  # Ruta al archivo almacenado
    
    # Fechas
    issued_at = db.Column(db.Date, index=True)
    expires_at = db.Column(db.Date, index=True)
    
    # Estado de verificación
    verification_status = db.Column(db.String(50), default='pending', index=True)  # pending, verified, rejected, expired
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)  # Usuario que verificó
    verified_at = db.Column(db.DateTime, index=True)
    verification_notes = db.Column(db.Text)
    
    # Blockchain
    blockchain_tx_hash = db.Column(db.String(100), index=True)  # Hash de transacción si se registra on-chain
    blockchain_timestamp = db.Column(db.DateTime, index=True)
    
    # Metadata
    is_primary = db.Column(db.Boolean, default=False, index=True)  # Documento principal para KYC
    tags = db.Column(db.Text)  # JSON array de tags adicionales
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# =====================================
# MODELOS PARA TRAZABILIDAD Y EVENTOS
# =====================================

class TraceEvent(db.Model):
    """Modelo para eventos de trazabilidad (on-chain y off-chain)"""
    __tablename__ = 'trace_events'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False, index=True)  # e.g., 'lot_creation', 'reception', 'drying', 'export'
    entity_type = db.Column(db.String(50), nullable=False, index=True)  # 'lot', 'batch', 'contract', 'deal'
    entity_id = db.Column(db.String(100), nullable=False, index=True)  # ID de la entidad relacionada
    
    # Información del evento
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(255), index=True)  # Ubicación geográfica
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)  # Usuario que realizó la acción
    actor_name = db.Column(db.String(255))  # Nombre del actor (cache para performance)
    
    # Datos técnicos del evento
    event_data = db.Column(db.Text)  # JSON con datos específicos del evento
    measurements = db.Column(db.Text)  # JSON con mediciones (peso, humedad, temperatura, etc.)
    
    # Blockchain
    blockchain_tx_hash = db.Column(db.String(100), index=True)  # Hash de transacción si se registra on-chain
    blockchain_block_number = db.Column(db.Integer, index=True)
    blockchain_timestamp = db.Column(db.DateTime, index=True)
    
    # Firma digital
    digital_signature_id = db.Column(db.Integer, db.ForeignKey('digital_signatures.id'), index=True)
    
    # Estado y metadata
    status = db.Column(db.String(50), default='active', index=True)  # active, revoked, disputed
    is_public = db.Column(db.Boolean, default=True, index=True)  # Si es visible públicamente
    tags = db.Column(db.Text)  # JSON array de tags para filtrado
    
    # Timestamps
    event_timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # Cuando ocurrió el evento
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    actor = db.relationship('User', backref='trace_events')
    digital_signature = db.relationship('DigitalSignature', backref='trace_event')
    # Relación con TraceTimeline (un evento puede ser padre de múltiples timelines)
    timelines = db.relationship('TraceTimeline', backref='parent_event', lazy='dynamic')
    
    def to_dict(self, include_private=False):
        """Serializar evento de trazabilidad"""
        base_data = {
            'id': self.id,
            'event_type': self.event_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'actor_id': self.actor_id,
            'actor_name': self.actor_name,
            'event_timestamp': self.event_timestamp.isoformat() if self.event_timestamp else None,
            'status': self.status,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_private:
            import json
            base_data.update({
                'event_data': json.loads(self.event_data) if self.event_data else None,
                'measurements': json.loads(self.measurements) if self.measurements else None,
                'blockchain_tx_hash': self.blockchain_tx_hash,
                'blockchain_block_number': self.blockchain_block_number,
                'tags': json.loads(self.tags) if self.tags else None
            })
        
        return base_data
    
    def get_event_hash(self):
        """Generar hash del evento para integridad"""
        import hashlib
        import json
        
        # Crear representación canónica del evento
        event_repr = {
            'event_type': self.event_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'title': self.title,
            'description': self.description or '',
            'location': self.location or '',
            'actor_id': self.actor_id,
            'event_timestamp': self.event_timestamp.isoformat() if self.event_timestamp else '',
            'event_data': self.event_data or '{}',
            'measurements': self.measurements or '{}'
        }
        
        # Ordenar claves para consistencia
        canonical_json = json.dumps(event_repr, sort_keys=True)
        return hashlib.sha256(canonical_json.encode()).hexdigest()

class TraceTimeline(db.Model):
    """Modelo para timeline de trazabilidad con jerarquía de eventos"""
    __tablename__ = 'trace_timelines'
    
    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(50), nullable=False, index=True)  # 'lot', 'batch', 'contract', 'deal'
    entity_id = db.Column(db.String(100), nullable=False, index=True)  # ID de la entidad principal
    
    # Jerarquía de eventos
    parent_event_id = db.Column(db.Integer, db.ForeignKey('trace_events.id'), index=True)  # Evento padre
    # Nota: La relación child_events se define en TraceEvent para evitar problemas de lazy loading
    
    # Información del timeline
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='active', index=True)  # active, completed, archived
    
    # Estadísticas del timeline
    total_events = db.Column(db.Integer, default=0, index=True)
    completed_events = db.Column(db.Integer, default=0, index=True)
    blockchain_events = db.Column(db.Integer, default=0, index=True)  # Eventos registrados en blockchain
    
    # Fechas importantes
    started_at = db.Column(db.DateTime, index=True)  # Primer evento
    completed_at = db.Column(db.DateTime, index=True)  # Último evento completado
    estimated_completion = db.Column(db.DateTime, index=True)  # Fecha estimada de finalización
    
    # Metadata
    tags = db.Column(db.Text)  # JSON array de tags para filtrado
    custom_data = db.Column(db.Text)  # JSON con datos específicos del timeline
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ========================================
# ERP MODULES - Dispatch Management
# ========================================

class Dispatch(db.Model):
    """Modelo para gestión de despachos de cacao"""
    __tablename__ = 'dispatches'
    
    id = db.Column(db.Integer, primary_key=True)
    dispatch_code = db.Column(db.String(50), unique=True, nullable=False)  # e.g., DSP-2025-001
    
    # Relaciones con contratos y batches
    contract_id = db.Column(db.Integer, db.ForeignKey('export_contracts.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch_nfts.id'), nullable=False)
    
    # Información del despacho
    quantity_mt = db.Column(db.Numeric(10, 3), nullable=False)  # Cantidad en toneladas métricas
    destination_country = db.Column(db.String(100), nullable=False)
    destination_port = db.Column(db.String(255))
    destination_company = db.Column(db.String(255))
    
    # Información de envío
    shipping_date = db.Column(db.Date, nullable=False)
    estimated_delivery_date = db.Column(db.Date)
    actual_delivery_date = db.Column(db.Date)
    
    # Información logística
    carrier_name = db.Column(db.String(255))  # Nombre de la compañía transportista
    vessel_name = db.Column(db.String(255))  # Nombre del barco/avión
    tracking_number = db.Column(db.String(100))  # Número de seguimiento
    bill_of_lading = db.Column(db.String(100))  # Conocimiento de embarque
    
    # Estado del despacho
    status = db.Column(db.String(50), default='planned')  # planned, in_transit, delivered, cancelled
    
    # Información financiera
    freight_cost_usd = db.Column(db.Numeric(12, 2))  # Costo de flete
    insurance_cost_usd = db.Column(db.Numeric(12, 2))  # Costo de seguro
    other_costs_usd = db.Column(db.Numeric(12, 2))  # Otros costos
    
    # Usuario que creó el despacho
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Documentos adjuntos (JSON array de rutas de archivos)
    documents = db.Column(db.Text)  # JSON string
    
    # Notas adicionales
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    contract = db.relationship('ExportContract', backref='dispatches')
    batch = db.relationship('BatchNFT', backref='dispatches')
    created_by = db.relationship('User', backref='created_dispatches')
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        import json
        return {
            'id': self.id,
            'dispatch_code': self.dispatch_code,
            'contract_id': self.contract_id,
            'batch_id': self.batch_id,
            'quantity_mt': float(self.quantity_mt) if self.quantity_mt else 0,
            'destination_country': self.destination_country,
            'destination_port': self.destination_port,
            'destination_company': self.destination_company,
            'shipping_date': self.shipping_date.isoformat() if self.shipping_date else None,
            'estimated_delivery_date': self.estimated_delivery_date.isoformat() if self.estimated_delivery_date else None,
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'carrier_name': self.carrier_name,
            'vessel_name': self.vessel_name,
            'tracking_number': self.tracking_number,
            'bill_of_lading': self.bill_of_lading,
            'status': self.status,
            'freight_cost_usd': float(self.freight_cost_usd) if self.freight_cost_usd else 0,
            'insurance_cost_usd': float(self.insurance_cost_usd) if self.insurance_cost_usd else 0,
            'other_costs_usd': float(self.other_costs_usd) if self.other_costs_usd else 0,
            'created_by_id': self.created_by_id,
            'documents': json.loads(self.documents) if self.documents else [],
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def total_cost_usd(self):
        """Calcular costo total del despacho"""
        costs = [self.freight_cost_usd, self.insurance_cost_usd, self.other_costs_usd]
        return sum(float(cost) for cost in costs if cost is not None)
    
    def generate_dispatch_code(self):
        """Generar código único para el despacho"""
        from datetime import datetime
        year = datetime.now().year
        # Contar despachos del año actual
        count = Dispatch.query.filter(
            Dispatch.dispatch_code.like(f'DSP-{year}-%')
        ).count()
        self.dispatch_code = f'DSP-{year}-{str(count + 1).zfill(3)}'

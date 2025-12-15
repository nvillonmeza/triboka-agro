"""
Database Models for Triboka BaaS Platform
PostgreSQL models using SQLAlchemy
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

class PlanType(Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class LotStatus(Enum):
    REGISTERED = "registered"
    IN_PROCESS = "in_process"
    QUALITY_CHECKED = "quality_checked"
    READY_FOR_EXPORT = "ready_for_export"
    EXPORTED = "exported"
    DELIVERED = "delivered"

class Company(db.Model):
    """Company/Organization model"""
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    address = Column(Text)
    country = Column(String(100))
    
    # Subscription info
    plan_type = Column(String(50), default='basic')
    plan_start_date = Column(DateTime, default=datetime.utcnow)
    plan_end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Blockchain info
    wallet_address = Column(String(42))  # Ethereum address
    private_key_encrypted = Column(Text)  # Encrypted private key
    
    # API access
    api_key = Column(String(64), unique=True)
    api_calls_count = Column(Integer, default=0)
    api_calls_limit = Column(Integer, default=1000)
    
    # Relationships
    users = relationship("User", back_populates="company")
    lots = relationship("Lot", back_populates="company")
    nfts = relationship("NFTCertificate", back_populates="company")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'email': self.email,
            'plan_type': self.plan_type,
            'is_active': self.is_active,
            'api_calls_count': self.api_calls_count,
            'api_calls_limit': self.api_calls_limit,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class User(db.Model):
    """User model for company administrators"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50), default='admin')  # admin, operator, viewer
    is_active = Column(Boolean, default=True)
    
    # Company relationship
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    company = relationship("Company", back_populates="users")
    
    # Authentication
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_active': self.is_active,
            'company_id': self.company_id,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Lot(db.Model):
    """Cacao lot model for traceability"""
    __tablename__ = 'lots'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    lot_number = Column(String(100), unique=True, nullable=False)
    
    # Basic info
    origin_location = Column(String(255))
    origin_gps_lat = Column(Float)
    origin_gps_lng = Column(Float)
    harvest_date = Column(DateTime)
    
    # Quantity and quality
    quantity_kg = Column(Float, nullable=False)
    quality_grade = Column(String(50))  # Premium, Standard, Commercial
    moisture_percentage = Column(Float)
    cocoa_percentage = Column(Float)
    
    # Status and tracking
    status = Column(String(50), default='registered')
    current_location = Column(String(255))
    
    # Blockchain info
    blockchain_tx_hash = Column(String(66))  # Transaction hash
    blockchain_block_number = Column(Integer)
    smart_contract_id = Column(String(100))
    
    # Company relationship
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    company = relationship("Company", back_populates="lots")
    
    # Relationships
    nft_certificates = relationship("NFTCertificate", back_populates="lot")
    quality_tests = relationship("QualityTest", back_populates="lot")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'lot_number': self.lot_number,
            'origin_location': self.origin_location,
            'origin_gps': {'lat': self.origin_gps_lat, 'lng': self.origin_gps_lng} if self.origin_gps_lat and self.origin_gps_lng else None,
            'harvest_date': self.harvest_date.isoformat() if self.harvest_date else None,
            'quantity_kg': self.quantity_kg,
            'quality_grade': self.quality_grade,
            'status': self.status,
            'blockchain_tx_hash': self.blockchain_tx_hash,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class NFTCertificate(db.Model):
    """NFT Certificate model for lot authenticity"""
    __tablename__ = 'nft_certificates'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    token_id = Column(String(100), unique=True)
    
    # Certificate info
    certificate_type = Column(String(50))  # origin, quality, export, delivery
    title = Column(String(255))
    description = Column(Text)
    image_url = Column(String(500))
    metadata_uri = Column(String(500))
    
    # Blockchain info
    contract_address = Column(String(42))
    token_standard = Column(String(20), default='ERC-721')
    blockchain_tx_hash = Column(String(66))
    block_number = Column(Integer)
    
    # Relationships
    lot_id = Column(Integer, ForeignKey('lots.id'), nullable=False)
    lot = relationship("Lot", back_populates="nft_certificates")
    
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    company = relationship("Company", back_populates="nfts")
    
    # Status
    is_minted = Column(Boolean, default=False)
    mint_date = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'token_id': self.token_id,
            'certificate_type': self.certificate_type,
            'title': self.title,
            'description': self.description,
            'image_url': self.image_url,
            'contract_address': self.contract_address,
            'blockchain_tx_hash': self.blockchain_tx_hash,
            'is_minted': self.is_minted,
            'mint_date': self.mint_date.isoformat() if self.mint_date else None,
            'lot_id': self.lot_id
        }

class QualityTest(db.Model):
    """Quality test results model"""
    __tablename__ = 'quality_tests'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    # Test info
    test_type = Column(String(100))  # moisture, cocoa_content, fermentation, etc.
    test_value = Column(Float)
    test_unit = Column(String(20))
    test_date = Column(DateTime, default=datetime.utcnow)
    test_location = Column(String(255))
    
    # Lab info
    lab_name = Column(String(255))
    lab_certificate = Column(String(255))
    tester_name = Column(String(255))
    
    # Results
    pass_status = Column(Boolean)
    notes = Column(Text)
    
    # Relationships
    lot_id = Column(Integer, ForeignKey('lots.id'), nullable=False)
    lot = relationship("Lot", back_populates="quality_tests")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'test_type': self.test_type,
            'test_value': self.test_value,
            'test_unit': self.test_unit,
            'test_date': self.test_date.isoformat() if self.test_date else None,
            'pass_status': self.pass_status,
            'notes': self.notes
        }

class Deal(db.Model):
    """Deal model for Admin Broker Mode - agreements between producers and exporters"""
    __tablename__ = 'deals'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))

    # Deal info
    description = Column(Text)
    terms = Column(Text)
    status = Column(String(50), default='draft')  # draft, active, closed

    # Parties
    producer_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    exporter_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    admin_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationships
    producer_company = relationship("Company", foreign_keys=[producer_id])
    exporter_company = relationship("Company", foreign_keys=[exporter_id])
    admin = relationship("User", foreign_keys=[admin_id])

    # Related entities
    members = relationship("DealMember", back_populates="deal", cascade="all, delete-orphan")
    notes = relationship("DealNote", back_populates="deal", cascade="all, delete-orphan")
    messages = relationship("DealMessage", back_populates="deal", cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, role='viewer'):
        """Convert to dictionary with role-based visibility"""
        base_data = {
            'id': self.id,
            'uuid': self.uuid,
            'description': self.description,
            'terms': self.terms if role in ['admin', 'producer', 'exporter'] else None,
            'status': self.status,
            'producer_id': self.producer_id,
            'exporter_id': self.exporter_id,
            'admin_id': self.admin_id,
            'producer_company': self.producer_company.name if self.producer_company else None,
            'exporter_company': self.exporter_company.name if self.exporter_company else None,
            'admin_name': self.admin.name if self.admin else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if role == 'admin':
            base_data['members_count'] = len(self.members)
            base_data['notes_count'] = len(self.notes)
            base_data['messages_count'] = len(self.messages)

        return base_data

class DealMember(db.Model):
    """Members of a deal (companies/users with specific roles)"""
    __tablename__ = 'deal_members'

    id = Column(Integer, primary_key=True)
    deal_id = Column(Integer, ForeignKey('deals.id'), nullable=False)
    party_id = Column(Integer, nullable=False)  # Company or User ID
    party_type = Column(String(20), nullable=False)  # 'company' or 'user'
    role_in_deal = Column(String(50), nullable=False)  # producer, exporter, admin, observer
    permissions = Column(JSON, default=list)  # List of permissions

    # Status
    invited_at = Column(DateTime, default=datetime.utcnow)
    joined_at = Column(DateTime)

    # Relationships
    deal = relationship("Deal", back_populates="members")

    def to_dict(self):
        return {
            'id': self.id,
            'deal_id': self.deal_id,
            'party_id': self.party_id,
            'party_type': self.party_type,
            'role_in_deal': self.role_in_deal,
            'permissions': self.permissions,
            'invited_at': self.invited_at.isoformat() if self.invited_at else None,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }

class DealNote(db.Model):
    """Notes within a deal with scope-based visibility"""
    __tablename__ = 'deal_notes'

    id = Column(Integer, primary_key=True)
    deal_id = Column(Integer, ForeignKey('deals.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Note content
    scope = Column(String(20), nullable=False)  # PUBLIC, PARTES, SOLO_ADMIN
    content = Column(Text, nullable=False)
    attachments = Column(JSON, default=list)  # List of attachment URLs/metadata

    # Relationships
    deal = relationship("Deal", back_populates="notes")
    author = relationship("User")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'deal_id': self.deal_id,
            'author_id': self.author_id,
            'author_name': self.author.name if self.author else 'Usuario desconocido',
            'scope': self.scope,
            'content': self.content,
            'attachments': self.attachments,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DealMessage(db.Model):
    """Messages within a deal conversation"""
    __tablename__ = 'deal_messages'

    id = Column(Integer, primary_key=True)
    deal_id = Column(Integer, ForeignKey('deals.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default='text')  # text, file, system
    attachments = Column(JSON, default=list)  # List of attachment URLs/metadata

    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)

    # Relationships
    deal = relationship("Deal", back_populates="messages")
    author = relationship("User")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DealFinancePrivate(db.Model):
    """Private financial information for deals (admin only)"""
    __tablename__ = 'deal_finance_private'

    id = Column(Integer, primary_key=True)
    deal_id = Column(Integer, ForeignKey('deals.id'), unique=True, nullable=False)

    # Financial data
    costo_admin = Column(Float)  # Admin cost per unit
    precio_admin = Column(Float)  # Admin price per unit
    margen_pct = Column(Float)  # Calculated margin percentage
    margen_abs = Column(Float)  # Calculated absolute margin
    currency = Column(String(3), default='USD')
    notes = Column(Text)

    # Relationships
    deal = relationship("Deal")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def calculate_margin(self):
        """Calculate margins based on cost and price"""
        if self.costo_admin and self.precio_admin and self.precio_admin > 0:
            self.margen_abs = self.precio_admin - self.costo_admin
            self.margen_pct = (self.margen_abs / self.precio_admin) * 100
        else:
            self.margen_abs = None
            self.margen_pct = None

class DealTraceLink(db.Model):
    """Links between deals and traceability data (lots, batches)"""
    __tablename__ = 'deal_trace_links'

    id = Column(Integer, primary_key=True)
    deal_id = Column(Integer, ForeignKey('deals.id'), nullable=False)

    # Linked entities (stored as JSON arrays)
    lote_ids = Column(Text, default='[]')  # JSON array of lot IDs
    batch_ids = Column(Text, default='[]')  # JSON array of batch IDs
    events = Column(Text, default='[]')  # JSON array of traceability events

    created_at = Column(DateTime, default=datetime.utcnow)

    def get_lote_ids(self):
        """Get lote IDs as list"""
        try:
            import json
            return json.loads(self.lote_ids) if self.lote_ids else []
        except:
            return []

    def get_batch_ids(self):
        """Get batch IDs as list"""
        try:
            import json
            return json.loads(self.batch_ids) if self.batch_ids else []
        except:
            return []

    def get_events(self):
        """Get events as list"""
        try:
            import json
            return json.loads(self.events) if self.events else []
        except:
            return []
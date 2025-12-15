"""
Triboka BaaS - Blockchain-as-a-Service Platform
Flask Application Configuration
"""

import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'triboka-baas-secret-key-2025'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://triboka_user:triboka_pass@localhost/triboka_baas'
    
    # Blockchain Configuration
    BLOCKCHAIN_NETWORK = os.environ.get('BLOCKCHAIN_NETWORK') or 'ganache'
    BLOCKCHAIN_RPC_URL = os.environ.get('BLOCKCHAIN_RPC_URL') or 'http://localhost:8545'
    CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS') or None
    
    # API Configuration
    API_RATE_LIMIT = "100 per hour"
    
    # Business Configuration
    SUPPORTED_PLANS = {
        'basic': {
            'name': 'Basic Plan',
            'price': 99,
            'max_lots': 100,
            'max_nfts': 50,
            'features': ['basic_traceability', 'api_access']
        },
        'professional': {
            'name': 'Professional Plan', 
            'price': 299,
            'max_lots': 500,
            'max_nfts': 250,
            'features': ['basic_traceability', 'api_access', 'custom_branding', 'priority_support']
        },
        'enterprise': {
            'name': 'Enterprise Plan',
            'price': 499,
            'max_lots': -1,  # unlimited
            'max_nfts': -1,  # unlimited
            'features': ['all_features', 'dedicated_node', 'custom_integration']
        }
    }
    
    NFT_COMMISSION = 10  # USD per NFT certificate

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'postgresql://triboka_user:triboka_pass@localhost/triboka_baas_dev'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://triboka_user:triboka_pass@localhost/triboka_baas_prod'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
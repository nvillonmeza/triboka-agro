#!/usr/bin/env python3
"""
Tests unitarios para el endpoint /api/analytics/esg
Verifica estructura de datos y tipos básicos para evitar UndefinedError en templates
"""

import unittest
import json
import sys
import os
from datetime import datetime

# Añadir directorio padre al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar la aplicación
from app_web3 import app, db
from models_simple import User, Company

class TestESGAPI(unittest.TestCase):
    """Suite de tests para el endpoint ESG Analytics"""
    
    def setUp(self):
        """Configuración inicial antes de cada test"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Crear tablas en memoria
        db.create_all()
        
        # Crear empresa de prueba
        company = Company(
            name="Test Company",
            company_type="exporter",
            email="test@company.com"
        )
        db.session.add(company)
        db.session.commit()
        
        # Crear usuario de prueba
        from werkzeug.security import generate_password_hash
        user = User(
            name="Test User",
            email="test@test.com",
            password_hash=generate_password_hash("password123"),
            role="admin",
            company_id=company.id
        )
        db.session.add(user)
        db.session.commit()
        
        # Login para obtener token
        login_response = self.app.post('/api/auth/login', 
                                     data=json.dumps({
                                         'email': 'test@test.com',
                                         'password': 'password123'
                                     }),
                                     content_type='application/json')
        
        self.assertEqual(login_response.status_code, 200)
        login_data = json.loads(login_response.data)
        self.token = login_data['access_token']
        
    def tearDown(self):
        """Limpieza después de cada test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_esg_endpoint_authentication_required(self):
        """Test: Endpoint requiere autenticación"""
        response = self.app.get('/api/analytics/esg')
        self.assertEqual(response.status_code, 401)
        
    def test_esg_endpoint_returns_valid_json(self):
        """Test: Endpoint devuelve JSON válido con autenticación"""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.get('/api/analytics/esg', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        # Verificar que es JSON parseable
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
        
    def test_esg_data_structure_required_keys(self):
        """Test: Estructura de datos contiene claves requeridas por template"""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.get('/api/analytics/esg', headers=headers)
        data = json.loads(response.data)
        
        # Verificar claves principales
        required_main_keys = ['overall', 'environmental', 'social', 'governance', 'metrics']
        for key in required_main_keys:
            self.assertIn(key, data, f"Clave principal '{key}' faltante en respuesta ESG")
            self.assertIsInstance(data[key], dict, f"Clave '{key}' debe ser un diccionario")
            
    def test_esg_overall_section(self):
        """Test: Sección 'overall' contiene campos esperados"""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.get('/api/analytics/esg', headers=headers)
        data = json.loads(response.data)
        
        overall = data['overall']
        required_fields = ['esg_score', 'sustainability_rating', 'last_updated', 'improvement_areas', 'strengths']
        
        for field in required_fields:
            self.assertIn(field, overall, f"Campo '{field}' faltante en overall")
            
        # Verificar tipos específicos
        self.assertIsInstance(overall['esg_score'], (int, float))
        self.assertIsInstance(overall['sustainability_rating'], str)
        self.assertIsInstance(overall['improvement_areas'], list)
        self.assertIsInstance(overall['strengths'], list)
        
    def test_esg_governance_certifications(self):
        """Test: governance.certifications existe (causa común de UndefinedError)"""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.get('/api/analytics/esg', headers=headers)
        data = json.loads(response.data)
        
        governance = data['governance']
        self.assertIn('certifications', governance, "governance.certifications faltante")
        
        certifications = governance['certifications']
        required_cert_fields = ['organic_pct', 'fair_trade_pct', 'rainforest_alliance_pct', 'total_certified_lots']
        
        for field in required_cert_fields:
            self.assertIn(field, certifications, f"Campo certifications.{field} faltante")
            self.assertIsInstance(certifications[field], (int, float), f"certifications.{field} debe ser numérico")
            
    def test_esg_governance_transparency_audit_compliance(self):
        """Test: governance.transparency.audit_compliance existe"""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.get('/api/analytics/esg', headers=headers)
        data = json.loads(response.data)
        
        transparency = data['governance']['transparency']
        self.assertIn('audit_compliance', transparency, "governance.transparency.audit_compliance faltante")
        self.assertIsInstance(transparency['audit_compliance'], (int, float))
        
    def test_esg_governance_supply_chain(self):
        """Test: governance.supply_chain existe"""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.get('/api/analytics/esg', headers=headers)
        data = json.loads(response.data)
        
        governance = data['governance']
        self.assertIn('supply_chain', governance, "governance.supply_chain faltante")
        
        supply_chain = governance['supply_chain']
        required_sc_fields = ['traceability_score', 'verified_suppliers', 'ethical_sourcing']
        
        for field in required_sc_fields:
            self.assertIn(field, supply_chain, f"Campo supply_chain.{field} faltante")
            self.assertIsInstance(supply_chain[field], (int, float))
            
    def test_esg_environmental_structure(self):
        """Test: Sección environmental tiene la estructura completa"""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.get('/api/analytics/esg', headers=headers)
        data = json.loads(response.data)
        
        environmental = data['environmental']
        required_sections = ['carbon_footprint', 'water_usage', 'biodiversity', 'waste_management']
        
        for section in required_sections:
            self.assertIn(section, environmental, f"Sección environmental.{section} faltante")
            self.assertIsInstance(environmental[section], dict)
            
    def test_esg_social_structure(self):
        """Test: Sección social tiene la estructura completa"""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.get('/api/analytics/esg', headers=headers)
        data = json.loads(response.data)
        
        social = data['social']
        required_sections = ['fair_trade', 'worker_welfare', 'community_impact', 'gender_equality']
        
        for section in required_sections:
            self.assertIn(section, social, f"Sección social.{section} faltante")
            self.assertIsInstance(social[section], dict)
            
    def test_esg_data_ranges_reasonable(self):
        """Test: Los valores ESG están en rangos razonables"""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.get('/api/analytics/esg', headers=headers)
        data = json.loads(response.data)
        
        # ESG score debe estar entre 0 y 100
        esg_score = data['overall']['esg_score']
        self.assertGreaterEqual(esg_score, 0, "ESG score no puede ser negativo")
        self.assertLessEqual(esg_score, 100, "ESG score no puede exceder 100")
        
        # Percentajes deben estar entre 0 y 100
        governance = data['governance']
        if 'certifications' in governance:
            for cert_type, value in governance['certifications'].items():
                if 'pct' in cert_type:
                    self.assertGreaterEqual(value, 0, f"{cert_type} no puede ser negativo")
                    self.assertLessEqual(value, 100, f"{cert_type} no puede exceder 100%")

if __name__ == '__main__':
    # Ejecutar tests
    print("🧪 Ejecutando tests unitarios para ESG API...")
    unittest.main(verbosity=2)
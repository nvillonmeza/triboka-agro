"""
Suite completa de tests para Triboka Backend - Fase 2
Tests unitarios e integración para validar todos los módulos implementados
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Configuración de Flask para testing
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_web3 import app, db
from models_simple import User, Company, ExportContract, ContractFixation, ProducerLot, BatchNFT, TraceEvent
from routes.traceability import traceability_bp, check_entity_permissions
from routes.erp import erp_bp, ERPConnector
from routes.performance import performance_bp
from routes.analytics import analytics_bp, AnalyticsEngine


@pytest.fixture
def client():
    """Cliente de test para Flask"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Crear datos de prueba
            _create_test_data()
            yield client


@pytest.fixture
def auth_headers(client):
    """Headers de autenticación para tests"""
    # Crear usuario de prueba
    user_data = {
        'email': 'test@example.com',
        'password': 'testpass123',
        'name': 'Test User',
        'role': 'admin'
    }

    # Registrar usuario
    response = client.post('/api/auth/register', json=user_data)
    assert response.status_code == 201

    # Login
    login_data = {
        'email': 'test@example.com',
        'password': 'testpass123'
    }
    response = client.post('/api/auth/login', json=login_data)
    assert response.status_code == 200

    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


def _create_test_data():
    """Crear datos de prueba para tests"""
    # Crear empresa de prueba
    company = Company(
        name='Test Company',
        company_type='exporter',
        email='test@company.com'
    )
    db.session.add(company)

    # Crear usuario de prueba
    user = User(
        email='test@example.com',
        password_hash='hashed_password',
        name='Test User',
        role='admin',
        company_id=1
    )
    db.session.add(user)

    # Crear contrato de prueba
    contract = ExportContract(
        contract_code='TEST-001',
        buyer_company_id=1,
        exporter_company_id=1,
        product_type='cacao',
        total_volume_mt=1.0,
        status='active'
    )
    db.session.add(contract)

    # Crear lote de prueba
    lot = ProducerLot(
        producer_company_id=1,
        lot_code='LOT-001',
        product_type='cacao',
        weight_kg=500,
        quality_grade='A',
        harvest_date=datetime.utcnow().date(),
        location='Test Farm',
        status='available'
    )
    db.session.add(lot)

    db.session.commit()


# =====================================
# TESTS DE TRAZABILIDAD
# =====================================

class TestTraceability:
    """Tests para el módulo de trazabilidad blockchain"""

    def test_create_traceability_event_success(self, client, auth_headers):
        """Test creación exitosa de evento de trazabilidad"""
        event_data = {
            'event_type': 'PRODUCER_INIT',
            'entity_type': 'lot',
            'entity_id': '1',
            'measurements': {
                'weight_kg': 500,
                'location': 'Test Farm',
                'harvest_date': '2025-11-13'
            },
            'notes': 'Test event'
        }

        response = client.post('/api/traceability/events',
                             json=event_data,
                             headers=auth_headers)

        assert response.status_code == 201
        data = response.get_json()
        assert 'event_id' in data
        assert data['event']['event_type'] == 'PRODUCER_INIT'

    def test_create_traceability_event_invalid_type(self, client, auth_headers):
        """Test evento con tipo inválido"""
        event_data = {
            'event_type': 'INVALID_EVENT',
            'entity_type': 'lot',
            'entity_id': '1',
            'measurements': {}
        }

        response = client.post('/api/traceability/events',
                             json=event_data,
                             headers=auth_headers)

        assert response.status_code == 400
        assert 'no válido' in response.get_json()['error']

    def test_get_traceability_events(self, client, auth_headers):
        """Test obtener eventos de trazabilidad"""
        # Primero crear un evento
        event_data = {
            'event_type': 'PRODUCER_INIT',
            'entity_type': 'lot',
            'entity_id': '1',
            'measurements': {'weight_kg': 500}
        }
        client.post('/api/traceability/events', json=event_data, headers=auth_headers)

        # Obtener eventos
        response = client.get('/api/traceability/events', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'events' in data
        assert len(data['events']) > 0

    def test_get_entity_timeline(self, client, auth_headers):
        """Test obtener timeline de entidad"""
        # Crear evento primero
        event_data = {
            'event_type': 'PRODUCER_INIT',
            'entity_type': 'lot',
            'entity_id': '1',
            'measurements': {'weight_kg': 500}
        }
        client.post('/api/traceability/events', json=event_data, headers=auth_headers)

        # Obtener timeline
        response = client.get('/api/traceability/timeline/lot/1', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'timeline' in data
        assert data['entity_type'] == 'lot'
        assert data['entity_id'] == '1'

    def test_validate_traceability_chain(self, client, auth_headers):
        """Test validación de cadena de trazabilidad"""
        # Crear evento primero
        event_data = {
            'event_type': 'PRODUCER_INIT',
            'entity_type': 'lot',
            'entity_id': '1',
            'measurements': {'weight_kg': 500}
        }
        client.post('/api/traceability/events', json=event_data, headers=auth_headers)

        # Validar cadena
        response = client.get('/api/traceability/validate-chain/lot/1', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'is_valid' in data
        assert 'validation_details' in data

    def test_check_entity_permissions_admin(self, client, auth_headers):
        """Test verificación de permisos para admin"""
        from routes.traceability import check_entity_permissions

        # Obtener usuario admin
        user = User.query.filter_by(email='test@example.com').first()

        # Debería tener acceso a cualquier entidad
        assert check_entity_permissions(user, 'lot', '1') == True
        assert check_entity_permissions(user, 'batch', '1') == True


# =====================================
# TESTS DE ERP
# =====================================

class TestERP:
    """Tests para el módulo ERP"""

    def test_get_erp_systems(self, client, auth_headers):
        """Test obtener sistemas ERP soportados"""
        response = client.get('/api/erp/systems', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'systems' in data
        assert 'sap' in data['systems']
        assert 'dynamics' in data['systems']

    @patch('routes.erp.ERPConnector.test_connection')
    def test_create_erp_connection_success(self, mock_test, client, auth_headers):
        """Test creación exitosa de conexión ERP"""
        mock_test.return_value = True

        connection_data = {
            'system_type': 'sap',
            'name': 'SAP Test',
            'base_url': 'https://sap.example.com',
            'username': 'testuser',
            'password': 'testpass'
        }

        response = client.post('/api/erp/connections',
                             json=connection_data,
                             headers=auth_headers)

        assert response.status_code == 201
        data = response.get_json()
        assert 'connection_id' in data
        assert data['status'] == 'connected'

    def test_create_erp_connection_invalid_system(self, client, auth_headers):
        """Test conexión ERP con sistema inválido"""
        connection_data = {
            'system_type': 'invalid_system',
            'name': 'Invalid ERP',
            'base_url': 'https://invalid.com'
        }

        response = client.post('/api/erp/connections',
                             json=connection_data,
                             headers=auth_headers)

        assert response.status_code == 400
        assert 'no soportado' in response.get_json()['error']

    @patch('routes.erp.ERPConnector')
    def test_sync_companies_to_erp(self, mock_connector, client, auth_headers):
        """Test sincronización de compañías con ERP"""
        mock_instance = Mock()
        mock_instance.sync_companies.return_value = {'synced': 1}
        mock_connector.return_value = mock_instance

        sync_data = {
            'erp_system_type': 'sap',
            'erp_base_url': 'https://sap.example.com',
            'company_ids': [1]
        }

        response = client.post('/api/erp/sync/companies',
                             json=sync_data,
                             headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'companies_synced' in data

    def test_test_erp_connection(self, client, auth_headers):
        """Test prueba de conexión ERP"""
        test_data = {
            'system_type': 'sap',
            'base_url': 'https://sap.example.com',
            'username': 'test',
            'password': 'test'
        }

        response = client.post('/api/erp/test-connection',
                             json=test_data,
                             headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'connection_test' in data


# =====================================
# TESTS DE RENDIMIENTO
# =====================================

class TestPerformance:
    """Tests para el módulo de rendimiento"""

    def test_get_system_metrics(self, client, auth_headers):
        """Test obtener métricas del sistema"""
        response = client.get('/api/performance/metrics/system', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'metrics' in data
        assert 'timestamp' in data

    def test_get_endpoint_metrics(self, client, auth_headers):
        """Test obtener métricas de endpoints"""
        response = client.get('/api/performance/metrics/endpoints', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'endpoints' in data
        assert 'total_endpoints' in data

    def test_health_check(self, client):
        """Test health check del sistema"""
        response = client.get('/api/performance/health')

        assert response.status_code in [200, 503]  # 200 si todo ok, 503 si hay problemas
        data = response.get_json()
        assert 'status' in data
        assert 'timestamp' in data

    @patch('routes.performance.redis_manager')
    def test_clear_cache(self, mock_redis, client, auth_headers):
        """Test limpieza de cache"""
        mock_redis.get_connection.return_value.flushdb.return_value = None

        response = client.post('/api/performance/cache/clear', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data

    def test_optimize_query_companies(self, client, auth_headers):
        """Test optimización de consulta de compañías"""
        query_data = {
            'query_type': 'companies'
        }

        response = client.post('/api/performance/optimize/query',
                             json=query_data,
                             headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'query_info' in data
        assert 'execution_time_seconds' in data


# =====================================
# TESTS DE ANALYTICS
# =====================================

class TestAnalytics:
    """Tests para el módulo de analytics"""

    def test_get_supply_chain_metrics(self, client, auth_headers):
        """Test obtener métricas de cadena de suministro"""
        response = client.get('/api/analytics/supply-chain', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'metrics' in data
        assert 'generated_at' in data

    def test_get_financial_analytics(self, client, auth_headers):
        """Test obtener análisis financiero"""
        response = client.get('/api/analytics/financial', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'analytics' in data
        assert 'generated_at' in data

    def test_get_quality_analytics(self, client, auth_headers):
        """Test obtener análisis de calidad"""
        response = client.get('/api/analytics/quality', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'analytics' in data
        assert 'generated_at' in data

    def test_get_realtime_dashboard(self, client, auth_headers):
        """Test obtener dashboard en tiempo real"""
        response = client.get('/api/analytics/dashboard', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'recent_activity' in data
        assert 'current_status' in data
        assert 'timestamp' in data

    def test_get_kpi_dashboard(self, client, auth_headers):
        """Test obtener KPIs del dashboard"""
        response = client.get('/api/analytics/kpis', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'kpis' in data
        assert 'timestamp' in data

    def test_get_system_alerts(self, client, auth_headers):
        """Test obtener alertas del sistema"""
        response = client.get('/api/analytics/alerts', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'alerts' in data
        assert isinstance(data['alerts'], list)


# =====================================
# TESTS DE INTEGRACIÓN
# =====================================

class TestIntegration:
    """Tests de integración entre módulos"""

    def test_full_traceability_workflow(self, client, auth_headers):
        """Test workflow completo de trazabilidad"""
        # 1. Crear lote
        lot_data = {
            'producer_company_id': 1,
            'lot_code': 'INT-001',
            'product_type': 'cacao_baba',
            'weight_kg': 1000,
            'quality_score': 90,
            'location': 'Integration Farm'
        }

        response = client.post('/api/lots', json=lot_data, headers=auth_headers)
        assert response.status_code == 201
        lot_id = response.get_json()['lot']['id']

        # 2. Crear evento PRODUCER_INIT
        event_data = {
            'event_type': 'PRODUCER_INIT',
            'entity_type': 'lot',
            'entity_id': str(lot_id),
            'measurements': {
                'weight_kg': 1000,
                'location': 'Integration Farm',
                'harvest_date': '2025-11-13'
            }
        }

        response = client.post('/api/traceability/events',
                             json=event_data,
                             headers=auth_headers)
        assert response.status_code == 201

        # 3. Verificar timeline
        response = client.get(f'/api/traceability/timeline/lot/{lot_id}',
                            headers=auth_headers)
        assert response.status_code == 200
        timeline = response.get_json()
        assert len(timeline['timeline']) > 0

        # 4. Validar cadena
        response = client.get(f'/api/traceability/validate-chain/lot/{lot_id}',
                            headers=auth_headers)
        assert response.status_code == 200
        validation = response.get_json()
        assert 'is_valid' in validation

    def test_contract_to_fixation_workflow(self, client, auth_headers):
        """Test workflow contrato → fijación"""
        # 1. Crear contrato
        contract_data = {
            'contract_number': 'WF-001',
            'buyer_company_id': 1,
            'seller_company_id': 1,
            'product_type': 'cacao',
            'quantity_kg': 2000,
            'price_per_kg': 3.0,
            'contract_date': '2025-11-13',
            'status': 'active'
        }

        response = client.post('/api/contracts', json=contract_data, headers=auth_headers)
        assert response.status_code == 201
        contract_id = response.get_json()['contract']['id']

        # 2. Crear fijación
        fixation_data = {
            'contract_id': contract_id,
            'fixed_quantity_mt': 1.5,
            'spot_price_usd': 3.2,
            'fixation_date': '2025-11-13'
        }

        response = client.post('/api/fixations', json=fixation_data, headers=auth_headers)
        assert response.status_code == 201

        # 3. Verificar que aparecen en analytics
        response = client.get('/api/analytics/financial', headers=auth_headers)
        assert response.status_code == 200
        analytics = response.get_json()['analytics']
        assert analytics['fixation_analysis']['total_fixations'] >= 1


# =====================================
# UTILIDADES DE TEST
# =====================================

def run_all_tests():
    """Ejecutar todos los tests"""
    print("🚀 Ejecutando suite completa de tests para Triboka Fase 2...")

    # Ejecutar con pytest
    import subprocess
    result = subprocess.run([
        'python', '-m', 'pytest',
        'tests/test_complete_suite.py',
        '-v', '--tb=short'
    ], capture_output=True, text=True)

    print("📊 Resultados de los tests:")
    print(result.stdout)

    if result.stderr:
        print("⚠️  Errores/Warnings:")
        print(result.stderr)

    return result.returncode == 0


if __name__ == '__main__':
    # Ejecutar tests si se llama directamente
    success = run_all_tests()
    exit(0 if success else 1)
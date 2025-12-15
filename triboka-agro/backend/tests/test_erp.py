# tests/test_erp.py
"""
Tests unitarios para el módulo ERP
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from routes.erp import ERPConnector, ERP_SYSTEMS


class TestERPSystems:
    """Tests para configuración de sistemas ERP"""

    def test_erp_systems_defined(self):
        """Verificar que todos los sistemas ERP estén definidos"""
        expected_systems = ['sap', 'dynamics', 'oracle', 'custom']

        for system in expected_systems:
            assert system in ERP_SYSTEMS
            assert 'name' in ERP_SYSTEMS[system]
            assert 'api_version' in ERP_SYSTEMS[system]
            assert 'endpoints' in ERP_SYSTEMS[system]

    def test_sap_endpoints(self):
        """Verificar endpoints de SAP"""
        sap = ERP_SYSTEMS['sap']
        assert sap['name'] == 'SAP ERP'
        assert 'companies' in sap['endpoints']
        assert 'contracts' in sap['endpoints']
        assert 'fixations' in sap['endpoints']

    def test_dynamics_endpoints(self):
        """Verificar endpoints de Dynamics"""
        dynamics = ERP_SYSTEMS['dynamics']
        assert dynamics['name'] == 'Microsoft Dynamics 365'
        assert 'companies' in dynamics['endpoints']
        assert 'contracts' in dynamics['endpoints']


class TestERPConnector:
    """Tests para el conector ERP"""

    @pytest.fixture
    def mock_session(self):
        """Sesión HTTP mock"""
        session = MagicMock()
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {'success': True}
        session.request.return_value = response
        return session

    def test_connector_initialization(self):
        """Verificar inicialización del conector"""
        with patch('routes.erp.requests.Session', return_value=self.mock_session()):
            config = {
                'base_url': 'https://erp.example.com',
                'api_key': 'test_key',
                'username': 'test_user',
                'password': 'test_pass'
            }

            connector = ERPConnector('sap', config)

            assert connector.system_type == 'sap'
            assert connector.base_url == 'https://erp.example.com'
            assert connector.api_key == 'test_key'

    def test_sap_authentication(self):
        """Verificar autenticación SAP (Basic Auth)"""
        with patch('routes.erp.requests.Session', return_value=self.mock_session()) as mock_session_class:
            mock_session = self.mock_session()
            mock_session_class.return_value = mock_session

            config = {
                'base_url': 'https://sap.example.com',
                'username': 'sap_user',
                'password': 'sap_pass'
            }

            connector = ERPConnector('sap', config)

            # Verificar que se configuró Basic Auth
            assert mock_session.auth == ('sap_user', 'sap_pass')

    def test_dynamics_authentication(self):
        """Verificar autenticación Dynamics (API Key)"""
        with patch('routes.erp.requests.Session', return_value=self.mock_session()) as mock_session_class:
            mock_session = self.mock_session()
            mock_session_class.return_value = mock_session

            config = {
                'base_url': 'https://dynamics.example.com',
                'api_key': 'dynamics_key'
            }

            connector = ERPConnector('dynamics', config)

            # Verificar que se configuró el header de autorización
            assert 'Authorization' in mock_session.headers

    def test_connection_test_success(self):
        """Verificar test de conexión exitoso"""
        with patch('routes.erp.requests.Session', return_value=self.mock_session()) as mock_session_class:
            mock_session = self.mock_session()
            mock_session_class.return_value = mock_session

            config = {'base_url': 'https://erp.example.com'}
            connector = ERPConnector('custom', config)

            result = connector.test_connection()
            assert result == True

    def test_connection_test_failure(self):
        """Verificar test de conexión fallido"""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_session.request.return_value = mock_response

        with patch('routes.erp.requests.Session', return_value=mock_session):
            config = {'base_url': 'https://erp.example.com'}
            connector = ERPConnector('custom', config)

            result = connector.test_connection()
            assert result == False

    @patch('routes.erp.requests.Session')
    def test_sync_companies(self, mock_session_class, mock_session):
        """Verificar sincronización de compañías"""
        mock_session_class.return_value = mock_session

        config = {'base_url': 'https://erp.example.com'}
        connector = ERPConnector('custom', config)

        companies_data = [{
            'id': 1,
            'name': 'Test Company',
            'tax_id': '123456'
        }]

        result = connector.sync_companies(companies_data)

        # Verificar que se hizo la petición correcta
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0][0] == 'POST'  # method
        assert 'companies' in call_args[0][1]  # endpoint
        assert call_args[1]['json'] == {'companies': companies_data}  # data

    @patch('routes.erp.requests.Session')
    def test_sync_contracts(self, mock_session_class, mock_session):
        """Verificar sincronización de contratos"""
        mock_session_class.return_value = mock_session

        config = {'base_url': 'https://erp.example.com'}
        connector = ERPConnector('custom', config)

        contracts_data = [{
            'id': 1,
            'contract_number': 'C001',
            'total_value': 10000
        }]

        result = connector.sync_contracts(contracts_data)

        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0][0] == 'POST'
        assert 'contracts' in call_args[0][1]
        assert call_args[1]['json'] == {'contracts': contracts_data}

    @patch('routes.erp.requests.Session')
    def test_sync_fixations(self, mock_session_class, mock_session):
        """Verificar sincronización de fijaciones"""
        mock_session_class.return_value = mock_session

        config = {'base_url': 'https://erp.example.com'}
        connector = ERPConnector('custom', config)

        fixations_data = [{
            'id': 1,
            'fixed_price': 2500,
            'fixed_quantity_mt': 100
        }]

        result = connector.sync_fixations(fixations_data)

        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0][0] == 'POST'
        assert 'fixations' in call_args[0][1]
        assert call_args[1]['json'] == {'fixations': fixations_data}


class TestERPAPI:
    """Tests para endpoints ERP"""

    def test_get_erp_systems(self, client, auth_headers):
        """Obtener sistemas ERP disponibles"""
        response = client.get('/api/erp/systems', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()

        assert 'systems' in data
        assert 'sap' in data['systems']
        assert 'dynamics' in data['systems']
        assert 'oracle' in data['systems']
        assert 'custom' in data['systems']

    def test_create_connection_missing_fields(self, client, auth_headers):
        """Crear conexión sin campos requeridos debe fallar"""
        response = client.post('/api/erp/connections',
                             json={},
                             headers=auth_headers)

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_create_connection_invalid_system(self, client, auth_headers):
        """Crear conexión con sistema inválido debe fallar"""
        connection_data = {
            'system_type': 'invalid_system',
            'name': 'Test Connection',
            'base_url': 'https://erp.example.com'
        }

        response = client.post('/api/erp/connections',
                             json=connection_data,
                             headers=auth_headers)

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'no soportado' in data['error']

    @patch('routes.erp.ERPConnector')
    def test_create_connection_success(self, mock_connector_class, client, auth_headers):
        """Crear conexión exitosamente"""
        # Mock del conector
        mock_connector = MagicMock()
        mock_connector.test_connection.return_value = True
        mock_connector_class.return_value = mock_connector

        connection_data = {
            'system_type': 'sap',
            'name': 'SAP Test',
            'base_url': 'https://sap.example.com',
            'username': 'test_user',
            'password': 'test_pass'
        }

        response = client.post('/api/erp/connections',
                             json=connection_data,
                             headers=auth_headers)

        assert response.status_code == 201
        data = response.get_json()

        assert 'message' in data
        assert 'connection' in data
        assert data['connection']['system_type'] == 'sap'
        assert data['connection']['status'] == 'active'

    @patch('routes.erp.ERPConnector')
    def test_test_connection_success(self, mock_connector_class, client, auth_headers):
        """Probar conexión exitosamente"""
        mock_connector = MagicMock()
        mock_connector.test_connection.return_value = True
        mock_connector.system_type = 'sap'
        mock_connector_class.return_value = mock_connector

        # Primero crear la conexión
        connection_data = {
            'system_type': 'sap',
            'name': 'SAP Test',
            'base_url': 'https://sap.example.com'
        }

        create_response = client.post('/api/erp/connections',
                                    json=connection_data,
                                    headers=auth_headers)

        assert create_response.status_code == 201
        connection_id = create_response.get_json()['connection']['id']

        # Luego probar la conexión
        test_response = client.post(f'/api/erp/test-connection/{connection_id}',
                                  headers=auth_headers)

        assert test_response.status_code == 200
        data = test_response.get_json()
        assert data['status'] == 'connected'
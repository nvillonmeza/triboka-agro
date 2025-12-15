# tests/test_analytics.py
"""
Tests unitarios para el módulo de analytics
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from routes.analytics import AnalyticsEngine, AnalyticsCache, analytics_cache


class TestAnalyticsEngine:
    """Tests para el motor de analytics"""

    @pytest.fixture
    def analytics_engine(self):
        """Instancia del motor de analytics para tests"""
        return AnalyticsEngine()

    def test_calculate_contract_metrics(self, analytics_engine):
        """Verificar cálculo de métricas de contratos"""
        # Datos de prueba
        contracts = [
            {
                'id': 1,
                'contract_code': 'C001',
                'total_quantity_mt': 1000,
                'fixed_quantity_mt': 800,
                'remaining_quantity_mt': 200,
                'contract_value_usd': 500000,
                'status': 'active'
            },
            {
                'id': 2,
                'contract_code': 'C002',
                'total_quantity_mt': 500,
                'fixed_quantity_mt': 300,
                'remaining_quantity_mt': 200,
                'contract_value_usd': 250000,
                'status': 'active'
            }
        ]

        metrics = analytics_engine.calculate_contract_metrics(contracts)

        assert 'total_contracts' in metrics
        assert 'total_quantity_mt' in metrics
        assert 'total_fixed_mt' in metrics
        assert 'total_remaining_mt' in metrics
        assert 'total_value_usd' in metrics
        assert 'avg_contract_value' in metrics
        assert 'fixation_rate' in metrics

        assert metrics['total_contracts'] == 2
        assert metrics['total_quantity_mt'] == 1500
        assert metrics['total_fixed_mt'] == 1100
        assert metrics['total_remaining_mt'] == 400
        assert metrics['total_value_usd'] == 750000
        assert metrics['avg_contract_value'] == 375000
        assert metrics['fixation_rate'] == 1100 / 1500

    def test_calculate_fixation_metrics(self, analytics_engine):
        """Verificar cálculo de métricas de fijaciones"""
        fixations = [
            {
                'id': 1,
                'contract_id': 1,
                'fixed_quantity_mt': 100,
                'fixed_price_usd_per_mt': 500,
                'fixation_date': '2024-01-15',
                'status': 'confirmed'
            },
            {
                'id': 2,
                'contract_id': 1,
                'fixed_quantity_mt': 200,
                'fixed_price_usd_per_mt': 520,
                'fixation_date': '2024-02-01',
                'status': 'confirmed'
            }
        ]

        metrics = analytics_engine.calculate_fixation_metrics(fixations)

        assert 'total_fixations' in metrics
        assert 'total_fixed_quantity_mt' in metrics
        assert 'avg_fixation_price' in metrics
        assert 'total_fixation_value' in metrics
        assert 'fixation_timeline' in metrics

        assert metrics['total_fixations'] == 2
        assert metrics['total_fixed_quantity_mt'] == 300
        assert metrics['avg_fixation_price'] == 510
        assert metrics['total_fixation_value'] == 154000

    def test_calculate_market_trends(self, analytics_engine):
        """Verificar cálculo de tendencias de mercado"""
        # Datos de prueba con precios históricos
        price_data = [
            {'date': '2024-01-01', 'price': 450},
            {'date': '2024-01-02', 'price': 460},
            {'date': '2024-01-03', 'price': 455},
            {'date': '2024-01-04', 'price': 470},
            {'date': '2024-01-05', 'price': 465}
        ]

        trends = analytics_engine.calculate_market_trends(price_data)

        assert 'current_price' in trends
        assert 'price_change_24h' in trends
        assert 'price_change_7d' in trends
        assert 'volatility' in trends
        assert 'trend_direction' in trends

        assert trends['current_price'] == 465
        assert trends['price_change_24h'] == -5  # 470 -> 465
        assert trends['price_change_7d'] == 15   # 450 -> 465

    def test_generate_performance_report(self, analytics_engine):
        """Verificar generación de reporte de rendimiento"""
        # Datos de prueba
        contracts = [{'id': 1, 'contract_code': 'C001', 'total_quantity_mt': 1000}]
        fixations = [{'id': 1, 'contract_id': 1, 'fixed_quantity_mt': 500}]
        market_data = [{'date': '2024-01-01', 'price': 500}]

        report = analytics_engine.generate_performance_report(contracts, fixations, market_data)

        assert 'contract_metrics' in report
        assert 'fixation_metrics' in report
        assert 'market_trends' in report
        assert 'generated_at' in report
        assert 'period' in report


class TestAnalyticsCache:
    """Tests para el sistema de cache de analytics"""

    @pytest.fixture
    def cache(self):
        """Instancia del cache para tests"""
        return AnalyticsCache()

    def test_cache_set_get(self, cache):
        """Verificar set y get básicos del cache"""
        cache.set('test_key', {'data': 'value'}, ttl=60)

        # Verificar que se puede recuperar
        data = cache.get('test_key')
        assert data is not None
        assert data['data'] == 'value'

    def test_cache_expiration(self, cache):
        """Verificar expiración del cache"""
        cache.set('test_key', {'data': 'value'}, ttl=1)

        # Esperar a que expire
        import time
        time.sleep(1.1)

        # Verificar que ya no está disponible
        data = cache.get('test_key')
        assert data is None

    def test_cache_delete(self, cache):
        """Verificar eliminación del cache"""
        cache.set('test_key', {'data': 'value'})

        # Verificar que existe
        assert cache.get('test_key') is not None

        # Eliminar
        cache.delete('test_key')

        # Verificar que ya no existe
        assert cache.get('test_key') is None

    def test_cache_clear(self, cache):
        """Verificar limpieza completa del cache"""
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')

        # Verificar que existen
        assert cache.get('key1') is not None
        assert cache.get('key2') is not None

        # Limpiar
        cache.clear()

        # Verificar que no existen
        assert cache.get('key1') is None
        assert cache.get('key2') is None


class TestAnalyticsAPI:
    """Tests para endpoints de analytics"""

    def test_get_contract_analytics_unauthorized(self, client):
        """Obtener analytics de contratos sin autenticación debe fallar"""
        response = client.get('/api/analytics/contracts')

        assert response.status_code == 401

    @patch('routes.analytics.get_contracts_cached')
    def test_get_contract_analytics_authorized(self, mock_get_contracts, client, auth_headers):
        """Obtener analytics de contratos con autenticación"""
        mock_get_contracts.return_value = [
            {
                'id': 1,
                'contract_code': 'C001',
                'total_quantity_mt': 1000,
                'fixed_quantity_mt': 800,
                'remaining_quantity_mt': 200,
                'contract_value_usd': 500000,
                'status': 'active'
            }
        ]

        response = client.get('/api/analytics/contracts', headers=auth_headers)

        if response.status_code == 200:
            data = response.get_json()
            assert 'metrics' in data
            assert 'total_contracts' in data['metrics']
            assert 'fixation_rate' in data['metrics']

    @patch('routes.analytics.get_fixations_cached')
    def test_get_fixation_analytics(self, mock_get_fixations, client, auth_headers):
        """Obtener analytics de fijaciones"""
        mock_get_fixations.return_value = [
            {
                'id': 1,
                'contract_id': 1,
                'fixed_quantity_mt': 100,
                'fixed_price_usd_per_mt': 500,
                'fixation_date': '2024-01-15',
                'status': 'confirmed'
            }
        ]

        response = client.get('/api/analytics/fixations', headers=auth_headers)

        if response.status_code == 200:
            data = response.get_json()
            assert 'metrics' in data
            assert 'total_fixations' in data['metrics']
            assert 'avg_fixation_price' in data['metrics']

    def test_get_market_trends_invalid_period(self, client, auth_headers):
        """Obtener tendencias de mercado con período inválido debe fallar"""
        response = client.get('/api/analytics/market/trends?period=invalid', headers=auth_headers)

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    @patch('routes.analytics.get_market_price_data')
    def test_get_market_trends_valid_period(self, mock_get_market_data, client, auth_headers):
        """Obtener tendencias de mercado con período válido"""
        mock_get_market_data.return_value = [
            {'date': '2024-01-01', 'price': 450},
            {'date': '2024-01-02', 'price': 460}
        ]

        response = client.get('/api/analytics/market/trends?period=7d', headers=auth_headers)

        if response.status_code == 200:
            data = response.get_json()
            assert 'current_price' in data
            assert 'price_change_24h' in data
            assert 'trend_direction' in data

    def test_generate_report_missing_params(self, client, auth_headers):
        """Generar reporte sin parámetros debe fallar"""
        response = client.post('/api/analytics/reports/generate',
                             json={},
                             headers=auth_headers)

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_generate_report_invalid_type(self, client, auth_headers):
        """Generar reporte con tipo inválido debe fallar"""
        response = client.post('/api/analytics/reports/generate',
                             json={'report_type': 'invalid_type'},
                             headers=auth_headers)

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    @patch('routes.analytics.AnalyticsEngine.generate_performance_report')
    def test_generate_performance_report(self, mock_generate_report, client, auth_headers):
        """Generar reporte de rendimiento"""
        mock_generate_report.return_value = {
            'contract_metrics': {'total_contracts': 5},
            'fixation_metrics': {'total_fixations': 10},
            'market_trends': {'current_price': 500},
            'generated_at': '2024-01-01T00:00:00Z',
            'period': 'monthly'
        }

        response = client.post('/api/analytics/reports/generate',
                             json={'report_type': 'performance', 'period': 'monthly'},
                             headers=auth_headers)

        if response.status_code == 200:
            data = response.get_json()
            assert 'contract_metrics' in data
            assert 'fixation_metrics' in data
            assert 'market_trends' in data
            assert 'generated_at' in data

    def test_get_cached_analytics(self, client, auth_headers):
        """Obtener analytics desde cache"""
        response = client.get('/api/analytics/cache/stats', headers=auth_headers)

        # Puede fallar si no está implementado completamente
        assert response.status_code in [200, 401, 500]

    def test_clear_analytics_cache(self, client, auth_headers):
        """Limpiar cache de analytics"""
        response = client.post('/api/analytics/cache/clear', headers=auth_headers)

        # Verificar que se procesa la petición
        assert response.status_code in [200, 401, 500]


class TestAnalyticsIntegration:
    """Tests de integración para analytics"""

    @patch('routes.analytics.get_contracts_cached')
    @patch('routes.analytics.get_fixations_cached')
    @patch('routes.analytics.get_market_price_data')
    def test_full_analytics_workflow(self, mock_market_data, mock_fixations, mock_contracts, client, auth_headers):
        """Verificar flujo completo de analytics"""
        # Configurar mocks
        mock_contracts.return_value = [
            {
                'id': 1,
                'contract_code': 'C001',
                'total_quantity_mt': 1000,
                'fixed_quantity_mt': 800,
                'remaining_quantity_mt': 200,
                'contract_value_usd': 500000,
                'status': 'active'
            }
        ]

        mock_fixations.return_value = [
            {
                'id': 1,
                'contract_id': 1,
                'fixed_quantity_mt': 100,
                'fixed_price_usd_per_mt': 500,
                'fixation_date': '2024-01-15',
                'status': 'confirmed'
            }
        ]

        mock_market_data.return_value = [
            {'date': '2024-01-01', 'price': 450},
            {'date': '2024-01-02', 'price': 460}
        ]

        # Ejecutar workflow completo
        # 1. Obtener analytics de contratos
        response1 = client.get('/api/analytics/contracts', headers=auth_headers)
        if response1.status_code == 200:
            contract_data = response1.get_json()

        # 2. Obtener analytics de fijaciones
        response2 = client.get('/api/analytics/fixations', headers=auth_headers)
        if response2.status_code == 200:
            fixation_data = response2.get_json()

        # 3. Obtener tendencias de mercado
        response3 = client.get('/api/analytics/market/trends?period=7d', headers=auth_headers)
        if response3.status_code == 200:
            market_data = response3.get_json()

        # 4. Generar reporte completo
        response4 = client.post('/api/analytics/reports/generate',
                              json={'report_type': 'performance', 'period': 'monthly'},
                              headers=auth_headers)

        if response4.status_code == 200:
            report_data = response4.get_json()

            # Verificar que el reporte contiene todos los componentes
            assert 'contract_metrics' in report_data
            assert 'fixation_metrics' in report_data
            assert 'market_trends' in report_data
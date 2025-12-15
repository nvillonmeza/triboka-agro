"""
Módulo de Optimización de Rendimiento
Implementa caching con Redis y optimización de consultas
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json
import logging
import redis
import time
from functools import wraps
from typing import Dict, List, Optional, Any, Callable
import hashlib

from models_simple import db, ExportContract, ContractFixation, ProducerLot, BatchNFT, TraceEvent, Company, User
from blockchain_service import get_blockchain_integration

logger = logging.getLogger(__name__)

performance_bp = Blueprint('performance', __name__)

# Configuración de Redis
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'decode_responses': True,
    'socket_connect_timeout': 5,
    'socket_timeout': 5,
    'retry_on_timeout': True,
    'max_connections': 20
}

# Instancia global de Redis
redis_client = None

def get_redis_client():
    """Obtener cliente Redis con inicialización lazy"""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.Redis(**REDIS_CONFIG)
            # Probar conexión
            redis_client.ping()
            logger.info("Redis connection established")
        except redis.ConnectionError as e:
            logger.warning(f"Redis connection failed: {str(e)}")
            redis_client = None
    return redis_client

def cache_key(*args, **kwargs):
    """Generar clave de cache consistente"""
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()

def cached(timeout: int = 300, key_prefix: str = ""):
    """Decorador para caching de funciones"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            redis_client = get_redis_client()
            if not redis_client:
                # Si no hay Redis, ejecutar función normalmente
                return func(*args, **kwargs)

            # Generar clave de cache
            cache_key_full = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"

            # Intentar obtener del cache
            try:
                cached_result = redis_client.get(cache_key_full)
                if cached_result:
                    logger.debug(f"Cache hit for {cache_key_full}")
                    return json.loads(cached_result)
            except Exception as e:
                logger.warning(f"Cache read error: {str(e)}")

            # Ejecutar función y cachear resultado
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            # Solo cachear si la ejecución tomó tiempo significativo
            if execution_time > 0.1:  # Más de 100ms
                try:
                    redis_client.setex(cache_key_full, timeout, json.dumps(result, default=str))
                    logger.debug(f"Cached result for {cache_key_full}")
                except Exception as e:
                    logger.warning(f"Cache write error: {str(e)}")

            return result
        return wrapper
    return decorator

class PerformanceMonitor:
    """Monitor de rendimiento para endpoints"""

    def __init__(self):
        self.redis_client = get_redis_client()
        # Para testing: diccionario en memoria para métricas
        self.metrics = {}

    def record_request(self, endpoint: str, method: str, response_time: float, status_code: int, user_id: Optional[int] = None):
        """Registrar métricas de una petición"""
        endpoint_key = f"{endpoint}:{method}"

        # Inicializar métricas para este endpoint si no existen
        if endpoint_key not in self.metrics:
            self.metrics[endpoint_key] = {
                'count': 0,
                'response_times': [],
                'status_codes': {},
                'total_response_time': 0.0,
                'min_response_time': float('inf'),
                'max_response_time': 0.0,
                'last_updated': datetime.utcnow().isoformat()
            }

        # Actualizar métricas
        metrics = self.metrics[endpoint_key]
        metrics['count'] += 1
        metrics['response_times'].append(response_time)
        metrics['total_response_time'] += response_time
        metrics['min_response_time'] = min(metrics['min_response_time'], response_time)
        metrics['max_response_time'] = max(metrics['max_response_time'], response_time)
        metrics['last_updated'] = datetime.utcnow().isoformat()

        # Contar códigos de estado
        status_str = str(status_code)
        if status_str not in metrics['status_codes']:
            metrics['status_codes'][status_str] = 0
        metrics['status_codes'][status_str] += 1

        # Mantener solo las últimas 100 mediciones de tiempo de respuesta
        if len(metrics['response_times']) > 100:
            # Remover la medición más antigua y ajustar totales
            oldest_time = metrics['response_times'].pop(0)
            metrics['total_response_time'] -= oldest_time
            # Recalcular min/max si es necesario
            if metrics['response_times']:
                metrics['min_response_time'] = min(metrics['response_times'])
                metrics['max_response_time'] = max(metrics['response_times'])

        # También registrar en Redis si está disponible
        if not self.redis_client:
            return

        timestamp = datetime.utcnow().isoformat()

        # Métricas por endpoint
        redis_endpoint_key = f"metrics:endpoint:{endpoint}:{method}"
        self.redis_client.lpush(redis_endpoint_key, json.dumps({
            'timestamp': timestamp,
            'response_time': response_time,
            'status_code': status_code,
            'user_id': user_id
        }))
        # Mantener solo las últimas 1000 entradas
        self.redis_client.ltrim(redis_endpoint_key, 0, 999)

        # Contadores generales
        self.redis_client.incr(f"counters:requests:{status_code}")
        self.redis_client.incr("counters:requests:total")

        # Tiempos de respuesta por endpoint
        self.redis_client.lpush(f"response_times:{endpoint}", response_time)
        self.redis_client.ltrim(f"response_times:{endpoint}", 0, 999)

    def get_endpoint_metrics(self, endpoint: str, method: str = None, hours: int = 24) -> Dict:
        """Obtener métricas de un endpoint"""
        endpoint_key = f"{endpoint}:{method}" if method else None

        # Si tenemos métricas en memoria para este endpoint específico
        if endpoint_key and endpoint_key in self.metrics:
            metrics = self.metrics[endpoint_key]
            return {
                'count': metrics['count'],
                'avg_response_time': metrics['total_response_time'] / metrics['count'] if metrics['count'] > 0 else 0,
                'min_response_time': metrics['min_response_time'] if metrics['min_response_time'] != float('inf') else 0,
                'max_response_time': metrics['max_response_time'],
                'status_codes': metrics['status_codes'],
                'last_updated': metrics['last_updated']
            }

        # Si no hay métricas en memoria o no está disponible, intentar Redis
        if not self.redis_client:
            return {}

        metrics = {}

        # Obtener tiempos de respuesta
        response_times_key = f"response_times:{endpoint}"
        response_times = self.redis_client.lrange(response_times_key, 0, -1)

        if response_times:
            times = [float(t) for t in response_times]
            metrics['response_times'] = {
                'avg': sum(times) / len(times),
                'min': min(times),
                'max': max(times),
                'count': len(times)
            }

        # Obtener peticiones recientes
        if method:
            requests_key = f"metrics:endpoint:{endpoint}:{method}"
            requests_data = self.redis_client.lrange(requests_key, 0, -1)
            if requests_data:
                requests = [json.loads(r) for r in requests_data]
                # Filtrar por tiempo (últimas N horas)
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                recent_requests = [
                    r for r in requests
                    if datetime.fromisoformat(r['timestamp']) > cutoff_time
                ]

                status_counts = {}
                for req in recent_requests:
                    status = req['status_code']
                    status_counts[status] = status_counts.get(status, 0) + 1

                metrics['requests'] = {
                    'total': len(recent_requests),
                    'status_codes': status_counts,
                    'period_hours': hours
                }

        return metrics

    def reset_metrics(self):
        """Resetear métricas (para testing)"""
        self.metrics.clear()

    def get_system_metrics(self) -> Dict:
        """Obtener métricas generales del sistema"""
        if not self.redis_client:
            return {}

        metrics = {}

        # Contadores generales
        total_requests = self.redis_client.get("counters:requests:total") or 0
        error_4xx = self.redis_client.get("counters:requests:4xx") or 0
        error_5xx = self.redis_client.get("counters:requests:5xx") or 0

        metrics['requests'] = {
            'total': int(total_requests),
            'errors_4xx': int(error_4xx),
            'errors_5xx': int(error_5xx),
            'success_rate': ((int(total_requests) - int(error_4xx) - int(error_5xx)) / int(total_requests) * 100) if int(total_requests) > 0 else 0
        }

        # Información de Redis
        try:
            redis_info = self.redis_client.info()
            metrics['redis'] = {
                'connected_clients': redis_info.get('connected_clients', 0),
                'used_memory_human': redis_info.get('used_memory_human', '0B'),
                'total_connections_received': redis_info.get('total_connections_received', 0),
                'uptime_in_seconds': redis_info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            logger.warning(f"Error getting Redis info: {str(e)}")
            metrics['redis'] = {'status': 'error', 'message': str(e)}

        return metrics

# Instancia global del monitor
performance_monitor = PerformanceMonitor()

def performance_monitoring_middleware():
    """Middleware para monitoreo de rendimiento"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                response_time = time.time() - start_time

                # Registrar métricas
                endpoint = request.endpoint or 'unknown'
                method = request.method
                status_code = 200  # Asumir éxito por defecto

                # Obtener user_id si está disponible
                user_id = None
                try:
                    user_id = get_jwt_identity()
                except:
                    pass

                performance_monitor.record_request(
                    endpoint=endpoint,
                    method=method,
                    response_time=response_time,
                    status_code=status_code,
                    user_id=user_id
                )

                return result

            except Exception as e:
                response_time = time.time() - start_time
                # Registrar error
                endpoint = request.endpoint or 'unknown'
                method = request.method
                status_code = 500

                performance_monitor.record_request(
                    endpoint=endpoint,
                    method=method,
                    response_time=response_time,
                    status_code=status_code,
                    user_id=get_jwt_identity() if 'jwt' in str(request.headers) else None
                )
                raise e

        return wrapper
    return decorator

@performance_bp.before_request
def setup_performance_monitoring():
    """Configurar monitoreo antes de cada petición"""
    g.start_time = time.time()

@performance_bp.after_request
def record_performance_metrics(response):
    """Registrar métricas después de cada petición"""
    if hasattr(g, 'start_time'):
        response_time = time.time() - g.start_time
        endpoint = request.endpoint or 'unknown'
        method = request.method
        status_code = response.status_code

        user_id = None
        try:
            user_id = get_jwt_identity()
        except:
            pass

        performance_monitor.record_request(
            endpoint=endpoint,
            method=method,
            response_time=response_time,
            status_code=status_code,
            user_id=user_id
        )

    return response

@performance_bp.route('/cache/clear', methods=['POST'])
@jwt_required()
def clear_cache():
    """Limpiar cache de Redis"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para gestionar cache'}), 403

        redis_client = get_redis_client()
        if redis_client:
            redis_client.flushdb()
            return jsonify({'message': 'Cache limpiado exitosamente'})
        else:
            return jsonify({'error': 'Redis no disponible'}), 503

    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@performance_bp.route('/cache/stats', methods=['GET'])
@jwt_required()
def get_cache_stats():
    """Obtener estadísticas del cache"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para ver estadísticas de cache'}), 403

        redis_client = get_redis_client()
        if not redis_client:
            return jsonify({'error': 'Redis no disponible'}), 503

        # Obtener información de Redis
        info = redis_client.info()
        db_size = redis_client.dbsize()

        # Obtener keys por patrón
        cache_keys = {}
        patterns = ['contracts:*', 'fixations:*', 'lots:*', 'traceability:*', 'companies:*']

        for pattern in patterns:
            keys = redis_client.keys(pattern)
            cache_keys[pattern] = len(keys)

        return jsonify({
            'redis_info': {
                'version': info.get('redis_version'),
                'uptime_days': info.get('uptime_in_days'),
                'connected_clients': info.get('connected_clients'),
                'used_memory_human': info.get('used_memory_human'),
                'total_connections_received': info.get('total_connections_received')
            },
            'cache_stats': {
                'total_keys': db_size,
                'keys_by_pattern': cache_keys
            }
        })

    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@performance_bp.route('/metrics', methods=['GET'])
@jwt_required()
def get_performance_metrics():
    """Obtener métricas de rendimiento"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para ver métricas de rendimiento'}), 403

        # Obtener métricas del sistema
        system_metrics = performance_monitor.get_system_metrics()

        # Obtener métricas de endpoints populares
        popular_endpoints = [
            ('contracts.get_contracts', 'GET'),
            ('fixations.get_fixations', 'GET'),
            ('traceability.get_trace_events', 'GET'),
            ('lots.get_producer_lots', 'GET')
        ]

        endpoint_metrics = {}
        for endpoint, method in popular_endpoints:
            metrics = performance_monitor.get_endpoint_metrics(endpoint, method)
            if metrics:
                endpoint_metrics[f"{endpoint}:{method}"] = metrics

        return jsonify({
            'system_metrics': system_metrics,
            'endpoint_metrics': endpoint_metrics,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@performance_bp.route('/optimize/queries', methods=['POST'])
@jwt_required()
def optimize_queries():
    """Ejecutar optimización de consultas"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role != 'admin':
            return jsonify({'error': 'Solo administradores pueden optimizar consultas'}), 403

        # Ejecutar análisis de rendimiento de consultas
        optimizations = []

        # 1. Verificar índices en tablas principales
        with db.engine.connect() as conn:
            # Contratos
            result = conn.execute("SELECT indexname FROM pg_indexes WHERE tablename = 'export_contracts'")
            contract_indexes = [row[0] for row in result]

            required_indexes = [
                'ix_export_contracts_buyer_company_id',
                'ix_export_contracts_exporter_company_id',
                'ix_export_contracts_status',
                'ix_export_contracts_start_date'
            ]

            for index in required_indexes:
                if index not in contract_indexes:
                    optimizations.append({
                        'type': 'missing_index',
                        'table': 'export_contracts',
                        'index': index,
                        'recommendation': f'CREATE INDEX {index} ON export_contracts ({index.replace("ix_export_contracts_", "")});'
                    })

            # Fijaciones
            result = conn.execute("SELECT indexname FROM pg_indexes WHERE tablename = 'contract_fixations'")
            fixation_indexes = [row[0] for row in result]

            required_fixation_indexes = [
                'ix_contract_fixations_export_contract_id',
                'ix_contract_fixations_fixation_date',
                'ix_contract_fixations_status'
            ]

            for index in required_fixation_indexes:
                if index not in fixation_indexes:
                    optimizations.append({
                        'type': 'missing_index',
                        'table': 'contract_fixations',
                        'index': index,
                        'recommendation': f'CREATE INDEX {index} ON contract_fixations ({index.replace("ix_contract_fixations_", "")});'
                    })

            # Eventos de trazabilidad
            result = conn.execute("SELECT indexname FROM pg_indexes WHERE tablename = 'trace_events'")
            trace_indexes = [row[0] for row in result]

            required_trace_indexes = [
                'ix_trace_events_batch_nft_id',
                'ix_trace_events_event_type',
                'ix_trace_events_timestamp',
                'ix_trace_events_producer_company_id'
            ]

            for index in required_trace_indexes:
                if index not in trace_indexes:
                    optimizations.append({
                        'type': 'missing_index',
                        'table': 'trace_events',
                        'index': index,
                        'recommendation': f'CREATE INDEX {index} ON trace_events ({index.replace("ix_trace_events_", "")});'
                    })

        return jsonify({
            'message': 'Análisis de optimización completado',
            'optimizations_found': len(optimizations),
            'optimizations': optimizations
        })

    except Exception as e:
        logger.error(f"Error optimizing queries: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@performance_bp.route('/optimize/apply', methods=['POST'])
@jwt_required()
def apply_optimizations():
    """Aplicar optimizaciones de base de datos"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role != 'admin':
            return jsonify({'error': 'Solo administradores pueden aplicar optimizaciones'}), 403

        data = request.get_json()
        optimizations = data.get('optimizations', [])

        applied = []
        failed = []

        with db.engine.connect() as conn:
            for opt in optimizations:
                try:
                    if opt['type'] == 'missing_index':
                        # Ejecutar creación de índice
                        conn.execute(opt['recommendation'])
                        applied.append(opt)
                        logger.info(f"Applied optimization: {opt['recommendation']}")
                except Exception as e:
                    failed.append({
                        'optimization': opt,
                        'error': str(e)
                    })
                    logger.error(f"Failed to apply optimization: {str(e)}")

            conn.commit()

        return jsonify({
            'message': 'Optimizaciones aplicadas',
            'applied': len(applied),
            'failed': len(failed),
            'results': {
                'successful': applied,
                'failed': failed
            }
        })

    except Exception as e:
        logger.error(f"Error applying optimizations: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# Funciones de cache para consultas comunes
@cached(timeout=300, key_prefix="contracts")
def get_contracts_cached(filters: Dict = None) -> List[Dict]:
    """Obtener contratos con cache"""
    query = ExportContract.query

    if filters:
        if 'status' in filters:
            query = query.filter(ExportContract.status == filters['status'])
        if 'buyer_company_id' in filters:
            query = query.filter(ExportContract.buyer_company_id == filters['buyer_company_id'])
        if 'start_date_from' in filters:
            query = query.filter(ExportContract.start_date >= filters['start_date_from'])
        if 'start_date_to' in filters:
            query = query.filter(ExportContract.start_date <= filters['start_date_to'])

    contracts = query.all()
    return [contract.to_dict() for contract in contracts]

@cached(timeout=600, key_prefix="fixations")
def get_fixations_cached(contract_id: Optional[int] = None) -> List[Dict]:
    """Obtener fijaciones con cache"""
    query = ContractFixation.query

    if contract_id:
        query = query.filter(ContractFixation.export_contract_id == contract_id)

    fixations = query.all()
    return [fixation.to_dict() for fixation in fixations]

@cached(timeout=300, key_prefix="trace_events")
def get_trace_events_cached(batch_nft_id: Optional[int] = None, event_type: Optional[str] = None) -> List[Dict]:
    """Obtener eventos de trazabilidad con cache"""
    query = TraceEvent.query

    if batch_nft_id:
        query = query.filter(TraceEvent.batch_nft_id == batch_nft_id)
    if event_type:
        query = query.filter(TraceEvent.event_type == event_type)

    events = query.order_by(TraceEvent.timestamp).all()
    return [event.to_dict() for event in events]

@cached(timeout=1800, key_prefix="companies")
def get_companies_cached(company_type: Optional[str] = None) -> List[Dict]:
    """Obtener empresas con cache"""
    query = Company.query

    if company_type:
        query = query.filter(Company.company_type == company_type)

    companies = query.all()
    return [company.to_dict() for company in companies]


class RedisManager:
    """Gestor de Redis para operaciones de cache y rendimiento"""

    def __init__(self):
        self.redis_client = get_redis_client()

    def set_cache(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Almacenar valor en cache con TTL"""
        try:
            if self.redis_client:
                return self.redis_client.setex(key, ttl, json.dumps(value, default=str))
            return False
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False

    def get_cache(self, key: str) -> Optional[Any]:
        """Obtener valor del cache"""
        try:
            if self.redis_client:
                data = self.redis_client.get(key)
                if data:
                    return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting cache: {str(e)}")
            return None

    def delete_cache(self, key: str) -> bool:
        """Eliminar clave del cache"""
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            return False
        except Exception as e:
            logger.error(f"Error deleting cache: {str(e)}")
            return False

    def clear_cache_pattern(self, pattern: str) -> int:
        """Limpiar cache por patrón"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache pattern: {str(e)}")
            return 0

    def get_cache_stats(self) -> Dict:
        """Obtener estadísticas del cache"""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                return {
                    'connected': True,
                    'used_memory': info.get('used_memory_human', 'N/A'),
                    'total_keys': self.redis_client.dbsize(),
                    'uptime_days': info.get('uptime_in_days', 0)
                }
            return {'connected': False}
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {'connected': False, 'error': str(e)}

    def record_performance_metric(self, endpoint: str, method: str, response_time: float,
                                status_code: int, user_id: Optional[int] = None):
        """Registrar métrica de rendimiento"""
        try:
            if not self.redis_client:
                return

            # Usar el PerformanceMonitor existente
            performance_monitor.record_request(endpoint, method, response_time, status_code, user_id)

        except Exception as e:
            logger.error(f"Error recording performance metric: {str(e)}")

    def get_performance_metrics(self, endpoint: str = None, hours: int = 24) -> Dict:
        """Obtener métricas de rendimiento"""
        try:
            if endpoint:
                return performance_monitor.get_endpoint_metrics(endpoint, hours=hours)
            else:
                return performance_monitor.get_system_metrics()
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            return {}


# Instancia global del gestor de Redis
redis_manager = RedisManager()

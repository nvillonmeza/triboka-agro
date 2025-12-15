"""
Módulo de Dashboards Analíticos Avanzados
Implementa métricas en tiempo real, reportes y visualizaciones
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, date
import json
import logging
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np

from models_simple import db, ExportContract, ContractFixation, ProducerLot, BatchNFT, TraceEvent, Company, User
from blockchain_service import get_blockchain_integration
from routes.performance import cached, performance_monitor

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__)

class AnalyticsEngine:
    """Motor de análisis para métricas avanzadas"""

    def __init__(self):
        self.performance_monitor = performance_monitor

    @cached(timeout=300, key_prefix="analytics")
    def get_supply_chain_metrics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict:
        """Obtener métricas de la cadena de suministro"""
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        metrics = {
            'contracts': {},
            'fixations': {},
            'lots': {},
            'traceability': {},
            'blockchain': {}
        }

        # Métricas de contratos
        contracts_query = ExportContract.query.filter(
            ExportContract.created_at >= start_date,
            ExportContract.created_at <= end_date
        )

        contracts = contracts_query.all()
        metrics['contracts'] = {
            'total': len(contracts),
            'by_status': Counter(c.status for c in contracts),
            'by_product_type': Counter(c.product_type for c in contracts),
            'total_volume_mt': sum(float(c.total_volume_mt) for c in contracts if c.total_volume_mt),
            'avg_differential': np.mean([float(c.differential_usd) for c in contracts if c.differential_usd]) if contracts else 0
        }

        # Métricas de fijaciones
        fixations_query = ContractFixation.query.filter(
            ContractFixation.created_at >= start_date,
            ContractFixation.created_at <= end_date
        )

        fixations = fixations_query.all()
        metrics['fixations'] = {
            'total': len(fixations),
            'total_volume_mt': sum(float(f.fixed_quantity_mt) for f in fixations if f.fixed_quantity_mt),
            'total_value_usd': sum(float(f.total_value_usd) for f in fixations if f.total_value_usd),
            'avg_spot_price': np.mean([float(f.spot_price_usd) for f in fixations if f.spot_price_usd]) if fixations else 0
        }

        # Métricas de lotes
        lots_query = ProducerLot.query.filter(
            ProducerLot.created_at >= start_date,
            ProducerLot.created_at <= end_date
        )

        lots = lots_query.all()
        metrics['lots'] = {
            'total': len(lots),
            'by_quality_grade': Counter(l.quality_grade for l in lots if l.quality_grade),
            'total_volume_mt': sum(float(l.volume_mt) for l in lots if l.volume_mt),
            'avg_humidity': np.mean([float(l.humidity_percent) for l in lots if l.humidity_percent]) if lots else 0,
            'avg_fermentation_days': np.mean([l.fermentation_days for l in lots if l.fermentation_days]) if lots else 0
        }

        # Métricas de trazabilidad
        trace_query = TraceEvent.query.filter(
            TraceEvent.timestamp >= start_date,
            TraceEvent.timestamp <= end_date
        )

        trace_events = trace_query.all()
        metrics['traceability'] = {
            'total_events': len(trace_events),
            'by_event_type': Counter(e.event_type for e in trace_events),
            'events_per_day': self._group_events_by_date(trace_events),
            'supply_chain_stages': self._calculate_supply_chain_progress(trace_events)
        }

        # Métricas de blockchain
        blockchain = get_blockchain_integration()
        metrics['blockchain'] = {
            'total_transactions': len(trace_events),  # Simplificado
            'gas_usage_estimate': len(trace_events) * 21000,  # Estimación básica
            'network_status': 'active' if blockchain else 'inactive'
        }

        return metrics

    def _group_events_by_date(self, events: List) -> Dict[str, int]:
        """Agrupar eventos por fecha"""
        date_counts = defaultdict(int)
        for event in events:
            date_str = event.timestamp.date().isoformat()
            date_counts[date_str] += 1
        return dict(date_counts)

    def _calculate_supply_chain_progress(self, events: List) -> Dict:
        """Calcular progreso de la cadena de suministro"""
        # Definir etapas del proceso
        stages = {
            'producer_init': ['PRODUCER_INIT'],
            'reception': ['RECEPCIÓN'],
            'quality_control': ['CALIDAD'],
            'processing': ['DRYING', 'FERMENTATION', 'STORAGE'],
            'export': ['EXPORT_PREPARATION', 'CUSTOMS_CLEARANCE', 'SHIPMENT']
        }

        progress = {}
        for stage, event_types in stages.items():
            stage_events = [e for e in events if e.event_type in event_types]
            progress[stage] = {
                'events': len(stage_events),
                'unique_batches': len(set(e.batch_nft_id for e in stage_events if e.batch_nft_id))
            }

        return progress

    @cached(timeout=600, key_prefix="analytics")
    def get_financial_analytics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict:
        """Obtener análisis financiero"""
        if not start_date:
            start_date = date.today() - timedelta(days=90)
        if not end_date:
            end_date = date.today()

        analytics = {
            'revenue': {},
            'costs': {},
            'profitability': {},
            'price_trends': {},
            'market_insights': {}
        }

        # Análisis de ingresos
        fixations = ContractFixation.query.filter(
            ContractFixation.fixation_date >= start_date,
            ContractFixation.fixation_date <= end_date
        ).all()

        if fixations:
            total_revenue = sum(float(f.total_value_usd) for f in fixations if f.total_value_usd)
            analytics['revenue'] = {
                'total_usd': total_revenue,
                'avg_per_fixation': total_revenue / len(fixations),
                'by_month': self._group_revenue_by_month(fixations),
                'by_product_type': self._group_revenue_by_product(fixations)
            }

        # Tendencias de precios
        price_data = []
        for f in fixations:
            if f.spot_price_usd:
                price_data.append({
                    'date': f.fixation_date,
                    'price': float(f.spot_price_usd),
                    'product_type': f.export_contract.product_type if f.export_contract else 'Unknown'
                })

        if price_data:
            df = pd.DataFrame(price_data)
            analytics['price_trends'] = {
                'avg_price': df['price'].mean(),
                'price_volatility': df['price'].std(),
                'price_range': {
                    'min': df['price'].min(),
                    'max': df['price'].max()
                },
                'by_product': df.groupby('product_type')['price'].agg(['mean', 'std', 'count']).to_dict()
            }

        # Insights de mercado
        analytics['market_insights'] = self._calculate_market_insights(fixations)

        return analytics

    def _group_revenue_by_month(self, fixations: List) -> Dict:
        """Agrupar ingresos por mes"""
        monthly_revenue = defaultdict(float)
        for f in fixations:
            if f.fixation_date and f.total_value_usd:
                month_key = f.fixation_date.strftime('%Y-%m')
                monthly_revenue[month_key] += float(f.total_value_usd)
        return dict(monthly_revenue)

    def _group_revenue_by_product(self, fixations: List) -> Dict:
        """Agrupar ingresos por tipo de producto"""
        product_revenue = defaultdict(float)
        for f in fixations:
            if f.export_contract and f.total_value_usd:
                product_type = f.export_contract.product_type or 'Unknown'
                product_revenue[product_type] += float(f.total_value_usd)
        return dict(product_revenue)

    def _calculate_market_insights(self, fixations: List) -> Dict:
        """Calcular insights de mercado"""
        insights = {
            'top_buyers': [],
            'price_distribution': {},
            'seasonal_patterns': {},
            'quality_premium': {}
        }

        if not fixations:
            return insights

        # Top compradores
        buyer_revenue = defaultdict(float)
        for f in fixations:
            if f.export_contract and f.export_contract.buyer_company and f.total_value_usd:
                buyer_name = f.export_contract.buyer_company.name
                buyer_revenue[buyer_name] += float(f.total_value_usd)

        insights['top_buyers'] = sorted(
            [{'buyer': k, 'revenue_usd': v} for k, v in buyer_revenue.items()],
            key=lambda x: x['revenue_usd'],
            reverse=True
        )[:10]

        # Distribución de precios
        prices = [float(f.spot_price_usd) for f in fixations if f.spot_price_usd]
        if prices:
            insights['price_distribution'] = {
                'quartiles': {
                    '25': np.percentile(prices, 25),
                    '50': np.percentile(prices, 50),
                    '75': np.percentile(prices, 75)
                },
                'outliers': {
                    'low': np.percentile(prices, 5),
                    'high': np.percentile(prices, 95)
                }
            }

        return insights

    @cached(timeout=300, key_prefix="analytics")
    def get_quality_analytics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict:
        """Obtener análisis de calidad"""
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        analytics = {
            'quality_distribution': {},
            'defect_rates': {},
            'processing_efficiency': {},
            'certification_status': {}
        }

        # Análisis de lotes por calidad
        lots = ProducerLot.query.filter(
            ProducerLot.created_at >= start_date,
            ProducerLot.created_at <= end_date
        ).all()

        if lots:
            quality_grades = Counter(l.quality_grade for l in lots if l.quality_grade)
            analytics['quality_distribution'] = dict(quality_grades)

            # Eficiencia de procesamiento
            fermentation_days = [l.fermentation_days for l in lots if l.fermentation_days]
            if fermentation_days:
                analytics['processing_efficiency'] = {
                    'avg_fermentation_days': np.mean(fermentation_days),
                    'fermentation_range': {
                        'min': min(fermentation_days),
                        'max': max(fermentation_days)
                    }
                }

        # Análisis de eventos de calidad
        quality_events = TraceEvent.query.filter(
            TraceEvent.timestamp >= start_date,
            TraceEvent.timestamp <= end_date,
            TraceEvent.event_type == 'CALIDAD'
        ).all()

        if quality_events:
            # Analizar mediciones de calidad
            defect_rates = []
            for event in quality_events:
                if event.measurements:
                    measurements = json.loads(event.measurements) if isinstance(event.measurements, str) else event.measurements
                    if 'defect_rate' in measurements:
                        defect_rates.append(float(measurements['defect_rate']))

            if defect_rates:
                analytics['defect_rates'] = {
                    'avg_defect_rate': np.mean(defect_rates),
                    'defect_rate_range': {
                        'min': min(defect_rates),
                        'max': max(defect_rates)
                    },
                    'acceptable_rate': len([r for r in defect_rates if r <= 5.0]) / len(defect_rates) * 100
                }

        return analytics

    def get_real_time_metrics(self) -> Dict:
        """Obtener métricas en tiempo real"""
        # Obtener métricas del monitor de rendimiento
        performance_metrics = self.performance_monitor.get_system_metrics()

        # Métricas de negocio en tiempo real
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Contratos de hoy
        today_contracts = ExportContract.query.filter(
            ExportContract.created_at >= today_start
        ).count()

        # Fijaciones de hoy
        today_fixations = ContractFixation.query.filter(
            ContractFixation.created_at >= today_start
        ).count()

        # Eventos de trazabilidad de hoy
        today_events = TraceEvent.query.filter(
            TraceEvent.timestamp >= today_start
        ).count()

        return {
            'timestamp': now.isoformat(),
            'performance': performance_metrics,
            'business_today': {
                'contracts_created': today_contracts,
                'fixations_created': today_fixations,
                'trace_events_created': today_events
            },
            'system_health': {
                'database_status': 'healthy',  # Simplificado
                'blockchain_status': 'connected' if get_blockchain_integration() else 'disconnected',
                'cache_status': 'available' if performance_monitor.redis_client else 'unavailable'
            }
        }

    def calculate_contract_metrics(self, contracts: List[Dict]) -> Dict:
        """Calcular métricas de contratos"""
        if not contracts:
            return {
                'total_contracts': 0,
                'total_quantity_mt': 0,
                'total_fixed_mt': 0,
                'total_remaining_mt': 0,
                'total_value_usd': 0,
                'avg_contract_value': 0,
                'fixation_rate': 0
            }

        total_quantity = sum(c.get('total_quantity_mt', 0) for c in contracts)
        total_fixed = sum(c.get('fixed_quantity_mt', 0) for c in contracts)
        total_value = sum(c.get('contract_value_usd', 0) for c in contracts)

        return {
            'total_contracts': len(contracts),
            'total_quantity_mt': total_quantity,
            'total_fixed_mt': total_fixed,
            'total_remaining_mt': total_quantity - total_fixed,
            'total_value_usd': total_value,
            'avg_contract_value': total_value / len(contracts) if contracts else 0,
            'fixation_rate': total_fixed / total_quantity if total_quantity > 0 else 0
        }

    def calculate_fixation_metrics(self, fixations: List[Dict]) -> Dict:
        """Calcular métricas de fijaciones"""
        if not fixations:
            return {
                'total_fixations': 0,
                'total_fixed_quantity_mt': 0,
                'avg_fixation_price': 0,
                'total_fixation_value': 0,
                'fixation_timeline': {}
            }

        total_quantity = sum(f.get('fixed_quantity_mt', 0) for f in fixations)
        prices = [f.get('fixed_price_usd_per_mt', 0) for f in fixations if f.get('fixed_price_usd_per_mt', 0) > 0]
        avg_price = sum(prices) / len(prices) if prices else 0
        total_value = sum(f.get('fixed_quantity_mt', 0) * f.get('fixed_price_usd_per_mt', 0) for f in fixations)

        # Timeline de fijaciones
        timeline = {}
        for f in fixations:
            date_str = f.get('fixation_date', '')
            if date_str:
                if date_str not in timeline:
                    timeline[date_str] = 0
                timeline[date_str] += f.get('fixed_quantity_mt', 0)

        return {
            'total_fixations': len(fixations),
            'total_fixed_quantity_mt': total_quantity,
            'avg_fixation_price': avg_price,
            'total_fixation_value': total_value,
            'fixation_timeline': timeline
        }

    def calculate_market_trends(self, price_data: List[Dict]) -> Dict:
        """Calcular tendencias de mercado"""
        if not price_data:
            return {
                'current_price': 0,
                'price_change_24h': 0,
                'price_change_7d': 0,
                'volatility': 0,
                'trend_direction': 'stable'
            }

        # Ordenar por fecha
        sorted_data = sorted(price_data, key=lambda x: x['date'])

        current_price = sorted_data[-1]['price']
        previous_price = sorted_data[-2]['price'] if len(sorted_data) > 1 else current_price

        # Cambio 24h (último vs penúltimo)
        price_change_24h = current_price - previous_price

        # Cambio 7d (último vs hace 7 días)
        week_ago_index = max(0, len(sorted_data) - 7)
        week_ago_price = sorted_data[week_ago_index]['price']
        price_change_7d = current_price - week_ago_price

        # Volatilidad (desviación estándar)
        prices = [p['price'] for p in sorted_data]
        volatility = np.std(prices) if len(prices) > 1 else 0

        # Dirección de tendencia
        if price_change_7d > 10:
            trend_direction = 'upward'
        elif price_change_7d < -10:
            trend_direction = 'downward'
        else:
            trend_direction = 'stable'

        return {
            'current_price': current_price,
            'price_change_24h': price_change_24h,
            'price_change_7d': price_change_7d,
            'volatility': volatility,
            'trend_direction': trend_direction
        }

    def generate_performance_report(self, contracts: List[Dict], fixations: List[Dict], market_data: List[Dict]) -> Dict:
        """Generar reporte de rendimiento completo"""
        contract_metrics = self.calculate_contract_metrics(contracts)
        fixation_metrics = self.calculate_fixation_metrics(fixations)
        market_trends = self.calculate_market_trends(market_data)

        return {
            'contract_metrics': contract_metrics,
            'fixation_metrics': fixation_metrics,
            'market_trends': market_trends,
            'generated_at': datetime.utcnow().isoformat(),
            'period': 'custom'
        }

# Instancia global del motor de análisis
analytics_engine = AnalyticsEngine()

class AnalyticsCache:
    """Sistema de cache para analytics"""

    def __init__(self):
        self.cache = {}
        self.expiration_times = {}

    def set(self, key: str, value: Any, ttl: int = 300):
        """Almacenar valor en cache con TTL"""
        self.cache[key] = value
        self.expiration_times[key] = datetime.utcnow() + timedelta(seconds=ttl)

    def get(self, key: str) -> Optional[Any]:
        """Obtener valor del cache si no ha expirado"""
        if key in self.cache:
            if datetime.utcnow() < self.expiration_times[key]:
                return self.cache[key]
            else:
                # Expirado, eliminar
                del self.cache[key]
                del self.expiration_times[key]
        return None

    def delete(self, key: str):
        """Eliminar clave del cache"""
        if key in self.cache:
            del self.cache[key]
        if key in self.expiration_times:
            del self.expiration_times[key]

    def clear(self):
        """Limpiar todo el cache"""
        self.cache.clear()
        self.expiration_times.clear()

    def get_stats(self) -> Dict:
        """Obtener estadísticas del cache"""
        now = datetime.utcnow()
        expired_keys = [k for k, exp in self.expiration_times.items() if now >= exp]

        # Limpiar expirados
        for key in expired_keys:
            self.delete(key)

        return {
            'total_keys': len(self.cache),
            'expired_keys_cleaned': len(expired_keys)
        }

# Instancia global del cache de analytics
analytics_cache = AnalyticsCache()

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

@analytics_bp.route('/dashboard/overview', methods=['GET'])
@jwt_required()
def get_dashboard_overview():
    """Obtener vista general del dashboard"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        # Parámetros de fecha
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        start_date = date.fromisoformat(start_date_str) if start_date_str else None
        end_date = date.fromisoformat(end_date_str) if end_date_str else None

        # Obtener métricas principales
        supply_chain = analytics_engine.get_supply_chain_metrics(start_date, end_date)
        financial = analytics_engine.get_financial_analytics(start_date, end_date)
        quality = analytics_engine.get_quality_analytics(start_date, end_date)
        real_time = analytics_engine.get_real_time_metrics()

        return jsonify({
            'supply_chain': supply_chain,
            'financial': financial,
            'quality': quality,
            'real_time': real_time,
            'period': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            }
        })

    except Exception as e:
        logger.error(f"Error getting dashboard overview: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@analytics_bp.route('/reports/supply-chain', methods=['GET'])
@jwt_required()
def get_supply_chain_report():
    """Obtener reporte detallado de cadena de suministro"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        start_date = date.fromisoformat(start_date_str) if start_date_str else date.today() - timedelta(days=30)
        end_date = date.fromisoformat(end_date_str) if end_date_str else date.today()

        metrics = analytics_engine.get_supply_chain_metrics(start_date, end_date)

        # Generar insights adicionales
        insights = []

        # Analizar eficiencia de la cadena
        if metrics['traceability']['supply_chain_stages']:
            stages = metrics['traceability']['supply_chain_stages']
            total_batches = sum(stage['unique_batches'] for stage in stages.values())

            if total_batches > 0:
                completion_rate = stages.get('export', {}).get('unique_batches', 0) / total_batches * 100
                insights.append({
                    'type': 'supply_chain_efficiency',
                    'title': 'Tasa de Completación de Cadena de Suministro',
                    'value': f"{completion_rate:.1f}%",
                    'description': f"{stages.get('export', {}).get('unique_batches', 0)} de {total_batches} lotes han completado el proceso de exportación"
                })

        # Analizar volumen por producto
        if metrics['contracts']['by_product_type']:
            top_product = max(metrics['contracts']['by_product_type'].items(), key=lambda x: x[1])
            insights.append({
                'type': 'product_dominance',
                'title': 'Producto Principal',
                'value': top_product[0],
                'description': f"{top_product[1]} contratos representan el producto más comercializado"
            })

        return jsonify({
            'metrics': metrics,
            'insights': insights,
            'generated_at': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting supply chain report: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@analytics_bp.route('/reports/financial', methods=['GET'])
@jwt_required()
def get_financial_report():
    """Obtener reporte financiero detallado"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        start_date = date.fromisoformat(start_date_str) if start_date_str else date.today() - timedelta(days=90)
        end_date = date.fromisoformat(end_date_str) if end_date_str else date.today()

        analytics = analytics_engine.get_financial_analytics(start_date, end_date)

        # Generar recomendaciones financieras
        recommendations = []

        if analytics.get('price_trends', {}).get('price_volatility', 0) > 100:
            recommendations.append({
                'type': 'risk_management',
                'priority': 'high',
                'title': 'Alta Volatilidad de Precios',
                'description': 'Considere estrategias de cobertura para mitigar riesgos de precio',
                'action': 'Implementar contratos de futuros o opciones'
            })

        if analytics.get('market_insights', {}).get('top_buyers'):
            top_buyers = analytics['market_insights']['top_buyers'][:3]
            recommendations.append({
                'type': 'relationship_building',
                'priority': 'medium',
                'title': 'Enfoque en Compradores Principales',
                'description': f"Los 3 principales compradores representan {sum(b['revenue_usd'] for b in top_buyers):.0f} USD en ingresos",
                'action': 'Desarrollar relaciones estratégicas con estos compradores'
            })

        return jsonify({
            'analytics': analytics,
            'recommendations': recommendations,
            'generated_at': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting financial report: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@analytics_bp.route('/reports/quality', methods=['GET'])
@jwt_required()
def get_quality_report():
    """Obtener reporte de calidad detallado"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        start_date = date.fromisoformat(start_date_str) if start_date_str else date.today() - timedelta(days=30)
        end_date = date.fromisoformat(end_date_str) if end_date_str else date.today()

        analytics = analytics_engine.get_quality_analytics(start_date, end_date)

        # Generar alertas de calidad
        alerts = []

        if analytics.get('defect_rates', {}).get('avg_defect_rate', 0) > 7.0:
            alerts.append({
                'level': 'high',
                'type': 'quality_issue',
                'title': 'Tasa de Defectos Elevada',
                'description': f"Tasa promedio de defectos: {analytics['defect_rates']['avg_defect_rate']:.1f}%",
                'recommendation': 'Revisar procesos de fermentación y secado'
            })

        if analytics.get('processing_efficiency', {}).get('avg_fermentation_days', 0) > 7:
            alerts.append({
                'level': 'medium',
                'type': 'efficiency_issue',
                'title': 'Tiempo de Fermentación Excesivo',
                'description': f"Tiempo promedio de fermentación: {analytics['processing_efficiency']['avg_fermentation_days']:.1f} días",
                'recommendation': 'Optimizar condiciones de fermentación'
            })

        return jsonify({
            'analytics': analytics,
            'alerts': alerts,
            'generated_at': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting quality report: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@analytics_bp.route('/real-time', methods=['GET'])
@jwt_required()
def get_real_time_data():
    """Obtener datos en tiempo real"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        # Datos en tiempo real
        real_time_data = analytics_engine.get_real_time_metrics()

        # Eventos recientes (últimas 24 horas)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_events = TraceEvent.query.filter(
            TraceEvent.timestamp >= yesterday
        ).order_by(TraceEvent.timestamp.desc()).limit(10).all()

        recent_events_data = []
        for event in recent_events:
            recent_events_data.append({
                'id': event.id,
                'event_type': event.event_type,
                'timestamp': event.timestamp.isoformat(),
                'batch_nft_id': event.batch_nft_id,
                'producer_company': event.producer_company.name if event.producer_company else None
            })

        # Alertas activas
        alerts = []

        # Verificar contratos próximos a vencer
        expiring_contracts = ExportContract.query.filter(
            ExportContract.end_date <= date.today() + timedelta(days=30),
            ExportContract.end_date >= date.today(),
            ExportContract.status == 'active'
        ).count()

        if expiring_contracts > 0:
            alerts.append({
                'type': 'contract_expiry',
                'level': 'medium',
                'message': f"{expiring_contracts} contratos vencerán en los próximos 30 días",
                'action_required': True
            })

        return jsonify({
            'real_time_data': real_time_data,
            'recent_events': recent_events_data,
            'alerts': alerts,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting real time data: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@analytics_bp.route('/contracts', methods=['GET'])
@jwt_required()
def get_contract_analytics():
    """Obtener analytics de contratos"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        # Obtener contratos del usuario
        contracts = get_contracts_cached()  # Usar función cacheada

        # Calcular métricas
        metrics = analytics_engine.calculate_contract_metrics(contracts)

        return jsonify({'metrics': metrics})

    except Exception as e:
        logger.error(f"Error getting contract analytics: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@analytics_bp.route('/fixations', methods=['GET'])
@jwt_required()
def get_fixation_analytics():
    """Obtener analytics de fijaciones"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        # Obtener fijaciones
        fixations = get_fixations_cached()  # Usar función cacheada

        # Calcular métricas
        metrics = analytics_engine.calculate_fixation_metrics(fixations)

        return jsonify({'metrics': metrics})

    except Exception as e:
        logger.error(f"Error getting fixation analytics: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@cached(timeout=300, key_prefix="market_prices")
def get_market_price_data(period: str = '7d') -> List[Dict]:
    """Obtener datos de precios de mercado (simulado)"""
    # En una implementación real, esto obtendría datos de APIs externas
    # Por ahora, devolver datos simulados
    base_price = 500
    days = 7 if period == '7d' else 30

    data = []
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=i)).date()
        # Simular variación de precio
        variation = (i % 10 - 5) * 2  # -10 a +10
        price = base_price + variation

        data.append({
            'date': date.isoformat(),
            'price': price
        })

    return data

@analytics_bp.route('/market/trends', methods=['GET'])
@jwt_required()
def get_market_trends():
    """Obtener tendencias de mercado"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        period = request.args.get('period', '7d')

        # Validar período
        valid_periods = ['1d', '7d', '30d', '90d']
        if period not in valid_periods:
            return jsonify({'error': 'Período no válido. Use: 1d, 7d, 30d, 90d'}), 400

        # Obtener datos de precios
        price_data = get_market_price_data(period)

        # Calcular tendencias
        trends = analytics_engine.calculate_market_trends(price_data)

        return jsonify(trends)

    except Exception as e:
        logger.error(f"Error getting market trends: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@analytics_bp.route('/reports/generate', methods=['POST'])
@jwt_required()
def generate_analytics_report():
    """Generar reporte de analytics"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        data = request.get_json()
        report_type = data.get('report_type')
        period = data.get('period', 'monthly')

        if not report_type:
            return jsonify({'error': 'Tipo de reporte requerido'}), 400

        valid_types = ['performance', 'financial', 'supply_chain', 'quality']
        if report_type not in valid_types:
            return jsonify({'error': f'Tipo de reporte no válido. Use: {", ".join(valid_types)}'}), 400

        # Obtener datos según el tipo de reporte
        if report_type == 'performance':
            contracts = get_contracts_cached()
            fixations = get_fixations_cached()
            market_data = get_market_price_data('30d')

            report = analytics_engine.generate_performance_report(contracts, fixations, market_data)

        elif report_type == 'financial':
            report = analytics_engine.get_financial_analytics()

        elif report_type == 'supply_chain':
            report = analytics_engine.get_supply_chain_metrics()

        elif report_type == 'quality':
            report = analytics_engine.get_quality_analytics()

        return jsonify(report)

    except Exception as e:
        logger.error(f"Error generating analytics report: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@analytics_bp.route('/cache/stats', methods=['GET'])
@jwt_required()
def get_analytics_cache_stats():
    """Obtener estadísticas del cache de analytics"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para ver estadísticas de cache'}), 403

        # Obtener estadísticas del cache
        stats = analytics_cache.get_stats()

        return jsonify(stats)

    except Exception as e:
        logger.error(f"Error getting analytics cache stats: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@analytics_bp.route('/cache/clear', methods=['POST'])
@jwt_required()
def clear_analytics_cache():
    """Limpiar cache de analytics"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para limpiar cache'}), 403

        # Limpiar cache
        analytics_cache.clear()

        return jsonify({'message': 'Cache de analytics limpiado exitosamente'})

    except Exception as e:
        logger.error(f"Error clearing analytics cache: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
@jwt_required()
def export_analytics_report(report_type):
    """Exportar reporte analítico"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if report_type not in ['supply_chain', 'financial', 'quality']:
            return jsonify({'error': 'Tipo de reporte no válido'}), 400

        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        format_type = request.args.get('format', 'json')  # json, csv

        start_date = date.fromisoformat(start_date_str) if start_date_str else date.today() - timedelta(days=30)
        end_date = date.fromisoformat(end_date_str) if end_date_str else date.today()

        # Obtener datos según el tipo de reporte
        if report_type == 'supply_chain':
            data = analytics_engine.get_supply_chain_metrics(start_date, end_date)
        elif report_type == 'financial':
            data = analytics_engine.get_financial_analytics(start_date, end_date)
        elif report_type == 'quality':
            data = analytics_engine.get_quality_analytics(start_date, end_date)

        if format_type == 'csv':
            # Convertir a CSV (simplificado)
            csv_data = json.dumps(data, default=str)
            return jsonify({
                'format': 'csv',
                'data': csv_data,
                'filename': f'{report_type}_report_{start_date}_{end_date}.csv'
            })
        else:
            return jsonify({
                'report_type': report_type,
                'data': data,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'exported_at': datetime.utcnow().isoformat()
            })

    except Exception as e:
        logger.error(f"Error exporting analytics report: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
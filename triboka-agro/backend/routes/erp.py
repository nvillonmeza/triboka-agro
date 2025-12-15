"""
Módulo ERP - Integración con sistemas contables
Permite sincronizar datos con sistemas ERP externos
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json
import logging
import requests
from typing import Dict, List, Optional, Any

from models_simple import db, ExportContract, ContractFixation, ProducerLot, BatchNFT, Company, User
from blockchain_service import get_blockchain_integration

logger = logging.getLogger(__name__)

erp_bp = Blueprint('erp', __name__)

# Configuración de sistemas ERP soportados
ERP_SYSTEMS = {
    'sap': {
        'name': 'SAP Business One',
        'api_version': 'v1',
        'endpoints': {
            'companies': '/b1s/v1/BusinessPartners',
            'items': '/b1s/v1/Items',
            'orders': '/b1s/v1/Orders',
            'invoices': '/b1s/v1/Invoices'
        }
    },
    'dynamics': {
        'name': 'Microsoft Dynamics 365',
        'api_version': 'v9.2',
        'endpoints': {
            'companies': '/api/data/v9.2/accounts',
            'items': '/api/data/v9.2/products',
            'orders': '/api/data/v9.2/salesorders',
            'invoices': '/api/data/v9.2/invoices'
        }
    },
    'oracle': {
        'name': 'Oracle ERP Cloud',
        'api_version': 'v1',
        'endpoints': {
            'companies': '/fscmRestApi/resources/11.13.18.05/suppliers',
            'items': '/fscmRestApi/resources/11.13.18.05/items',
            'orders': '/fscmRestApi/resources/11.13.18.05/procurementOrders',
            'invoices': '/fscmRestApi/resources/11.13.18.05/invoices'
        }
    },
    'custom': {
        'name': 'Sistema ERP Personalizado',
        'api_version': 'v1',
        'endpoints': {
            'companies': '/api/companies',
            'items': '/api/items',
            'orders': '/api/orders',
            'invoices': '/api/invoices'
        }
    }
}

class ERPConnector:
    """Conector genérico para sistemas ERP"""

    def __init__(self, system_type: str, config: Dict[str, Any]):
        self.system_type = system_type
        self.config = config
        self.base_url = config.get('base_url', '').rstrip('/')
        self.api_key = config.get('api_key')
        self.username = config.get('username')
        self.password = config.get('password')
        self.session = requests.Session()

        # Configurar autenticación
        self._setup_auth()

    def _setup_auth(self):
        """Configurar autenticación según el tipo de sistema"""
        if self.system_type == 'sap':
            # SAP Business One usa Basic Auth
            if self.username and self.password:
                self.session.auth = (self.username, self.password)
        elif self.system_type == 'dynamics':
            # Dynamics 365 usa Bearer token
            if self.api_key:
                self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})
        elif self.system_type == 'oracle':
            # Oracle usa Basic Auth con API keys
            if self.username and self.password:
                self.session.auth = (self.username, self.password)
        else:
            # Sistema personalizado
            if self.api_key:
                self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})

    def test_connection(self) -> bool:
        """Probar conexión con el sistema ERP"""
        try:
            # Intentar una petición simple para verificar conectividad
            test_url = f"{self.base_url}/health" if self.system_type != 'sap' else f"{self.base_url}/b1s/v1/Login"
            response = self.session.get(test_url, timeout=10)

            if self.system_type == 'sap':
                # SAP devuelve 200 incluso si las credenciales son inválidas
                return response.status_code in [200, 401]
            else:
                return response.status_code == 200

        except Exception as e:
            logger.error(f"Error testing ERP connection: {str(e)}")
            return False

    def sync_company(self, company_data: Dict) -> Optional[Dict]:
        """Sincronizar datos de empresa"""
        try:
            endpoint = ERP_SYSTEMS[self.system_type]['endpoints']['companies']
            url = f"{self.base_url}{endpoint}"

            # Mapear datos según el sistema ERP
            mapped_data = self._map_company_data(company_data)

            response = self.session.post(url, json=mapped_data, timeout=30)

            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Error syncing company: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error syncing company: {str(e)}")
            return None

    def sync_contract(self, contract_data: Dict) -> Optional[Dict]:
        """Sincronizar datos de contrato"""
        try:
            endpoint = ERP_SYSTEMS[self.system_type]['endpoints']['orders']
            url = f"{self.base_url}{endpoint}"

            # Mapear datos según el sistema ERP
            mapped_data = self._map_contract_data(contract_data)

            response = self.session.post(url, json=mapped_data, timeout=30)

            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Error syncing contract: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error syncing contract: {str(e)}")
            return None

    def sync_fixation(self, fixation_data: Dict) -> Optional[Dict]:
        """Sincronizar datos de fijación"""
        try:
            endpoint = ERP_SYSTEMS[self.system_type]['endpoints']['invoices']
            url = f"{self.base_url}{endpoint}"

            # Mapear datos según el sistema ERP
            mapped_data = self._map_fixation_data(fixation_data)

            response = self.session.post(url, json=mapped_data, timeout=30)

            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Error syncing fixation: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error syncing fixation: {str(e)}")
            return None

    def sync_companies(self, companies_data: List[Dict]) -> Dict:
        """Sincronizar múltiples empresas"""
        results = []
        errors = []

        for company_data in companies_data:
            try:
                result = self.sync_company(company_data)
                if result:
                    results.append(result)
                else:
                    errors.append({'company': company_data.get('name', 'Unknown'), 'error': 'Sync failed'})
            except Exception as e:
                errors.append({'company': company_data.get('name', 'Unknown'), 'error': str(e)})

        return {
            'synced': len(results),
            'errors': len(errors),
            'results': results,
            'failed': errors
        }

    def sync_contracts(self, contracts_data: List[Dict]) -> Dict:
        """Sincronizar múltiples contratos"""
        results = []
        errors = []

        for contract_data in contracts_data:
            try:
                result = self.sync_contract(contract_data)
                if result:
                    results.append(result)
                else:
                    errors.append({'contract': contract_data.get('contract_code', 'Unknown'), 'error': 'Sync failed'})
            except Exception as e:
                errors.append({'contract': contract_data.get('contract_code', 'Unknown'), 'error': str(e)})

        return {
            'synced': len(results),
            'errors': len(errors),
            'results': results,
            'failed': errors
        }

    def sync_fixations(self, fixations_data: List[Dict]) -> Dict:
        """Sincronizar múltiples fijaciones"""
        results = []
        errors = []

        for fixation_data in fixations_data:
            try:
                result = self.sync_fixation(fixation_data)
                if result:
                    results.append(result)
                else:
                    errors.append({'fixation': fixation_data.get('id', 'Unknown'), 'error': 'Sync failed'})
            except Exception as e:
                errors.append({'fixation': fixation_data.get('id', 'Unknown'), 'error': str(e)})

        return {
            'synced': len(results),
            'errors': len(errors),
            'results': results,
            'failed': errors
        }

    def _map_company_data(self, company_data: Dict) -> Dict:
        """Mapear datos de empresa según el sistema ERP"""
        if self.system_type == 'sap':
            return {
                'CardCode': company_data.get('erp_code', company_data['name'][:15]),
                'CardName': company_data['name'],
                'CardType': 'cSupplier' if company_data.get('company_type') == 'producer' else 'cCustomer',
                'Address': company_data.get('address', ''),
                'Phone1': company_data.get('phone', ''),
                'EmailAddress': company_data.get('email', ''),
                'FederalTaxID': company_data.get('tax_id', '')
            }
        elif self.system_type == 'dynamics':
            return {
                'name': company_data['name'],
                'accounttypecode': 3 if company_data.get('company_type') == 'producer' else 1,  # Vendor or Customer
                'telephone1': company_data.get('phone', ''),
                'emailaddress1': company_data.get('email', ''),
                'address1_line1': company_data.get('address', ''),
                'address1_city': company_data.get('city', ''),
                'address1_country': company_data.get('country', '')
            }
        else:
            # Mapeo genérico
            return company_data

    def _map_contract_data(self, contract_data: Dict) -> Dict:
        """Mapear datos de contrato según el sistema ERP"""
        if self.system_type == 'sap':
            return {
                'DocType': 'dDocument_Items',
                'CardCode': contract_data.get('buyer_erp_code', contract_data['buyer_company']),
                'DocDate': contract_data['start_date'][:10],
                'DocDueDate': contract_data['end_date'][:10],
                'Comments': f"Contrato {contract_data['contract_code']} - {contract_data['product_type']}",
                'DocumentLines': [{
                    'ItemCode': contract_data.get('product_erp_code', contract_data['product_type']),
                    'Quantity': contract_data['total_volume_mt'],
                    'UnitPrice': contract_data.get('differential_usd', 0),
                    'WarehouseCode': contract_data.get('warehouse_code', '01')
                }]
            }
        elif self.system_type == 'dynamics':
            return {
                'name': f"Contrato {contract_data['contract_code']}",
                'customerid@odata.bind': f"/accounts({contract_data.get('buyer_erp_id', 1)})",
                'description': f"Contrato de exportación - {contract_data['product_type']}",
                'totalamount': contract_data.get('total_value_usd', 0),
                'statuscode': 1  # Active
            }
        else:
            # Mapeo genérico
            return contract_data

    def _map_fixation_data(self, fixation_data: Dict) -> Dict:
        """Mapear datos de fijación según el sistema ERP"""
        if self.system_type == 'sap':
            return {
                'DocType': 'dDocument_Items',
                'CardCode': fixation_data.get('buyer_erp_code', fixation_data['buyer_company']),
                'DocDate': fixation_data['fixation_date'][:10],
                'Comments': f"Fijación {fixation_data['contract_code']} - {fixation_data['fixed_quantity_mt']}MT",
                'DocumentLines': [{
                    'ItemCode': fixation_data.get('product_erp_code', fixation_data['product_type']),
                    'Quantity': fixation_data['fixed_quantity_mt'],
                    'UnitPrice': fixation_data['spot_price_usd'] + fixation_data.get('differential_usd', 0),
                    'WarehouseCode': fixation_data.get('warehouse_code', '01')
                }]
            }
        elif self.system_type == 'dynamics':
            return {
                'name': f"Fijación {fixation_data['contract_code']}",
                'customerid@odata.bind': f"/accounts({fixation_data.get('buyer_erp_id', 1)})",
                'description': f"Fijación de precio - {fixation_data['fixed_quantity_mt']}MT",
                'totalamount': fixation_data['total_value_usd'],
                'statuscode': 1  # Active
            }
        else:
            # Mapeo genérico
            return fixation_data

# Instancia global de conectores ERP
erp_connectors = {}

@erp_bp.route('/systems', methods=['GET'])
@jwt_required()
def get_erp_systems():
    """Obtener lista de sistemas ERP soportados"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para gestionar sistemas ERP'}), 403

        return jsonify({
            'systems': ERP_SYSTEMS,
            'supported_systems': list(ERP_SYSTEMS.keys())
        })

    except Exception as e:
        logger.error(f"Error getting ERP systems: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@erp_bp.route('/connections', methods=['GET'])
@jwt_required()
def get_erp_connections():
    """Obtener conexiones ERP configuradas"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para gestionar conexiones ERP'}), 403

        # En una implementación real, estas conexiones se almacenarían en BD
        # Por ahora, devolver configuración de ejemplo
        connections = [
            {
                'id': 'sap_prod',
                'system_type': 'sap',
                'name': 'SAP Producción',
                'base_url': 'https://sap.company.com',
                'status': 'configured',
                'last_sync': '2024-11-13T10:30:00Z'
            },
            {
                'id': 'dynamics_test',
                'system_type': 'dynamics',
                'name': 'Dynamics Test',
                'base_url': 'https://dynamics.company.com',
                'status': 'configured',
                'last_sync': '2024-11-12T15:45:00Z'
            }
        ]

        return jsonify({'connections': connections})

    except Exception as e:
        logger.error(f"Error getting ERP connections: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@erp_bp.route('/connections', methods=['POST'])
@jwt_required()
def create_erp_connection():
    """Crear nueva conexión ERP"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para gestionar conexiones ERP'}), 403

        data = request.get_json()

        required_fields = ['system_type', 'name', 'base_url']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400

        system_type = data['system_type']
        if system_type not in ERP_SYSTEMS:
            return jsonify({'error': f'Sistema ERP no soportado: {system_type}'}), 400

        # Crear configuración del conector
        config = {
            'base_url': data['base_url'],
            'api_key': data.get('api_key'),
            'username': data.get('username'),
            'password': data.get('password')
        }

        # Probar conexión
        connector = ERPConnector(system_type, config)
        if not connector.test_connection():
            return jsonify({'error': 'No se pudo conectar al sistema ERP'}), 400

        # Almacenar conector (en producción, guardar en BD)
        connection_id = f"{system_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        erp_connectors[connection_id] = connector

        return jsonify({
            'message': 'Conexión ERP creada exitosamente',
            'connection_id': connection_id,
            'system_type': system_type,
            'status': 'connected'
        }), 201

    except Exception as e:
        logger.error(f"Error creating ERP connection: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@erp_bp.route('/sync/company/<int:company_id>', methods=['POST'])
@jwt_required()
def sync_company_to_erp(company_id):
    """Sincronizar empresa con sistema ERP"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para sincronizar con ERP'}), 403

        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Empresa no encontrada'}), 404

        data = request.get_json()
        connection_id = data.get('connection_id')

        if not connection_id or connection_id not in erp_connectors:
            return jsonify({'error': 'Conexión ERP no encontrada'}), 400

        connector = erp_connectors[connection_id]

        # Preparar datos de la empresa
        company_data = {
            'id': company.id,
            'name': company.name,
            'company_type': company.company_type,
            'email': company.email,
            'country': company.country,
            'blockchain_address': company.blockchain_address
        }

        # Sincronizar
        result = connector.sync_company(company_data)

        if result:
            return jsonify({
                'message': 'Empresa sincronizada exitosamente con ERP',
                'erp_response': result
            })
        else:
            return jsonify({'error': 'Error sincronizando con ERP'}), 500

    except Exception as e:
        logger.error(f"Error syncing company to ERP: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@erp_bp.route('/sync/contract/<int:contract_id>', methods=['POST'])
@jwt_required()
def sync_contract_to_erp(contract_id):
    """Sincronizar contrato con sistema ERP"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para sincronizar con ERP'}), 403

        contract = ExportContract.query.get(contract_id)
        if not contract:
            return jsonify({'error': 'Contrato no encontrado'}), 404

        data = request.get_json()
        connection_id = data.get('connection_id')

        if not connection_id or connection_id not in erp_connectors:
            return jsonify({'error': 'Conexión ERP no encontrada'}), 400

        connector = erp_connectors[connection_id]

        # Preparar datos del contrato
        contract_data = {
            'contract_id': contract.id,
            'contract_code': contract.contract_code,
            'buyer_company': contract.buyer_company.name if contract.buyer_company else 'N/A',
            'exporter_company': contract.exporter_company.name if contract.exporter_company else 'N/A',
            'product_type': contract.product_type,
            'product_grade': contract.product_grade,
            'total_volume_mt': float(contract.total_volume_mt),
            'differential_usd': float(contract.differential_usd),
            'start_date': contract.start_date.isoformat() if contract.start_date else None,
            'end_date': contract.end_date.isoformat() if contract.end_date else None,
            'delivery_date': contract.delivery_date.isoformat() if contract.delivery_date else None,
            'status': contract.status
        }

        # Sincronizar
        result = connector.sync_contract(contract_data)

        if result:
            return jsonify({
                'message': 'Contrato sincronizado exitosamente con ERP',
                'erp_response': result
            })
        else:
            return jsonify({'error': 'Error sincronizando con ERP'}), 500

    except Exception as e:
        logger.error(f"Error syncing contract to ERP: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@erp_bp.route('/sync/fixation/<int:fixation_id>', methods=['POST'])
@jwt_required()
def sync_fixation_to_erp(fixation_id):
    """Sincronizar fijación con sistema ERP"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para sincronizar con ERP'}), 403

        fixation = ContractFixation.query.get(fixation_id)
        if not fixation:
            return jsonify({'error': 'Fijación no encontrada'}), 404

        data = request.get_json()
        connection_id = data.get('connection_id')

        if not connection_id or connection_id not in erp_connectors:
            return jsonify({'error': 'Conexión ERP no encontrada'}), 400

        connector = erp_connectors[connection_id]

        # Preparar datos de la fijación
        contract = fixation.export_contract
        fixation_data = {
            'fixation_id': fixation.id,
            'contract_code': contract.contract_code if contract else 'N/A',
            'buyer_company': contract.buyer_company.name if contract and contract.buyer_company else 'N/A',
            'product_type': contract.product_type if contract else 'N/A',
            'fixed_quantity_mt': float(fixation.fixed_quantity_mt),
            'spot_price_usd': float(fixation.spot_price_usd),
            'differential_usd': float(contract.differential_usd) if contract else 0,
            'total_value_usd': float(fixation.total_value_usd),
            'fixation_date': fixation.fixation_date.isoformat() if fixation.fixation_date else None
        }

        # Sincronizar
        result = connector.sync_fixation(fixation_data)

        if result:
            return jsonify({
                'message': 'Fijación sincronizada exitosamente con ERP',
                'erp_response': result
            })
        else:
            return jsonify({'error': 'Error sincronizando con ERP'}), 500

    except Exception as e:
        logger.error(f"Error syncing fixation to ERP: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@erp_bp.route('/sync/bulk', methods=['POST'])
@jwt_required()
def bulk_sync_to_erp():
    """Sincronización masiva con ERP"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para sincronización masiva'}), 403

        data = request.get_json()
        connection_id = data.get('connection_id')
        entity_type = data.get('entity_type')  # 'companies', 'contracts', 'fixations'
        entity_ids = data.get('entity_ids', [])

        if not connection_id or connection_id not in erp_connectors:
            return jsonify({'error': 'Conexión ERP no encontrada'}), 400

        if not entity_type or entity_type not in ['companies', 'contracts', 'fixations']:
            return jsonify({'error': 'Tipo de entidad no válido'}), 400

        connector = erp_connectors[connection_id]

        results = []
        errors = []

        if entity_type == 'companies':
            entities = Company.query.filter(Company.id.in_(entity_ids)).all() if entity_ids else Company.query.all()
            for company in entities:
                try:
                    company_data = {
                        'id': company.id,
                        'name': company.name,
                        'company_type': company.company_type,
                        'email': company.email,
                        'country': company.country
                    }
                    result = connector.sync_company(company_data)
                    if result:
                        results.append({'id': company.id, 'status': 'success', 'erp_id': result.get('id')})
                    else:
                        errors.append({'id': company.id, 'error': 'Sync failed'})
                except Exception as e:
                    errors.append({'id': company.id, 'error': str(e)})

        elif entity_type == 'contracts':
            entities = ExportContract.query.filter(ExportContract.id.in_(entity_ids)).all() if entity_ids else ExportContract.query.all()
            for contract in entities:
                try:
                    contract_data = contract.to_dict()
                    result = connector.sync_contract(contract_data)
                    if result:
                        results.append({'id': contract.id, 'status': 'success', 'erp_id': result.get('id')})
                    else:
                        errors.append({'id': contract.id, 'error': 'Sync failed'})
                except Exception as e:
                    errors.append({'id': contract.id, 'error': str(e)})

        elif entity_type == 'fixations':
            entities = ContractFixation.query.filter(ContractFixation.id.in_(entity_ids)).all() if entity_ids else ContractFixation.query.all()
            for fixation in entities:
                try:
                    contract = fixation.export_contract
                    fixation_data = fixation.to_dict()
                    fixation_data.update({
                        'contract_code': contract.contract_code if contract else 'N/A',
                        'buyer_company': contract.buyer_company.name if contract and contract.buyer_company else 'N/A',
                        'product_type': contract.product_type if contract else 'N/A',
                        'differential_usd': float(contract.differential_usd) if contract else 0
                    })
                    result = connector.sync_fixation(fixation_data)
                    if result:
                        results.append({'id': fixation.id, 'status': 'success', 'erp_id': result.get('id')})
                    else:
                        errors.append({'id': fixation.id, 'error': 'Sync failed'})
                except Exception as e:
                    errors.append({'id': fixation.id, 'error': str(e)})

        return jsonify({
            'message': f'Sincronización masiva completada',
            'results': results,
            'errors': errors,
            'summary': {
                'total': len(results) + len(errors),
                'successful': len(results),
                'failed': len(errors)
            }
        })

    except Exception as e:
        logger.error(f"Error in bulk sync: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@erp_bp.route('/test-connection/<connection_id>', methods=['POST'])
@jwt_required()
def test_erp_connection(connection_id):
    """Probar conexión con sistema ERP"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Sin permisos para probar conexiones ERP'}), 403

        if connection_id not in erp_connectors:
            return jsonify({'error': 'Conexión ERP no encontrada'}), 404

        connector = erp_connectors[connection_id]

        is_connected = connector.test_connection()

        return jsonify({
            'connection_id': connection_id,
            'status': 'connected' if is_connected else 'disconnected',
            'system_type': connector.system_type,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Error testing ERP connection: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

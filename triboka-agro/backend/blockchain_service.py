"""
Integración Web3 para interactuar con los smart contracts
Sistema de conexión blockchain para Triboka Agro
"""

import json
import os
from web3 import Web3
# Para Web3 v7+ no se necesita geth_poa_middleware
# from web3.middleware import geth_poa_middleware
from eth_account import Account
from typing import Optional, Dict, List, Any
import logging
from decimal import Decimal

# Importar configuración blockchain
from blockchain_config import (
    BLOCKCHAIN_CONFIG, CONTRACT_ADDRESSES, CONTRACT_ROLES, 
    TEST_ACCOUNTS, get_contract_abi, get_network_config, load_contract_config
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlockchainService:
    """Servicio para interactuar con los smart contracts"""
    
    def __init__(self, network: str = "hardhat"):
        self.network = network
        self.config = load_contract_config(network) or {}
        self.network_config = get_network_config(network)
        self.w3 = None
        self.contracts = {}
        self.account = None
        self._setup_web3()
        self._load_contracts()

    def _load_config(self):
        """Cargar configuración de contratos"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"✅ Config loaded from {self.config_path}")
        except FileNotFoundError:
            logger.warning(f"⚠️ Config file not found: {self.config_path}")
            self.config = {}

    def _setup_web3(self):
        """Configurar conexión Web3"""
        provider_url = self.network_config.get('rpc_url', 'http://127.0.0.1:8545')

        try:
            self.w3 = Web3(Web3.HTTPProvider(provider_url))
            
            # Para Web3 v7+ no se necesita el middleware POA
            # if self.network in ['mumbai', 'polygon']:
            #     self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

            # Configurar cuenta de prueba por defecto (deployer)
            default_account = TEST_ACCOUNTS['deployer']
            private_key = default_account['private_key']
            
            if private_key:
                if not private_key.startswith('0x'):
                    private_key = '0x' + private_key
                self.account = Account.from_key(private_key)
                logger.info(f"✅ Account configured: {self.account.address}")

            if self.w3.is_connected():
                logger.info(f"✅ Connected to {self.network} network")
                logger.info(f"📊 Chain ID: {self.w3.eth.chain_id}")
                self.simulation_mode = False
            else:
                logger.warning(f"⚠️ Failed to connect to {provider_url}, using simulation mode")
                self.simulation_mode = True
                # Configurar cuenta simulada
                default_account = TEST_ACCOUNTS['deployer']
                private_key = default_account['private_key']
                if private_key:
                    if not private_key.startswith('0x'):
                        private_key = '0x' + private_key
                    self.account = Account.from_key(private_key)
                    logger.info(f"✅ Simulation account configured: {self.account.address}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to {provider_url}: {e}")
            logger.info("🔧 Running in simulation mode")
            self.simulation_mode = True
            self.w3 = None
            # Configurar cuenta simulada
            default_account = TEST_ACCOUNTS['deployer']
            private_key = default_account['private_key']
            if private_key:
                if not private_key.startswith('0x'):
                    private_key = '0x' + private_key
                self.account = Account.from_key(private_key)
                logger.info(f"✅ Simulation account configured: {self.account.address}")

    def _load_contracts(self):
        """Cargar contratos y ABIs"""
        if not CONTRACT_ADDRESSES:
            logger.warning("⚠️ No contract addresses found")
            return
        
        for contract_name, address in CONTRACT_ADDRESSES.items():
            try:
                # Obtener ABI desde función helper
                abi = get_contract_abi(contract_name)
                if not abi:
                    logger.error(f"❌ ABI not found for {contract_name}")
                    continue
                
                # Crear instancia del contrato
                contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(address),
                    abi=abi
                )
                
                self.contracts[contract_name] = contract
                logger.info(f"✅ Contract loaded: {contract_name} at {address}")
                
            except Exception as e:
                logger.error(f"❌ Failed to load contract {contract_name}: {e}")

    def get_contract(self, contract_name: str):
        """Obtener instancia de contrato"""
        return self.contracts.get(contract_name)

    def is_connected(self) -> bool:
        """Verificar conexión blockchain"""
        if hasattr(self, 'simulation_mode') and self.simulation_mode:
            return True  # En modo simulación, siempre está "conectado"
        return self.w3 and self.w3.is_connected()

    def get_balance(self, address: Optional[str] = None) -> float:
        """Obtener balance de una dirección"""
        if not address and self.account:
            address = self.account.address
        
        if not address:
            return 0.0
        
        try:
            balance_wei = self.w3.eth.get_balance(address)
            return float(self.w3.from_wei(balance_wei, 'ether'))
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return 0.0

    def estimate_gas(self, transaction) -> int:
        """Estimar gas para una transacción"""
        try:
            return self.w3.eth.estimate_gas(transaction)
        except Exception as e:
            logger.error(f"Error estimating gas: {e}")
            return 100000  # Default gas limit

    def send_transaction(self, transaction) -> Optional[str]:
        """Enviar transacción firmada"""
        if not self.account:
            logger.error("No account configured for transactions")
            return None

        try:
            # Configurar transacción
            transaction.update({
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': self.estimate_gas(transaction),
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.w3.eth.chain_id
            })

            # Firmar transacción
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            
            # Enviar transacción
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"✅ Transaction sent: {tx_hash.hex()}")
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"❌ Transaction failed: {e}")
            return None

    def wait_for_transaction_receipt(self, tx_hash: str, timeout: int = 60) -> Optional[Dict]:
        """Esperar confirmación de transacción"""
        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            logger.info(f"✅ Transaction confirmed: {tx_hash}")
            return dict(receipt)
        except Exception as e:
            logger.error(f"❌ Transaction timeout or failed: {e}")
            return None

class AgroExportContractService:
    """Servicio específico para AgroExportContract"""
    
    def __init__(self, blockchain_service: BlockchainService):
        self.blockchain = blockchain_service
        self.contract = blockchain_service.get_contract('AgroExportContract')

    def create_contract(self, 
                       buyer_address: str,
                       exporter_address: str,
                       contract_code: str,
                       product_type: str,
                       product_grade: str,
                       total_volume_mt: int,
                       differential_usd: int,
                       start_date: int,
                       end_date: int,
                       delivery_date: int) -> Optional[str]:
        """Crear nuevo contrato de exportación"""
        
        if not self.contract:
            logger.error("AgroExportContract not loaded")
            return None

        try:
            # Preparar transacción
            function = self.contract.functions.createContract(
                buyer_address,
                exporter_address,
                contract_code,
                product_type,
                product_grade,
                total_volume_mt,
                differential_usd,
                start_date,
                end_date,
                delivery_date
            )

            transaction = function.build_transaction({
                'from': self.blockchain.account.address if self.blockchain.account else None
            })

            # Enviar transacción
            tx_hash = self.blockchain.send_transaction(transaction)
            if tx_hash:
                receipt = self.blockchain.wait_for_transaction_receipt(tx_hash)
                if receipt and receipt['status'] == 1:
                    # Extraer contract ID del evento
                    logs = self.contract.events.ContractCreated().process_receipt(receipt)
                    if logs:
                        contract_id = logs[0]['args']['contractId']
                        logger.info(f"✅ Contract created with ID: {contract_id.hex()}")
                        return contract_id.hex()
            
            return None

        except Exception as e:
            logger.error(f"❌ Error creating contract: {e}")
            return None

    def register_fixation(self,
                         contract_id: str,
                         fixed_quantity_mt: int,
                         spot_price_usd: int,
                         lot_ids: List[int],
                         notes: str = "") -> Optional[str]:
        """Registrar nueva fijación"""
        
        if not self.contract:
            logger.error("AgroExportContract not loaded")
            return None

        try:
            # Convertir contract_id a bytes32
            if isinstance(contract_id, str):
                if contract_id.startswith('0x'):
                    contract_id_bytes = bytes.fromhex(contract_id[2:])
                else:
                    contract_id_bytes = bytes.fromhex(contract_id)
            else:
                contract_id_bytes = contract_id

            # Preparar transacción
            function = self.contract.functions.registerFixation(
                contract_id_bytes,
                fixed_quantity_mt,
                spot_price_usd,
                lot_ids,
                notes
            )

            transaction = function.build_transaction({
                'from': self.blockchain.account.address if self.blockchain.account else None
            })

            # Enviar transacción
            tx_hash = self.blockchain.send_transaction(transaction)
            if tx_hash:
                receipt = self.blockchain.wait_for_transaction_receipt(tx_hash)
                if receipt and receipt['status'] == 1:
                    # Extraer fixation ID del evento
                    logs = self.contract.events.FixationRegistered().process_receipt(receipt)
                    if logs:
                        fixation_id = logs[0]['args']['fixationId']
                        logger.info(f"✅ Fixation registered with ID: {fixation_id.hex()}")
                        return fixation_id.hex()
            
            return None

        except Exception as e:
            logger.error(f"❌ Error registering fixation: {e}")
            return None

    def get_contract_info(self, contract_id: str) -> Optional[Dict]:
        """Obtener información del contrato"""
        if not self.contract:
            return None

        try:
            # Convertir contract_id a bytes32
            if isinstance(contract_id, str):
                if contract_id.startswith('0x'):
                    contract_id_bytes = bytes.fromhex(contract_id[2:])
                else:
                    contract_id_bytes = bytes.fromhex(contract_id)
            else:
                contract_id_bytes = contract_id

            result = self.contract.functions.getContract(contract_id_bytes).call()
            
            return {
                'buyer': result[0],
                'exporter': result[1],
                'contract_code': result[2],
                'product_type': result[3],
                'product_grade': result[4],
                'total_volume_mt': result[5],
                'differential_usd': result[6],
                'contract_date': result[7],
                'start_date': result[8],
                'end_date': result[9],
                'delivery_date': result[10],
                'fixed_volume_mt': result[11],
                'status': result[12]
            }

        except Exception as e:
            logger.error(f"❌ Error getting contract info: {e}")
            return None

class ProducerLotNFTService:
    """Servicio específico para ProducerLotNFT"""
    
    def __init__(self, blockchain_service: BlockchainService):
        self.blockchain = blockchain_service
        self.contract = blockchain_service.get_contract('ProducerLotNFT')

    def create_lot(self,
                   producer_address: str,
                   producer_name: str,
                   farm_name: str,
                   location: str,
                   product_type: str,
                   weight_kg: int,
                   quality_grade: str,
                   harvest_date: int,
                   certifications: List[str],
                   metadata_uri: str = "") -> Optional[int]:
        """Crear nuevo lote NFT"""
        
        if not self.contract:
            logger.error("ProducerLotNFT not loaded")
            return None

        try:
            # Preparar transacción
            function = self.contract.functions.createLot(
                producer_address,
                producer_name,
                farm_name,
                location,
                product_type,
                weight_kg,
                quality_grade,
                harvest_date,
                certifications,
                metadata_uri
            )

            transaction = function.build_transaction({
                'from': self.blockchain.account.address if self.blockchain.account else None
            })

            # Enviar transacción
            tx_hash = self.blockchain.send_transaction(transaction)
            if tx_hash:
                receipt = self.blockchain.wait_for_transaction_receipt(tx_hash)
                if receipt and receipt['status'] == 1:
                    # Extraer lot ID del evento
                    logs = self.contract.events.LotCreated().process_receipt(receipt)
                    if logs:
                        lot_id = logs[0]['args']['lotId']
                        logger.info(f"✅ Lot NFT created with ID: {lot_id}")
                        return lot_id
            
            return None

        except Exception as e:
            logger.error(f"❌ Error creating lot NFT: {e}")
            return None

    def get_lot_info(self, lot_id: int) -> Optional[Dict]:
        """Obtener información del lote"""
        if not self.contract:
            return None

        try:
            result = self.contract.functions.getLot(lot_id).call()
            
            return {
                'producer': result[0],
                'producer_name': result[1],
                'farm_name': result[2],
                'location': result[3],
                'product_type': result[4],
                'weight_kg': result[5],
                'quality_grade': result[6],
                'harvest_date': result[7],
                'purchase_date': result[8],
                'purchase_price_usd': result[9],
                'certifications': result[10],
                'status': result[11],
                'contract_id': result[12],
                'shipment_id': result[13]
            }

        except Exception as e:
            logger.error(f"❌ Error getting lot info: {e}")
            return None

class BlockchainIntegration:
    """Clase principal para integración blockchain"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.blockchain = BlockchainService(config_path)
        self.agro_contract = AgroExportContractService(self.blockchain)
        self.nft_service = ProducerLotNFTService(self.blockchain)

    def is_ready(self) -> bool:
        """Verificar si la integración está lista"""
        simulation_mode = getattr(self.blockchain, 'simulation_mode', False)
        if simulation_mode:
            return True  # En modo simulación, siempre está listo
        return (self.blockchain.is_connected() and 
                self.blockchain.account is not None and
                len(self.blockchain.contracts) > 0)

    def get_status(self) -> Dict:
        """Obtener estado de la integración"""
        connected = self.blockchain.is_connected()
        simulation_mode = getattr(self.blockchain, 'simulation_mode', False)
        
        if simulation_mode:
            # En modo simulación, proporcionar datos simulados
            return {
                'connected': True,
                'network': 'hardhat-simulation',
                'chain_id': 1337,
                'account': self.blockchain.account.address if self.blockchain.account else None,
                'balance': 10.0,  # Balance simulado
                'contracts_loaded': 3,  # Número simulado de contratos
                'contracts': ['AgroExportContract', 'ProducerLotNFT', 'DocumentRegistry'],
                'simulation_mode': True
            }
        else:
            return {
                'connected': connected,
                'network': self.blockchain.network_config.get('name', 'unknown'),
                'chain_id': self.blockchain.w3.eth.chain_id if self.blockchain.w3 and connected else None,
                'account': self.blockchain.account.address if self.blockchain.account else None,
                'balance': self.blockchain.get_balance() if connected else 0.0,
                'contracts_loaded': len(self.blockchain.contracts),
                'contracts': list(self.blockchain.contracts.keys()),
                'simulation_mode': False
            }

# Instancia global
blockchain_integration = None

def get_blockchain_integration() -> BlockchainIntegration:
    """Obtener instancia singleton de integración blockchain"""
    global blockchain_integration
    if blockchain_integration is None:
        blockchain_integration = BlockchainIntegration()
    return blockchain_integration
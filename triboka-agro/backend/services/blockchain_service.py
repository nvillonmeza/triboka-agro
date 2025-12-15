"""
Blockchain Service for Triboka BaaS Platform
Handles integration with Polygon Edge blockchain
"""

import json
import requests
from web3 import Web3
from eth_account import Account
from datetime import datetime
import hashlib
import logging

from config.config import Config

logger = logging.getLogger(__name__)

class BlockchainService:
    def __init__(self):
        self.config = Config.get_instance()
        self.w3 = Web3(Web3.HTTPProvider(self.config.BLOCKCHAIN_RPC_URL))
        self.chain_id = self.config.BLOCKCHAIN_CHAIN_ID
        
        # Contract addresses and ABIs
        self.nft_contract_address = self.config.NFT_CONTRACT_ADDRESS
        self.lot_registry_address = self.config.LOT_REGISTRY_ADDRESS
        
        # Load contract ABIs
        self.nft_abi = self._load_contract_abi('nft_contract.json')
        self.lot_registry_abi = self._load_contract_abi('lot_registry.json')
        
        # Initialize contracts
        if self.nft_contract_address and self.nft_abi:
            self.nft_contract = self.w3.eth.contract(
                address=self.nft_contract_address,
                abi=self.nft_abi
            )
        
        if self.lot_registry_address and self.lot_registry_abi:
            self.lot_registry_contract = self.w3.eth.contract(
                address=self.lot_registry_address,
                abi=self.lot_registry_abi
            )
        
        # Platform wallet for transactions
        self.platform_wallet = Account.from_key(self.config.BLOCKCHAIN_PRIVATE_KEY)
    
    def _load_contract_abi(self, filename):
        """Load contract ABI from file"""
        try:
            with open(f'blockchain/abis/{filename}', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Contract ABI file {filename} not found")
            return None
    
    def is_connected(self):
        """Check if blockchain connection is active"""
        try:
            return self.w3.is_connected()
        except Exception as e:
            logger.error(f"Blockchain connection error: {e}")
            return False
    
    def get_balance(self, address=None):
        """Get ETH balance for address"""
        try:
            address = address or self.platform_wallet.address
            balance_wei = self.w3.eth.get_balance(address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return None
    
    def register_lot(self, lot):
        """Register cacao lot on blockchain"""
        try:
            if not self.lot_registry_contract:
                return {'success': False, 'error': 'Lot registry contract not available'}
            
            # Create lot hash for blockchain
            lot_data = {
                'lot_number': lot.lot_number,
                'origin_location': lot.origin_location,
                'quantity_kg': lot.quantity_kg,
                'harvest_date': lot.harvest_date.isoformat() if lot.harvest_date else '',
                'company_id': str(lot.company_id)
            }
            
            lot_hash = self._create_data_hash(lot_data)
            
            # Prepare transaction
            nonce = self.w3.eth.get_transaction_count(self.platform_wallet.address)
            
            # Build transaction
            transaction = self.lot_registry_contract.functions.registerLot(
                lot.lot_number,
                lot.origin_location,
                int(lot.quantity_kg * 1000),  # Convert to grams
                lot_hash,
                lot.company.wallet_address if lot.company.wallet_address else self.platform_wallet.address
            ).build_transaction({
                'chainId': self.chain_id,
                'gas': 200000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': nonce,
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.platform_wallet.privateKey)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            return {
                'success': True,
                'tx_hash': receipt.transactionHash.hex(),
                'block_number': receipt.blockNumber,
                'gas_used': receipt.gasUsed,
                'contract_address': self.lot_registry_address
            }
            
        except Exception as e:
            logger.error(f"Error registering lot on blockchain: {e}")
            return {'success': False, 'error': str(e)}
    
    def mint_nft(self, nft_certificate):
        """Mint NFT certificate on blockchain"""
        try:
            if not self.nft_contract:
                return {'success': False, 'error': 'NFT contract not available'}
            
            # Prepare metadata
            metadata = {
                'name': nft_certificate.title,
                'description': nft_certificate.description,
                'image': nft_certificate.image_url or '',
                'attributes': self._get_nft_attributes(nft_certificate),
                'external_url': f"{self.config.API_BASE_URL}/nfts/{nft_certificate.uuid}/verify"
            }
            
            # Upload metadata to IPFS or use centralized storage
            metadata_uri = self._store_metadata(metadata, nft_certificate.uuid)
            
            # Get recipient address (company wallet or platform wallet)
            recipient = nft_certificate.company.wallet_address or self.platform_wallet.address
            
            # Prepare transaction
            nonce = self.w3.eth.get_transaction_count(self.platform_wallet.address)
            
            # Build mint transaction
            transaction = self.nft_contract.functions.mintCertificate(
                recipient,
                nft_certificate.token_id,
                metadata_uri
            ).build_transaction({
                'chainId': self.chain_id,
                'gas': 300000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': nonce,
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.platform_wallet.privateKey)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            return {
                'success': True,
                'tx_hash': receipt.transactionHash.hex(),
                'block_number': receipt.blockNumber,
                'gas_used': receipt.gasUsed,
                'contract_address': self.nft_contract_address,
                'metadata_uri': metadata_uri
            }
            
        except Exception as e:
            logger.error(f"Error minting NFT: {e}")
            return {'success': False, 'error': str(e)}
    
    def verify_nft(self, nft_certificate):
        """Verify NFT on blockchain"""
        try:
            if not self.nft_contract or not nft_certificate.is_minted:
                return {'verified': False, 'error': 'NFT not minted or contract unavailable'}
            
            # Get NFT data from blockchain
            try:
                token_uri = self.nft_contract.functions.tokenURI(nft_certificate.token_id).call()
                owner = self.nft_contract.functions.ownerOf(nft_certificate.token_id).call()
                
                return {
                    'verified': True,
                    'owner': owner,
                    'token_uri': token_uri,
                    'contract_address': self.nft_contract_address,
                    'blockchain_tx_hash': nft_certificate.blockchain_tx_hash
                }
                
            except Exception as contract_error:
                logger.error(f"Contract call error: {contract_error}")
                return {'verified': False, 'error': 'Token not found on blockchain'}
            
        except Exception as e:
            logger.error(f"Error verifying NFT: {e}")
            return {'verified': False, 'error': str(e)}
    
    def get_transaction_status(self, tx_hash):
        """Get transaction status and details"""
        try:
            if not tx_hash:
                return {'status': 'unknown', 'error': 'No transaction hash provided'}
            
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            transaction = self.w3.eth.get_transaction(tx_hash)
            
            current_block = self.w3.eth.block_number
            confirmations = current_block - receipt.blockNumber
            
            return {
                'status': 'confirmed' if receipt.status == 1 else 'failed',
                'block_number': receipt.blockNumber,
                'confirmations': confirmations,
                'gas_used': receipt.gasUsed,
                'gas_price': transaction.gasPrice,
                'tx_hash': tx_hash
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction status: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def get_lot_history(self, lot_number):
        """Get blockchain history for a lot"""
        try:
            if not self.lot_registry_contract:
                return {'success': False, 'error': 'Lot registry contract not available'}
            
            # Get lot registration event
            lot_filter = self.lot_registry_contract.events.LotRegistered.create_filter(
                fromBlock=0,
                argument_filters={'lotNumber': lot_number}
            )
            
            events = lot_filter.get_all_entries()
            
            history = []
            for event in events:
                history.append({
                    'event': 'LotRegistered',
                    'block_number': event.blockNumber,
                    'tx_hash': event.transactionHash.hex(),
                    'data': dict(event.args)
                })
            
            return {'success': True, 'history': history}
            
        except Exception as e:
            logger.error(f"Error getting lot history: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_data_hash(self, data):
        """Create SHA256 hash of data"""
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def _get_nft_attributes(self, nft_certificate):
        """Generate NFT attributes from certificate data"""
        attributes = [
            {
                'trait_type': 'Certificate Type',
                'value': nft_certificate.certificate_type.title()
            },
            {
                'trait_type': 'Lot Number',
                'value': nft_certificate.lot.lot_number
            },
            {
                'trait_type': 'Origin Location',
                'value': nft_certificate.lot.origin_location
            },
            {
                'trait_type': 'Quantity (kg)',
                'value': nft_certificate.lot.quantity_kg,
                'display_type': 'number'
            },
            {
                'trait_type': 'Company',
                'value': nft_certificate.company.name
            },
            {
                'trait_type': 'Issue Date',
                'value': nft_certificate.created_at.strftime('%Y-%m-%d')
            }
        ]
        
        # Add quality grade if available
        if nft_certificate.lot.quality_grade:
            attributes.append({
                'trait_type': 'Quality Grade',
                'value': nft_certificate.lot.quality_grade
            })
        
        # Add harvest date if available
        if nft_certificate.lot.harvest_date:
            attributes.append({
                'trait_type': 'Harvest Date',
                'value': nft_certificate.lot.harvest_date.strftime('%Y-%m-%d')
            })
        
        return attributes
    
    def _store_metadata(self, metadata, certificate_uuid):
        """Store NFT metadata (centralized for now, can be upgraded to IPFS)"""
        # For now, return API endpoint for metadata
        # In production, this should upload to IPFS
        return f"{self.config.API_BASE_URL}/nfts/{certificate_uuid}/metadata"
    
    def estimate_gas_price(self):
        """Get current gas price estimate"""
        try:
            gas_price = self.w3.eth.gas_price
            return self.w3.from_wei(gas_price, 'gwei')
        except Exception as e:
            logger.error(f"Error getting gas price: {e}")
            return 20  # Default 20 gwei
    
    def get_network_stats(self):
        """Get blockchain network statistics"""
        try:
            latest_block = self.w3.eth.get_block('latest')
            
            return {
                'connected': self.is_connected(),
                'latest_block': latest_block.number,
                'gas_price_gwei': float(self.estimate_gas_price()),
                'platform_balance': self.get_balance(),
                'platform_address': self.platform_wallet.address,
                'nft_contract_address': self.nft_contract_address,
                'lot_registry_address': self.lot_registry_address
            }
        except Exception as e:
            logger.error(f"Error getting network stats: {e}")
            return {'connected': False, 'error': str(e)}
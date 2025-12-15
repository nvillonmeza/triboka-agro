# 🔧 Configuración de Blockchain para Triboka Agro
# Direcciones de contratos deployados y configuración Web3

import json
import os

# Configuración de red
BLOCKCHAIN_CONFIG = {
    "network": "hardhat",
    "rpc_url": "http://127.0.0.1:8545",
    "chain_id": 1337,
    "gas_limit": 3000000,
    "gas_price": 20000000000  # 20 gwei
}

# Direcciones de contratos deployados
CONTRACT_ADDRESSES = {
    "AgroExportContract": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
    "ProducerLotNFT": "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512", 
    "DocumentRegistry": "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"
}

# Roles de contratos
CONTRACT_ROLES = {
    "AgroExportContract": {
        "DEFAULT_ADMIN_ROLE": "0x0000000000000000000000000000000000000000000000000000000000000000",
        "OPERATOR_ROLE": "0x97667070c54ef182b0f5858b034beac1b6f3089aa2d3188bb1e8929f4fa9b929",
        "EXPORTER_ROLE": "0xaf60a13a1620ed8606730e7105f2af60851db04bb2ce1a068e80262de457512a",
        "BUYER_ROLE": "0xf8cd32ed93fc2f9fc78152a14807c9609af3d99c5fe4dc6b8b106a801aaddfe90e"
    },
    "ProducerLotNFT": {
        "DEFAULT_ADMIN_ROLE": "0x0000000000000000000000000000000000000000000000000000000000000000",
        "MINTER_ROLE": "0x9f2df0fed2c77648de5860a4cc508cd0818c85b8b8a1ab4ceeef8d981c8956a6",
        "OPERATOR_ROLE": "0x97667070c54ef182b0f5858b034beac1b6f3089aa2d3188bb1e8929f4fa9b929",
        "PRODUCER_ROLE": "0x8eb467f061ca67f42a2d2ca4a346fc9fb645efc0ba75056ee9f71c3a0ccc10a8"
    },
    "DocumentRegistry": {
        "DEFAULT_ADMIN_ROLE": "0x0000000000000000000000000000000000000000000000000000000000000000",
        "ISSUER_ROLE": "0x114e74f6ea3bd819998f78687bfcb11b140da08e9b7d222fa9c1f1ba1f2aa122",
        "VERIFIER_ROLE": "0x0ce23c3e399818cfee81a7ab0880f714e53d7672b08df0fa62f2843416e1ea09",
        "OPERATOR_ROLE": "0x97667070c54ef182b0f5858b034beac1b6f3089aa2d3188bb1e8929f4fa9b929"
    }
}

# Cuentas de prueba (Hardhat)
TEST_ACCOUNTS = {
    "deployer": {
        "address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "private_key": "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    },
    "exporter": {
        "address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "private_key": "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    },
    "buyer": {
        "address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
        "private_key": "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
    },
    "producer": {
        "address": "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
        "private_key": "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a"
    }
}

def load_contract_config(network="hardhat"):
    """Cargar configuración de contratos desde archivo JSON"""
    config_file = f"/home/rootpanel/web/app.triboka.com/blockchain/config/contracts-{network}.json"
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    else:
        return None

def get_contract_abi(contract_name):
    """Obtener ABI de contrato desde artifacts"""
    abi_file = f"/home/rootpanel/web/app.triboka.com/blockchain/artifacts/contracts/{contract_name}.sol/{contract_name}.json"
    
    if os.path.exists(abi_file):
        with open(abi_file, 'r') as f:
            artifact = json.load(f)
            return artifact['abi']
    else:
        return None

# Funciones de utilidad
def get_contract_address(contract_name):
    """Obtener dirección de contrato específico"""
    return CONTRACT_ADDRESSES.get(contract_name)

def get_role_hash(contract_name, role_name):
    """Obtener hash de rol específico"""
    return CONTRACT_ROLES.get(contract_name, {}).get(role_name)

def get_test_account(account_type):
    """Obtener cuenta de prueba por tipo"""
    return TEST_ACCOUNTS.get(account_type)

# Configuración para diferentes redes
NETWORK_CONFIGS = {
    "hardhat": {
        "rpc_url": "http://127.0.0.1:8545",
        "chain_id": 1337,
        "name": "Hardhat Local"
    },
    "localhost": {
        "rpc_url": "http://127.0.0.1:8545", 
        "chain_id": 1337,
        "name": "Localhost"
    },
    "mumbai": {
        "rpc_url": "https://rpc-mumbai.maticvigil.com",
        "chain_id": 80001,
        "name": "Polygon Mumbai Testnet"
    },
    "polygon": {
        "rpc_url": "https://polygon-rpc.com",
        "chain_id": 137,
        "name": "Polygon Mainnet"
    }
}

def get_network_config(network="hardhat"):
    """Obtener configuración de red específica"""
    return NETWORK_CONFIGS.get(network, NETWORK_CONFIGS["hardhat"])
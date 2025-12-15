#!/usr/bin/env python3
"""
Test para verificar endpoint de contratos
"""
import requests
import json
import sys

def test_contracts():
    """Probar endpoint de contratos con autenticación"""
    
    # 1. Login como admin
    print("🔐 Intentando login como admin...")
    login_url = "http://localhost:5003/api/auth/login"
    login_data = {
        "email": "admin@triboka.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Error en login: {response.text}")
            return False
        
        data = response.json()
        token = data.get('access_token')
        if not token:
            print(f"   ❌ No se recibió token: {data}")
            return False
        
        print(f"   ✅ Login exitoso, token recibido")
        
    except Exception as e:
        print(f"   ❌ Excepción en login: {e}")
        return False
    
    # 2. Obtener contratos
    print("\n📄 Obteniendo contratos...")
    contracts_url = "http://localhost:5003/api/contracts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(contracts_url, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Error: {response.text}")
            return False
        
        contracts = response.json()
        print(f"   ✅ {len(contracts)} contratos encontrados")
        
        if contracts:
            print(f"\n📋 Primer contrato:")
            first = contracts[0]
            print(f"   ID: {first.get('id')}")
            print(f"   Código: {first.get('contract_code')}")
            print(f"   Exportador: {first.get('exporter_company')}")
            print(f"   Comprador: {first.get('buyer_company')}")
            print(f"   Producto: {first.get('product_type')}")
            print(f"   Volumen: {first.get('total_volume_mt')} MT")
            print(f"   Estado: {first.get('status')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEST ENDPOINT DE CONTRATOS")
    print("=" * 60)
    
    success = test_contracts()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST COMPLETADO EXITOSAMENTE")
    else:
        print("❌ TEST FALLIDO")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

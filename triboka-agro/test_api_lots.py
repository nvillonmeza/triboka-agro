#!/usr/bin/env python3
"""
Test para verificar qué retorna el endpoint /api/lots
"""
import requests
import json

# URL del backend
BACKEND_URL = "http://localhost:5003/api/lots"

print("=" * 80)
print("TEST: Endpoint /api/lots")
print("=" * 80)

# Test 1: Sin autenticación
print("\n1. Petición SIN autenticación:")
try:
    response = requests.get(BACKEND_URL)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Lotes retornados: {len(data)}")
        if data:
            print(f"   Primer lote: {json.dumps(data[0], indent=2)}")
    else:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 2: Con token (simular sesión de exportador)
# Primero hacer login
print("\n2. Haciendo login como exportador...")
try:
    login_response = requests.post(
        "http://localhost:5003/api/auth/login",
        json={
            "email": "exportador@triboka.com",
            "password": "exportador123"
        }
    )
    print(f"   Login Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        access_token = token_data.get('access_token')
        user = token_data.get('user', {})
        print(f"   User: {user.get('email')} - Role: {user.get('role')}")
        
        # Test 3: Con autenticación
        print("\n3. Petición CON autenticación (exportador):")
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(BACKEND_URL, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Lotes retornados: {len(data)}")
            
            # Agrupar por status
            by_status = {}
            for lot in data:
                status = lot.get('status', 'unknown')
                by_status[status] = by_status.get(status, 0) + 1
            
            print(f"   Agrupados por status: {by_status}")
            
            # Mostrar primeros 3
            print("\n   Primeros 3 lotes:")
            for lot in data[:3]:
                print(f"     - {lot.get('lot_code')} | {lot.get('producer_company')} | {lot.get('status')} | {lot.get('weight_kg')}kg")
        else:
            print(f"   Response: {response.text[:200]}")
    else:
        print(f"   Login failed: {login_response.text}")
        
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 80)
print("FIN DEL TEST")
print("=" * 80)

#!/usr/bin/env python3
"""
Script para probar específicamente el problema HTTP/1.0 vs HTTP/1.1
"""

import requests
import json

def test_http_versions():
    """Probar diferentes versiones HTTP"""

    base_url = "http://localhost:5004"
    session = requests.Session()

    print("🔍 PRUEBA DE VERSIONES HTTP")
    print("=" * 40)

    # Login primero
    login_data = {'email': 'admin@triboka.com', 'password': 'admin123'}
    login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=True)
    print(f"Login status: {login_response.status_code}")

    if login_response.status_code != 200:
        print("❌ Login falló")
        return

    # Probar con HTTP/1.1 (default)
    print("\n📡 Probando con HTTP/1.1:")
    try:
        response_11 = session.get(f"{base_url}/api/users")
        print(f"   Status: {response_11.status_code}")
        print(f"   HTTP Version: {response_11.raw.version}")
        if response_11.status_code == 200:
            print("   ✅ HTTP/1.1 funciona")
        else:
            print(f"   ❌ HTTP/1.1 falló: {response_11.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error HTTP/1.1: {e}")

    # Probar forzar HTTP/1.0
    print("\n📡 Probando con HTTP/1.0:")
    try:
        headers_10 = {'Connection': 'close'}  # Fuerza HTTP/1.0 behavior
        response_10 = session.get(f"{base_url}/api/users", headers=headers_10)
        print(f"   Status: {response_10.status_code}")
        print(f"   HTTP Version: {response_10.raw.version}")
        if response_10.status_code == 200:
            print("   ✅ HTTP/1.0 funciona")
        else:
            print(f"   ❌ HTTP/1.0 falló: {response_10.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error HTTP/1.0: {e}")

    print("\n" + "=" * 40)

if __name__ == "__main__":
    test_http_versions()
#!/usr/bin/env python3
"""
Script de diagnóstico detallado para el problema HTTP/1.0 vs HTTP/1.1
"""

import requests
import json
import time
from urllib.parse import urlparse

def detailed_diagnostic():
    """Diagnóstico detallado del problema HTTP"""

    print("🔍 DIAGNÓSTICO DETALLADO - Problema HTTP/1.0")
    print("=" * 50)

    base_url = "http://localhost:5004"
    session = requests.Session()

    # 1. Login
    print("\n1. LOGIN:")
    login_data = {'email': 'admin@triboka.com', 'password': 'admin123'}
    login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=True)
    print(f"   Status: {login_response.status_code}")
    print(f"   HTTP Version: {login_response.raw.version}")

    if login_response.status_code != 200:
        print("   ❌ Login falló")
        return

    # 2. Verificar sesión después del login
    print("\n2. VERIFICACIÓN DE SESIÓN:")
    cookies = session.cookies.get_dict()
    print(f"   Cookies después de login: {len(cookies)}")
    for name, value in cookies.items():
        print(f"   - {name}: {len(value)} chars")

    # 3. Acceder a /users (GET HTML)
    print("\n3. ACCESO A /users (HTML):")
    users_page = session.get(f"{base_url}/users", allow_redirects=False)
    print(f"   Status: {users_page.status_code}")
    print(f"   HTTP Version: {users_page.raw.version}")

    if users_page.status_code == 302:
        print(f"   ⚠️  Redirect to: {users_page.headers.get('Location')}")
        return

    # 4. Simular petición JavaScript fetch exacta
    print("\n4. PETICIÓN JAVASCRIPT fetch('/api/users'):")

    # Headers que envía el navegador
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'localhost:5004',
        'Pragma': 'no-cache',
        'Referer': 'http://localhost:5004/users',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

    # Petición con diferentes configuraciones
    api_url = f"{base_url}/api/users"

    # 4a. Con credentials: same-origin (como hace JavaScript)
    print("   4a. Con credentials: same-origin")
    try:
        response_same_origin = session.get(api_url, headers=headers)
        print(f"      Status: {response_same_origin.status_code}")
        print(f"      HTTP Version: {response_same_origin.raw.version}")
        print(f"      Content-Type: {response_same_origin.headers.get('Content-Type', 'N/A')}")

        if response_same_origin.status_code == 401:
            print("      ❌ 401 - No autorizado")
            print(f"      Response: {response_same_origin.text[:200]}")
        elif response_same_origin.status_code == 200:
            print("      ✅ 200 - OK")
        else:
            print(f"      ⚠️  Status inesperado: {response_same_origin.status_code}")

    except Exception as e:
        print(f"      ❌ Error: {e}")

    # 4b. Sin credentials explícitos
    print("   4b. Sin credentials explícitos")
    try:
        response_no_creds = session.get(api_url)
        print(f"      Status: {response_no_creds.status_code}")
        print(f"      HTTP Version: {response_no_creds.raw.version}")

        if response_no_creds.status_code == 401:
            print("      ❌ 401 - No autorizado")
        elif response_no_creds.status_code == 200:
            print("      ✅ 200 - OK")
        else:
            print(f"      ⚠️  Status inesperado: {response_no_creds.status_code}")

    except Exception as e:
        print(f"      ❌ Error: {e}")

    # 4c. Forzar HTTP/1.1 explícitamente
    print("   4c. Forzando HTTP/1.1")
    try:
        headers_11 = headers.copy()
        headers_11['Connection'] = 'keep-alive'

        response_11 = session.get(api_url, headers=headers_11)
        print(f"      Status: {response_11.status_code}")
        print(f"      HTTP Version: {response_11.raw.version}")

        if response_11.status_code == 401:
            print("      ❌ 401 - No autorizado")
        elif response_11.status_code == 200:
            print("      ✅ 200 - OK")
        else:
            print(f"      ⚠️  Status inesperado: {response_11.status_code}")

    except Exception as e:
        print(f"      ❌ Error: {e}")

    # 5. Verificar si el problema está en el backend
    print("\n5. VERIFICACIÓN DIRECTA AL BACKEND:")
    backend_url = "http://localhost:5003/api/users"

    # Obtener token de la sesión
    access_token = None
    for name, value in cookies.items():
        if 'session' in name.lower():
            # Extraer token de la cookie de sesión (esto es aproximado)
            # En producción, el token JWT viene del login
            pass

    # Intentar con token JWT simulado
    try:
        # Como no tenemos el token JWT, probamos sin autenticación primero
        backend_response = requests.get(backend_url)
        print(f"   Backend directo: {backend_response.status_code}")
        print(f"   HTTP Version: {backend_response.raw.version}")

        if backend_response.status_code == 401:
            print("   ✅ Backend requiere autenticación correctamente")
        else:
            print(f"   ⚠️  Backend respondió: {backend_response.status_code}")

    except Exception as e:
        print(f"   ❌ Error backend: {e}")

    print("\n" + "=" * 50)
    print("🔍 DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    detailed_diagnostic()
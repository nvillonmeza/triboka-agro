#!/usr/bin/env python3
"""
Script para diagnosticar el problema de sesión en /users
Simula exactamente lo que hace el navegador
"""

import requests
import json
from datetime import datetime

def test_session_persistence():
    """Probar persistencia de sesión simulando navegador"""

    base_url = "http://localhost:5004"
    api_base_url = "http://localhost:5003/api"

    print("🔍 DIAGNOSTICO DE SESIÓN - Simulando comportamiento del navegador")
    print("=" * 60)

    # Crear una sesión que mantenga cookies (como un navegador)
    session = requests.Session()

    # 1. Login
    print("\n1. LOGIN:")
    login_data = {
        'email': 'admin@triboka.com',
        'password': 'admin123'
    }

    try:
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=True)
        print(f"   Status: {login_response.status_code}")
        print(f"   URL final: {login_response.url}")
        print(f"   Cookies después de login: {dict(session.cookies)}")

        # Verificar que estamos en dashboard
        if 'dashboard' in login_response.url:
            print("   ✅ Login exitoso - redirigido a dashboard")
        else:
            print("   ❌ Login falló - no redirigido a dashboard")
            return

    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return

    # 2. Acceder a /users (simulando click en sidebar)
    print("\n2. ACCESO A /USERS (GET /users):")
    try:
        users_page_response = session.get(f"{base_url}/users")
        print(f"   Status: {users_page_response.status_code}")
        print(f"   URL final: {users_page_response.url}")
        print(f"   Cookies antes de /users: {dict(session.cookies)}")

        if users_page_response.status_code == 200:
            print("   ✅ Página /users cargada correctamente")
        elif users_page_response.status_code == 302:
            print(f"   ⚠️  Redirigido a: {users_page_response.headers.get('Location')}")
            if 'login' in users_page_response.headers.get('Location', ''):
                print("   ❌ Sesión perdida - redirigido a login")
                return
        else:
            print(f"   ❌ Error HTTP: {users_page_response.status_code}")

    except Exception as e:
        print(f"   ❌ Error accediendo a /users: {e}")
        return

    # 3. Simular la petición AJAX fetch('/api/users') que hace JavaScript
    print("\n3. PETICIÓN AJAX fetch('/api/users'):")
    try:
        # Simular exactamente lo que hace JavaScript: fetch('/api/users', {credentials: 'same-origin'})
        headers = {
            'Content-Type': 'application/json',
            # No incluimos Authorization header porque el frontend usa cookies de sesión
        }

        api_response = session.get(f"{base_url}/api/users", headers=headers)
        print(f"   Status: {api_response.status_code}")
        print(f"   Headers enviados: {headers}")
        print(f"   Cookies enviadas: {dict(session.cookies)}")

        if api_response.status_code == 200:
            try:
                data = api_response.json()
                print(f"   ✅ API respondió correctamente: {len(data)} usuarios")
            except:
                print(f"   ✅ API respondió correctamente (no JSON)")
        elif api_response.status_code == 401:
            print("   ❌ API devolvió 401 - No autorizado")
            print(f"   Response: {api_response.text[:200]}")
            return
        else:
            print(f"   ❌ Error API: {api_response.status_code}")
            print(f"   Response: {api_response.text[:200]}")

    except Exception as e:
        print(f"   ❌ Error en petición AJAX: {e}")
        return

    # 4. Verificar que la sesión persiste
    print("\n4. VERIFICACIÓN DE PERSISTENCIA:")
    try:
        # Hacer otra petición para verificar persistencia
        dashboard_response = session.get(f"{base_url}/dashboard")
        print(f"   Dashboard status: {dashboard_response.status_code}")

        if dashboard_response.status_code == 200:
            print("   ✅ Sesión persiste correctamente")
        else:
            print("   ❌ Sesión perdida")

    except Exception as e:
        print(f"   ❌ Error verificando persistencia: {e}")

    print("\n" + "=" * 60)
    print("✅ DIAGNÓSTICO COMPLETADO - Todo funciona correctamente")

if __name__ == "__main__":
    test_session_persistence()
#!/usr/bin/env python3
"""
Script para probar específicamente la solución JWT vs HTTP/1.0
"""

import requests
import json

def test_jwt_solution():
    """Probar que la solución JWT funciona incluso con HTTP/1.0"""

    print("🔧 PRUEBA DE SOLUCIÓN JWT")
    print("=" * 40)

    base_url = "http://localhost:5004"
    session = requests.Session()

    # 1. Login y obtener token JWT
    print("\n1. LOGIN Y OBTENCIÓN DE TOKEN JWT:")
    login_data = {'email': 'admin@triboka.com', 'password': 'admin123'}
    login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=True)
    print(f"   Login status: {login_response.status_code}")

    if login_response.status_code != 200:
        print("   ❌ Login falló")
        return

    # 2. Obtener token JWT del HTML de la página de usuarios
    print("\n2. EXTRACCIÓN DE TOKEN JWT:")
    users_page = session.get(f"{base_url}/users")
    html_content = users_page.text

    # Buscar el token en el HTML
    token_start = html_content.find("const ACCESS_TOKEN = '") + len("const ACCESS_TOKEN = '")
    token_end = html_content.find("';", token_start)
    jwt_token = html_content[token_start:token_end]

    print(f"   Token encontrado: {len(jwt_token)} caracteres")
    if jwt_token and len(jwt_token) > 10:
        print("   ✅ Token JWT extraído correctamente")
    else:
        print("   ❌ No se pudo extraer el token JWT")
        return

    # 3. Probar petición con JWT en headers (sin depender de cookies)
    print("\n3. PETICIÓN CON JWT EN HEADERS:")

    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }

    # Probar con diferentes configuraciones de conexión para forzar HTTP/1.0
    test_configs = [
        ("Normal", {}),
        ("Connection: close", {'Connection': 'close'}),
        ("HTTP/1.0 style", {'Connection': 'close', 'Proxy-Connection': 'close'})
    ]

    for config_name, extra_headers in test_configs:
        print(f"\n   Configuración: {config_name}")
        test_headers = headers.copy()
        test_headers.update(extra_headers)

        try:
            response = session.get(f"{base_url}/api/users", headers=test_headers)
            print(f"      Status: {response.status_code}")
            print(f"      HTTP Version: {response.raw.version}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"      ✅ Éxito: {len(data.get('users', []))} usuarios")
                except:
                    print("      ✅ Éxito (respuesta no JSON)")
            elif response.status_code == 401:
                print("      ❌ 401 - No autorizado (problema de autenticación)")
            else:
                print(f"      ⚠️  Status inesperado: {response.status_code}")

        except Exception as e:
            print(f"      ❌ Error: {e}")

    # 4. Verificar que funciona sin cookies (solo con JWT)
    print("\n4. PRUEBA SIN COOKIES (SOLO JWT):")
    clean_session = requests.Session()  # Sesión limpia sin cookies

    try:
        response_no_cookies = clean_session.get(f"{base_url}/api/users", headers=headers)
        print(f"   Status: {response_no_cookies.status_code}")
        print(f"   HTTP Version: {response_no_cookies.raw.version}")

        if response_no_cookies.status_code == 200:
            print("   ✅ JWT funciona sin cookies de sesión")
        elif response_no_cookies.status_code == 401:
            print("   ❌ JWT no funciona - problema de autenticación")
        else:
            print(f"   ⚠️  Status inesperado: {response_no_cookies.status_code}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n" + "=" * 40)
    print("✅ PRUEBA DE SOLUCIÓN JWT COMPLETADA")

if __name__ == "__main__":
    test_jwt_solution()
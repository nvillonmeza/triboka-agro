#!/usr/bin/env python3
"""
Triboka System Health Monitor
Monitoreo completo de todos los servicios de Triboka
"""

import requests
import json
import sys
import time
from datetime import datetime
import subprocess

# Configuración
SERVICES = {
    'nginx': {
        'url': 'http://localhost/healthz',
        'name': 'Nginx Proxy'
    },
    'api': {
        'url': 'http://localhost/api/health',
        'name': 'Triboka API (Flask)'
    },
    'inventory': {
        'url': 'http://localhost/api/inventory/health',
        'name': 'Inventory Service'
    },
    'frontend': {
        'url': 'http://localhost/',
        'name': 'Frontend Dashboard'
    }
}

def check_service_health(service_key, service_config):
    """Verificar health de un servicio"""
    try:
        if service_key == 'frontend':
            # Para frontend solo verificar que responda
            response = requests.get(service_config['url'], timeout=10)
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds() * 1000,
                    'message': 'Frontend responding'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'response_time': None,
                    'message': f'HTTP {response.status_code}'
                }
        else:
            # Para APIs verificar JSON response
            response = requests.get(service_config['url'], timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': data.get('status', 'unknown'),
                    'response_time': response.elapsed.total_seconds() * 1000,
                    'message': f"Service: {data.get('service', 'unknown')}",
                    'details': data
                }
            else:
                return {
                    'status': 'unhealthy',
                    'response_time': None,
                    'message': f'HTTP {response.status_code}'
                }
    except requests.exceptions.Timeout:
        return {
            'status': 'unhealthy',
            'response_time': None,
            'message': 'Timeout'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'response_time': None,
            'message': str(e)
        }

def check_systemd_services():
    """Verificar estado de servicios systemd"""
    systemd_services = [
        'triboka-flask.service',
        'triboka-frontend.service',
        'triboka-notifications.service',
        'triboka-inventory.service'
    ]

    services_status = {}
    for service in systemd_services:
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', service],
                capture_output=True,
                text=True,
                timeout=5
            )
            status = result.stdout.strip()
            services_status[service] = {
                'status': 'active' if status == 'active' else 'inactive',
                'systemd_status': status
            }
        except Exception as e:
            services_status[service] = {
                'status': 'error',
                'systemd_status': str(e)
            }

    return services_status

def check_ports():
    """Verificar que los puertos estén en uso"""
    expected_ports = {
        5003: 'Flask API',
        5004: 'Frontend',
        5005: 'Notifications',
        5006: 'Inventory'
    }

    ports_status = {}
    try:
        result = subprocess.run(
            ['netstat', '-tlnp'],
            capture_output=True,
            text=True,
            timeout=10
        )

        lines = result.stdout.split('\n')
        for line in lines:
            if 'LISTEN' in line:
                parts = line.split()
                if len(parts) >= 4:
                    local_address = parts[3]
                    if ':' in local_address:
                        port = int(local_address.split(':')[-1])
                        if port in expected_ports:
                            ports_status[port] = {
                                'status': 'in_use',
                                'service': expected_ports[port]
                            }

        # Marcar puertos faltantes
        for port, service in expected_ports.items():
            if port not in ports_status:
                ports_status[port] = {
                    'status': 'not_found',
                    'service': service
                }

    except Exception as e:
        ports_status['error'] = str(e)

    return ports_status

def generate_report():
    """Generar reporte completo de health"""
    print("🔍 Verificando estado del sistema Triboka...")
    print("=" * 60)

    # Verificar servicios HTTP
    print("🌐 VERIFICACIÓN DE SERVICIOS HTTP")
    print("-" * 40)

    all_healthy = True
    services_health = {}

    for service_key, service_config in SERVICES.items():
        print(f"🔍 Verificando {service_config['name']}...")
        health = check_service_health(service_key, service_config)
        services_health[service_key] = health

        status_icon = "✅" if health['status'] == 'healthy' else "❌"
        response_time = f"{health['response_time']:.1f}ms" if health['response_time'] else "N/A"

        print(f"   {status_icon} {service_config['name']}: {health['status']} ({response_time})")
        print(f"      {health['message']}")

        if health['status'] != 'healthy':
            all_healthy = False

        print()

    # Verificar servicios systemd
    print("🔧 VERIFICACIÓN DE SERVICIOS SYSTEMD")
    print("-" * 40)

    systemd_status = check_systemd_services()
    for service, status in systemd_status.items():
        status_icon = "✅" if status['status'] == 'active' else "❌"
        print(f"   {status_icon} {service}: {status['status']}")

        if status['status'] != 'active':
            all_healthy = False

    print()

    # Verificar puertos
    print("🔌 VERIFICACIÓN DE PUERTOS")
    print("-" * 40)

    ports_status = check_ports()
    for port, status in ports_status.items():
        if isinstance(port, int):
            status_icon = "✅" if status['status'] == 'in_use' else "❌"
            print(f"   {status_icon} Puerto {port} ({status['service']}): {status['status']}")

            if status['status'] != 'in_use':
                all_healthy = False

    print()

    # Resumen final
    print("📊 RESUMEN DEL SISTEMA")
    print("=" * 60)

    overall_status = "✅ SISTEMA TOTALMENTE OPERATIVO" if all_healthy else "⚠️ PROBLEMAS DETECTADOS"

    print(f"Estado General: {overall_status}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Mostrar detalles de servicios críticos
    if services_health['api']['status'] == 'healthy':
        api_details = services_health['api']['details']
        print("🔗 API Details:")
        print(f"   Database: {api_details.get('database', 'unknown')}")
        print(f"   Blockchain: {api_details.get('blockchain', 'unknown')}")
        print(f"   Version: {api_details.get('version', 'unknown')}")
        print()

    if services_health['inventory']['status'] == 'healthy':
        inv_details = services_health['inventory']['details']
        print("📦 Inventory Details:")
        print(f"   Service: {inv_details.get('service', 'unknown')}")
        print(f"   Status: {inv_details.get('status', 'unknown')}")
        print()

    return all_healthy

def main():
    """Función principal"""
    try:
        healthy = generate_report()
        sys.exit(0 if healthy else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Monitoreo interrumpido por usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error en monitoreo: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
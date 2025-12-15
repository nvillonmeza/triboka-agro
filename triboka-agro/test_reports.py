#!/usr/bin/env python3
"""
Script para probar el endpoint de reportes de analytics
"""
import requests
import json
from datetime import datetime

def test_tenant_reports():
    """Probar los reportes de analytics por tenant"""

    # Configuración
    base_url = "http://localhost:5000"
    headers = {
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsImV4cCI6MTc0MDY5NzYwMH0.example_token',
        'Content-Type': 'application/json'
    }

    # UUIDs de tenants de prueba
    tenants = {
        'triboka': '550e8400-e29b-41d4-a716-446655440001',
        'cooperativa': '550e8400-e29b-41d4-a716-446655440002'
    }

    print("🧪 Probando endpoint de reportes de analytics...\n")

    for tenant_name, tenant_uuid in tenants.items():
        print(f"📊 Generando reporte para {tenant_name.upper()}...")

        try:
            # Reporte mensual
            response = requests.get(
                f"{base_url}/api/analytics/tenant/{tenant_uuid}/reporte",
                headers=headers,
                params={'periodo': 'mes', 'formato': 'json'}
            )

            if response.status_code == 200:
                data = response.json()
                reporte = data.get('reporte', {})

                print("✅ Reporte generado exitosamente")
                print(f"   📅 Período: {reporte['metadata']['periodo']}")
                print(f"   📦 Total lotes: {reporte['resumen_ejecutivo']['total_lotes']}")
                print(f"   ⚖️ Peso total recibido: {reporte['resumen_ejecutivo']['peso_total_recibido_kg']} kg")
                print(f"   🌞 Peso total seco: {reporte['resumen_ejecutivo']['peso_total_seco_kg']} kg")
                print(f"   📉 Merma total: {reporte['resumen_ejecutivo']['merma_total_kg']} kg")
                print(f"   👥 Productores activos: {reporte['resumen_ejecutivo']['productores_activos']}")
                print(f"   📊 Eficiencia global: {reporte['resumen_ejecutivo']['eficiencia_global']}%")
                # KPIs específicos
                if 'kpis_exportadora' in reporte:
                    kpis = reporte['kpis_exportadora']
                    print("   📈 KPIs Exportadora:")
                    print(f"      Producción diaria promedio: {kpis['produccion_diaria_promedio_qq']} QQ")
                    print(f"      Eficiencia secado: {kpis['eficiencia_secado']}%")
                    print(f"      Desviación merma: {kpis['merma_esperada_vs_real']['desviacion']}%")
                elif 'kpis_cooperativa' in reporte:
                    kpis = reporte['kpis_cooperativa']
                    print("   📈 KPIs Cooperativa:")
                    print(f"      Participación productores: {kpis['participacion_productores']}")
                    print(f"      Promedio lotes por productor: {kpis['distribucion_por_productor']['promedio_lotes_por_productor']}")
                    print(f"      Productor más activo: {kpis['distribucion_por_productor']['productor_mas_activo']}")
                    print(f"      Calidad consistente: {kpis['calidad_consistente']}%")
                # Estados de lotes
                print(f"   🔄 Estados de lotes: {reporte['detalle_estados']}")

                print(f"   📋 Detalle de {len(reporte['lotes_detalle'])} lotes incluido\n")

            else:
                print(f"❌ Error {response.status_code}: {response.text}\n")

        except Exception as e:
            print(f"❌ Error de conexión: {str(e)}\n")

    # Probar diferentes períodos
    print("🕐 Probando diferentes períodos para Triboka...")
    tenant_uuid = tenants['triboka']

    periodos = ['dia', 'semana', 'trimestre']
    for periodo in periodos:
        try:
            response = requests.get(
                f"{base_url}/api/analytics/tenant/{tenant_uuid}/reporte",
                headers=headers,
                params={'periodo': periodo, 'formato': 'json'}
            )

            if response.status_code == 200:
                data = response.json()
                reporte = data.get('reporte', {})
                print(f"✅ Reporte {periodo}: {reporte['resumen_ejecutivo']['total_lotes']} lotes")
            else:
                print(f"❌ Error en período {periodo}: {response.status_code}")

        except Exception as e:
            print(f"❌ Error en período {periodo}: {str(e)}")

    print("\n🎉 Pruebas de reportes completadas!")

if __name__ == "__main__":
    test_tenant_reports()
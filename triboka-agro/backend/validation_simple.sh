#!/bin/bash
# validation_simple.sh - Validación simplificada de Fase 1

echo "🔍 VALIDACIÓN SIMPLIFICADA - FASE 1 TRIBOKA"
echo "==========================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "📁 VERIFICACIÓN DE DOCUMENTACIÓN"
echo "--------------------------------"

docs=(
    "fase_1_planificacion/arquitectura_tecnica.md"
    "fase_1_planificacion/especificaciones_apis.md"
    "fase_1_planificacion/plan_seguridad_compliance.md"
    "fase_1_planificacion/diagramas_uml_modelos.md"
    "fase_1_planificacion/estrategia_despliegue_devops.md"
    "fase_1_planificacion/especificaciones_roles_permisos.md"
    "fase_1_planificacion/FASE_1_COMPLETADA.md"
    "README_DOCUMENTACION_COMPLETA.md"
)

doc_count=0
for doc in "${docs[@]}"; do
    if [ -f "/home/rootpanel/web/app.triboka.com/backend/documentacion_tecnica_triboka/$doc" ]; then
        echo -e "✅ $doc"
        ((doc_count++))
    else
        echo -e "❌ $doc"
    fi
done

echo ""
echo "🔧 VERIFICACIÓN DE SERVICIOS"
echo "----------------------------"

services=(
    "triboka-flask.service"
    "triboka-agro-frontend.service"
    "nginx"
)

service_count=0
for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo -e "✅ $service"
        ((service_count++))
    else
        echo -e "❌ $service"
    fi
done

echo ""
echo "🌐 VERIFICACIÓN DE ACCESIBILIDAD"
echo "--------------------------------"

urls=(
    "https://app.triboka.com/api/health|API Backend"
    "https://app.triboka.com/health|Frontend Dashboard"
    "https://app.triboka.com/|Nginx Proxy"
)

url_count=0
for url_entry in "${urls[@]}"; do
    IFS='|' read -r url name <<< "$url_entry"
    if curl -k -s --max-time 5 "$url" > /dev/null 2>&1; then
        echo -e "✅ $name"
        ((url_count++))
    else
        echo -e "❌ $name"
    fi
done

echo ""
echo "💾 VERIFICACIÓN DE BASE DE DATOS"
echo "--------------------------------"

if [ -f "/home/rootpanel/web/app.triboka.com/instance/triboka_production.db" ]; then
    echo -e "✅ Base de datos SQLite existe"
    db_exists=1
else
    echo -e "❌ Base de datos no encontrada"
    db_exists=0
fi

echo ""
echo "📊 RESULTADOS"
echo "============="

total_checks=$((8 + 3 + 3 + 1))  # docs + services + urls + db
passed_checks=$((doc_count + service_count + url_count + db_exists))

echo "Documentos: $doc_count/8"
echo "Servicios: $service_count/3"
echo "URLs: $url_count/3"
echo "Base de datos: $db_exists/1"
echo ""
echo "Total: $passed_checks/$total_checks verificaciones exitosas"

if [ $passed_checks -ge 14 ]; then
    echo -e "${GREEN}🎉 FASE 1 VALIDADA EXITOSAMENTE${NC}"
    echo "El sistema está listo para proceder con Fase 2"
    exit 0
elif [ $passed_checks -ge 12 ]; then
    echo -e "${YELLOW}⚠️  FASE 1 CASI COMPLETA${NC}"
    echo "Revisar elementos faltantes"
    exit 1
else
    echo -e "${RED}❌ FASE 1 REQUIERE ATENCIÓN${NC}"
    echo "Corregir problemas críticos"
    exit 1
fi
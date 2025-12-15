#!/bin/bash
# Script de verificación de Triboka ERP

echo "🔍 Verificando estructura de Triboka ERP..."
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contadores
PASSED=0
FAILED=0

# Función para verificar archivos
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $2"
        ((FAILED++))
    fi
}

# Función para verificar directorios
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $2"
        ((FAILED++))
    fi
}

echo "📁 Verificando estructura de directorios..."
check_dir "/home/rootpanel/web/app.triboka.com/triboka-erp" "Directorio principal ERP"
check_dir "/home/rootpanel/web/app.triboka.com/triboka-erp/backend" "Backend"
check_dir "/home/rootpanel/web/app.triboka.com/triboka-erp/frontend" "Frontend"
check_dir "/home/rootpanel/web/app.triboka.com/triboka-erp/logs" "Logs"
check_dir "/home/rootpanel/web/app.triboka.com/triboka-erp/backend/modules" "Módulos"
check_dir "/home/rootpanel/web/app.triboka.com/triboka-erp/backend/config" "Configuración"
check_dir "/home/rootpanel/web/app.triboka.com/triboka-erp/frontend/templates" "Templates"
check_dir "/home/rootpanel/web/app.triboka.com/triboka-erp/frontend/static" "Estáticos"
echo ""

echo "📄 Verificando archivos principales..."
check_file "/home/rootpanel/web/app.triboka.com/triboka-erp/app.py" "Aplicación principal"
check_file "/home/rootpanel/web/app.triboka.com/triboka-erp/README.md" "README"
check_file "/home/rootpanel/web/app.triboka.com/triboka-erp/requirements.txt" "Requirements"
check_file "/home/rootpanel/web/app.triboka.com/triboka-erp/backend/config/config.py" "Configuración"
check_file "/home/rootpanel/web/app.triboka.com/triboka-erp/backend/modules/inventory_service.py" "Servicio de inventario"
check_file "/home/rootpanel/web/app.triboka.com/triboka-erp/frontend/templates/index.html" "Template principal"
check_file "/home/rootpanel/web/app.triboka.com/triboka-erp/frontend/templates/inventory.html" "Template inventario"
echo ""

echo "🔧 Verificando scripts y servicios..."
check_file "/home/rootpanel/web/app.triboka.com/start_triboka_erp.sh" "Script inicio ERP"
check_file "/home/rootpanel/web/app.triboka.com/stop_triboka_erp.sh" "Script detener ERP"
check_file "/home/rootpanel/web/app.triboka.com/triboka-erp.service" "Servicio systemd ERP"
echo ""

echo "🔗 Verificando permisos de ejecución..."
if [ -x "/home/rootpanel/web/app.triboka.com/start_triboka_erp.sh" ]; then
    echo -e "${GREEN}✓${NC} Script inicio ERP es ejecutable"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Script inicio ERP no es ejecutable"
    ((FAILED++))
fi

if [ -x "/home/rootpanel/web/app.triboka.com/stop_triboka_erp.sh" ]; then
    echo -e "${GREEN}✓${NC} Script detener ERP es ejecutable"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Script detener ERP no es ejecutable"
    ((FAILED++))
fi
echo ""

echo "🐍 Verificando dependencias Python..."
cd /home/rootpanel/web/app.triboka.com

if [ -d ".venv" ]; then
    source .venv/bin/activate
    
    python3 -c "import flask" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Flask instalado"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Flask no instalado"
        ((FAILED++))
    fi
    
    python3 -c "import flask_cors" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Flask-CORS instalado"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Flask-CORS no instalado"
        ((FAILED++))
    fi
    
    python3 -c "import flask_jwt_extended" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Flask-JWT-Extended instalado"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Flask-JWT-Extended no instalado"
        ((FAILED++))
    fi
else
    echo -e "${YELLOW}⚠${NC} Entorno virtual no encontrado"
fi
echo ""

echo "📊 Resumen:"
echo -e "Verificaciones pasadas: ${GREEN}$PASSED${NC}"
echo -e "Verificaciones falladas: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Triboka ERP está correctamente configurado!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Hay $FAILED verificaciones que requieren atención${NC}"
    exit 1
fi

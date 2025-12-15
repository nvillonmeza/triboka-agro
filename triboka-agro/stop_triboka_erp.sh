#!/bin/bash
# Script para detener Triboka ERP

echo "🛑 Deteniendo Triboka ERP..."

# Leer PIDs si existen
if [ -f "/home/rootpanel/web/app.triboka.com/triboka-erp/erp.pid" ]; then
    ERP_PID=$(cat /home/rootpanel/web/app.triboka.com/triboka-erp/erp.pid)
    if ps -p $ERP_PID > /dev/null 2>&1; then
        echo "🏢 Deteniendo Dashboard ERP (PID: $ERP_PID)..."
        kill $ERP_PID
        echo "✅ Dashboard ERP detenido"
    fi
    rm /home/rootpanel/web/app.triboka.com/triboka-erp/erp.pid
fi

if [ -f "/home/rootpanel/web/app.triboka.com/triboka-erp/inventory.pid" ]; then
    INVENTORY_PID=$(cat /home/rootpanel/web/app.triboka.com/triboka-erp/inventory.pid)
    if ps -p $INVENTORY_PID > /dev/null 2>&1; then
        echo "📦 Deteniendo módulo Inventario (PID: $INVENTORY_PID)..."
        kill $INVENTORY_PID
        echo "✅ Inventario detenido"
    fi
    rm /home/rootpanel/web/app.triboka.com/triboka-erp/inventory.pid
fi

# Intentar matar procesos por puerto si los PIDs no funcionaron
echo "🔍 Verificando procesos en puertos..."
pkill -f "python.*app.py.*5050"
pkill -f "python.*inventory_service.py"

echo "✅ Triboka ERP detenido completamente"

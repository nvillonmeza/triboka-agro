#!/bin/bash

# Script de migración para el sistema de contratos agrícolas
echo "🔄 Migrando a Sistema de Contratos Agrícolas..."

# Hacer backup de la base de datos actual
echo "📦 Creando backup de base de datos..."
cd /home/rootpanel/web/app.triboka.com/backend
cp triboka_test.db triboka_test_backup_$(date +%Y%m%d_%H%M%S).db

# Renombrar aplicación actual
echo "📁 Preparando nueva aplicación..."
mv app_test.py app_test_old.py
mv app_contracts.py app_test.py

# Crear nueva base de datos
echo "🗄️ Creando nueva base de datos..."
rm -f agro_contracts.db
python3 -c "
from app_test import init_db
init_db()
print('✅ Base de datos inicializada')
"

# Reiniciar la aplicación
echo "🔄 Reiniciando aplicación..."
screen -S flask -X quit 2>/dev/null
sleep 2
screen -dmS flask bash -c 'cd /home/rootpanel/web/app.triboka.com/backend && python3 app_test.py'

echo "✅ Migración completada!"
echo "🚀 Aplicación ejecutándose en puerto 5003"
echo "📊 Dashboard: https://app.triboka.com"
echo "🔑 Login: demo@agroexport.com / demo123"
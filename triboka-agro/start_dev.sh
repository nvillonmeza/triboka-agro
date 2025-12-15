#!/bin/bash
# Script para iniciar TRIBOKA Agro en desarrollo local

cd /Users/nestorvillon/Documents/TRIBOKA-APP/triboka-agro

# Activar entorno virtual
source venv/bin/activate

# Ir al directorio backend
cd backend

# Inicializar base de datos si no existe
if [ ! -f "triboka.db" ]; then
    echo "📊 Inicializando base de datos..."
    python init_db_simple.py
fi

# Ejecutar la aplicación
echo "🚀 Iniciando TRIBOKA Agro API en http://localhost:5003"
echo "📧 Usuario demo: demo@agroexport.com"
echo "🔑 Password: demo123"
echo ""
python app_simple.py
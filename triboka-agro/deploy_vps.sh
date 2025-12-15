#!/bin/bash

# TRIBOKA Agro VPS Deployment Script
# Despliegue completo en VPS con dominio agro.triboka.com
# Fecha: 3 de diciembre de 2025

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables de configuración
DOMAIN="agro.triboka.com"
PROJECT_DIR="/opt/triboka-agro"
VENV_DIR="$PROJECT_DIR/venv"
USER="triboka"
DB_PATH="$PROJECT_DIR/triboka_agro.db"

# Función de logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Verificar si estamos ejecutando como root
if [[ $EUID -eq 0 ]]; then
   error "Este script no debe ejecutarse como root. Use un usuario con sudo."
fi

log "🚀 Iniciando despliegue de TRIBOKA Agro en VPS"

# Paso 1: Actualizar sistema
log "📦 Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Paso 2: Instalar dependencias del sistema
log "🔧 Instalando dependencias del sistema..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    wget \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    python3-dev \
    sqlite3 \
    supervisor

# Paso 3: Configurar PostgreSQL
log "🗄️ Configurando PostgreSQL..."
sudo -u postgres createuser --createdb --superuser $USER || warning "Usuario ya existe"
sudo -u postgres createdb -O $USER triboka_agro || warning "Base de datos ya existe"

# Paso 4: Configurar Redis
log "🔄 Configurando Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Paso 5: Crear usuario del proyecto
log "👤 Creando usuario del proyecto..."
sudo useradd -m -s /bin/bash $USER || warning "Usuario ya existe"
sudo usermod -aG sudo $USER

# Paso 6: Clonar o copiar proyecto
log "📁 Configurando directorio del proyecto..."
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR

# Asumiendo que el código está en el directorio actual, copiarlo
if [ -d "./triboka-agro" ]; then
    log "Copiando código del proyecto..."
    sudo cp -r ./triboka-agro/* $PROJECT_DIR/
else
    error "Directorio triboka-agro no encontrado. Asegúrate de tener el código del proyecto."
fi

sudo chown -R $USER:$USER $PROJECT_DIR

# Paso 7: Configurar entorno virtual Python
log "🐍 Configurando entorno virtual Python..."
sudo -u $USER bash -c "cd $PROJECT_DIR && python3 -m venv $VENV_DIR"
sudo -u $USER bash -c "source $VENV_DIR/bin/activate && pip install --upgrade pip"

# Paso 8: Instalar dependencias Python
log "📦 Instalando dependencias Python..."
sudo -u $USER bash -c "cd $PROJECT_DIR && source $VENV_DIR/bin/activate && pip install -r requirements.txt"

# Paso 9: Configurar variables de entorno
log "⚙️ Configurando variables de entorno..."
cat > $PROJECT_DIR/.env << EOF
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=postgresql://$USER@localhost/triboka_agro
REDIS_URL=redis://localhost:6379/0
DOMAIN=$DOMAIN
JWT_SECRET_KEY=$(openssl rand -hex 32)
BLOCKCHAIN_RPC_URL=https://polygon-rpc.com/
BLOCKCHAIN_PRIVATE_KEY=your_private_key_here
YAHOO_FINANCE_API_KEY=your_yahoo_key_here
EOF

sudo chown $USER:$USER $PROJECT_DIR/.env
sudo chmod 600 $PROJECT_DIR/.env

# Paso 10: Inicializar base de datos
log "🗄️ Inicializando base de datos..."
sudo -u $USER bash -c "cd $PROJECT_DIR && source $VENV_DIR/bin/activate && python init_database.py"

# Paso 11: Crear datos de prueba
log "📊 Creando datos de prueba..."
sudo -u $USER bash -c "cd $PROJECT_DIR && source $VENV_DIR/bin/activate && python init_test_data.py"

# Paso 12: Configurar servicios systemd
log "🔧 Configurando servicios systemd..."

# Servicio Flask
sudo tee /etc/systemd/system/triboka-agro.service > /dev/null << EOF
[Unit]
Description=TRIBOKA Agro Flask Application
After=network.target postgresql.service redis.service

[Service]
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/flask run --host=0.0.0.0 --port=5003
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Servicio Celery Worker
sudo tee /etc/systemd/system/triboka-celery.service > /dev/null << EOF
[Unit]
Description=TRIBOKA Agro Celery Worker
After=network.target redis.service

[Service]
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/celery -A app.celery worker --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Servicio Celery Beat
sudo tee /etc/systemd/system/triboka-celery-beat.service > /dev/null << EOF
[Unit]
Description=TRIBOKA Agro Celery Beat
After=network.target redis.service

[Service]
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/celery -A app.celery beat --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Paso 13: Configurar Nginx
log "🌐 Configurando Nginx..."
sudo tee /etc/nginx/sites-available/$DOMAIN > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location = /favicon.ico { access_log off; log_not_found off; }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:5003;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $PROJECT_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Paso 14: Configurar SSL con Let's Encrypt
log "🔒 Configurando SSL con Let's Encrypt..."
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Paso 15: Iniciar servicios
log "▶️ Iniciando servicios..."
sudo systemctl daemon-reload
sudo systemctl enable triboka-agro
sudo systemctl enable triboka-celery
sudo systemctl enable triboka-celery-beat
sudo systemctl start triboka-agro
sudo systemctl start triboka-celery
sudo systemctl start triboka-celery-beat

# Paso 16: Configurar firewall
log "🔥 Configurando firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Paso 17: Configurar monitoreo básico
log "📊 Configurando monitoreo básico..."
sudo tee /etc/cron.d/triboka-monitor > /dev/null << EOF
*/5 * * * * $USER cd $PROJECT_DIR && source $VENV_DIR/bin/activate && python monitor_system.py
EOF

# Paso 18: Verificar despliegue
log "✅ Verificando despliegue..."
sleep 10

if curl -s -o /dev/null -w "%{http_code}" http://localhost:5003/health | grep -q "200"; then
    log "✅ TRIBOKA Agro desplegado exitosamente!"
    log "🌐 URL: https://$DOMAIN"
    log "📊 Dashboard: https://$DOMAIN/dashboard"
    log "🔑 API Docs: https://$DOMAIN/api/docs"
else
    error "❌ Error en el despliegue. Verifica los logs."
fi

# Paso 19: Instrucciones finales
log "📋 Próximos pasos:"
echo "1. Configura el DNS para que $DOMAIN apunte a $(curl -s ifconfig.me)"
echo "2. Actualiza las claves API en $PROJECT_DIR/.env"
echo "3. Configura el wallet blockchain si es necesario"
echo "4. Ejecuta pruebas: python test_api_lots.py"
echo "5. Monitorea logs: sudo journalctl -u triboka-agro -f"

log "🎉 ¡Despliegue completado!"</content>
<parameter name="filePath">/Users/nestorvillon/Documents/TRIBOKA-APP/triboka-agro/deploy_vps.sh
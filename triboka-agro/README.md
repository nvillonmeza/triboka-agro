# 🌐 Triboka BaaS Platform - Documentación Técnica

## 📋 Información General

**Triboka BaaS (Blockchain-as-a-Service)** es una plataforma integral para la trazabilidad y gestión de productos agrícolas de exportación, con integración blockchain para certificaciones NFT.

### 🎯 Características Principales
- ✅ Gestión de empresas y usuarios
- ✅ Trazabilidad de productos agrícolas
- ✅ Certificaciones digitales NFT
- ✅ Dashboard de analytics
- ✅ API RESTful completa
- ✅ Autenticación JWT
- ✅ Base de datos SQLite
- ✅ **🆕 ERP Completo Multi-Módulo**
- ✅ **Módulo de Despacho y Logística**
- ✅ **Módulo de Compras y Ventas**
- ✅ **Módulo de Dashboard Analytics**
- ✅ **Arquitectura SaaS Multi-Tenant**
- ✅ **Backend Operativo 100%**

---

## � URLs de Acceso

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Página Principal** | https://app.triboka.com | Landing page y acceso al sistema |
| **Dashboard** | https://app.triboka.com/dashboard.html | Panel de control empresarial |
| **API Base** | https://app.triboka.com/api | Endpoints de la API |
| **Estado API** | https://app.triboka.com/status.html | Monitoreo del estado de la API |
| **🆕 ERP Backend** | http://erp.triboka.com:5007 | Backend ERP completo (Despacho, Compras, Dashboard) |
| **🆕 ERP Health** | http://erp.triboka.com:5007/health | Estado de salud del ERP |
| **🆕 ERP API Docs** | http://erp.triboka.com:5007/api/despacho/test | Test endpoint del módulo despacho |

---

## 🔐 Credenciales de Acceso

### 👤 Usuario Demo - Empresa AgroExport
```
Email:    demo@agroexport.com
Password: demo123
Empresa:  AgroExport Demo S.A.
Rol:      Administrador
```

### 🏢 Datos de la Empresa Demo
```
Nombre:        AgroExport Demo S.A.
Tipo:          Exportador de productos agrícolas
RUC/NIT:       20123456789
Teléfono:      +51 1 234-5678
Email:         info@agroexport.com
Dirección:     Av. Exportadores 123, Lima, Perú
Website:       https://agroexport.com
Productos:     Cacao, Café, Quinua, Aguacate
```

---

## 🔧 Configuración Técnica

### 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   nginx Proxy   │    │   Backend API   │
│   (HTML/JS)     │◄───┤   (SSL/HTTPS)   │◄───┤   (Flask/Python)│
│   Port: 443     │    │   Port: 443     │    │   Port: 5003    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   SQLite DB     │
                       │   (Local)       │
                       └─────────────────┘
```

### 📁 Estructura de Directorios

```
/home/rootpanel/web/app.triboka.com/
├── backend/                    # Backend API (Flask)
│   ├── app_test.py            # Aplicación principal
│   ├── start_api.py           # Script de inicio
│   ├── models_simple.py       # Modelos de base de datos
│   ├── triboka.db            # Base de datos SQLite
│   ├── venv/                 # Entorno virtual Python
│   └── requirements.txt      # Dependencias Python
├── public_html/              # Frontend web
│   ├── index.html           # Landing page
│   ├── dashboard.html       # Dashboard empresarial
│   ├── status.html          # Página de estado API
│   ├── debug_api.html       # Herramienta de debug
│   └── test_api.html        # Herramienta de testing
└── README.md                # Esta documentación
```

### 🐍 Backend (Flask API)

**Ubicación:** `/home/rootpanel/web/app.triboka.com/backend/`
**Puerto:** `5003`
**Proceso:** Ejecutándose en screen session `triboka_api`

#### Dependencias Python
```bash
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-JWT-Extended==4.5.3
Flask-CORS==4.0.0
Werkzeug==3.0.1
```

#### Comando de Inicio
```bash
cd /home/rootpanel/web/app.triboka.com/backend/
source venv/bin/activate
python start_api.py 5003
```

#### Estado del Servicio
```bash
# ✅ TRIBOKA ERP BACKEND - 100% OPERATIVO
# Servicio: triboka-erp-backend
# Puerto: 5007
# URL: http://erp.triboka.com:5007
# Estado: ✅ Activo y funcionando

# Verificar estado del servicio
sudo systemctl status triboka-erp-backend

# Verificar procesos
ps aux | grep python3 | grep app_cacao

# Verificar puerto
ss -tulpn | grep 5007

# Test de conectividad
curl -s http://localhost:5007/health
curl -s http://localhost:5007/api/despacho/test
```

### 🎯 Estado Actual del Sistema

| Componente | Estado | Puerto | URL |
|------------|--------|--------|-----|
| **Triboka ERP Backend** | ✅ 100% Completo | 5007 | http://erp.triboka.com:5007 |
| **Módulo Despacho** | ✅ Registrado | - | /api/despacho/* |
| **Módulo Compras/Ventas** | ✅ Registrado | - | /api/compras-ventas/* |
| **Módulo Dashboard** | ✅ Registrado | - | /api/dashboard/* |
| **Base de Datos ERP** | ✅ SQLite | - | /triboka-erp/instance/triboka_erp.db |
| **Servicio Systemd** | ✅ Configurado | - | triboka-erp-backend.service |

### 📊 Módulos ERP Implementados

#### ✅ Módulo de Despacho (23 rutas)
- Gestión de carriers y transportistas
- Vehículos y rutas de transporte
- Seguimiento GPS en tiempo real
- Órdenes de despacho y logística

#### ✅ Módulo de Compras y Ventas
- Gestión de clientes y proveedores
- Contratos de compra y venta
- Recepción de contratos
- Batches de exportación

#### ✅ Módulo de Dashboard Analytics
- KPIs en tiempo real
- Analytics por tenant
- Tendencias históricas
- Reportes de eficiencia
- Comparativos globales

### 🌐 Configuración nginx

**Archivo de configuración:** `/etc/nginx/conf.d/domains/app.triboka.com.conf`

#### Configuración SSL y Proxy
```nginx
server {
    listen 443 ssl http2;
    server_name app.triboka.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/app.triboka.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.triboka.com/privkey.pem;
    
    # Document Root
    root /home/rootpanel/web/app.triboka.com/public_html;
    index index.html;
    
    # API Proxy to Backend
    location /api/ {
        proxy_pass http://127.0.0.1:5003/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS Headers
        add_header Access-Control-Allow-Origin "https://app.triboka.com" always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS, PUT, DELETE" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
        
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }
}
```

---

## � API Endpoints

### 🏥 Sistema
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Estado de salud de la API |
| GET | `/api/info` | Información de la plataforma |

### 🔐 Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/register` | Registro de usuario |
| POST | `/api/auth/login` | Inicio de sesión |

### 🏢 Empresas
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/companies/profile` | Perfil de empresa |

### 📦 Productos/Lotes
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/lots` | Listar productos |
| POST | `/api/lots` | Crear producto |

### 🏆 Certificaciones NFT
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/nfts` | Listar certificados NFT |
| POST | `/api/nfts/create` | Crear certificado NFT |

### 📊 Analytics
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard` | Métricas generales del dashboard |
| GET | `/api/analytics/dashboard/{tenant_uuid}` | Dashboard específico por tenant |
| GET | `/api/analytics/tenant/{tenant_uuid}/tendencias` | Tendencias históricas |
| GET | `/api/analytics/tenant/{tenant_uuid}/eficiencia` | Métricas de eficiencia |
| GET | `/api/analytics/tenant/{tenant_uuid}/comparativo` | Comparativo global |
| GET | `/api/analytics/tenant/{tenant_uuid}/reporte` | Reporte completo |

---

## 🧪 Datos de Prueba

### 📦 Productos Demo Disponibles

#### 1. Cacao Premium Orgánico
```json
{
  "id": 1,
  "product_name": "Cacao Premium Orgánico",
  "origin": "Valle del Huallaga, Perú",
  "quantity": 1000,
  "unit": "kg",
  "quality_grade": "Premium",
  "harvest_date": "2024-08-15",
  "certifications": ["Orgánico", "Fair Trade"],
  "price_per_unit": 8.50
}
```

#### 2. Café Especial Altura
```json
{
  "id": 2,
  "product_name": "Café Especial Altura",
  "origin": "Chanchamayo, Perú",
  "quantity": 500,
  "unit": "kg",
  "quality_grade": "Especial",
  "harvest_date": "2024-09-10",
  "certifications": ["UTZ", "Rainforest Alliance"],
  "price_per_unit": 12.00
}
```

#### 3. Quinua Blanca Real
```json
{
  "id": 3,
  "product_name": "Quinua Blanca Real",
  "origin": "Altiplano, Bolivia",
  "quantity": 250,
  "unit": "kg",
  "quality_grade": "Premium",
  "harvest_date": "2024-07-20",
  "certifications": ["Orgánico"],
  "price_per_unit": 6.80
}
```

#### 4. Aguacate Hass
```json
{
  "id": 4,
  "product_name": "Aguacate Hass",
  "origin": "La Libertad, Perú",
  "quantity": 2000,
  "unit": "kg",
  "quality_grade": "Exportación",
  "harvest_date": "2024-10-05",
  "certifications": ["Global GAP"],
  "price_per_unit": 3.20
}
```

### 🏆 Certificados NFT Demo

1. **Certificado de Origen - Cacao Premium** (Token ID: #001)
2. **Certificado de Calidad - Café Especial** (Token ID: #002)
3. **Certificado Fair Trade - Quinua Real** (Token ID: #003)

---

## 🔧 Comandos de Administración

### � Iniciar/Reiniciar API
```bash
# Cambiar al directorio backend
cd /home/rootpanel/web/app.triboka.com/backend/

# Activar entorno virtual
source venv/bin/activate

# Método 1: Inicio directo
python start_api.py 5003

# Método 2: Con screen (recomendado para producción)
screen -dmS triboka_api bash -c "source venv/bin/activate && python start_api.py 5003"
```

### 🔄 Reiniciar nginx
```bash
# Recargar configuración
sudo systemctl reload nginx

# Reiniciar servicio completo
sudo systemctl restart nginx

# Verificar estado
sudo systemctl status nginx
```

### 📊 Monitoreo del Sistema
```bash
# Verificar API funcionando
curl -k -s https://app.triboka.com/api/health

# Verificar procesos Python
ps aux | grep python | grep 5003

# Verificar puertos abiertos
ss -tulpn | grep 5003

# Ver logs de nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 💾 Base de Datos
```bash
# Ubicación de la base de datos
/home/rootpanel/web/app.triboka.com/backend/triboka.db

# Backup de la base de datos
cp /home/rootpanel/web/app.triboka.com/backend/triboka.db \
   /home/rootpanel/backups/triboka_db_$(date +%Y%m%d_%H%M%S).db

# Acceder a la base de datos (SQLite)
sqlite3 /home/rootpanel/web/app.triboka.com/backend/triboka.db
```

---

## 🐛 Troubleshooting

### ❌ Problemas Comunes

#### 1. API no responde
```bash
# Verificar proceso
ps aux | grep start_api
# Si no existe, reiniciar:
cd /home/rootpanel/web/app.triboka.com/backend/
screen -dmS triboka_api bash -c "source venv/bin/activate && python start_api.py 5003"
```

#### 2. Error 502 Bad Gateway
```bash
# Verificar que la API esté ejecutándose en puerto 5003
ss -tulpn | grep 5003
# Verificar configuración nginx
sudo nginx -t
sudo systemctl reload nginx
```

#### 3. CORS Errors
```bash
# Verificar configuración CORS en nginx
sudo nano /etc/nginx/conf.d/domains/app.triboka.com.conf
# Buscar las líneas add_header Access-Control-Allow-*
```

#### 4. Mixed Content Policy
- Asegurar que todas las URLs usen `https://app.triboka.com/api`
- Nunca usar `http://147.93.185.25:5003` directamente en el frontend

### 📞 Verificación de Estado
```bash
# Test completo del sistema
curl -k -s https://app.triboka.com/api/health && echo "✅ API Health OK"
curl -k -s https://app.triboka.com/api/api/info | jq .name && echo "✅ API Info OK"
nginx -t && echo "✅ Nginx Config OK"
```

---

## 📈 Métricas del Dashboard

### 📊 Datos Actuales (Demo)
- **Total Productos:** 4 lotes registrados
- **Valor Total:** $67,940.00 USD
- **Certificados NFT:** 3 activos
- **Última Actualización:** Automática

### 🎯 KPIs Disponibles
- Distribución por tipo de producto
- Valor total del inventario
- Certificaciones por tipo
- Cronología de productos
- Estados de calidad

---

## � Seguridad

### 🛡️ Medidas Implementadas
- ✅ HTTPS obligatorio (SSL/TLS)
- ✅ Autenticación JWT
- ✅ CORS configurado correctamente
- ✅ Proxy reverso nginx
- ✅ Headers de seguridad

### � Rotación de Tokens
- Los tokens JWT tienen duración limitada
- Se requiere re-autenticación periódica
- Logout invalida tokens del lado cliente

---

## � Soporte Técnico

### 🛠️ Información del Sistema
- **OS:** Linux (Ubuntu/Debian based)
- **Web Server:** nginx
- **Backend:** Python 3.x + Flask
- **Database:** SQLite
- **SSL:** Let's Encrypt
- **Proxy:** nginx reverse proxy

### � Contacto
Para soporte técnico o consultas sobre la plataforma:
- **Plataforma:** https://app.triboka.com
- **Estado API:** https://app.triboka.com/status.html
- **Documentación:** Este archivo README.md

---

## 📝 Changelog

### v2.1.0 (Noviembre 2025) - ERP BACKEND 100% COMPLETO
- ✅ **ERP Backend completamente operativo** en puerto 5007
- ✅ **Módulo de Despacho**: 23 rutas implementadas (carriers, vehículos, rutas, tracking GPS)
- ✅ **Módulo de Compras y Ventas**: Clientes, contratos, batches de exportación
- ✅ **Módulo de Dashboard Analytics**: KPIs, tendencias, eficiencia, comparativos
- ✅ **Servicio Systemd configurado** y funcionando automáticamente
- ✅ **PYTHONPATH corregido** para importaciones de módulos
- ✅ **Base de datos ERP dedicada** con modelos completos
- ✅ **Arquitectura modular** con registro dinámico de blueprints
- ✅ **API Health check** y endpoints de prueba funcionales
- ✅ **Documentación actualizada** con estado actual del sistema

### v2.0.0 (Noviembre 2025)
- ✅ Implementación completa de Triboka ERP Multi-Tenant
- ✅ Dashboard Analytics por Tenant con KPIs específicos
- ✅ Arquitectura SaaS con aislamiento de datos
- ✅ Endpoints de tendencias, eficiencia y reportes avanzados
- ✅ Servicio ERP Backend en puerto 5007
- ✅ Base de datos SQLite con tenant_id en todas las tablas
- ✅ Sistema de reportes JSON con filtros por período
- ✅ Comparativos globales y percentiles por tenant

### v1.0.0 (Noviembre 2024)
- ✅ Implementación inicial de la API
- ✅ Frontend completo con dashboard
- ✅ Sistema de autenticación JWT
- ✅ Base de datos SQLite
- ✅ Configuración nginx con SSL
- ✅ Datos demo para pruebas
- ✅ Resolución de Mixed Content Policy
- ✅ Documentación completa

---

*Última actualización: 14 de Noviembre, 2025*
*Versión de la documentación: 2.1.0*
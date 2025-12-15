# 🏗️ ARQUITECTURA TÉCNICA TRIBOKA

## 📋 Información Técnica del Sistema

### Despliegue y Servidor
- **Estado**: Sistema desplegado y operativo en producción ✅
- **Servidor Web**: Nginx como proxy reverso con SSL (HTTPS obligatorio) ✅
- **Dirección Pública**: https://app.triboka.com ✅
- **Configuración Nginx**: nginx_complete_system.conf (escucha en 147.93.185.25:443, redirige HTTP a HTTPS) ✅
- **Archivos Estáticos**: Servidos directamente por nginx desde /home/rootpanel/web/app.triboka.com/frontend/static/ ✅
- **Seguridad**: Headers de seguridad (X-Frame-Options, X-Content-Type-Options, etc.), HSTS, WebSocket support ✅

### Servicios Systemctl ✅
- **Backend API**: Servicio `triboka-flask.service` (Flask + SQLAlchemy + JWT + Web3.py)
- **Frontend Dashboard**: Servicio `triboka-frontend.service` (HTML/Bootstrap + JavaScript)
- **ERP Backend**: Servicio `triboka-erp-backend.service` (puerto 5007)
- **ERP Frontend**: Servicio `triboka-erp-frontend.service` (puerto 5051)
- **Gestión de Servicios**: systemctl start/stop/restart/status para cada componente

### Puertos Internos (Backend/Frontend) ✅
- **Backend API Principal**: Puerto interno **5003** (accesible via nginx en `https://app.triboka.com/api/`)
- **Frontend Dashboard Principal**: Puerto interno **5004** (accesible via nginx en `https://app.triboka.com/`)
- **ERP Backend**: Puerto interno **5007**
- **ERP Frontend**: Puerto interno **5051**
- **Base de datos**: SQLite (única instancia compartida en /home/rootpanel/web/app.triboka.com/backend/)

### Arquitectura Actual ✅
- **Backend Principal**: Flask + SQLAlchemy + JWT + Web3.py (servicio systemctl en puerto 5003)
- **Frontend Principal**: HTML/Bootstrap + JavaScript (servicio systemctl en puerto 5004)
- **ERP Backend**: Flask + SQLAlchemy (servicio systemctl en puerto 5007)
- **ERP Frontend**: HTML/Bootstrap + JavaScript (servicio systemctl en puerto 5051)
- **Blockchain**: Polygon testnet/mainnet para trazabilidad
- **Base de datos**: SQLite con modelos relacionales (instancia compartida)
- **Proxy Reverso**: Nginx maneja SSL, redirecciones, balanceo de carga y enrutamiento a servicios internos
- **Gestión**: Todos los componentes corren como servicios systemctl independientes con auto-restart

### Endpoints Principales (Accesibles via HTTPS) ✅
- Autenticación: `https://app.triboka.com/api/login`, `/api/register`, `/api/profile`
- Lotes: `https://app.triboka.com/api/lots` (GET/POST), `/api/lots/{id}` (GET/PUT)
- Contratos: `https://app.triboka.com/api/contracts` (GET/POST), `/api/contracts/{id}` (GET)
- Batches: `https://app.triboka.com/api/batches` (GET/POST), `/api/batches/{id}` (GET)
- Deals: `https://app.triboka.com/api/deals` (GET/POST), `/api/deals/{id}` (GET) ✅ **Implementado**
- Contextos: `https://app.triboka.com/api/auth/context`, `/api/auth/change-context` ✅ **Implementado**

---

## 🏛️ Arquitectura General

### Arquitectura Multi-Nivel
```
Triboka Master (Admin Global)
├── Empresas (sucacao.triboka.com)
│   ├── ERP Backend (puerto 5007)
│   ├── ERP Frontend (puerto 5051)
│   └── Base de datos independiente
└── Productores (Triboka Agro)
    ├── Portal Productores (puerto 5004)
    └── Trazabilidad Blockchain
```

### Tecnologías Implementadas
- **Backend**: Python 3.12, Flask 3.0, SQLAlchemy
- **Frontend**: HTML5, Bootstrap 5, JavaScript ES6+
- **Base de Datos**: SQLite (preparado para PostgreSQL)
- **Autenticación**: JWT con sesiones Flask
- **Blockchain**: Web3.py, Polygon Network
- **Servidor**: Nginx, Systemd, SSL/TLS
- **Monitoreo**: Zabbix (parcial)

---

**Estado**: ✅ IMPLEMENTADO Y OPERATIVO EN PRODUCCIÓN</content>
<parameter name="filePath">/home/rootpanel/web/app.triboka.com/backend/documentacion_tecnica_triboka/fase_1_planificacion/arquitectura_tecnica.md
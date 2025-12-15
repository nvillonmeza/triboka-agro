# Arquitectura de Servicios Triboka - Estado Actual

## Servicios Systemctl Activos

### Backend API Principal
- **Servicio**: `triboka-flask.service`
- **Tecnología**: Flask + SQLAlchemy + JWT + Web3.py
- **Puerto**: 5003
- **URL**: `https://app.triboka.com/api/`
- **Estado**: ✅ Activo

### Frontend Triboka Agro
- **Servicio**: `triboka-agro-frontend.service`
- **Tecnología**: Next.js + React + TypeScript + Tailwind CSS
- **Puerto**: 3001
- **URL**: `https://app.triboka.com/`
- **Estado**: ✅ Activo

### Frontend Triboka (Legacy)
- **Servicio**: `triboka-nextjs-frontend.service`
- **Tecnología**: Next.js + React
- **Puerto**: 3000
- **URL**: `https://triboka.com/` (o subdominio específico)
- **Estado**: ✅ Activo

### ERP Backend
- **Servicio**: `triboka-erp-backend.service`
- **Tecnología**: Flask + SQLAlchemy + JWT
- **Puerto**: 5007
- **URL**: `https://app.triboka.com/erp/api/`
- **Estado**: ✅ Activo

### ERP Frontend
- **Servicio**: `triboka-erp-frontend.service`
- **Tecnología**: Flask + Bootstrap 5 + JavaScript
- **Puerto**: 5051
- **URL**: `https://app.triboka.com/erp/`
- **Estado**: ✅ Activo

## Gestión de Servicios
Para gestionar estos servicios, usar:
```bash
sudo systemctl start/stop/restart/status [servicio]
```

Ejemplos:
- `sudo systemctl status triboka-flask.service`
- `sudo systemctl restart triboka-agro-frontend.service`

## Arquitectura de Red
- **Dominio Principal**: `app.triboka.com` (Triboka Agro)
- **Dominio ERP**: `erp.triboka.com` (sistema ERP)
- **Dominio Legacy**: `triboka.com` (sistema anterior)

## Configuración Nginx
La configuración actual en `/etc/nginx/conf.d/app.triboka.com.conf` maneja:
- Proxy reverso para todos los servicios
- SSL/TLS termination
- Enrutamiento basado en paths
- Servir archivos estáticos

## Estado de Verificación
✅ Todos los servicios verificados y funcionando correctamente
✅ Puertos correctos asignados
✅ URLs de frontend citadas sin localhost
✅ Arquitectura documentada completamente

# 🚀 Guía de Despliegue: Infraestructura Centralizada TRIBOKA

Esta guía te llevará paso a paso para desplegar el ecosistema unificado en tu VPS.

## 📋 Prerrequisitos
1.  **VPS** con Ubuntu 20.04/22.04 LTS (limpio preferiblemente).
2.  **Dominio** (`triboka.com`) con acceso al panel DNS.
3.  **Cliente SSH** para conectar a tu VPS.

## 🛠️ Paso 1: Configuración de DNS
Antes de tocar el servidor, configura los siguientes registros tipo **A** en tu proveedor de dominio apuntando a la **IP Pública de tu VPS**:

| Tipo | Host | Valor | Propósito |
| :--- | :--- | :--- | :--- |
| A | `auth` | `[IP_DEL_VPS]` | Login Unificado (Keycloak) |
| A | `api` | `[IP_DEL_VPS]` | Backend App Móvil |
| A | `erp` | `[IP_DEL_VPS]` | Sistema ERP |
| A | `agro` | `[IP_DEL_VPS]` | Sistema Web |
| A | `proxy` | `[IP_DEL_VPS]` | Panel de Administración Nginx |

*(Espera unos minutos a que se propaguen)*

## 🐳 Paso 2: Instalación de Docker en el VPS
Conéctate por SSH y ejecuta estos comandos uno por uno:

```bash
# 1. Actualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Eliminar script
rm get-docker.sh

# 4. Instalar Docker Compose (si no vino con docker)
sudo apt install docker-compose-plugin -y
```

## 🏗️ Paso 3: Despliegue del "Núcleo"
Crearemos la carpeta del proyecto y el archivo maestro.

```bash
# Crear directorio
sudo mkdir -p /opt/triboka-stack
cd /opt/triboka-stack

# Crear archivo docker-compose.yml
sudo nano docker-compose.yml
```

**Copia y pega el siguiente contenido en el editor `nano`.** (Usa `Ctrl+O` para guardar y `Ctrl+X` para salir).

```yaml
version: '3.8'

networks:
  triboka-net:
    driver: bridge

volumes:
  postgres_data:
  keycloak_data:
  npm_data:
  npm_le:

services:
  # ----------------------------------------------------
  # 1. BASE DE DATOS CENTRAL (PostgreSQL)
  # ----------------------------------------------------
  db:
    image: postgres:15
    container_name: triboka_db
    restart: always
    environment:
      POSTGRES_USER: triboka_admin
      POSTGRES_PASSWORD: CambiarEstaPasswordSegura123!
      POSTGRES_DB: keycloak
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - triboka-net

  # ----------------------------------------------------
  # 2. PROXY INVERSO (Nginx Proxy Manager)
  # ----------------------------------------------------
  npm:
    image: 'jc21/nginx-proxy-manager:latest'
    container_name: triboka_proxy
    restart: unless-stopped
    ports:
      - '80:80'     # HTTP
      - '81:81'     # Panel de Admin
      - '443:443'   # HTTPS
    volumes:
      - npm_data:/data
      - npm_le:/etc/letsencrypt
    networks:
      - triboka-net

  # ----------------------------------------------------
  # 3. IDENTITY PROVIDER (Keycloak)
  # ----------------------------------------------------
  keycloak:
    image: quay.io/keycloak/keycloak:22.0
    container_name: triboka_auth
    command: start-dev --import-realm # Modo Dev para inicio fácil, Prod proxied=edge
    environment:
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://db:5432/keycloak
      KC_DB_USERNAME: triboka_admin
      KC_DB_PASSWORD: CambiarEstaPasswordSegura123!
      KC_HOSTNAME: auth.triboka.com # CAMBIAR POR TU DOMINIO REAL
      KC_PROXY: edge
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: AdminPassword123!
    depends_on:
      - db
    networks:
      - triboka-net

  # ----------------------------------------------------
  # 4. APP BACKEND (Placeholder - Backend Python)
  # ----------------------------------------------------
  app_backend:
    image: python:3.9-slim
    container_name: triboka_app_backend
    # En el futuro, aquí harás un 'build: .' de tu código
    # Por ahora, usamos un servidor simple para probar que funciona
    command: python -m http.server 5000
    expose:
      - "5000"
    networks:
      - triboka-net

  # ----------------------------------------------------
  # 5. ERP (Ejemplo con Odoo 16)
  # ----------------------------------------------------
  erp:
    image: odoo:16.0
    container_name: triboka_erp
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      - HOST=db
      - USER=triboka_admin
      - PASSWORD=CambiarEstaPasswordSegura123!
    networks:
      - triboka-net
```

### Iniciar Servicios
```bash
sudo docker compose up -d
```
*Si todo sale bien, verás "Started" en verde para todos los servicios.*

## 🚦 Paso 4: Configurar los Dominios (HTTPS)

1.  Abre tu navegador y ve a `http://[IP_DEL_VPS]:81`.
2.  Entra al **Nginx Proxy Manager**:
    *   **Email:** `admin@example.com`
    *   **Password:** `changeme`
    *   *(Te pedirá cambiar esto inmediatamente)*.
3.  **Añadir Proxy Hosts:**
    Ve a "Proxy Hosts" > "Add Proxy Host" y crea uno para cada servicio:

    **Para Keycloak (Auth):**
    *   Domain Names: `auth.triboka.com`
    *   Scheme: `http`
    *   Forward Hostname: `keycloak` (nombre del servicio en docker)
    *   Forward Port: `8080`
    *   **Pestaña SSL:** Request a new SSL Certificate (Let's Encrypt), Force SSL, HTTP/2.

    **Para App Backend (API):**
    *   Domain Names: `api.triboka.com`
    *   Forward Hostname: `app_backend`
    *   Forward Port: `5000`
    *   **Pestaña SSL:** Request new SSL.

    **Para ERP:**
    *   Domain Names: `erp.triboka.com`
    *   Forward Hostname: `erp`
    *   Forward Port: `8069`
    *   **Pestaña SSL:** Request new SSL.

## ✅ Paso 5: Verificación Final

1.  Entra a `https://auth.triboka.com` -> Deberías ver la consola de administración de Keycloak.
2.  Entra a `https://api.triboka.com` -> Deberías ver la respuesta del servidor Python simple.
3.  **Tu App Flutter:** Ya está configurada para apuntar a estos dominios. Al principio fallará la conexión real (porque el backend es un placeholder), **activando automáticamente el Modo Simulación** que programamos. ¡Magia! ✨

---
> **Nota de Seguridad:** En el `docker-compose.yml`, cambia todas las contraseñas (`POSTGRES_PASSWORD`, `KEYCLOAK_ADMIN_PASSWORD`) por unas reales antes de desplegar.

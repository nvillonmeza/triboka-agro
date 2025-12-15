# 🏗️ Plan Maestro de Infraestructura Centralizada (VPS)

**Objetivo:** Centralizar el ecosistema TRIBOKA (App Móvil, Web Agro, ERP) en un único VPS robusto para tener soberanía de datos, reducción de latencia y control total.

## 1. Arquitectura Propuesta: "Nucleo Unificado"

Utilizaremos una arquitectura de **Contenedores (Docker)** con un **Proxy Inverso** y, crucialmente, un **Proveedor de Identidad (Keycloak)** para unificar el login.

```mermaid
graph TD
    UserApp[📱 App Móvil] -->|api.triboka.com| ReverseProxy
    UserWeb[💻 Triboka Agro Web] -->|agro.triboka.com| ReverseProxy
    UserERP[🏢 ERP Admin] -->|erp.triboka.com| ReverseProxy
    UserAuth[🔐 Login Unificado] -->|auth.triboka.com| ReverseProxy

    subgraph "VPS (Tu Servidor Central)"
        ReverseProxy[🚦 Nginx Proxy Manager]
        
        subgraph "Seguridad & Datos"
            Keycloak[🔑 Keycloak (SSO / Auth)]
            DB[(🗄️ PostgreSQL Central)]
            Redis[(🚀 Redis Cache)]
        end

        subgraph "Aplicaciones"
            BackendApp[🐍 Backend App Mobile]
            BackendWeb[🌐 Triboka Agro Web]
            BackendERP[⚙️ ERP System]
        end
    end
    
    ReverseProxy -->|SSL| Keycloak
    ReverseProxy -->|SSL| BackendApp
    ReverseProxy -->|SSL| BackendWeb
    ReverseProxy -->|SSL| BackendERP
    
    BackendApp -->|Valida Token| Keycloak
    BackendWeb -->|Valida Token| Keycloak
    BackendERP -->|Valida Token| Keycloak
    
    Keycloak --> DB
    BackendApp --> DB
```

---

## 2. El Corazón: Single Sign-On (SSO) con Keycloak 🔑
Para cumplir tu deseo de "un solo usuario para todo", implementaremos **Keycloak**.
- **Qué es:** Un estándar industrial (Open Source) para gestión de identidades.
- **Beneficio:** Tu usuario crea su cuenta UNA vez. Con esa cuenta entra a la App, a la Web y al ERP. Si cambias la contraseña, cambia en todos lados.
- **Roles Globales:** Puedes definir roles como `admin`, `proveedor`, `exportador` en Keycloak y esos roles viajan a todas tus apps.

---

## 3. Requisitos de Hardware Actualizados
Al sumar Keycloak (que es Java y consume RAM), necesitamos asegurar:
- **RAM:** Mínimo 8GB (Ideal 16GB).
- **CPU:** 4 vCPUs.

---

## 4. Estrategia de Implementación (Paso a Paso)

### Fase 1: Dockerización 🐳
Cada sistema en su contenedor.

### Fase 2: Despliegue de Infraestructura Base 🏗️
Levantar el "esqueleto" primero:
1.  **PostgreSQL** (Base de datos).
2.  **Keycloak** (Sistema de Login).
3.  **Nginx Proxy Manager** (Gestor de Dominios).

### Fase 3: Integración de Apps 🔌
Una vez Keycloak está vivo (`auth.triboka.com`), configuramos cada app para usarlo:
- **App Móvil:** Usará el protocolo **OpenID Connect (OIDC)**. Al abrir la app, si no hay sesión, se abre el login de Triboka (Keycloak).
- **ERP/Web:** Lo mismo. Redireccionan a Keycloak para autenticar.

---

## 3. Estrategia de Implementación (Paso a Paso)

### Fase 1: Preparación ("Containerización") 🐳
Antes de tocar el servidor, debemos asegurarnos que cada sistema pueda correr en una "caja" (Docker).

1.  **Triboka App Backend:**
    - Crear `Dockerfile`.
    - Definir variables de entorno en `.env` (DB_URL, SECRET_KEY).
2.  **Triboka Agro Web:**
    - Crear `Dockerfile` separado.
3.  **ERP:**
    - Si es Odoo/Dolibarr etc., usar imágenes oficiales.
    - Si es custom, crear `Dockerfile`.

### Fase 2: Configuración del VPS 🛡️
1.  **Harding (Seguridad Básica):**
    - Crear usuario `deploy` (no usar root).
    - Configurar firewall UFW (Solo puertos 22, 80, 443 abiertos).
    - Deshabilitar login por contraseña (solo SSH Key).
2.  **Instalación de Motor:**
    - Instalar Docker y Docker Compose.

### Fase 3: La Base de Datos Unificada 🗄️
En lugar de tener 3 bases de datos dispersas, levantaremos un servicio poderoso de PostgreSQL (o MySQL).
- **Ventaja:** Backups unificados.
- **Estrategia:** Crear usuarios y DBs separadas (`triboka_app_db`, `triboka_erp_db`) dentro del mismo servidor para seguridad, O un esquema compartido si los datos se cruzan mucho.

### Fase 4: El Proxy Inverso (Tu Controlador de Tráfico) 🚦
Usaremos **Nginx Proxy Manager**.
- **Por qué:** Tiene interfaz gráfica web. Facilita muchísimo poner Certificados SSL (candado verde HTTPS) gratuitos con Let's Encrypt.
- **Función:** Recibe `api.triboka.com`, encripta la conexión y pasa la petición al contenedor del backend internamente.

---

## 4. Estructura de Carpetas en el VPS

Organizaremos todo en `/opt/triboka-stack`:

```text
/opt/triboka-stack/
├── docker-compose.yml      # El archivo maestro que levanta TODO
├── .env                    # Contraseñas y secretos (NO subir a git)
├── data/
│   ├── postgres/           # Datos persistentes de la DB
│   ├── redis/              # Datos de caché
│   └── npm/                # Certificados SSL y configs del Proxy
├── services/
│   ├── app-backend/        # Código del backend móvil
│   ├── web-agro/           # Código del sistema web
│   └── erp/                # Configuración del ERP
└── backups/                # Scripts de respaldo automático
```

---

## 5. Siguientes Pasos Inmediatos

Para poder escribir el `docker-compose.yml` exacto, necesito confirmar:

1.  **Tecnología del ERP:** ¿Es un software comercial (Odoo, ERPNext) o desarrollo propio? ¿Qué lenguaje/DB usa?
2.  **Tecnología de Triboka Agro Web:** ¿Es PHP, Python, Node.js?
3.  **Base de Datos:** ¿Prefieres PostgreSQL o MySQL? (Recomiendo Postgres para sistemas complejos).

---

> [!TIP]
> **Beneficio "Ecosistema":** Al tener todo en la misma red interna de Docker, el Backend de la App puede consultar directamente la base de datos del ERP a velocidad luz (sin salir a internet), permitiendo integraciones en tiempo real increíbles (ej: stock real, facturación automática).

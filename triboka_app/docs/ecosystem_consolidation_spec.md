# Especificación de Consolidación de Ecosistema (Web & App)

Este documento define la arquitectura para unificar `agro.triboka.com` (Web) y `TRIBOKA-APP` (Móvil) en un solo sistema gestionado centralmente.

## 1. Gestión Unificada de Usuarios y Empresas

**Objetivo**: Centralizar la administración. Eliminar la redundancia de "Gestión de Empresas" separada.

### Cambios en Base de Datos (VPS)
*   **Tabla `users`**: Debe ser la tabla maestra.
    *   Añadir campo: `company_name` (String) - Reemplaza la necesidad de una tabla `companies` separada para validación básica.
    *   Añadir campo: `role` (Enum) - Valores permitidos: `productor`, `centro_acopio`, `exportadora`, `admin`.
    *   **CORRECCIÓN CRÍTICA**: En el formulario de registro Web, cambiar la opción "Inspector" por **"Centro de Acopio"** para que coincida con la App.

### Frontend Web (Instrucciones)
*   **Gestión de Empresas**: Eliminar o Ocultar módulo.
*   **Gestión de Usuarios**: Al crear/editar usuario, permitir ingresar el "Nombre de la Empresa" directamente.
*   **Deal / Broker**: Ocultar secciones del menú (comentar el código de navegación en el sidebar/header).

---

## 2. Sistema de Licenciamiento (Control de Acceso)

**Objetivo**: Controlar activo/inactivo y tiempos de suscripción para Web y App desde el panel Web.

### Base de Datos
*   **Tabla `licenses`**:
    *   `user_id` (FK)
    *   `status` (active / inactive / suspended)
    *   `plan_type` (basic / pro / enterprise)
    *   `start_date` (Timestamp)
    *   `expiration_date` (Timestamp)

### API Endpoints (Para la App)

#### A. Verificación de Licencia (Login)
**POST** `/api/auth/login`
*   **Lógica Servidor**: Además de validar credenciales, consultar tabla `licenses`.
*   **Respuesta Exitosa**:
    ```json
    {
      "token": "...",
      "user": { ... },
      "license": {
        "status": "active",
        "expiration": "2025-12-31"
      }
    }
    ```
*   **Error (Licencia Vencida)**: `403 Forbidden` - "Licencia expirada. Contacte soporte."

#### B. Chequeo de Estado (Middleware)
**GET** `/api/user/status`
*   La App puede llamar a esto periódicamente. Si devuelve `status: inactive`, la App cierra sesión localmente.

---

## 3. Soporte y Tickets Unificados

**Objetivo**: Que un usuario de la App pueda reportar un problema y se gestione en el panel Web.

### API Endpoint
**POST** `/api/support/tickets`
*   **Body**:
    ```json
    {
      "subject": "Error al sincronizar lotes",
      "description": "...",
      "priority": "high"
    }
    ```
*   **Web Dashboard**: Mostrar estos tickets en el módulo de Soporte existente.

---

## 4. API Management

**Estrategia**:
*   Mover el módulo "Api Management" de la Web para que simplemente muestre las credenciales API (`client_id`, `client_secret`) que usan las Apps o integraciones de terceros.
*   Redireccionar tráfico de API a `api.triboka.com` (o usar `agro.triboka.com/api` como prefijo estandarizado).

---

## 5. Resumen de Acciones Inmediatas en VPS

1.  **Frontend**:
    *   Renombrar rol "Inspector" -> "Centro de Acopio" en formulario de registro.
    *   Ocultar ítems de menú "Deals", "Brokers", "Empresas".
2.  **Backend**:
    *   Asegurar que el Login devuelva el estado de la **Licencia**.
    *   Exponer endpoint de **Tickets** para consumo móvil.

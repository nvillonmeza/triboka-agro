# 📘 MASTER GUIDE: Desarrollo del Ecosistema TRIBOKA

Este documento es la "Biblia de Desarrollo" para el sistema TRIBOKA Agro. Unifica la visión de la App Móvil, el Backend y la Infraestructura Centralizada en VPS.

---

## 🏗️ 1. Arquitectura del Ecosistema

El sistema opera bajo una arquitectura de **"Núcleo Centralizado"** donde múltiples interfaces (App, Web, ERP) consumen servicios de un único VPS soberano.

### Diagrama de Componentes

```mermaid
graph TD
    %% Clientes / Frontends
    Mobile[📱 Flutter App]
    Web[💻 Angular/React Web]
    ERP_UI[🏢 ERP Admin UI]

    %% Capa de Entrada (VPS)
    subgraph "VPS: TRIBOKA CLOUD"
        Nginx[🚦 Nginx Proxy Manager]
        
        subgraph "Seguridad"
            Keycloak[🔐 Keycloak Identity Provider]
        end
        
        subgraph "Backends (Microservicios o Monolito Modular)"
            API_Core[🐍 API Core (Python/Node)]
            Socket_Srv[⚡ Chat/Notificaciones (Socket.IO)]
            ERP_Core[⚙️ Motor ERP (Odoo/Propio)]
        end
        
        subgraph "Persistencia"
            Postgres[(🗄️ PostgreSQL)]
            Redis[(🚀 Redis Cache)]
        end
    end

    %% Conexiones
    Mobile -->|HTTPS / REST| Nginx
    Mobile -->|WSS / Socket| Nginx
    Web --> Nginx
    
    Nginx -->|auth.triboka.com| Keycloak
    Nginx -->|api.triboka.com| API_Core
    Nginx -->|socket.triboka.com| Socket_Srv
    
    API_Core --> Postgres
    API_Core --> Keycloak
    API_Core --> Redis
```

---

## 🛠️ 2. Guía de Desarrollo: Infraestructura (DevOps)

**Objetivo:** Mantener el "Suelo" donde todo corre.
**Tecnología:** Docker, Docker Compose, Ubuntu Server.

### Pasos de Desarrollo
1.  **Configuración Inicial:** Sigue al pie de la letra el archivo `infrastructure_deployment_guide.md` generado en este proyecto.
2.  **Gestión de Secretos:** Nunca subas el archivo `.env` al repositorio. Mantenlo seguro en el servidor.
3.  **Backups:** Configurar un script cron en el VPS que haga `pg_dump` de la base de datos cada noche y lo suba a un S3 o Google Drive externo.

---

## 📱 3. Guía de Desarrollo: App Móvil (Frontend)

**Objetivo:** La interfaz principal para el agricultor y exportador.
**Tecnología:** Flutter (Dart), Hive (Local DB), Provider (Estado).

### Patrones Clave
*   **Modo Híbrido (Simulación/Producción):**
    *   La app está diseñada para "*Fallar con Estilo*".
    *   Si `ApiConfig.apiBaseUrl` no responde, los servicios (`AnalyticsService`, `ContractService`) activan automáticamente `_isSimulated = true`.
    *   **Regla de Oro:** Al desarrollar nuevas features, SIEMPRE implementa primero el fallback simulado. Esto permite testear la UI sin backend.

*   **Gestión de Estado (Provider):**
    *   Usa `ChangeNotifier` para lógica de negocio.
    *   Evita lógica compleja dentro de los Widgets (UI). Mueve todo a los `Services`.

*   **Persistencia (Offline-First):**
    *   Usa **Hive** para guardar datos críticos (Login, Contratos, Calculadoras).
    *   La app debe abrir y ser útil sin internet.

### Estructura de Proyecto
```text
lib/
├── models/         # Clases de datos (json_serializable)
├── services/       # Lógica de negocio y conexión API
├── pages/          # Pantallas (Scaffolds)
├── widgets/        # Componentes reusables
└── utils/          # Constantes, temas y helpers
```

---

## 🐍 4. Guía de Desarrollo: Backend (El Próximo Paso)

Actualmente la app tiene URLs apuntando a `api.triboka.com`. Tu misión ahora es construir ese backend.

### Recomendación de Stack
*   **Lenguaje:** Python (FastAPI o Django) o Node.js (NestJS).
*   **Base de Datos:** PostgreSQL (Ya incluida en tu Docker).

### Endpoints Requeridos (API Contract)

Para que la app funcione "Real" sin cambiar código, tu backend debe exponer:

**1. Analytics (`GET /analytics/{role}`)**
*   **Response:** JSON con `stock_kg`, `active_contracts`, etc.

**2. Contratos (`GET /contracts`, `POST /contracts`)**
*   **Response:** Lista de contratos. El modelo debe coincidir con `lib/models/contract_model.dart`.

**3. Chat (`Socket.IO`)**
*   **Eventos:** `join_chat`, `send_chat_message`, `new_chat_message`.
*   Referencia: Ver lógica en `lib/services/chat_service.dart`.

---

## 🚀 5. Flujo de Trabajo (Workflow)

### Ciclo Diario
1.  **Local:** Desarrollas en tu máquina (`localhost`). La app apunta a `localhost` o usa simulación.
2.  **Push:** Subes cambios a Git (`git push`).
3.  **Deploy Backend:** En el VPS, haces `git pull` en la carpeta del backend y reinicias el contenedor (`docker compose restart app_backend`).
4.  **Deploy App:** Generas el APK (`flutter build apk`) y lo distribuyes a los usuarios.

### Comandos Útiles

**En Flutter:**
```bash
# Correr con modo release (más rápido)
flutter run --release

# Generar iconos si cambias el logo
flutter pub run flutter_launcher_icons
```

**En el VPS (Docker):**
```bash
# Ver logs en vivo
docker compose logs -f --tail=100

# Reiniciar solo un servicio
docker compose restart triboka_api
```

---

## 🔮 6. Futuro y Escalabilidad

1.  **Notificaciones Push:** Integrar Firebase Cloud Messaging (FCM) en el backend Python para despertar la app cuando llega un mensaje de chat.
2.  **CI/CD:** Configurar GitHub Actions para que al hacer push, se despliegue solo al VPS.
3.  **Blockchain:** Conectar el `ContractService` del backend a una red real (Ethereum/Polygon) para notarizar los contratos PDF generados.

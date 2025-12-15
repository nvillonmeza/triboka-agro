# Triboka Agro System Design Skillbook

Este documento describe, paso a paso, la arquitectura y las decisiones tomadas para reconstruir el sistema Triboka Agro (frontend + API blockchain-ready + base de datos inicializable). Sirve como manual para replicar el mismo nivel de funcionalidad en otro dominio (por ejemplo, logística, salud o energía) reutilizando el mismo diseño.

---

## 1. Principios de Diseño
- **Separación de responsabilidades**: backend (`backend/app_web3.py`) expone APIs REST y maneja blockchain/DB; frontend (`frontend/app.py`) consume esas APIs y renderiza vistas.
- **Inicialización determinista**: `backend/init_database.py` siempre puede poblar la base con datos de referencia (usuarios, empresas, contratos) para pruebas o restauraciones.
- **Autenticación centralizada**: backend emite JWT y el frontend los guarda en sesión server-side para mantener sesiones seguras.
- **Compatibilidad progresiva**: fallback a modelos simplificados (`models_simple.py`) cuando el sistema completo no está disponible, permitiendo usar SQLite puro.

---

## 2. Arquitectura General
```
frontend/app.py          backend/app_web3.py           SQLite / Web3
┌────────────┐          ┌───────────────────┐          ┌────────────┐
│ Flask Web  │  HTTP    │ Flask REST (JWT)  │   ORM    │ triboka_    │
│ Dashboard  │ ───────► │ + Blockchain svc  │ ───────► │ agro.db     │
└────────────┘          └───────────────────┘          └────────────┘
```
- **Frontend**: vistas Jinja2 con Bootstrap, rutas `/login`, `/dashboard`, `/users`, etc. Usa `requests` para llamar al backend desde el servidor.
- **Backend**: Flask API con SQLAlchemy, JWT y servicio `blockchain_service` cargando contratos y cuentas Web3.
- **Base de datos**: SQLite (`instance/triboka_agro.db`) gestionada por SQLAlchemy; `init_database.py` sincroniza nombres de archivo para que API y scripts usen el mismo origen.

---

## 3. Flujo de Autenticación
1. Usuario envía credenciales → `frontend/app.py` llama a `/api/auth/login` en backend.
2. Backend valida contra `users` y responde con JWT + datos del usuario.
3. Frontend guarda `access_token` y `user` en `session` y renderiza dashboard.
4. Cada llamada posterior (`/api/users`, `/api/contracts`, etc.) usa `api_request()` que adjunta el encabezado `Authorization: Bearer <token>`.
5. Para rutas AJAX del frontend (`/api/users`), se crea un **proxy autenticado** que reutiliza el token desde la sesión y evita CORS o manejo manual en JavaScript.

---

## 4. Backend Paso a Paso
1. **Configurar Flask y SQLAlchemy** en `app_web3.py` con `SQLALCHEMY_DATABASE_URI='sqlite:///triboka_agro.db'`.
2. **Declarar modelos** en `models_simple.py` (Company, User, ExportContract, ContractFixation, ProducerLot) con `to_dict()` para respuestas JSON.
3. **Inicializar Blockchain** via `blockchain_service.get_blockchain_integration()` para registrar contratos y obtener estados.
4. **Auth Endpoints**: `/api/auth/login` (JWT), `/api/auth/register` (creación simple). Verificar `is_active` para controlar accesos.
5. **Usuarios Endpoint**: `/api/users` protegido con `@jwt_required()` y restricción de roles (`admin`, `operator`). Devuelve lista ordenada.
6. **Resto de endpoints**: `/api/contracts`, `/api/lots`, `/api/analytics/*` con filtros por rol.
7. **Manejo de errores** consistente: `try/except` con respuesta JSON y rollback cuando aplica.

---

## 5. Frontend Paso a Paso
1. **Flask App** (`frontend/app.py`) con `API_BASE_URL = 'http://localhost:5003/api'`.
2. **Utilidades**: `api_request()` para centralizar peticiones al backend usando token de sesión.
3. **Rutas principales**
   - `/login`: renderiza formulario, envía POST, guarda token y redirige.
   - `/dashboard`, `/contracts`, `/companies`, `/users`: renderizan plantillas y se aseguran de que `user` exista en sesión.
4. **Proxy API**: ruta `/api/users` en frontend que reenvía la solicitud al backend usando la sesión. Esto permite que el JavaScript del template consulte `/api/users` sin perder autenticación.
5. **Plantillas** (`templates/users.html`): pre-cargan datos iniciales (`users_data`) desde el renderizado del servidor, y luego refrescan con fetch. El script maneja filtros, paginación y mensajes al usuario.

---

## 6. Inicialización de la Base de Datos
1. `init_database.py` detecta si existen módulos avanzados. Si no, crea un Flask mínimo con la misma URI (`sqlite:///triboka_agro.db`).
2. `initialize_database(reset=True)` borra tablas (si se indica) y corre `create_sample_data()`.
3. `create_sample_data()` crea empresas y usuarios con credenciales estándar:
   - admin@triboka.com / admin123
   - export@cacao.com / export123
   - buyer@chocolate.com / buyer123
   - producer@farm.com / producer123
4. Copiar la base desde `instance/agro_contracts.db` a `instance/triboka_agro.db` garantiza que el backend utilice datos reales.

---

## 7. Reinicios y Deploy
- **Backend**: ejecutar `nohup python3 app_web3.py > backend.log 2>&1 &` y validar con `curl` (health/login).
- **Frontend**: `nohup python3 app.py > frontend.log 2>&1 &`. Verificar que `sessions` y `proxy` funcionen.
- **Puertos**: frontend 5004, backend 5003. Usar `lsof -ti:<port>` para liberar puertos antes de reiniciar.
- **Logs**: `backend.log`, `frontend.log` almacenan estados y errores.

---

## 8. Cómo Rehacer el Sistema para Otro Dominio
1. **Cambiar vocabulario**: reemplazar nombres (por ejemplo, `Company` → `Clinic`, `ExportContract` → `TreatmentPlan`). Mantener roles; sólo renombrar campos y plantillas.
2. **Actualizar datos iniciales**: editar `create_sample_data()` en `init_database.py` con empresas/usuarios nuevos.
3. **Modificar vistas**: duplicar plantillas en `frontend/templates/` según el nuevo dominio manteniendo la estructura base + dashboard.
4. **Endpoints**: adaptar lógica en `app_web3.py` (nuevos atributos, validaciones) y actualizar `models_simple.py` para reflejar nuevas tablas.
5. **Frontend JS**: reusar componentes de tabla/filtrado; cambiar columnas, etiquetas y roles mostrados.
6. **Testing rápido**: usar `curl` para validar `/api/auth/login`, `/api/users`, `/api/contracts`, etc. antes de abrir el dashboard.
7. **Blockchain opcional**: si el nuevo dominio no necesita Web3, `blockchain_service` puede simular respuestas. Ajustar `get_blockchain_integration()` para devolver indicadores predeterminados.

---

## 9. Buenas Prácticas
- Documentar credenciales de demo y cómo regenerarlas.
- Mantener `.db` dentro de `instance/` para cumplir convenciones Flask.
- Evitar múltiples procesos del mismo servidor para no duplicar puertos (controlar con `ps aux` + `kill`).
- Usar `session` del frontend para almacenar tokens; nunca enviarlos al cliente directamente.
- Cuando se agreguen endpoints, recordar crear proxies si el frontend los requiere vía fetch.

---

## 10. Checklist de Replicación Rápida
1. Clonar estructura (`backend/`, `frontend/`, `instance/`).
2. Ajustar `API_BASE_URL` si los puertos cambian.
3. Ejecutar `python3 init_database.py` hasta ver el mensaje de éxito.
4. Copiar `instance/agro_contracts.db` a `instance/<nuevo>.db` si se requiere un seed diferente.
5. Iniciar backend y frontend con `nohup`.
6. Probar logins con `curl` y desde el navegador.
7. Confirmar `/users`, `/contracts`, `/lots` en el dashboard.

Con estas pautas puedes reconstruir el mismo patrón para cualquier sistema similar: separar web+API, reutilizar inicialización de base de datos, proxies autenticados en el frontend y un pipeline claro de despliegue local.

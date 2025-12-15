¡Entendido! Aquí tienes un documento único y completo para tu repo llamado BACKEND.md que cubre todo el backend de la aplicación: arquitectura, despliegue en VPS, seguridad, DB, endpoints, sockets, colas, IoT, notificaciones, backups, pruebas, y ejemplos de código con FastAPI + SQLAlchemy + Postgres + Redis + Socket.IO. Copia/pega tal cual en tu proyecto.

⸻

🧠 BACKEND.md — ERP Cacao (Triboka / Global VCE)

1) Visión general

Backend modular para un ERP de cacao con:
	•	API REST (FastAPI / Uvicorn / Gunicorn)
	•	WebSockets (Socket.IO) para chat/eventos
	•	PostgreSQL para datos transaccionales
	•	Redis para caché, colas y rate-limit
	•	Storage local para documentos (contratos, facturas, guías, análisis)
	•	Jobs (Celery) para tareas programadas (backups, sincronizaciones)
	•	Nginx como reverse proxy + SSL

Objetivos: seguridad, trazabilidad por contrato/lote, mensajería entre socios, cálculos (TM→QQ), gestión por roles (Proveedor, Centro, Exportadora, Admin), integraciones (IoT, FCM, Odoo opcional).

⸻

2) Stack técnico
	•	Lenguaje: Python 3.12
	•	Framework: FastAPI
	•	DB: PostgreSQL 16 (SQLAlchemy + Alembic)
	•	Tiempo real: Socket.IO (ASGI)
	•	Cache/colas: Redis
	•	Jobs: Celery + Beat (programación)
	•	Web server: Uvicorn/Gunicorn detrás de Nginx
	•	Auth: OAuth2 Password Flow + JWT (access/refresh)
	•	Logs/Observabilidad: Loguru, Prometheus (opcional), Sentry (opcional)

⸻

3) Arquitectura lógica (módulos)

API Gateway (FastAPI)
 ├─ Auth (JWT)
 ├─ Users & Roles (RBAC)
 ├─ Empresas (perfil empresa, licencias opc.)
 ├─ Gestión (KPIs por rol)
 ├─ Calculadora (spot/diferenciales TM→QQ)
 ├─ Contratos (doc repo + lotes + estados)
 ├─ Documentos (upload/download seguro)
 ├─ Lotes (trazabilidad, humedad, peso)
 ├─ Chat (Socket.IO) por contrato/socio
 ├─ IoT (lecturas pesaje/humedad, CSV/RS232)
 ├─ Exportadoras (demanda mensual/contratos)
 ├─ Notificaciones (FCM/Email)
 └─ Admin (métricas, backups, seeds)


⸻

4) Estructura del proyecto

backend/
├─ app/
│  ├─ main.py                 # FastAPI app + mounts
│  ├─ dependencies.py         # auth/roles/current_user
│  ├─ core/
│  │  ├─ config.py            # settings (.env)
│  │  ├─ security.py          # JWT, hashing, rate limit
│  │  ├─ database.py          # SessionLocal, engine
│  │  └─ storage.py           # rutas de archivos
│  ├─ models/                 # SQLAlchemy (1 archivo por entidad)
│  ├─ schemas/                # Pydantic (request/response)
│  ├─ routers/                # Endpoints por módulo
│  ├─ services/               # lógica negocio (contratos, calc, iot, fcm…)
│  ├─ workers/                # Celery tasks (backups, fob sync…)
│  ├─ sockets/                # Socket.IO namespaces/rooms
│  └─ utils/                  # helpers (uuid, pdf, csv)
├─ alembic/                   # migraciones DB
├─ tests/                     # pytest
├─ docker/
│  ├─ Dockerfile.app
│  ├─ Dockerfile.celery
│  ├─ nginx.conf
│  └─ compose.yml
├─ .env.example
└─ pyproject.toml / requirements.txt


⸻

5) Variables de entorno (.env)

APP_NAME=erp_cacao
ENV=prod
SECRET_KEY=supersecreto_largo_256bits
JWT_ACCESS_TTL=900
JWT_REFRESH_TTL=604800

DB_HOST=postgres
DB_PORT=5432
DB_USER=triboka
DB_PASS=triboka_pass
DB_NAME=triboka_prod

REDIS_URL=redis://redis:6379/0
STORAGE_ROOT=/srv/triboka_app/storage

FCM_KEY=AAA...  # opcional
SMTP_HOST=smtp.mailserver.com
SMTP_USER=noreply@tu-dominio.com
SMTP_PASS=pass

# IoT / crawling FOB opcional:
IOT_TOKEN=...
MPCEIP_BASE_URL=https://datosabiertos.gob.ec/...


⸻

6) Modelo de datos (resumen)

Entidades clave:
	•	Usuario (id, nombre, email, rol, empresa_id, hash_password, config_json)
	•	Empresa (id, nombre, tipo[proveedor/centro/exportadora], ruc, logo_url, ubicacion_json)
	•	Contrato (id, codigo, exportadora_id, contraparte_id, fecha_firma, volumen_tm, precio_fijado_tm, estado, archivo_pdf)
	•	DocumentoContrato (id, contrato_id, tipo, nombre_archivo, url_archivo, subido_por, fecha_subida)
	•	Lote (id, codigo_lote, empresa_id, contrato_id, peso_qq, humedad, estado, metadata_json)
	•	Mensaje (id, chat_id, sender_id, texto, timestamp, leido, adjunto_url)
	•	Chat (id, contrato_id, usuario1_id, usuario2_id)
	•	Calculo (id, usuario_id, spot_tm, diferencial, precio_qq, fecha)
	•	DemandaExportadora (id, empresa_id, volumen_tm_mensual, contrato_tipo, vigente_desde, vigente_hasta)
	•	PrecioFOB (id, mes, anio, valor_usd_tm, fuente)

Multi-tenant: por ahora una sola DB con separación por empresa_id y revisiones de permisos por rol. Escalable a multibase más adelante.

⸻

7) Permisos (RBAC)
	•	Proveedor: ve/gestiona sus lotes, adjunta docs a contratos donde participa, chat con contrapartes activas.
	•	Centro: ve su stock, proveedores asociados, contratos con exportadoras, sube docs.
	•	Exportadora: crea contratos, ve/adjunta docs, demanda mensual, chat, confirma recepciones.
	•	Admin: ve todo, backups, seeds, gestión usuarios/empresas.

Middleware/dep:

def role_required(roles: list[str]):
    def decorator(route):
        ...
    return decorator


⸻

8) Endpoints (resumen por módulo)

Auth
	•	POST /auth/register
	•	POST /auth/login
	•	POST /auth/refresh
	•	POST /auth/logout

Usuarios/Empresas
	•	GET /me (perfil + rol + empresa)
	•	PUT /me (update datos, config_json)
	•	GET /empresas/{id} / PUT /empresas/{id} (admin/export)

Gestión (dashboard por rol)
	•	GET /gestion/{rol} → KPIs dinámicos (stock, humedad, contratos, entregas, volumen, …)

Calculadora
	•	POST /calculadora
Body: { "spot": 6319, "diferenciales": [200, 300] }
Res: { "precios": { "dif_200": 277.03, "dif_300": 272.49 }, "divisor": 22.0462 }

Contratos & Documentos
	•	POST /contratos (crea contrato)
	•	GET /contratos?estado=Activo (filtra/pagina)
	•	GET /contratos/{id}
	•	PUT /contratos/{id} (cambia estado, volumen, precio)
	•	DELETE /contratos/{id} (admin)
	•	POST /contratos/{id}/lotes (asociar lote)
	•	POST /contratos/{id}/documentos (subir archivo)
	•	GET /contratos/{id}/documentos (listar)
	•	GET /documentos/{doc_id}/download (descarga autorizada con URL firmada temporal)

Lotes
	•	POST /lotes (crear lote)
	•	GET /lotes?empresa_id=...&contrato_id=...
	•	PUT /lotes/{id} (humedad/estado/peso/metadata)
	•	GET /lotes/{id}

Chat (Socket.IO + REST lite)
	•	GET /chats?contrato_id=... (listar)
	•	WS /ws/chat (join room → room=contrato_id; eventos: send_message, receive_message)

Exportadoras (demanda)
	•	GET /exportadoras/demanda (lista)
	•	POST /exportadoras/demanda (crear/actualizar)

IoT
	•	POST /iot/pesaje { lote_id, peso, humedad, origen }
	•	POST /iot/siemens/csv (upload + parse seguro)
	•	Opcional: MQTT receiver

Notificaciones
	•	POST /notify (admin) → broadcast/segmentos
	•	Triggers automáticos: subida de doc, cambio de estado contrato, mensaje nuevo

Health/Admin
	•	GET /health (db/redis/uptime)
	•	POST /admin/backup (dispara Celery job)
	•	POST /admin/seed

Todas las listas paginadas: ?page=1&page_size=20 + filtros por fecha/estado.

⸻

9) Ejemplos de código

app/main.py

from fastapi import FastAPI
from app.core.config import settings
from app.routers import auth, gestion, calculadora, contratos, lotes, chat_rest, exportadoras, iot, files
from app.sockets.server import sio_app

app = FastAPI(title=settings.APP_NAME)

# Routers REST
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(gestion.router, prefix="/gestion", tags=["gestion"])
app.include_router(calculadora.router, prefix="/calculadora", tags=["calculadora"])
app.include_router(contratos.router, prefix="/contratos", tags=["contratos"])
app.include_router(lotes.router, prefix="/lotes", tags=["lotes"])
app.include_router(chat_rest.router, prefix="/chats", tags=["chat"])
app.include_router(exportadoras.router, prefix="/exportadoras", tags=["exportadoras"])
app.include_router(iot.router, prefix="/iot", tags=["iot"])
app.include_router(files.router, prefix="/documentos", tags=["documentos"])

# Montar Socket.IO como ASGI sub-app
app.mount("/ws", sio_app)

Calculadora (servicio)

DIVISOR_QQ = 22.0462

def precio_por_qq(spot_tm: float, diferencial: float) -> float:
    return round((spot_tm - diferencial) / DIVISOR_QQ, 2)

Subida de documentos (ruta segura)
	•	Validar tipo MIME
	•	Renombrar (uuid + hash)
	•	Guardar en STORAGE_ROOT/contratos/{codigo}/...

⸻

10) Seguridad
	•	JWT (access/refresh) con rotación y revocación basada en Redis
	•	RBAC por rol y pertenencia a empresa/contrato
	•	Rate-limit por IP/Ruta (Redis)
	•	CORS restringido a dominios de tu app
	•	Validación de archivos (tamaño, extensión, antivirus opcional)
	•	URLs firmadas y expiran para descargas de documentos
	•	TLS extremo a extremo (Nginx)

⸻

11) Despliegue (Docker Compose)

docker/compose.yml (resumen):

services:
  api:
    build: { context: .., dockerfile: docker/Dockerfile.app }
    env_file: ../.env
    depends_on: [db, redis]
  worker:
    build: { context: .., dockerfile: docker/Dockerfile.celery }
    env_file: ../.env
    depends_on: [api, redis, db]
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_PASSWORD: ${DB_PASS}
      POSTGRES_USER: ${DB_USER}
    volumes: ["pgdata:/var/lib/postgresql/data"]
  redis:
    image: redis:7
  nginx:
    image: nginx:1.25
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
      - "443:443"
    depends_on: [api]
volumes:
  pgdata:


⸻

12) Migraciones

alembic init alembic
alembic revision --autogenerate -m "init"
alembic upgrade head


⸻

13) Jobs (Celery)
	•	Backups (diario): pg_dump → /srv/backups/triboka/{YYYYMMDD}.sql
	•	Sincronización FOB (mensual): descarga CSV MPCEIP → precio_fob table
	•	Limpieza de URLs firmadas vencidas (cada hora)
	•	Purgado de logs (mensual)

⸻

14) Notificaciones
	•	FCM: push a usuarios afectados por eventos (doc subido, contrato actualizado, nuevo mensaje)
	•	Email: confirmaciones/soporte (SMTP)

⸻

15) Observabilidad
	•	Logs: JSON + niveles (info/warn/error), rotación diaria
	•	/health: estado DB/Redis
	•	Prometheus (opcional): métricas de API
	•	Sentry (opcional): errores

⸻

16) Pruebas
	•	pytest + httpx para endpoints
	•	DB de prueba (schema temporal)
	•	Tests de permisos por rol
	•	Tests de subida de archivos (mocks)

⸻

17) Políticas de datos
	•	Retención de documentos/contratos: configurable por empresa
	•	Exportación (portabilidad) por empresa
	•	Borrado: suave (soft delete) con deleted_at opcional

⸻

18) Versionado API
	•	Prefijo v1 si necesitas ruptura futura: /v1/contratos
	•	Changelog en docs/CHANGELOG.md

⸻

19) Semillas (seeds)
	•	Crear roles básicos, empresa demo, usuario admin
	•	Cargar demandas de exportadoras de ejemplo

⸻

20) Roadmap (prioridades)
	1.	Auth + Usuarios + Empresas
	2.	Contratos + Documentos + Lotes
	3.	Gestión (KPIs por rol)
	4.	Calculadora + Historial
	5.	Chat (WS) + Notificaciones
	6.	IoT (pesaje/humedad)
	7.	Exportadoras (demanda mensual)
	8.	Backups + Sincronización FOB

⸻

Anexo A — Snippet de Router: Contratos

@router.post("/", response_model=ContratoOut)
@role_required(["exportadora", "centro", "admin"])
def crear_contrato(payload: ContratoIn, user=Depends(get_current_user)):
    return contratos_service.crear(payload, user)

@router.get("/", response_model=Paginated[ContratoOut])
def listar_contratos(filtro: ContratoFiltro = Depends(), user=Depends(get_current_user)):
    return contratos_service.listar(user, filtro)

@router.post("/{contrato_id}/documentos", response_model=DocumentoOut)
def subir_documento(contrato_id: int, file: UploadFile, user=Depends(get_current_user)):
    return documentos_service.subir(contrato_id, file, user)

Anexo B — Snippet Socket.IO (Chat)

@sio.event
async def join(sid, data):
    room = f"contrato_{data['contrato_id']}"
    sio.enter_room(sid, room)

@sio.event
async def send_message(sid, data):
    # persistir en DB
    await sio.emit("receive_message", data, room=f"contrato_{data['contrato_id']}")


⸻


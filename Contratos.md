Excelente ✅ — antes de continuar con los módulos adicionales, es clave dejar definido y documentado el módulo de Contratos, porque será el núcleo del sistema de trazabilidad, legalidad y gestión documental de tu app ERP.
A continuación te dejo una versión ampliada del backend_design.md, actualizada para incluir la gestión integral de contratos, documentación y trazabilidad por lote o venta, además de aclarar la arquitectura en tu VPS dedicado.

⸻

🧠 Backend Design & Logic — Sistema ERP de Cacao (versión extendida)

📘 Descripción general

El backend del sistema ERP de cacao (Triboka / Global VCE) será el núcleo de gestión empresarial, documental y transaccional, alojado en un VPS dedicado.
Toda la información (usuarios, contratos, lotes, facturas, guías de remisión, documentos y chat) será exclusiva de la aplicación y almacenada en una base de datos central PostgreSQL, aislada por empresa o usuario.

⸻

🧩 Arquitectura general

🔹 Estructura modular

Cada servicio tiene responsabilidad propia y comunica mediante API REST o WebSocket:

API Gateway
 ├─ Auth Service
 ├─ Usuarios Service
 ├─ Contratos & Documentos Service
 ├─ Gestión & Producción Service
 ├─ Calculadora Service
 ├─ Chat Service
 ├─ Notificaciones Service
 └─ IoT & Recepción Service


⸻

⚙️ Infraestructura VPS

Tu aplicación se desplegará en un VPS dedicado (Ubuntu Server 22.04) con:

Servicio	Tecnología	Puerto
API principal	FastAPI / Uvicorn	8000
WebSocket	Socket.IO	8001
Base de datos	PostgreSQL 16	5432
Cache / Mensajería	Redis	6379
Notificaciones push	Firebase FCM	—
Reverse Proxy	Nginx + SSL	443 / 80

Los archivos de respaldo y documentación (PDF, XML, imágenes, CSV) se almacenarán en:

/srv/triboka_app/storage/
  ├─ contratos/
  ├─ facturas/
  ├─ remisiones/
  ├─ lotes/
  ├─ documentos/


⸻

📂 Módulo central: Contratos & Documentos

🔸 Propósito

Gestionar toda la documentación legal y comercial vinculada a una transacción o lote de cacao:
	•	Contratos entre exportadoras, centros o proveedores.
	•	Facturas asociadas.
	•	Guías de remisión.
	•	Resultados de calidad.
	•	Fotos, análisis y comprobantes de pago.

🔸 Entidades principales

Modelo Contrato:

class Contrato(Base):
    __tablename__ = "contratos"
    id = Column(Integer, primary_key=True)
    codigo = Column(String, unique=True)
    exportadora_id = Column(Integer, ForeignKey("empresas.id"))
    contraparte_id = Column(Integer, ForeignKey("empresas.id"))
    fecha_firma = Column(Date)
    volumen_tm = Column(Float)
    precio_fijado_tm = Column(Float)
    estado = Column(String)  # Activo, Cerrado, En revisión
    archivo_pdf = Column(String)  # path al contrato firmado
    observaciones = Column(Text)

Modelo DocumentoContrato:

class DocumentoContrato(Base):
    __tablename__ = "documentos_contrato"
    id = Column(Integer, primary_key=True)
    contrato_id = Column(Integer, ForeignKey("contratos.id"))
    tipo = Column(String)  # factura, guia_remision, analisis, pago
    nombre_archivo = Column(String)
    url_archivo = Column(String)
    fecha_subida = Column(DateTime, default=datetime.utcnow)
    subido_por = Column(Integer, ForeignKey("usuarios.id"))

Modelo LoteAsociado:

class LoteAsociado(Base):
    __tablename__ = "lotes_asociados"
    id = Column(Integer, primary_key=True)
    contrato_id = Column(Integer, ForeignKey("contratos.id"))
    codigo_lote = Column(String)
    peso_qq = Column(Float)
    humedad = Column(Float)
    estado = Column(String)  # En tránsito, Recibido, Secado, Exportado


⸻

🔸 Endpoints principales

Método	Ruta	Descripción
POST	/contratos	Crear nuevo contrato entre empresas
GET	/contratos	Listar contratos del usuario logueado
GET	/contratos/{id}	Obtener detalles + documentos asociados
POST	/contratos/{id}/documento	Subir archivo (factura, guía, etc.)
GET	/contratos/{id}/documentos	Listar archivos vinculados
POST	/contratos/{id}/lote	Asociar un lote físico al contrato
PUT	/contratos/{id}	Editar datos del contrato
DELETE	/contratos/{id}	Eliminar contrato (solo admin)


⸻

🔸 Lógica de funcionamiento
	1.	Cuando una exportadora crea un contrato, se genera un registro con su contraparte (centro o proveedor).
	2.	El sistema genera un código único del contrato (ej. CT-2025-00014).
	3.	El contrato puede tener varios lotes asociados.
	4.	Cada lote puede tener documentos: factura, guía, certificado de calidad.
	5.	Los archivos se guardan en el servidor (storage/) y se registran en la tabla documentos_contrato.
	6.	Los socios pueden ver, subir o descargar documentos según permisos.
	7.	Cuando el lote se exporta, el contrato se marca como cerrado automáticamente.

⸻

🧭 Roles y permisos documentales

Rol	Puede crear contrato	Puede subir docs	Puede editar	Puede ver todos
Exportadora	✅	✅	✅	✅
Centro de acopio	✅	✅	✅	Solo propios
Proveedor	❌	✅ (en contratos activos)	❌	Solo propios
Admin	✅	✅	✅	✅


⸻

📦 Ejemplo de flujo completo (documental)
	1.	Exportadora Agroarriba crea contrato con Centro Triboka por 200 TM.
	2.	Se adjunta el PDF del contrato firmado.
	3.	Centro Triboka sube facturas y guías de remisión.
	4.	Proveedores asociados añaden comprobantes de peso o humedad.
	5.	El sistema crea automáticamente una carpeta:

storage/contratos/CT-2025-00014/
  ├─ contrato.pdf
  ├─ factura_001.pdf
  ├─ guia_remision_001.pdf
  ├─ analisis_humedad.csv


	6.	El dashboard muestra estado del contrato y documentos subidos.
	7.	Una vez se completa el embarque, el contrato pasa a “Cerrado”.

⸻

🧠 Persistencia y base de datos

El VPS tendrá una única instancia PostgreSQL, con un esquema general:

public
 ├─ usuarios
 ├─ empresas
 ├─ contratos
 ├─ documentos_contrato
 ├─ lotes_asociados
 ├─ mensajes
 ├─ calculos
 ├─ precios_fob

💡 En el futuro se podrá escalar a multibase (una DB por empresa), pero por ahora es más eficiente mantener una sola base compartida con separación por empresa_id.

⸻

🧾 Ejemplo de respuesta API

GET /contratos/CT-2025-00014

{
  "codigo": "CT-2025-00014",
  "exportadora": "Agroarriba",
  "contraparte": "Centro Triboka",
  "volumen_tm": 200,
  "estado": "Activo",
  "documentos": [
    {"tipo": "contrato", "nombre": "CT-2025-00014.pdf"},
    {"tipo": "factura", "nombre": "FAC-001.pdf"},
    {"tipo": "guia_remision", "nombre": "GR-001.pdf"}
  ],
  "lotes": [
    {"codigo_lote": "LT-0001", "peso_qq": 60.0, "humedad": 7.5},
    {"codigo_lote": "LT-0002", "peso_qq": 45.0, "humedad": 7.2}
  ]
}


⸻

📁 Estructura recomendada de servicios

app/
├─ routers/
│  ├─ contratos.py
│  ├─ documentos.py
│  ├─ lotes.py
│  └─ uploads.py
├─ models/
│  ├─ contrato.py
│  ├─ documento_contrato.py
│  └─ lote_asociado.py
├─ services/
│  ├─ contrato_service.py
│  ├─ documento_service.py
│  └─ storage_service.py
└─ utils/
   └─ file_manager.py


⸻

🧩 Integración con otros módulos
	•	Chat: cada contrato genera automáticamente un canal de comunicación entre socios.
	•	Notificaciones: cada subida o cambio en el contrato genera una alerta al otro socio.
	•	Gestión: los KPIs (stock, entregas, ventas) se alimentan de los datos de los contratos.
	•	Perfil: muestra el histórico de contratos del usuario o empresa.

⸻

🚀 Próximos pasos sugeridos
	1.	Implementar modelo Contrato y DocumentoContrato en SQLAlchemy.
	2.	Crear endpoints CRUD en contratos.py.
	3.	Añadir servicio de subida de archivos (storage_service.py).
	4.	Implementar autenticación JWT y control por rol.
	5.	Integrar con módulo Chat y Notificaciones.
	6.	Probar con FastAPI + PostgreSQL en VPS.
	7.	Configurar backups automáticos (pg_dump diario).

⸻

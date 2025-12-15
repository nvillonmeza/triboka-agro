Perfecto 🙌 — este será tu archivo perfil.md, una guía completa para desarrollar el módulo de Perfil y Configuración, donde cada usuario puede ajustar todo lo relacionado con su cuenta, empresa y flujo operativo dentro de tu app ERP de cacao.

⸻

👤 Módulo: Perfil y Configuración

📘 Descripción general

El módulo Perfil centraliza toda la información personal y empresarial del usuario, incluyendo sus datos básicos, logotipo, permisos, rol, notificaciones y configuraciones globales del sistema.
Desde aquí se gestionan tanto los ajustes personales (nombre, correo, contraseña, idioma) como las preferencias de flujo de trabajo (por ejemplo, unidades de medida, notificaciones, alertas o integración con balanzas IoT).

⸻

🧭 Objetivos
	•	Mostrar el perfil del usuario actual (nombre, rol, empresa, correo, logo).
	•	Permitir editar datos básicos y contraseñas.
	•	Ofrecer un panel de configuración del sistema según el rol: proveedor, centro o exportadora.
	•	Activar o desactivar notificaciones y herramientas externas (por ejemplo, balanza, sensor, impresora).
	•	Administrar integraciones API (Odoo, Global_VCE, MPCEIP CSV, etc.).
	•	Acceder a soporte, política de privacidad y cerrar sesión.

⸻

🧱 Secciones principales

1. 🪪 Mi perfil

Contenido:
	•	Foto o logo de usuario/empresa.
	•	Nombre completo.
	•	Empresa asociada.
	•	Rol actual (Proveedor / Centro de Acopio / Exportadora / Admin).
	•	Estado de cuenta (Activo / En revisión / Suspendido).

Acciones:
	•	Editar datos personales.
	•	Cambiar contraseña.
	•	Subir nuevo logo o foto.

Ejemplo Flutter:

ListTile(
  leading: CircleAvatar(
    radius: 24,
    backgroundImage: NetworkImage(user.logoUrl),
  ),
  title: Text(user.nombre),
  subtitle: Text("${user.rol.toUpperCase()} • ${user.empresa}"),
  trailing: IconButton(
    icon: Icon(Icons.edit, color: Colors.green),
    onPressed: () => Navigator.pushNamed(context, '/editarPerfil'),
  ),
);


⸻

2. ⚙️ Configuraciones generales

Panel dinámico de ajustes globales según el rol y las necesidades del flujo.

Tipo de configuración	Descripción	Disponible para
Unidades de medida	Cambiar entre TM, kg, QQ	Todos
Sincronización IoT	Activar conexión con balanzas, sensores de humedad, impresoras	Centro / Exportadora
Alertas automáticas	Activar notificaciones de entrega, recepción o fijación	Todos
Integración con ERP externo (Odoo)	Conectar credenciales API	Admin / Exportadora
Idioma y región	Cambiar idioma, formato de fecha y moneda	Todos
Modo oscuro	Activar / desactivar tema oscuro	Todos

Ejemplo UI Flutter:

SwitchListTile(
  title: Text("Notificaciones automáticas"),
  subtitle: Text("Recibir alertas de nuevos contratos o entregas"),
  value: notificacionesActivas,
  onChanged: (v) => setState(() => notificacionesActivas = v),
);


⸻

3. 🏢 Configuración empresarial

Permite a los usuarios de nivel administrador modificar datos de su empresa.

Campos sugeridos:
	•	Nombre comercial
	•	RUC o ID fiscal
	•	Dirección y ubicación (latitud, longitud)
	•	Contacto principal
	•	Logo o imagen institucional
	•	Lista de usuarios asociados
	•	Tipo de empresa (Exportadora / Centro / Productor)

Acciones:
	•	Editar empresa.
	•	Añadir usuarios o colaboradores.
	•	Activar licencias.
	•	Realizar respaldos o restauraciones de base de datos.

⸻

4. 🧩 Integraciones y API

Panel para conectar o revisar integraciones con servicios externos:
	•	Odoo ERP: Sincronizar stock, órdenes y contratos.
	•	MPCEIP CSV: Actualizar precios FOB automáticamente.
	•	Global_VCE: Recepción de datos IoT (peso, humedad, secado).
	•	Firebase Cloud Messaging (FCM): Notificaciones push.

Ejemplo de campo de configuración:

TextField(
  controller: odooApiKeyController,
  decoration: InputDecoration(
    labelText: "Clave API Odoo",
    suffixIcon: Icon(Icons.lock_outline),
  ),
);


⸻

5. 🔔 Notificaciones y alertas

Gestión de alertas del sistema:
	•	Nuevos contratos asignados.
	•	Actualización de precios internacionales.
	•	Cambios de estado de lotes o entregas.
	•	Mensajes del módulo Chat.

Opciones:
	•	Activar/desactivar notificaciones push.
	•	Elegir qué eventos generan alerta (checkbox list).
	•	Configurar tono o canal de notificación.

⸻

6. 🧰 Soporte y seguridad

Zona final de opciones:
	•	Reportar un problema.
	•	Enviar sugerencias.
	•	Política de privacidad.
	•	Cerrar sesión.
	•	Ver versión de la aplicación.

Ejemplo:

ListTile(
  leading: Icon(Icons.logout, color: Colors.red),
  title: Text("Cerrar sesión"),
  onTap: () => logoutUser(),
);


⸻

🧠 Backend y estructura de datos

Tabla usuarios

id
nombre
rol
empresa_id
email
telefono
idioma
notificaciones
configuracion_json

Tabla empresas

id
nombre
tipo (centro/proveedor/exportadora)
ruc
direccion
logo_url
configuracion_json

Configuraciones se guardan como JSON:

{
  "unidad_medida": "TM",
  "modo_oscuro": true,
  "alertas": {
    "contratos": true,
    "precios": false,
    "mensajes": true
  },
  "iot_activo": false
}


⸻

📁 Estructura sugerida de archivos

lib/
├─ pages/
│  ├─ perfil_page.dart
│  ├─ editar_perfil_page.dart
│  └─ configuracion_page.dart
├─ widgets/
│  ├─ config_switch.dart
│  ├─ config_input.dart
│  └─ perfil_card.dart
└─ services/
   └─ settings_service.dart


⸻

🚀 Próximos pasos
	1.	Crear perfil_page.dart con los datos del usuario logueado.
	2.	Implementar configuracion_page.dart con opciones dinámicas por rol.
	3.	Añadir persistencia local (Hive o SharedPreferences).
	4.	Integrar API REST para guardar cambios.
	5.	Añadir modo oscuro, notificaciones y opciones IoT.
	6.	Unificar con menú inferior (Perfil como última pestaña).

⸻

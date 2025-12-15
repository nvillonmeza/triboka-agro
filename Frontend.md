Perfecto ⚡ — este archivo te servirá como documento maestro de diseño de interfaz y componentes visuales, ideal para desarrolladores y diseñadores del proyecto.
Aquí tienes el contenido completo para ui_design_prompt.md, donde explico cómo está estructurada tu app (estilo, animaciones, tipografía, íconos, gráficos, etc.), con la lógica visual que imita el “CSS mental” de Flutter.

⸻

🎨 Guía de Diseño UI / UX – Sistema ERP de Cacao

📘 Descripción general

Este documento describe la guía de diseño visual y técnico de la aplicación ERP de cacao (Triboka / Global VCE).
Está orientado a Flutter y detalla:
	•	librerías necesarias
	•	estructura general de interfaz
	•	estilos visuales (colores, tipografía, espacios)
	•	distribución de secciones
	•	animaciones y transiciones
	•	diseño de charts e íconos

El objetivo es garantizar coherencia visual y experiencia fluida en todas las pantallas, desde el login hasta el dashboard principal.

⸻

🧩 Estructura general de la aplicación

🧭 Distribución principal (Bottom Navigation)

La app tiene 5 secciones principales, accesibles desde la barra inferior (BottomNavigationBar):

Pestaña	Icono	Descripción
🏠 Inicio	Icons.home_outlined	Muestra el dashboard principal con la tendencia NY, demanda, centros y proveedores.
🧮 Calculadora	Icons.calculate_outlined	Permite calcular precios por TM o QQ, con diferenciales configurables.
⚙️ Gestión	Icons.business_center_outlined	Dashboard dinámico según el rol del usuario.
💬 Chat	Icons.chat_bubble_outline	Canal privado entre socios con contratos activos.
👤 Perfil	Icons.person_outline	Panel personal y configuraciones generales.


⸻

🧱 Estructura visual general

🌈 Paleta de colores
	•	Primario: Color(0xFF059669) → verde esmeralda
	•	Secundario: Color(0xFF10B981) → verde claro
	•	Complementario: Color(0xFFFBBF24) → ámbar
	•	Fondo claro: Color(0xFFF8FAFC)
	•	Texto principal: Color(0xFF1E293B)
	•	Texto secundario: Color(0xFF64748B)
	•	Card blanca: Colors.white

🌙 Se puede activar modo oscuro con ThemeMode.dark y el esquema de ColorScheme.dark().

⸻

✨ Tipografía
	•	Fuente: Poppins o Roboto
	•	Pesos:
	•	400 → texto base
	•	500 → etiquetas
	•	600 → títulos
	•	700 → encabezados

Ejemplo Flutter:

Text("Demanda de exportadoras",
  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14, color: Colors.black87),
);


⸻

🧭 Layout principal

Todas las pantallas siguen una estructura modular:

Scaffold(
  backgroundColor: Color(0xFFF8FAFC),
  appBar: PreferredSize(...),
  body: SafeArea(
    child: Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(children: [/* Contenido dinámico */]),
    ),
  ),
  bottomNavigationBar: CustomNavBar(),
);

🔹 Componentes comunes
	•	Card principal: esquinas redondeadas (radius: 16–20)
	•	Sombras suaves: BoxShadow(blurRadius: 8, color: Colors.black12)
	•	Botones primarios: color verde esmeralda, texto blanco
	•	Botones secundarios: gris claro, texto verde oscuro

⸻

🧭 Animaciones y transiciones

🔹 Librerías recomendadas
	•	animations → para FadeThroughTransition, SharedAxisTransition
	•	flutter_animate → para animaciones declarativas
	•	lottie → para animaciones JSON ilustrativas
	•	flutter_staggered_animations → para animar listas o cards
	•	flutter_animate_do (opcional) → para efectos tipo “pulse”, “slideIn”

Ejemplo:

FadeInUp(
  duration: Duration(milliseconds: 400),
  child: MyCardWidget(),
);


⸻

📊 Charts y visualización de datos

🔹 Librerías recomendadas
	•	fl_chart → gráficos de líneas, barras, pie charts
	•	syncfusion_flutter_charts (opcional, si se requiere zoom y exportación)
	•	charts_flutter_new → versión optimizada para Flutter 3+

🔹 Estilo de gráficos
	•	Bordes redondeados, sin cuadrícula dura.
	•	Líneas suaves tipo cubic.
	•	Paleta degradada (verde esmeralda → verde claro).
	•	Etiquetas flotantes pequeñas con fuente RobotoMono.

Ejemplo (FL Chart):

LineChart(LineChartData(
  lineBarsData: [
    LineChartBarData(
      isCurved: true,
      colors: [Color(0xFF10B981), Color(0xFF059669)],
      barWidth: 3,
      dotData: FlDotData(show: false),
    ),
  ],
  gridData: FlGridData(show: false),
  borderData: FlBorderData(show: false),
));


⸻

🧩 Componentes personalizados por sección

🏠 Inicio
	•	CardTendencia → gráfico del contrato NY.
	•	ExportadoraCard → muestra nombre, contrato y volumen mensual.
	•	StockCard → visualiza stock, humedad y tipo.
	•	SectionHeader → título + botón lateral (“Ver todo”).

🧮 Calculadora
	•	Inputs: TextField redondeados.
	•	Botones: “Añadir diferencial” y “Guardar cálculo”.
	•	Resultado: GridView con tarjetas para TM y QQ.
	•	Historial: lista colapsable con fecha y valores.

⚙️ Gestión
	•	Dashboard dinámico (3 tarjetas de KPI + detalles).
	•	Cambia contenido según rolActual.
	•	Cards codificadas por color: verde (stock), azul (logística), ámbar (contratos).
	•	Animaciones suaves al cambiar rol.

💬 Chat
	•	Diseño estilo WhatsApp Business:
	•	Mensajes alineados (derecha → emisor / izquierda → receptor).
	•	Color de fondo verde pastel (#DCFCE7).
	•	Avatar con inicial del socio.
	•	Librería: flutter_chat_ui o dash_chat_2.
	•	Soporte para archivos, PDF y fotos (opcional).

👤 Perfil
	•	Imagen o logo circular grande.
	•	Botones de acción con íconos edit, settings, logout.
	•	Sección de switches (SwitchListTile) para configuraciones.
	•	Modo oscuro con DynamicTheme.
	•	Tarjeta de empresa con logo, RUC y dirección.

⸻

🧠 Navegación y arquitectura

Patrón recomendado:
MVVM (Model–View–ViewModel) o Clean Architecture con repositorios.
Librerías:
	•	get o go_router → para navegación y control de rutas.
	•	provider o riverpod → para estados globales (rolActual, usuario, token).
	•	hive o shared_preferences → para almacenamiento local.

⸻

🧩 Estructura recomendada del proyecto

lib/
├─ main.dart
├─ routes.dart
├─ models/
│  ├─ usuario.dart
│  ├─ contrato.dart
│  └─ mensaje.dart
├─ services/
│  ├─ api_service.dart
│  ├─ chat_service.dart
│  ├─ settings_service.dart
│  └─ calculadora_service.dart
├─ pages/
│  ├─ inicio_page.dart
│  ├─ calculadora_page.dart
│  ├─ gestion_page.dart
│  ├─ chat_page.dart
│  └─ perfil_page.dart
├─ widgets/
│  ├─ cards/
│  │  ├─ tendencia_card.dart
│  │  ├─ exportadora_card.dart
│  │  ├─ stock_card.dart
│  │  └─ kpi_card.dart
│  └─ components/
│     ├─ nav_bar.dart
│     ├─ section_header.dart
│     ├─ message_bubble.dart
│     └─ toast_notification.dart
└─ themes/
   └─ app_theme.dart


⸻

🔔 Notificaciones y UX dinámica
	•	Integración con Firebase Cloud Messaging (FCM).
	•	Banner superior para nuevos mensajes o alertas de contrato.
	•	Vibración suave (HapticFeedback.mediumImpact()) al recibir evento clave.
	•	“Toast” visual al guardar o eliminar cálculos.

⸻

🎬 Animaciones recomendadas por sección

Sección	Animación	Librería
Inicio	FadeInUp de cada card	flutter_staggered_animations
Calculadora	Expand/Collapse al añadir diferencial	AnimatedContainer
Gestión	Cambio de dashboard por rol con SharedAxisTransition	animations
Chat	FadeInLeft y FadeInRight de burbujas	flutter_animate
Perfil	Hero animation entre avatar y editor	Hero


⸻

📱 Adaptabilidad y diseño responsivo
	•	Escala móvil vertical (maxWidth <= 600)
	•	Scroll principal con SingleChildScrollView
	•	SafeArea + Padding(16) por defecto
	•	Iconos Lucide o MaterialCommunityIcons
	•	Modo tablet: usar GridView.extent en lugar de ListView

⸻

📦 Librerías esenciales (Flutter pubspec.yaml)

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.8
  get: ^4.6.6
  provider: ^6.1.2
  fl_chart: ^0.65.0
  flutter_staggered_animations: ^1.1.1
  animations: ^2.0.8
  flutter_animate: ^4.2.0
  lottie: ^3.0.0
  hive: ^2.2.3
  shared_preferences: ^2.2.3
  firebase_core: ^3.0.0
  firebase_messaging: ^15.0.0
  dash_chat_2: ^1.2.3


⸻

🚀 Objetivo final del diseño

Lograr una interfaz moderna, liviana, adaptable, con colores cálidos del cacao, animaciones suaves y jerarquía clara de información.
Cada usuario debe sentir que su flujo está personalizado, eficiente y visualmente armonizado.

⸻

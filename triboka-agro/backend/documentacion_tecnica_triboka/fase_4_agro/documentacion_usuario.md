# 📖 Documentación de Usuario - Triboka Agro

**Versión:** 1.0.0
**Fecha:** 14 de noviembre de 2025

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Primeros Pasos](#primeros-pasos)
3. [Guía del Productor](#guía-del-productor)
4. [Guía del Exportador](#guía-del-exportador)
5. [Guía del Administrador](#guía-del-administrador)
6. [Guía del Comprador](#guía-del-comprador)
7. [Funcionalidades Comunes](#funcionalidades-comunes)
8. [Solución de Problemas](#solución-de-problemas)
9. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## 🌟 Introducción

Bienvenido a Triboka Agro, la plataforma blockchain para el comercio agrícola que conecta productores, exportadores, compradores y administradores en un ecosistema transparente y confiable.

### ¿Qué es Triboka Agro?

Triboka Agro es una plataforma digital que revoluciona el comercio agrícola mediante:

- **Certificación Blockchain**: Trazabilidad completa desde la siembra hasta la venta
- **Marketplace Inteligente**: Conexión directa entre productores y compradores
- **Gestión de Lotes**: Control completo del ciclo de vida de los productos agrícolas
- **Contratos Inteligentes**: Automatización de acuerdos comerciales
- **Dashboard Personalizado**: Interfaces adaptadas a cada rol de usuario

### Roles en la Plataforma

| Rol | Descripción | Funcionalidades Principales |
|-----|-------------|----------------------------|
| **Productor** | Agricultores y cooperativas | Gestión de lotes, certificación, ventas |
| **Exportador** | Empresas exportadoras | Marketplace, contratos, logística |
| **Comprador** | Importadores y distribuidores | Búsqueda, compra, seguimiento |
| **Administrador** | Equipo Triboka | Gestión del sistema, soporte |

---

## 🚀 Primeros Pasos

### Registro en la Plataforma

1. **Accede al sitio web**: Ve a `https://app.triboka.com`
2. **Haz clic en "Registrarse"**: Ubicado en la esquina superior derecha
3. **Selecciona tu rol**: Productor, Exportador, Comprador o Administrador
4. **Completa el formulario**:
   - Información personal (nombre, email, teléfono)
   - Información del negocio (empresa, ubicación, tipo de cultivo)
   - Documentos de verificación (DNI, certificados, etc.)
5. **Verifica tu email**: Recibirás un enlace de confirmación
6. **Completa tu perfil**: Añade foto, descripción y preferencias

### Configuración Inicial

Después del registro, configura tu cuenta:

```typescript
// Configuración recomendada por rol
const initialSetup = {
  producer: {
    farmLocation: true,
    cropTypes: true,
    certifications: true,
    bankAccount: true
  },
  exporter: {
    companyProfile: true,
    exportLicenses: true,
    logisticsPartners: true,
    paymentMethods: true
  },
  buyer: {
    importRequirements: true,
    preferredOrigins: true,
    qualityStandards: true,
    deliveryPreferences: true
  }
};
```

### Navegación Básica

La interfaz se adapta automáticamente a tu rol:

- **Sidebar izquierdo**: Navegación principal con opciones específicas
- **Header superior**: Notificaciones, perfil y búsqueda global
- **Dashboard central**: Métricas y acciones principales
- **Footer**: Enlaces de ayuda y soporte

---

## 🌾 Guía del Productor

### Dashboard del Productor

Al iniciar sesión, verás tu dashboard personalizado con:

- **Resumen de lotes activos**: Estado actual de tus cultivos
- **Ventas recientes**: Historial de transacciones
- **Certificaciones pendientes**: Documentos por validar
- **Alertas del sistema**: Notificaciones importantes

### Gestión de Lotes

#### Crear un Nuevo Lote

1. Ve a "Lotes" → "Crear Lote"
2. Selecciona el tipo de cultivo
3. Ingresa información básica:
   - Nombre del lote
   - Ubicación (coordenadas GPS)
   - Área cultivada
   - Fecha de siembra
   - Variedad del cultivo

```json
{
  "lote": {
    "nombre": "Café Orgánico Finca El Paraíso",
    "cultivo": "Café",
    "variedad": "Caturra",
    "area": 5.2,
    "ubicacion": {
      "latitud": 5.1234,
      "longitud": -75.5678,
      "finca": "El Paraíso",
      "municipio": "Salamina",
      "departamento": "Caldas"
    },
    "fechaSiembra": "2024-03-15",
    "certificaciones": ["Orgánico", "Fair Trade"]
  }
}
```

#### Registrar Actividades

Para cada lote, registra actividades importantes:

1. **Preparación del suelo**
2. **Siembra**
3. **Fertilización**
4. **Control de plagas**
5. **Cosecha**
6. **Post-cosecha**

Cada actividad incluye:
- Fecha y hora
- Descripción detallada
- Fotos o videos
- Insumos utilizados
- Condiciones climáticas

#### Certificación Blockchain

1. Una vez completadas las actividades, solicita certificación
2. El sistema genera un hash único de todos los datos
3. Se registra en la blockchain como "Certificado de Origen"
4. Recibe un QR code para compartir con compradores

### Ventas y Marketplace

#### Publicar un Lote para Venta

1. Selecciona un lote certificado
2. Define condiciones de venta:
   - Precio por kilogramo
   - Cantidad disponible
   - Calidad del producto
   - Condiciones de entrega

3. Publica en el marketplace
4. Recibe ofertas de compradores

#### Gestionar Ofertas

- **Revisar ofertas**: Compara precios y condiciones
- **Negociar**: Responde a contraofertas
- **Aceptar/Rechazar**: Confirma la venta
- **Generar contrato**: Automáticamente se crea un contrato inteligente

### Seguimiento de Pagos

- **Métodos de pago**: Transferencia bancaria, criptomonedas
- **Verificación**: Confirmación automática via blockchain
- **Historial**: Registro completo de todas las transacciones

---

## 🚛 Guía del Exportador

### Dashboard del Exportador

Tu dashboard incluye:

- **Oportunidades de mercado**: Lotes disponibles para exportación
- **Contratos activos**: Acuerdos comerciales en curso
- **Logística**: Estado de envíos y entregas
- **Análisis de mercado**: Tendencias de precios y demanda

### Navegación del Marketplace

#### Buscar Lotes

Usa filtros avanzados:

- **Tipo de cultivo**: Café, cacao, frutas, etc.
- **Origen**: País, región, finca específica
- **Certificaciones**: Orgánico, Fair Trade, Rainforest Alliance
- **Calidad**: Especialty, premium, estándar
- **Precio**: Rango de precios por kg
- **Disponibilidad**: Cantidad y fecha de cosecha

#### Sistema de Ofertas

1. **Oferta inicial**: Envía propuesta de compra
2. **Negociación**: Intercambia términos con el productor
3. **Contrato inteligente**: Acuerdo vinculante en blockchain
4. **Pago**: Liberación automática al cumplir condiciones

### Gestión de Contratos

#### Crear un Contrato

```json
{
  "contrato": {
    "comprador": "Exportadora XYZ Ltda",
    "vendedor": "Finca El Paraíso",
    "producto": "Café Orgánico",
    "cantidad": 1000,
    "precioUnitario": 8.50,
    "moneda": "USD",
    "condiciones": {
      "calidad": "Especialty Grade 1",
      "entrega": "FOB puerto Buenaventura",
      "pago": "30% anticipo, 70% contra entrega",
      "certificaciones": ["Orgánico", "Fair Trade"]
    },
    "fechas": {
      "contrato": "2024-11-14",
      "entrega": "2024-12-15",
      "pago": "2024-12-20"
    }
  }
}
```

#### Seguimiento de Cumplimiento

- **Verificación automática**: Sensores IoT y blockchain
- **Alertas**: Notificaciones de desviaciones
- **Documentación**: Fotos, certificados, análisis de laboratorio

### Logística y Envíos

#### Planificación de Envíos

1. **Coordinar con productores**: Confirmar fechas de cosecha
2. **Organizar transporte**: Camiones, contenedores, barcos
3. **Documentación aduanera**: Certificados de origen, fitosanitarios
4. **Seguimiento GPS**: Monitoreo en tiempo real

#### Gestión de Riesgos

- **Seguros**: Cobertura contra pérdidas
- **Contingencias**: Planes B para retrasos
- **Comunicación**: Actualizaciones constantes a compradores

---

## 🛒 Guía del Comprador

### Dashboard del Comprador

Incluye:

- **Búsquedas guardadas**: Filtros personalizados
- **Ofertas activas**: Propuestas enviadas
- **Contratos en curso**: Compras confirmadas
- **Historial de compras**: Registro completo

### Búsqueda Avanzada

#### Filtros Disponibles

```typescript
interface SearchFilters {
  cropType: string[];           // Tipo de cultivo
  origin: {
    country: string;
    region: string;
    farm: string;
  };
  certifications: string[];     // Certificaciones requeridas
  quality: {
    grade: string;
    score: number;             // Puntuación de calidad
  };
  price: {
    min: number;
    max: number;
    currency: string;
  };
  quantity: {
    min: number;
    max: number;
  };
  harvestDate: {
    from: Date;
    to: Date;
  };
  sustainability: {
    organic: boolean;
    fairTrade: boolean;
    carbonNeutral: boolean;
  };
}
```

#### Búsqueda por Calidad

- **Taza de cata**: Para café (aroma, sabor, acidez, cuerpo)
- **Análisis sensorial**: Para cacao y otros productos
- **Certificaciones**: Orgánico, biodinámico, etc.
- **Trazabilidad**: Desde semilla hasta exportación

### Proceso de Compra

#### Hacer una Oferta

1. **Seleccionar lote**: De los resultados de búsqueda
2. **Revisar detalles**: Certificaciones, fotos, análisis
3. **Enviar oferta**: Especificar cantidad y precio deseado
4. **Negociar**: Intercambiar términos si es necesario

#### Verificación de Calidad

Antes de la compra final:

- **Muestras**: Solicitar muestras físicas
- **Análisis de laboratorio**: Verificaciones independientes
- **Visitas a finca**: Inspecciones in situ
- **Referencias**: Historial del productor

### Seguimiento Post-Compra

#### Monitoreo de Envío

- **Actualizaciones GPS**: Seguimiento en tiempo real
- **Documentos**: Certificados y permisos aduaneros
- **Condiciones**: Temperatura, humedad durante transporte
- **Entrega**: Confirmación de recepción

#### Evaluación y Feedback

- **Calificar productor**: Sistema de reputación
- **Reportar problemas**: Canal directo de soporte
- **Recomendaciones**: Para futuras compras

---

## ⚙️ Guía del Administrador

### Panel de Administración

Acceso a funciones avanzadas:

- **Gestión de usuarios**: Aprobación de registros
- **Configuración del sistema**: Parámetros globales
- **Monitoreo**: Métricas y alertas
- **Soporte**: Gestión de tickets

### Gestión de Usuarios

#### Aprobación de Registros

1. **Revisar solicitudes**: Nuevos usuarios pendientes
2. **Verificar documentos**: DNI, certificados, licencias
3. **Aprobar/Rechazar**: Con comentarios si es necesario
4. **Asignar rol**: Confirmar el rol solicitado

#### Soporte al Usuario

- **Sistema de tickets**: Seguimiento de problemas
- **Chat en vivo**: Soporte directo
- **Base de conocimientos**: Artículos de ayuda
- **Webinars**: Capacitación para usuarios

### Configuración del Sistema

#### Parámetros Globales

```json
{
  "sistema": {
    "monedas": ["USD", "EUR", "COP"],
    "idiomas": ["es", "en", "pt"],
    "zonasHorarias": ["America/Bogota", "Europe/Madrid", "Asia/Tokyo"],
    "certificacionesActivas": ["Orgánico", "Fair Trade", "Rainforest Alliance", "UTZ"]
  },
  "limites": {
    "maxLotesPorUsuario": 50,
    "maxOfertasSimultaneas": 10,
    "maxTamanoArchivo": "10MB",
    "tiempoExpiracionOferta": "7d"
  }
}
```

#### Monitoreo y Analytics

- **Métricas de uso**: Actividad por rol y región
- **Rendimiento del sistema**: Tiempos de respuesta, uptime
- **Transacciones**: Volumen y valor mensual
- **Alertas**: Problemas críticos del sistema

---

## 🔧 Funcionalidades Comunes

### Gestión del Perfil

#### Editar Información Personal

1. Ve a "Perfil" → "Configuración"
2. Actualiza datos personales
3. Cambia contraseña
4. Gestiona preferencias de notificación

#### Configuración de Notificaciones

```json
{
  "notificaciones": {
    "email": {
      "ofertasNuevas": true,
      "contratosActualizados": true,
      "pagosRecibidos": true,
      "alertasSistema": false
    },
    "push": {
      "navegador": true,
      "movil": true
    },
    "sms": {
      "urgentes": true,
      "marketing": false
    }
  }
}
```

### Búsqueda y Filtros

#### Búsqueda Global

- **Barra de búsqueda**: En el header superior
- **Búsqueda por voz**: Para comodidad
- **Sugerencias inteligentes**: Autocompletado
- **Historial**: Búsquedas recientes

#### Filtros Avanzados

- **Guardar filtros**: Como "búsquedas guardadas"
- **Compartir filtros**: Con colegas
- **Alertas de búsqueda**: Notificaciones cuando aparecen nuevos lotes

### Comunicación

#### Mensajería Interna

- **Chat con usuarios**: Para negociar y coordinar
- **Grupos de discusión**: Por cultivo o región
- **Soporte técnico**: Canal directo con el equipo

#### Notificaciones

- **En tiempo real**: WebSocket para actualizaciones instantáneas
- **Email**: Resúmenes diarios/semanaales
- **Push notifications**: Para eventos importantes

---

## 🐛 Solución de Problemas

### Problemas Comunes

#### No puedo iniciar sesión

**Síntomas:**
- Error "Credenciales inválidas"
- Olvidé mi contraseña

**Soluciones:**
1. Verifica que el email y contraseña sean correctos
2. Usa "Olvidé mi contraseña" para resetear
3. Contacta soporte si el problema persiste

#### La página no carga

**Posibles causas:**
- Problemas de conexión a internet
- Cache del navegador
- Mantenimiento del sistema

**Soluciones:**
1. Actualiza la página (F5)
2. Limpia cache del navegador
3. Intenta con otro navegador
4. Verifica conexión a internet

#### Error al subir archivos

**Límites del sistema:**
- Tamaño máximo: 10MB por archivo
- Formatos permitidos: PDF, JPG, PNG, DOC
- Número máximo: 5 archivos por lote

**Solución:**
1. Comprime archivos grandes
2. Convierte a formatos permitidos
3. Divide en múltiples uploads si es necesario

### Contactar Soporte

#### Canales de Soporte

1. **Chat en vivo**: Disponible 24/7 en la plataforma
2. **Email**: soporte@triboka.com
3. **Teléfono**: +57 1 123 4567 (L-V 8am-6pm COT)
4. **WhatsApp**: +57 300 123 4567

#### Información a Proporcionar

Cuando reportes un problema, incluye:

- **Descripción detallada**: Qué estabas haciendo
- **Pasos para reproducir**: Cómo llegar al error
- **Capturas de pantalla**: Si es posible
- **Información del navegador**: Versión y sistema operativo
- **ID de usuario**: Para identificación rápida

---

## ❓ Preguntas Frecuentes

### Registro y Cuenta

**¿Cuánto tiempo toma aprobar mi registro?**
- Normalmente 24-48 horas hábiles
- Para productores con certificaciones: hasta 72 horas
- Recibirás notificación por email cuando esté aprobado

**¿Puedo cambiar mi rol después del registro?**
- Sí, contacta al soporte para solicitar el cambio
- Deberás proporcionar documentación adicional
- El cambio puede tomar 48-72 horas

**¿Es gratuita la plataforma?**
- Registro y uso básico: Gratuito
- Comisiones por transacción: 2-5% según el volumen
- Funciones premium: Suscripción mensual opcional

### Lotes y Certificaciones

**¿Qué certificaciones aceptan?**
- Orgánico, Fair Trade, Rainforest Alliance
- UTZ, 4C, Comercio Justo
- Certificaciones locales reconocidas

**¿Cómo se verifica la trazabilidad?**
- Cada actividad se registra con timestamp
- Fotos y coordenadas GPS
- Hash blockchain único por lote
- Verificación por terceros independientes

**¿Puedo vender lotes sin certificación completa?**
- Sí, pero con limitaciones en el marketplace
- Los compradores pueden requerir certificación completa
- Recomendamos completar el proceso para mejores precios

### Pagos y Contratos

**¿Qué métodos de pago aceptan?**
- Transferencia bancaria internacional
- Criptomonedas (ETH, USDC)
- PayPal para montos pequeños
- Carta de crédito para grandes volúmenes

**¿Los contratos son legalmente vinculantes?**
- Sí, son contratos inteligentes en blockchain
- Tienen validez legal en países participantes
- Recomendamos asesoría legal adicional

**¿Qué pasa si hay un conflicto?**
- Mediación a través de la plataforma
- Arbitraje blockchain si es necesario
- Equipo legal especializado disponible

### Seguridad y Privacidad

**¿Cómo protegen mis datos?**
- Encriptación end-to-end
- Cumplimiento GDPR y leyes locales
- Auditorías de seguridad regulares
- Acceso basado en roles estrictos

**¿Quién puede ver mi información?**
- Solo usuarios autorizados en transacciones
- Equipo de soporte cuando es necesario
- Autoridades solo con orden judicial

**¿Qué pasa con mis datos si cierro la cuenta?**
- Se anonimizan pero se mantienen por cumplimiento legal
- Puedes solicitar eliminación completa
- Historial de transacciones se preserva en blockchain

---

## 📞 Contacto y Soporte

### Información de Contacto

- **Email Principal**: info@triboka.com
- **Soporte Técnico**: soporte@triboka.com
- **Ventas**: ventas@triboka.com
- **Teléfono**: +57 1 123 4567
- **WhatsApp Business**: +57 300 123 4567

### Horarios de Atención

- **Soporte Técnico**: 24/7
- **Ventas**: L-V 8:00 - 18:00 COT
- **Chat en Vivo**: L-V 9:00 - 17:00 COT

### Redes Sociales

- **LinkedIn**: @TribokaAgro
- **Twitter**: @TribokaAgro
- **Instagram**: @TribokaAgro
- **YouTube**: Triboka Agro

---

*Gracias por elegir Triboka Agro. Estamos comprometidos a revolucionar el comercio agrícola con transparencia, confianza y sostenibilidad.*
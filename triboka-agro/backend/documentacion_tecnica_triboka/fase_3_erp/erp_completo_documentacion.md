# 🚀 **DOCUMENTACIÓN COMPLETA DEL ERP TRIBOKA**

## **Basado en "Idea del ERP.md" - Arquitectura Unificada Triboka Agro + ERP**

---

# 🌍 **VISIÓN GENERAL DEL SISTEMA UNIFICADO**

## **Triboka Agro + Triboka ERP: Arquitectura Unificada**

Este documento representa la **implementación completa** del sistema ERP empresarial para exportadoras de cacao, integrado con la plataforma Web3 de trazabilidad Triboka Agro.

### **Componentes del Sistema:**

#### **🔵 Triboka Agro (Plataforma Web3)**
- **Propósito:** Trazabilidad blockchain completa desde productor hasta exportador
- **Funcionalidades:** Registro de productores, lotes de origen, certificados, API pública
- **Enfoque:** Visión neutral, sin comercio directo

#### **🟫 Triboka ERP (Sistema Empresarial)**
- **Propósito:** Procesos industriales completos del cacao en exportadoras
- **Módulos:** Recepción, Calidad, Secado, Mermas, Almacenamiento, Batches, Contratos, Despachos
- **Integración:** Consume API de Triboka Agro y genera eventos blockchain posteriores

#### **🟧 Admin Triboka (Sistema Master)**
- **Propósito:** Gestión global de empresas, usuarios, licencias y monitoreo
- **Funcionalidades:** Control de API Keys, auditoría global, soporte multi-tenant

---

# 🧩 **ROLES Y PERMISOS DEL SISTEMA**

| Rol | Alcance | Permisos Principales |
|-----|---------|---------------------|
| **Productor** | Sus propios lotes | Crear lote, ver trazabilidad completa |
| **Exportadora - Admin Empresa** | Todo el ERP de su empresa | Control total del flujo industrial |
| **Exportadora - Acopio** | Módulo de recepción | Registrar llegada de lotes, pesos, impurezas |
| **Exportadora - Calidad** | Laboratorio | Análisis de corte, fermentación, humedad, impurezas |
| **Exportadora - Secado** | Procesos de secado | Registrar peso seco, mermas, duración |
| **Contabilidad** | Costos y análisis | Cálculos internos, reportes financieros |
| **Ventas/Exportación** | Contratos y despachos | Fijaciones, documentos, envíos |
| **Auditor Externo** | Solo lectura | Verificación sin edición |
| **Admin Triboka** | Sistema completo | Gestión de empresas, soporte global |
| **Broker** | Conexiones comerciales | Acuerdos entre partes |

---

# ⛓️ **CADENA COMPLETA DE TRAZABILIDAD BLOCKCHAIN**

## **Eventos Blockchain Oficiales:**

1. **`PRODUCER_INIT`** - Productor registra lote inicial (Triboka Agro)
2. **`RECEPCION_EXPORTADORA`** - Exportadora recibe lote (ERP)
3. **`CALIDAD_LABORATORIO`** - Análisis de calidad completado (ERP)
4. **`SECADO`** - Proceso de secado finalizado (ERP)
5. **`MERMA`** - Registro de pérdidas calculadas (ERP)
6. **`ALMACENAMIENTO`** - Movimiento a bodega (ERP)
7. **`BATCH`** - Creación de mezcla/lote de exportación (ERP)
8. **`FIJACION`** - Contrato de precio fijado (ERP)
9. **`DESPACHO`** - Mercancía enviada (ERP)
10. **`BROKER_DEAL`** - Acuerdo comercial intermediado (Admin)

### **Características Técnicas:**
- **Hash + Metadata:** Cada evento genera hash on-chain + metadata detallada off-chain
- **Blockchain Ligera:** Solo hashes principales, datos completos en Triboka Agro
- **Verificación:** Trazabilidad completa desde finca hasta cliente final

---

# 🔌 **INTEGRACIÓN ERP ↔ TRIBOKA AGRO**

## **4.1 Datos que el ERP obtiene de Agro:**

```json
{
  "codigo_lote": "1234-5678-ABC",
  "productor": {
    "nombre": "Finca El Paraíso",
    "ubicacion": "Manabí, Ecuador",
    "certificaciones": ["Orgánico", "FT", "Rainforest"]
  },
  "datos_iniciales": {
    "peso_inicial": 1000,
    "humedad_inicial": 58,
    "tipo_cacao": "Nacional Fino",
    "fecha_cosecha": "2025-10-15"
  },
  "fotos": ["url1.jpg", "url2.jpg"],
  "geolocalizacion": {"lat": -1.234, "lng": -78.456},
  "hash_inicial": "0xABC123...",
  "trazabilidad_hasta_ahora": [...]
}
```

## **4.2 Eventos que el ERP envía a Agro:**

**Endpoint estándar:**
```
POST /api/lotes/{codigo}/event/{tipo}
```

**Payload estandarizado:**
```json
{
  "tipo_evento": "SECADO",
  "timestamp": "2025-11-12T22:30:10Z",
  "empresa_id": 18,
  "responsable": "id_usuario",
  "metadata": {
    "peso_seco": 350,
    "peso_baba_inicial": 980,
    "humedad_inicial": 58,
    "humedad_final": 7,
    "merma_total": 65.3,
    "tipo_secado": "industrial",
    "imagenes": ["url1", "url2"]
  },
  "firma": "0xABC123..."
}
```

---

# 🏭 **MÓDULOS DEL ERP - ESPECIFICACIONES COMPLETAS**

## **5.1 Módulo de Recepción (Acopio)**

### **Datos Registrados:**
- **Peso bruto** (kg)
- **Tara** (kg) - peso de sacos/vaciado
- **Número de sacos**
- **Humedad inicial** (%)
- **Impurezas estimadas** (%)
- **Peso neto** (calculado)
- **Centro de acopio**
- **Fecha/hora recepción**
- **Responsable**
- **Fotos/evidencia**
- **QR código interno**

### **Cálculos Automáticos:**
```
peso_neto = peso_bruto - tara
peso_estimado_seco = peso_neto * (1 - humedad_inicial/100)
```

### **Evento Blockchain:** `RECEPCION_EXPORTADORA`

---

## **5.2 Módulo de Laboratorio/Calidad**

### **Análisis Completos:**
- **Corte de fermentación** (visual)
- **% Fermentación**
- **% Moho**
- **% Violetas**
- **% Impurezas reales** (vs estimadas)
- **% Humedad final**
- **Grado de cacao**
- **Observaciones detalladas**
- **Fotos del análisis**
- **Certificaciones adicionales**

### **Validaciones:**
- Humedad final debe ser < 8%
- Impurezas < 2%
- Fermentación adecuada por tipo

### **Evento Blockchain:** `CALIDAD_LABORATORIO`

---

## **5.3 Módulo de Secado**

### **Parámetros de Control:**
- **Humedad inicial** (%)
- **Humedad objetivo** (%) - típicamente 6-7%
- **Tipo de secado:** Natural / Industrial
- **Peso húmedo inicial** (kg)
- **Peso seco final** (kg)
- **Duración del proceso** (horas/días)
- **Secadora utilizada**
- **Turnos de trabajo**
- **Temperatura/humedad** (si industrial)

### **Cálculos de Mermas:**
```
merma_humedad = peso_humedo * (humedad_inicial - humedad_objetivo) / (100 - humedad_objetivo)
merma_total = peso_humedo - peso_seco
porcentaje_merma = (merma_total / peso_humedo) * 100
```

### **Evento Blockchain:** `SECADO`

---

## **5.4 Módulo de Mermas**

### **Fuentes de Mermas:**
- **Merma por humedad** (evaporación)
- **Merma por impurezas** (eliminación)
- **Merma por secado** (pérdidas industriales)
- **Merma total acumulada**

### **Tracking por Lote:**
- Merma en cada etapa
- Razones específicas
- Evidencia fotográfica
- Impacto en costos

### **Evento Blockchain:** `MERMA`

---

## **5.5 Módulo de Almacenamiento**

### **Funcionalidades:**
- **Definición de bodegas/silos**
- **Capacidad por ubicación**
- **Movimientos entre bodegas**
- **Inventario en tiempo real**
- **Control de acceso por roles**
- **QR tracking interno**
- **Auditoría de movimientos**

### **Datos Registrados:**
- Ubicación actual
- Fecha movimiento
- Responsable
- Motivo
- Cantidad movida

### **Evento Blockchain:** `ALMACENAMIENTO`

---

## **5.6 Módulo de Batches**

### **Composición de Lotes:**
- **Selección múltiple de lotes secos**
- **Porcentajes por lote origen**
- **Peso final del batch**
- **Clase de cacao resultante**
- **Código único del batch**
- **Fecha de mezcla**
- **Homogeneización completada**

### **Cálculos:**
```
peso_batch = Σ (peso_lote_i * porcentaje_i)
clase_resultante = promedio_ponderado(clases_origen)
```

### **Evento Blockchain:** `BATCH`

---

## **5.7 Módulo de Contratos**

### **Tipos de Contrato:**
- **Contrato de compra** (con productores)
- **Contrato de venta** (con clientes)
- **Acuerdos forward** (precio futuro)

### **Elementos del Contrato:**
- **Volumen** (TM)
- **Precio base** (diferencial)
- **Spot del día**
- **Fecha de fijación**
- **Relación con batch específico**
- **Condiciones especiales**

### **Workflow:**
1. Creación del contrato
2. Aprobación interna
3. Firma digital
4. Ejecución
5. Cierre

### **Evento Blockchain:** `FIJACION`

---

## **5.8 Módulo de Despacho**

### **Preparación del Envío:**
- **Selección de batch/lote**
- **Container asignado**
- **Documentos aduaneros**
- **Certificados de calidad**
- **Guía de transporte**
- **Fotos del embalaje**

### **Datos Logísticos:**
- **Puerto de origen**
- **Puerto de destino**
- **Nave asignada**
- **Fecha estimada**
- **Cliente final**
- **Documentos requeridos**

### **Evento Blockchain:** `DESPACHO`

---

# 🏢 **ARQUITECTURA MULTI-TENANT**

## **13.1 Arquitectura SaaS Implementada:**

### **Modelo Tenant:**
```python
class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    razon_social = db.Column(db.String(200))
    ruc = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(50))
    
    # Configuración
    moneda_principal = db.Column(db.String(10), default='USD')
    zona_horaria = db.Column(db.String(50), default='America/Guayaquil')
    
    # Límites
    max_usuarios = db.Column(db.Integer, default=10)
    max_lotes_activos = db.Column(db.Integer, default=1000)
    plan_suscripcion = db.Column(db.String(50), default='basico')
    
    # Relaciones
    productores = db.relationship('Productor', backref='tenant', lazy='dynamic')
    centros_acopio = db.relationship('CentroAcopio', backref='tenant', lazy='dynamic')
    lotes = db.relationship('LoteCacao', backref='tenant', lazy='dynamic')
    contratos_compra = db.relationship('ContratoCompra', backref='tenant', lazy='dynamic')
    contratos_venta = db.relationship('ContratoVenta', backref='tenant', lazy='dynamic')
    fijaciones = db.relationship('FijacionPrecio', backref='tenant', lazy='dynamic')
```

### **Aislamiento de Datos:**
- **tenant_id** en 8 tablas principales
- **Queries filtradas automáticamente**
- **Datos completamente separados** por empresa
- **UUID único** por tenant para APIs

### **Tenants de Ejemplo:**
- **Triboka Cacao S.A.** - Empresa principal
- **Cooperativa Cacaotera Manabí** - Cooperativa de productores

## **13.2 APIs Multi-Tenant:**

### **Headers Requeridos:**
```http
X-Tenant-UUID: ef17367b-41b7-44ab-9737-4fee8d3aa8f9
Authorization: Bearer <jwt_token>
```

### **Middleware de Tenant:**
```python
@app.before_request
def set_tenant():
    tenant_uuid = request.headers.get('X-Tenant-UUID')
    if tenant_uuid:
        tenant = Tenant.query.filter_by(uuid=tenant_uuid).first()
        if tenant:
            g.tenant = tenant
            g.tenant_id = tenant.id
        else:
            return jsonify({'error': 'Tenant no encontrado'}), 404
```

### **Queries con Tenant Isolation:**
```python
# Automáticamente filtrado por tenant
@lotes_bp.route('/api/lotes', methods=['GET'])
@jwt_required()
def get_lotes():
    lotes = LoteCacao.query.filter_by(tenant_id=g.tenant_id).all()
    return jsonify([lote.to_dict() for lote in lotes])
```

## **13.3 Beneficios Multi-Tenant:**

- **Escalabilidad:** 1000+ empresas en una instancia
- **Mantenimiento:** Updates simultáneos para todos
- **Costo:** Infraestructura compartida
- **Seguridad:** Aislamiento total de datos
- **Personalización:** Configuración por tenant

---

# 📦 **ARQUITECTURA TÉCNICA DEL FRONTEND**

## **6.1 Stack Tecnológico:**

- **Framework:** Next.js 14 con App Router
- **Lenguaje:** TypeScript
- **Estilos:** Tailwind CSS
- **UI Components:** shadcn/ui
- **Estado:** Zustand
- **APIs:** React Query (TanStack Query)
- **Autenticación:** JWT

## **6.2 Estructura de Directorios:**

```
/app
   /(public)
      /landing
      /login
   /(admin)
      /empresas
      /usuarios
   /(erp)
      /dashboard
      /recepcion
      /calidad
      /secado
      /bodegas
      /batches
      /contratos
      /despachos
   /(productor)
      /lotes
      /trazabilidad
/components
   /ui
   /forms
   /charts
/hooks
   /api
   /auth
/lib
   /utils
   /validations
/providers
   /auth
   /api
/styles
   /globals.css
```

## **6.3 Sistema de Autenticación:**

### **JWT Implementation:**
- **Almacenamiento:** httpOnly cookies (seguridad)
- **Renovación:** Automática antes de expirar
- **Payload:** Incluye roles y permisos
- **Middleware:** Protección de rutas

### **Middleware de Rutas:**
```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')
  const user = verifyToken(token)
  
  if (!user) return NextResponse.redirect('/login')
  
  // Verificar permisos por ruta
  const path = request.nextUrl.pathname
  if (path.startsWith('/erp') && !user.roles.includes('erp')) {
    return NextResponse.redirect('/no-permisos')
  }
}
```

## **6.4 Autorización por Roles:**

### **Layout por Módulo:**
```typescript
// app/(erp)/recepcion/layout.tsx
export default function Layout({ children }: { children: React.ReactNode }) {
  const { user } = useAuth()
  
  if (!user?.roles.includes('acopio')) {
    return <NoPermisos />
  }
  
  return (
    <SidebarProvider>
      <ErpSidebar role="acopio" />
      <main>{children}</main>
    </SidebarProvider>
  )
}
```

## **6.5 Interfaz de Usuario - UX:**

### **Sidebar Dinámico por Rol:**
```typescript
// components/ErpSidebar.tsx
const menuItems = {
  acopio: [
    { label: 'Recepción', href: '/erp/recepcion' },
    { label: 'Lotes Activos', href: '/erp/lotes' }
  ],
  calidad: [
    { label: 'Laboratorio', href: '/erp/calidad' },
    { label: 'Análisis Pendientes', href: '/erp/analisis' }
  ],
  secado: [
    { label: 'Procesos Activos', href: '/erp/secado' },
    { label: 'Mermas', href: '/erp/mermas' }
  ]
}
```

### **Dashboard Principal:**
- **KPIs en Cards:** Lotes activos, producción diaria, mermas promedio
- **Gráficos:** Evolución de procesos, eficiencia por centro
- **Notificaciones:** Alertas de calidad, procesos pendientes
- **Navegación Rápida:** Acceso directo a módulos principales

### **Formularios por Módulo:**
- **Wizard Steps:** Procesos complejos divididos en pasos
- **Validación en Tiempo Real:** Feedback inmediato
- **Carga de Evidencia:** Fotos, documentos, QR
- **Cálculos Automáticos:** Pesos, porcentajes, mermas

---

# 🔌 **INTEGRACIÓN CON API DE TRIBOKA AGRO**

## **7.1 Importación de Lotes:**

### **Flujo de Importación:**
1. **Usuario ingresa código:** `1234-5678-ABC`
2. **Frontend consulta API:**
   ```typescript
   const response = await api.get(`/lotes/${codigo}`)
   ```
3. **Muestra datos del lote:**
   - Nombre del productor
   - Ubicación y finca
   - Humedad inicial
   - Peso estimado
   - Fotos del lote
   - Trazabilidad hasta ahora

4. **Botón "Importar al ERP":**
   - Crea registro interno
   - Asigna código ERP único
   - Prepara para recepción física

## **7.2 Envío de Eventos Blockchain:**

### **Registro desde Frontend:**
```typescript
// components/SecadoForm.tsx
const handleSubmit = async (data: SecadoData) => {
  // Validar datos
  const validation = validateSecadoData(data)
  if (!validation.valid) return
  
  // Enviar a backend ERP
  const response = await api.post(`/lotes/${loteId}/secado`, data)
  
  // Backend envía evento a Triboka Agro
  // POST /api/lotes/{codigo}/event/secado
  
  // Actualizar UI
  toast.success('Proceso registrado y enviado a blockchain')
}
```

---

# 🗄️ **MODELO DE BASE DE DATOS**

## **8.1 Tablas Principales:**

```sql
-- Empresas y usuarios
empresas (id, nombre, api_key, licencia, configuracion)
usuarios (id, empresa_id, nombre, email, roles, permisos)

-- Datos maestros
productos (id, nombre, tipo, especificaciones)
centros_acopio (id, empresa_id, nombre, ubicacion, capacidad)
bodegas (id, empresa_id, nombre, tipo, capacidad)

-- Lotes y procesos
lotes_origen (id, codigo_agro, empresa_id, productor_id, datos_iniciales)
lotes_erp (id, lote_origen_id, codigo_interno, estado_actual)
recepcion (id, lote_erp_id, fecha, peso_bruto, tara, peso_neto, impurezas)
calidad (id, lote_erp_id, fecha, corte, fermentacion, humedad, impurezas, observaciones)
secado (id, lote_erp_id, fecha_inicio, fecha_fin, tipo, peso_inicial, peso_final, merma)
almacenamiento (id, lote_erp_id, bodega_id, fecha, tipo_movimiento, cantidad)
mermas (id, lote_erp_id, etapa, tipo_merma, cantidad, porcentaje, razon)

-- Batches y comercial
batches (id, empresa_id, codigo, fecha_creacion, peso_total, clase)
batch_detalles (id, batch_id, lote_erp_id, porcentaje, peso_contribuido)
contratos (id, empresa_id, tipo, cliente_id, volumen, precio, fecha_fijacion)
fijaciones (id, contrato_id, batch_id, precio_fijado, fecha)
despachos (id, batch_id, fecha, destino, documentos, estado)

-- Blockchain y auditoría
eventos_blockchain (id, lote_id, tipo_evento, hash, timestamp, metadata)
auditoria (id, usuario_id, accion, tabla, registro_id, fecha, cambios)
```

## **8.2 Relaciones y Constraints:**

- **Foreign Keys:** Todas las tablas relacionadas con IDs válidos
- **Unique Constraints:** Códigos únicos, combinaciones lógicas
- **Check Constraints:** Porcentajes entre 0-100, pesos positivos
- **Triggers:** Cálculos automáticos de mermas, actualización de estados

---

# 🔐 **SEGURIDAD Y AUTENTICACIÓN**

## **9.1 API Keys por Empresa:**
- **Generación:** Automática al crear empresa
- **Rotación:** Programada o manual
- **Limitación:** Rate limiting por hora/día
- **Validación:** En cada request a APIs

## **9.2 JWT con Roles:**
- **Firma:** RSA 256 bits
- **Expiración:** 1 hora para access, 7 días para refresh
- **Payload:** user_id, empresa_id, roles[], permisos[]
- **Renovación:** Automática vía refresh token

## **9.3 Autorización Granular:**
- **Por módulo:** Acceso completo o denegado
- **Por acción:** CRUD individual
- **Por registro:** Solo los de su empresa
- **Auditoría:** Log completo de acciones

## **9.4 Encriptación:**
- **Datos sensibles:** Encriptados en BD
- **Transmisiones:** TLS 1.3 obligatorio
- **Fotos/Evidencia:** Encriptadas en almacenamiento
- **Firmas blockchain:** Claves seguras

---

# 📊 **DASHBOARD EMPRESARIAL**

## **10.1 KPIs Principales:**

### **Métricas de Producción:**
- **Lotes activos:** En proceso vs completados
- **Peso recibido:** TM por día/semana/mes
- **Peso seco producido:** Eficiencia de procesos
- **Merma promedio:** Por tipo y etapa

### **Métricas de Calidad:**
- **% Rechazos:** Por impurezas o calidad
- **Tiempo promedio:** Por proceso (recepción → despacho)
- **Certificaciones:** Órgano, FT, Rainforest

### **Métricas Comerciales:**
- **Contratos activos:** Volumen comprometido
- **Batches listos:** Para despacho
- **Despachos pendientes:** Por puerto/cliente

## **10.2 Gráficos y Visualizaciones:**

### **Tendencias:**
- **Mermas vs tiempo:** Identificar mejoras
- **Secado vs humedad:** Eficiencia de procesos
- **Producción vs capacidad:** Utilización de recursos

### **Distribuciones:**
- **Mapa de bodegas:** Ocupación visual
- **Lotes por productor:** Diversidad de suministro
- **Calidad por centro:** Comparativa de acopios

### **Alertas y Notificaciones:**
- **Procesos atrasados:** > 24h sin movimiento
- **Calidad fuera de rango:** Humedad > 8%
- **Capacidad excedida:** Bodegas al 90%

---

# 💰 **MODELO DE NEGOCIO**

## **11.1 Para Empresas ERP:**

### **Licencias:**
- **Mensual/Anual:** $X por mes
- **Límite de lotes:** Máximo procesables
- **Límite de usuarios:** Por rol
- **API calls:** Incluidos + extras

### **Pago por Servicios:**
- **Eventos blockchain:** $Y por evento
- **Certificados premium:** $Z adicional
- **Soporte premium:** Planes diferenciados

## **11.2 Para Productores (Agro):**
- **Gratis:** Registro y trazabilidad básica
- **Comisión broker:** % por ventas intermediadas

## **11.3 Revenue Streams:**
- **Licencias SaaS:** Recurring revenue
- **Blockchain events:** Pay per use
- **Certificaciones:** Premium features
- **Consultoría:** Implementación y training

---

# 🛣️ **ROADMAP DE DESARROLLO**

## **Fase 1: Arquitectura Core (Completada)**
- ✅ Backend APIs RESTful
- ✅ Base de datos PostgreSQL
- ✅ Autenticación JWT
- ✅ Integración blockchain

## **Fase 2: Módulos Core (Completada)**
- ✅ Recepción (Acopio)
- ✅ Calidad (Laboratorio)
- ✅ Secado y Mermas
- ✅ Almacenamiento
- ✅ Batches

## **Fase 3: Módulos Empresariales (En Desarrollo)**
- 🚧 Contratos y Fijaciones
- 🚧 Despacho y Logística
- 🚧 Dashboard Analytics
- 🚧 Reportes Avanzados

## **Fase 4: Frontend Completo**
- ❌ Next.js App Router
- ❌ Componentes UI/UX
- ❌ Dashboard Interactivo
- ❌ Móvil Responsive

## **Fase 5: Escalabilidad**
- ❌ Multi-tenancy completo
- ❌ APIs externas
- ❌ Integración IoT
- ❌ IA para predicciones

---

# 🔧 **CONFIGURACIÓN TÉCNICA**

## **12.1 Arquitectura de Despliegue:**

```
ERP Backend (Flask/FastAPI)
├── Puerto: 5007
├── Base de datos: PostgreSQL
├── Cache: Redis
├── APIs: RESTful JSON

ERP Frontend (Next.js)
├── Puerto: 3002
├── SSR: App Router
├── API Client: React Query
├── UI: Tailwind + shadcn

Blockchain Integration
├── Red: Polygon
├── Smart Contracts: Solidity
├── Wallet: MetaMask
├── API: Web3.js
```

## **12.2 Variables de Entorno:**

```bash
# Base de datos
DATABASE_URL=postgresql://user:pass@localhost:5432/triboka_erp

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Blockchain
POLYGON_RPC_URL=https://polygon-rpc.com
CONTRACT_ADDRESS=0x...

# APIs
TRIBOKA_AGRO_API_URL=https://api.triboka.com
TRIBOKA_AGRO_API_KEY=your-api-key

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
```

## **12.3 Servicios Systemd:**

```ini
# /etc/systemd/system/triboka-erp-backend.service
[Unit]
Description=Triboka ERP Backend
After=network.target

[Service]
User=triboka
WorkingDirectory=/home/triboka/erp/backend
ExecStart=/home/triboka/erp/venv/bin/gunicorn -w 4 -b 0.0.0.0:5007 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

---

# 📋 **CHECKLIST DE IMPLEMENTACIÓN**

## **Backend APIs:**
- ✅ Empresas y usuarios
- ✅ Productores y centros acopio
- ✅ Lotes y recepción
- ✅ Calidad y laboratorio
- ✅ Secado y mermas
- ✅ Almacenamiento
- ✅ Batches
- 🚧 Contratos
- ❌ Despacho

## **Base de Datos:**
- ✅ Modelos SQLAlchemy
- ✅ Migraciones
- ✅ Índices de rendimiento
- ✅ Constraints y validaciones
- ✅ Triggers automáticos

## **Blockchain:**
- ✅ Conexión Polygon
- ✅ Smart contracts
- ✅ Eventos on-chain
- ✅ Verificación off-chain

## **Frontend:**
- ❌ Estructura Next.js
- ❌ Autenticación
- ❌ Dashboard básico
- ❌ Formularios por módulo

## **Seguridad:**
- ✅ JWT implementado
- ✅ API Keys
- ✅ Rate limiting
- ✅ Logs de auditoría

## **Testing:**
- 🚧 Unit tests básicos
- ❌ Integration tests
- ❌ E2E tests

---

# 🎯 **PRÓXIMOS PASOS**

## **Inmediatos (Esta Semana):**
1. **Completar Contratos:** APIs CRUD + workflow
2. **Dashboard Analytics:** KPIs principales + gráficos
3. **Reportes Básicos:** PDF/Excel export

## **Cortos (Próximas 2 Semanas):**
1. **Módulo Despacho:** Envíos + logística
2. **Frontend Next.js:** Reemplazar Flask
3. **Testing Completo:** Cobertura 80%+

## **Medianos (Próximo Mes):**
1. **Multi-tenancy:** Instancias por empresa
2. **APIs Externas:** Integración terceros
3. **Móvil:** App responsive completa

## **Largos (Próximos 3 Meses):**
1. **IA/ML:** Predicciones de calidad/costos
2. **IoT:** Sensores en procesos
3. **Blockchain Avanzado:** NFTs por lote

---

# 📞 **SOPORTE Y CONTACTO**

## **Equipo de Desarrollo:**
- **Lead Developer:** [Nombre]
- **Blockchain Specialist:** [Nombre]
- **UX/UI Designer:** [Nombre]

## **Documentación Técnica:**
- **API Docs:** `/docs` (Swagger)
- **Guías:** `/docs/guides`
- **Ejemplos:** `/docs/examples`

## **Soporte:**
- **Email:** soporte@triboka.com
- **Slack:** #erp-support
- **Issues:** GitHub repository

---

**Versión:** 1.0 - Noviembre 2025
**Última actualización:** [Fecha actual]
**Estado:** Documentación completa basada en "Idea del ERP.md"
# 📋 Especificaciones Técnicas - Triboka Agro Frontend

**Versión:** 1.0.0
**Fecha:** 14 de noviembre de 2025

---

## 📋 Tabla de Contenidos

1. [Visión General del Sistema](#visión-general-del-sistema)
2. [Arquitectura Técnica](#arquitectura-técnica)
3. [Especificaciones Funcionales](#especificaciones-funcionales)
4. [Especificaciones No Funcionales](#especificaciones-no-funcionales)
5. [Interfaces de Usuario](#interfaces-de-usuario)
6. [APIs y Integraciones](#apis-y-integraciones)
7. [Base de Datos](#base-de-datos)
8. [Seguridad](#seguridad)
9. [Performance y Escalabilidad](#performance-y-escalabilidad)

---

## 🎯 Visión General del Sistema

### Propósito y Alcance

Triboka Agro es una plataforma blockchain para el comercio agrícola que conecta productores, exportadores, compradores y administradores en un ecosistema transparente y confiable. El frontend proporciona una interfaz web moderna y responsiva para todas las operaciones del sistema.

### Usuarios Objetivo

| Usuario | Descripción | Volumen Estimado |
|---------|-------------|------------------|
| **Productores** | Agricultores y cooperativas | 10,000+ |
| **Exportadores** | Empresas exportadoras | 500+ |
| **Compradores** | Importadores y distribuidores | 1,000+ |
| **Administradores** | Equipo Triboka | 50 |

### Casos de Uso Principales

1. **Gestión de Lotes Agrícolas**
2. **Certificación Blockchain**
3. **Marketplace B2B**
4. **Contratos Inteligentes**
5. **Trazabilidad Completa**
6. **Análisis y Reportes**

---

## 🏗️ Arquitectura Técnica

### Stack Tecnológico

#### Frontend Framework
- **Next.js 16.0.3**: React framework con App Router
- **React 18**: Biblioteca de UI con Concurrent Features
- **TypeScript 5.0+**: Tipado estático obligatorio

#### Gestión de Estado
- **Zustand**: State management con persistencia
- **React Query**: Server state management y caching
- **Context API**: Estado local de componentes

#### UI/UX
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide Icons**: Iconografía consistente
- **Radix UI**: Componentes base accesibles
- **Framer Motion**: Animaciones y transiciones

#### Desarrollo y Calidad
- **ESLint**: Linting y estándares de código
- **Prettier**: Formateo automático
- **Jest**: Testing unitario
- **React Testing Library**: Testing de componentes
- **Playwright**: Testing E2E
- **Husky**: Git hooks

#### Despliegue y DevOps
- **Vercel/Netlify**: Hosting y CDN
- **GitHub Actions**: CI/CD
- **Docker**: Containerización
- **PM2**: Process management

### Arquitectura de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 App Router (Next.js)                    │ │
│  │  ┌─────────────┬─────────────┬─────────────┬──────────┐ │ │
│  │  │  Auth Pages │ Dashboard   │  Public     │ API      │ │ │
│  │  │             │ Pages       │  Pages      │ Routes    │ │ │
│  │  └─────────────┴─────────────┴─────────────┴──────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Component Layer                          │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐ │
│  │   Layout    │   Forms     │   Charts    │   UI       │ │ │
│  │ Components  │ Components  │ Components  │ Components │ │ │
│  └─────────────┴─────────────┴─────────────┴─────────────┘ │ │
├─────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                    │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐ │
│  │   Hooks     │   Stores    │   Services  │   Utils    │ │ │
│  │             │ (Zustand)   │             │            │ │ │
│  └─────────────┴─────────────┴─────────────┴─────────────┘ │ │
├─────────────────────────────────────────────────────────────┤
│                    Data Access Layer                       │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐ │
│  │   API       │   Cache     │   Local     │   External │ │ │
│  │   Client    │   (React    │   Storage   │   APIs      │ │ │
│  │             │   Query)    │             │             │ │ │
│  └─────────────┴─────────────┴─────────────┴─────────────┘ │ │
└─────────────────────────────────────────────────────────────┘
```

### Patrón de Arquitectura

#### Component Architecture Pattern

```typescript
// Patrón de composición para componentes reutilizables
interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
  'data-testid'?: string;
}

// Componente base
function BaseComponent({ className, children, ...props }: BaseComponentProps) {
  return (
    <div className={cn('base-component', className)} {...props}>
      {children}
    </div>
  );
}

// Componente específico que extiende el base
interface CardProps extends BaseComponentProps {
  title?: string;
  variant?: 'default' | 'elevated' | 'outlined';
}

function Card({ title, variant = 'default', children, ...props }: CardProps) {
  return (
    <BaseComponent
      className={cn('card', `card--${variant}`)}
      {...props}
    >
      {title && <h3 className="card__title">{title}</h3>}
      <div className="card__content">{children}</div>
    </BaseComponent>
  );
}
```

#### Custom Hooks Pattern

```typescript
// Patrón para hooks reutilizables
function useAsyncOperation<T, P extends any[]>(
  operation: (...args: P) => Promise<T>
) {
  const [state, setState] = useState<{
    data: T | null;
    loading: boolean;
    error: Error | null;
  }>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async (...args: P) => {
    setState({ data: null, loading: true, error: null });

    try {
      const data = await operation(...args);
      setState({ data, loading: false, error: null });
      return data;
    } catch (error) {
      setState({ data: null, loading: false, error: error as Error });
      throw error;
    }
  }, [operation]);

  return { ...state, execute };
}

// Uso específico
function useCreateProduct() {
  return useAsyncOperation(async (productData: CreateProductData) => {
    const response = await apiClient.post('/products', productData);
    return response.data;
  });
}
```

---

## 📋 Especificaciones Funcionales

### Módulo de Autenticación

#### Requisitos Funcionales

| ID | Requisito | Prioridad | Descripción |
|----|-----------|-----------|-------------|
| AUTH-001 | Login básico | Alta | Usuario puede iniciar sesión con email/contraseña |
| AUTH-002 | Registro por rol | Alta | Formularios de registro específicos por rol |
| AUTH-003 | Recuperación de contraseña | Media | Flujo de reset password via email |
| AUTH-004 | Autenticación persistente | Alta | Sesión mantiene estado entre recargas |
| AUTH-005 | Logout seguro | Alta | Cierre de sesión limpia todos los datos |
| AUTH-006 | Control de acceso por rol | Alta | Navegación y funciones según rol del usuario |

#### Casos de Uso Detallados

##### Login de Usuario

**Actores:** Todos los usuarios registrados
**Precondiciones:** Usuario tiene cuenta activa
**Postcondiciones:** Usuario autenticado y redirigido a dashboard

**Flujo Principal:**
1. Usuario ingresa email y contraseña
2. Sistema valida credenciales
3. Sistema genera JWT token
4. Sistema redirige a dashboard apropiado por rol
5. Sistema carga configuración específica del rol

**Flujos Alternativos:**
- **Credenciales inválidas:** Mostrar mensaje de error
- **Cuenta inactiva:** Mostrar mensaje y opción de contacto
- **Error de red:** Reintentar automáticamente

### Módulo de Dashboard

#### Dashboard por Rol

##### Dashboard de Productor

**Funcionalidades:**
- Resumen de lotes activos
- Estado de certificaciones
- Ventas recientes
- Alertas de cosecha
- Métricas de rendimiento

##### Dashboard de Exportador

**Funcionalidades:**
- Oportunidades de mercado
- Contratos activos
- Estado de envíos
- Análisis de precios
- Contactos de proveedores

##### Dashboard de Comprador

**Funcionalidades:**
- Búsquedas guardadas
- Ofertas activas
- Historial de compras
- Alertas de precio
- Análisis de mercado

##### Dashboard de Administrador

**Funcionalidades:**
- Métricas del sistema
- Gestión de usuarios
- Monitoreo de transacciones
- Reportes globales
- Configuración del sistema

### Módulo de Gestión de Lotes

#### Especificaciones de Lote

```typescript
interface Lote {
  id: string;
  nombre: string;
  cultivo: CultivoType;
  variedad: string;
  area: number; // en hectáreas
  ubicacion: {
    latitud: number;
    longitud: number;
    finca: string;
    municipio: string;
    departamento: string;
    pais: string;
  };
  fechaSiembra: Date;
  fechaCosechaEstimada: Date;
  certificaciones: Certificacion[];
  estado: LoteEstado;
  propietario: User;
  createdAt: Date;
  updatedAt: Date;
}

type CultivoType = 'cafe' | 'cacao' | 'banano' | 'palmaceite' | 'otros';
type LoteEstado = 'planificado' | 'sembrado' | 'creciendo' | 'cosechado' | 'certificado';
```

#### Actividades de Lote

**Tipos de Actividad:**
- Preparación del suelo
- Siembra
- Fertilización
- Control de plagas
- Riego
- Cosecha
- Post-cosecha
- Transporte

**Estructura de Actividad:**

```typescript
interface ActividadLote {
  id: string;
  loteId: string;
  tipo: ActividadType;
  fecha: Date;
  descripcion: string;
  insumos: Insumo[];
  condiciones: {
    temperatura?: number;
    humedad?: number;
    precipitacion?: number;
  };
  evidencia: {
    fotos: string[];
    documentos: string[];
  };
  responsable: User;
  blockchainHash?: string;
}
```

### Módulo de Marketplace

#### Búsqueda y Filtros

**Filtros Disponibles:**
- Tipo de cultivo
- Origen geográfico
- Certificaciones
- Calidad (puntuación)
- Precio por rango
- Cantidad disponible
- Fecha de cosecha
- Sostenibilidad

#### Sistema de Ofertas

**Estados de Oferta:**
- Enviada
- Recibida
- En negociación
- Aceptada
- Rechazada
- Expirada

**Flujo de Negociación:**
1. Comprador envía oferta inicial
2. Productor recibe notificación
3. Productor puede contraofertar
4. Iteración hasta acuerdo o rechazo
5. Generación automática de contrato

### Módulo de Contratos

#### Tipos de Contrato

1. **Contrato de Venta Directa**
   - Un productor, un comprador
   - Precio fijo, cantidad fija
   - Condiciones estándar

2. **Contrato de Suministro**
   - Un productor, un comprador
   - Volumen mensual/anual
   - Precios variables

3. **Contrato de Consignación**
   - Múltiples productores, un exportador
   - Gestión de inventario
   - Comisión por venta

#### Estados de Contrato

```typescript
type EstadoContrato =
  | 'borrador'
  | 'negociacion'
  | 'firmado'
  | 'activo'
  | 'cumplimiento'
  | 'completado'
  | 'cancelado'
  | 'disputa';
```

#### Condiciones del Contrato

```typescript
interface CondicionesContrato {
  producto: {
    tipo: string;
    variedad: string;
    certificaciones: string[];
    calidadMinima: string;
  };
  cantidad: {
    total: number;
    unidad: 'kg' | 'toneladas' | 'sacos';
    tolerancia: number; // +/- porcentaje
  };
  precio: {
    unitario: number;
    moneda: string;
    condicionesPago: string;
    ajustes: {
      calidad: boolean;
      mercado: boolean;
      inflacion: boolean;
    };
  };
  entrega: {
    fechaEstimada: Date;
    lugar: string;
    condiciones: string;
    multasPorRetraso: number;
  };
  responsabilidades: {
    vendedor: string[];
    comprador: string[];
  };
}
```

---

## 📊 Especificaciones No Funcionales

### Performance

#### Métricas de Rendimiento

| Aspecto | Objetivo | Medición |
|---------|----------|----------|
| **First Contentful Paint** | < 1.5s | Lighthouse |
| **Largest Contentful Paint** | < 2.5s | Lighthouse |
| **First Input Delay** | < 100ms | Lighthouse |
| **Cumulative Layout Shift** | < 0.1 | Lighthouse |
| **Time to Interactive** | < 3s | Lighthouse |

#### Optimizaciones Implementadas

- **Code Splitting:** Lazy loading de rutas y componentes
- **Image Optimization:** WebP, responsive images, lazy loading
- **Bundle Analysis:** Monitoring de tamaño de bundles
- **Caching Strategy:** HTTP caching, service worker
- **CDN:** Distribución global de assets

### Escalabilidad

#### Arquitectura Escalable

- **Micro-frontends:** Posibilidad de dividir en módulos independientes
- **Server-side Rendering:** SEO y performance inicial
- **Static Generation:** Páginas estáticas donde aplique
- **API Optimization:** GraphQL para queries eficientes
- **Database Sharding:** Preparación para crecimiento

#### Límites del Sistema

| Recurso | Límite | Justificación |
|---------|--------|---------------|
| Usuarios concurrentes | 10,000 | Capacidad inicial |
| Lotes por usuario | 100 | Gestión razonable |
| Tamaño de archivo | 10MB | Documentos y fotos |
| API calls/minuto | 1000 | Prevención de abuso |
| Sesión máxima | 24h | Seguridad |

### Disponibilidad

#### SLA (Service Level Agreement)

- **Disponibilidad General:** 99.9% uptime mensual
- **Disponibilidad Crítica:** 99.99% para funciones core
- **Tiempo de Respuesta:** < 500ms para APIs
- **Tiempo de Recuperación:** < 4 horas para incidentes
- **Backup:** Diariamente con retención de 30 días

#### Estrategias de Alta Disponibilidad

- **Load Balancing:** Distribución de carga
- **Failover:** Replicación de servicios
- **Circuit Breaker:** Protección contra fallos en cascada
- **Rate Limiting:** Protección contra sobrecarga
- **Monitoring:** Detección proactiva de problemas

### Usabilidad

#### Principios de Diseño

- **Mobile-First:** Diseño responsivo prioritario
- **Progressive Enhancement:** Funciona sin JavaScript
- **Accessibility:** Cumple WCAG 2.1 AA
- **Consistency:** Patrones de UI consistentes
- **Feedback:** Estados de carga y mensajes claros

#### Métricas de Usabilidad

- **Task Completion Rate:** > 95% para flujos principales
- **Time on Task:** < 3 minutos para tareas comunes
- **Error Rate:** < 5% en formularios
- **User Satisfaction:** > 4.5/5 en encuestas

### Compatibilidad

#### Navegadores Soportados

| Navegador | Versión Mínima | Notas |
|-----------|----------------|-------|
| Chrome | 90+ | Recomendado |
| Firefox | 88+ | Totalmente soportado |
| Safari | 14+ | iOS 14+ |
| Edge | 90+ | Basado en Chromium |
| Mobile Safari | iOS 14+ | Optimizado para móvil |

#### Dispositivos Soportados

- **Desktop:** 1024px ancho mínimo
- **Tablet:** 768px - 1024px
- **Mobile:** 320px - 768px
- **Touch:** Gestos nativos soportados

---

## 🎨 Interfaces de Usuario

### Sistema de Diseño

#### Paleta de Colores

```css
/* Colores Primarios */
--primary-50: #f0f9ff;
--primary-100: #e0f2fe;
--primary-500: #0ea5e9;
--primary-600: #0284c7;
--primary-900: #0c4a6e;

/* Colores Semánticos */
--success: #10b981;
--warning: #f59e0b;
--error: #ef4444;
--info: #3b82f6;

/* Colores Neutros */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-900: #111827;

/* Colores por Rol */
--producer: #059669;  /* Verde - agricultura */
--exporter: #dc2626;   /* Rojo - exportación */
--buyer: #2563eb;      /* Azul - importación */
--admin: #7c3aed;      /* Púrpura - administración */
```

#### Tipografía

```css
/* Familia Tipográfica */
--font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

/* Escalas Tipográficas */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 0.875rem; /* 14px - móvil, 16px desktop */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */

/* Pesos */
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

#### Espaciado

```css
/* Sistema de Espaciado (base 4px) */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
```

### Componentes Base

#### Botones

```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}
```

#### Formularios

```typescript
interface FormFieldProps {
  label: string;
  error?: string;
  required?: boolean;
  helpText?: string;
  children: React.ReactNode;
}

interface InputProps {
  type: 'text' | 'email' | 'password' | 'number' | 'tel';
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  error?: boolean;
}
```

#### Tablas de Datos

```typescript
interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
  pagination?: {
    page: number;
    pageSize: number;
    total: number;
  };
  onRowClick?: (row: T) => void;
  onSort?: (column: string, direction: 'asc' | 'desc') => void;
  selectable?: boolean;
  onSelectionChange?: (selectedRows: T[]) => void;
}
```

### Layouts por Rol

#### Layout Base

```typescript
interface AppLayoutProps {
  children: React.ReactNode;
  sidebar?: React.ReactNode;
  header?: React.ReactNode;
  footer?: React.ReactNode;
}

// Layout específico por rol
interface RoleLayoutProps extends AppLayoutProps {
  role: UserRole;
  navigation: NavigationItem[];
  user: User;
}
```

#### Navegación Sidebar

```typescript
interface NavigationItem {
  id: string;
  label: string;
  icon: LucideIcon;
  href: string;
  badge?: number;
  children?: NavigationItem[];
  permissions?: Permission[];
}

interface SidebarProps {
  navigation: NavigationItem[];
  currentPath: string;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}
```

---

## 🔌 APIs y Integraciones

### API Interna

#### Endpoints Principales

```typescript
// Autenticación
POST   /api/auth/login
POST   /api/auth/register
POST   /api/auth/refresh
POST   /api/auth/logout

// Usuarios
GET    /api/users/profile
PUT    /api/users/profile
GET    /api/users/:id

// Lotes
GET    /api/lotes
POST   /api/lotes
GET    /api/lotes/:id
PUT    /api/lotes/:id
DELETE /api/lotes/:id

// Actividades
POST   /api/lotes/:id/actividades
GET    /api/lotes/:id/actividades

// Marketplace
GET    /api/marketplace/search
POST   /api/marketplace/offers
PUT    /api/marketplace/offers/:id

// Contratos
POST   /api/contratos
GET    /api/contratos/:id
PUT    /api/contratos/:id/status
```

#### Esquemas de API

```typescript
// Respuesta estándar de API
interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
  errors?: ValidationError[];
  meta?: {
    pagination?: PaginationMeta;
    timestamp: string;
  };
}

interface PaginationMeta {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}

// Errores de validación
interface ValidationError {
  field: string;
  message: string;
  code: string;
}
```

### Integraciones Externas

#### Blockchain

```typescript
interface BlockchainService {
  // Certificación de lotes
  certifyLote(loteData: LoteData): Promise<CertificationResult>;

  // Verificación de trazabilidad
  verifyTraceability(loteId: string): Promise<TraceabilityData>;

  // Transferencia de propiedad
  transferOwnership(
    loteId: string,
    from: string,
    to: string
  ): Promise<TransactionResult>;
}

interface CertificationResult {
  transactionHash: string;
  certificateId: string;
  timestamp: Date;
  blockNumber: number;
}
```

#### Servicios de Mapas

```typescript
interface MapService {
  // Geocodificación
  geocode(address: string): Promise<GeocodeResult>;

  // Geocodificación inversa
  reverseGeocode(lat: number, lng: number): Promise<Address>;

  // Cálculo de rutas
  calculateRoute(
    origin: Coordinate,
    destination: Coordinate
  ): Promise<RouteResult>;
}

interface GeocodeResult {
  lat: number;
  lng: number;
  address: string;
  confidence: number;
}
```

#### Servicios de Email

```typescript
interface EmailService {
  // Envío de emails transaccionales
  sendTransactional(
    to: string,
    template: EmailTemplate,
    data: Record<string, any>
  ): Promise<EmailResult>;

  // Envío de emails masivos
  sendBulk(
    recipients: string[],
    template: EmailTemplate,
    data: Record<string, any>
  ): Promise<BulkEmailResult>;
}

type EmailTemplate =
  | 'welcome'
  | 'password-reset'
  | 'offer-received'
  | 'contract-signed'
  | 'shipment-update';
```

---

## 💾 Base de Datos

### Modelo de Datos

#### Entidades Principales

```sql
-- Usuarios
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role user_role NOT NULL,
  is_active BOOLEAN DEFAULT true,
  profile JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Lotes
CREATE TABLE lotes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre VARCHAR(255) NOT NULL,
  cultivo cultivo_type NOT NULL,
  variedad VARCHAR(100),
  area DECIMAL(10,2),
  ubicacion JSONB,
  fecha_siembra DATE,
  fecha_cosecha_estimada DATE,
  estado lote_estado DEFAULT 'planificado',
  propietario_id UUID REFERENCES users(id),
  certificaciones JSONB DEFAULT '[]',
  blockchain_hash VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Actividades de lote
CREATE TABLE actividades_lote (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lote_id UUID REFERENCES lotes(id),
  tipo actividad_type NOT NULL,
  fecha TIMESTAMP NOT NULL,
  descripcion TEXT,
  insumos JSONB DEFAULT '[]',
  condiciones JSONB,
  evidencia JSONB DEFAULT '{}',
  responsable_id UUID REFERENCES users(id),
  blockchain_hash VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Ofertas del marketplace
CREATE TABLE ofertas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lote_id UUID REFERENCES lotes(id),
  comprador_id UUID REFERENCES users(id),
  precio DECIMAL(10,2) NOT NULL,
  cantidad DECIMAL(10,2) NOT NULL,
  moneda VARCHAR(3) DEFAULT 'USD',
  condiciones JSONB,
  estado oferta_estado DEFAULT 'enviada',
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Contratos
CREATE TABLE contratos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tipo contrato_type NOT NULL,
  participantes JSONB NOT NULL,
  condiciones JSONB NOT NULL,
  estado contrato_estado DEFAULT 'borrador',
  blockchain_address VARCHAR(255),
  fecha_firma TIMESTAMP,
  fecha_vencimiento DATE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Índices de Performance

```sql
-- Índices para búsquedas comunes
CREATE INDEX idx_lotes_cultivo ON lotes(cultivo);
CREATE INDEX idx_lotes_estado ON lotes(estado);
CREATE INDEX idx_lotes_ubicacion ON lotes USING GIN(ubicacion);
CREATE INDEX idx_lotes_propietario ON lotes(propietario_id);

CREATE INDEX idx_actividades_lote_fecha ON actividades_lote(lote_id, fecha);
CREATE INDEX idx_ofertas_estado ON ofertas(estado, expires_at);
CREATE INDEX idx_contratos_estado ON contratos(estado, fecha_vencimiento);

-- Índices de texto completo
CREATE INDEX idx_lotes_search ON lotes USING GIN(to_tsvector('spanish', nombre || ' ' || variedad));
```

### Estrategias de Caching

#### Redis Cache Strategy

```typescript
interface CacheConfig {
  // Cache de usuarios (24h)
  user: { ttl: 86400, strategy: 'LRU' };

  // Cache de lotes (1h)
  lote: { ttl: 3600, strategy: 'LRU' };

  // Cache de búsquedas (15min)
  search: { ttl: 900, strategy: 'LRU' };

  // Cache de contratos (30min)
  contrato: { ttl: 1800, strategy: 'WRITE_THROUGH' };
}

class CacheManager {
  async get<T>(key: string): Promise<T | null> {
    // Implementación de cache con Redis
  }

  async set<T>(key: string, value: T, ttl: number): Promise<void> {
    // Implementación de cache con Redis
  }

  async invalidate(pattern: string): Promise<void> {
    // Invalidación de cache por patrón
  }
}
```

---

## 🔒 Seguridad

### Autenticación y Autorización

#### JWT Tokens

```typescript
interface JWTPayload {
  userId: string;
  email: string;
  role: UserRole;
  permissions: Permission[];
  iat: number;
  exp: number;
  iss: string;
  aud: string;
}

interface Permission {
  resource: string;
  action: 'create' | 'read' | 'update' | 'delete';
  scope?: 'own' | 'all';
}
```

#### Control de Acceso Basado en Roles (RBAC)

```typescript
const rolePermissions: Record<UserRole, Permission[]> = {
  producer: [
    { resource: 'lotes', action: 'create' },
    { resource: 'lotes', action: 'read', scope: 'own' },
    { resource: 'lotes', action: 'update', scope: 'own' },
    { resource: 'actividades', action: 'create', scope: 'own' },
    { resource: 'marketplace', action: 'read' },
    { resource: 'ofertas', action: 'read', scope: 'own' },
  ],
  exporter: [
    { resource: 'marketplace', action: 'read' },
    { resource: 'ofertas', action: 'create' },
    { resource: 'ofertas', action: 'read', scope: 'own' },
    { resource: 'ofertas', action: 'update', scope: 'own' },
    { resource: 'contratos', action: 'create' },
    { resource: 'contratos', action: 'read', scope: 'own' },
  ],
  buyer: [
    { resource: 'marketplace', action: 'read' },
    { resource: 'ofertas', action: 'create' },
    { resource: 'ofertas', action: 'read', scope: 'own' },
    { resource: 'contratos', action: 'read', scope: 'own' },
  ],
  admin: [
    { resource: '*', action: 'create' },
    { resource: '*', action: 'read' },
    { resource: '*', action: 'update' },
    { resource: '*', action: 'delete' },
  ],
};
```

### Validación de Datos

#### Sanitización de Input

```typescript
class InputSanitizer {
  static sanitizeString(input: string): string {
    return input
      .trim()
      .replace(/[<>]/g, '') // Remove potential HTML tags
      .substring(0, 1000); // Limit length
  }

  static sanitizeEmail(email: string): string {
    return email.toLowerCase().trim();
  }

  static sanitizeNumber(input: string, min?: number, max?: number): number {
    const num = parseFloat(input);
    if (isNaN(num)) throw new Error('Invalid number');

    if (min !== undefined && num < min) throw new Error(`Minimum value is ${min}`);
    if (max !== undefined && num > max) throw new Error(`Maximum value is ${max}`);

    return num;
  }
}
```

#### Protección contra Ataques Comunes

```typescript
// Rate limiting
const rateLimitConfig = {
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
};

// CORS configuration
const corsConfig = {
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
};

// Helmet security headers
const helmetConfig = {
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", 'data:', 'https:'],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true,
  },
};
```

### Encriptación de Datos

#### Encriptación en Reposo

```typescript
class DataEncryption {
  private algorithm = 'aes-256-gcm';
  private keyLength = 32;
  private ivLength = 16;

  async encrypt(text: string): Promise<string> {
    const salt = crypto.randomBytes(32);
    const key = await this.deriveKey(process.env.ENCRYPTION_KEY!, salt);
    const iv = crypto.randomBytes(this.ivLength);

    const cipher = crypto.createCipher(this.algorithm, key);
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');

    const authTag = cipher.getAuthTag();

    return JSON.stringify({
      encrypted,
      iv: iv.toString('hex'),
      salt: salt.toString('hex'),
      authTag: authTag.toString('hex'),
    });
  }

  async decrypt(encryptedData: string): Promise<string> {
    const { encrypted, iv, salt, authTag } = JSON.parse(encryptedData);

    const key = await this.deriveKey(process.env.ENCRYPTION_KEY!, Buffer.from(salt, 'hex'));
    const decipher = crypto.createDecipher(this.algorithm, key);

    decipher.setAuthTag(Buffer.from(authTag, 'hex'));

    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    return decrypted;
  }

  private async deriveKey(password: string, salt: Buffer): Promise<Buffer> {
    return new Promise((resolve, reject) => {
      crypto.pbkdf2(password, salt, 100000, this.keyLength, 'sha256', (err, derivedKey) => {
        if (err) reject(err);
        else resolve(derivedKey);
      });
    });
  }
}
```

---

## ⚡ Performance y Escalabilidad

### Optimizaciones de Frontend

#### Code Splitting

```typescript
// Lazy loading de páginas
const Dashboard = lazy(() => import('../pages/Dashboard'));
const Lotes = lazy(() => import('../pages/Lotes'));
const Marketplace = lazy(() => import('../pages/Marketplace'));

// Lazy loading de componentes pesados
const DataTable = lazy(() => import('../components/DataTable'));
const Charts = lazy(() => import('../components/Charts'));

// Route-based code splitting
function AppRoutes() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/lotes" element={<Lotes />} />
        <Route path="/marketplace" element={<Marketplace />} />
      </Routes>
    </Suspense>
  );
}
```

#### Image Optimization

```typescript
// Componente de imagen optimizada
interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  priority?: boolean;
  quality?: number;
  placeholder?: 'blur' | 'empty';
  blurDataURL?: string;
}

function OptimizedImage({
  src,
  alt,
  width,
  height,
  priority = false,
  quality = 75,
  placeholder = 'empty',
  blurDataURL,
}: OptimizedImageProps) {
  return (
    <Image
      src={src}
      alt={alt}
      width={width}
      height={height}
      priority={priority}
      quality={quality}
      placeholder={placeholder}
      blurDataURL={blurDataURL}
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
    />
  );
}
```

#### Bundle Analysis

```javascript
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer({
  // Configuración existente
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.optimization.splitChunks.cacheGroups = {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
        },
      };
    }

    return config;
  },
});
```

### Monitorización de Performance

#### Web Vitals Tracking

```typescript
// lib/web-vitals.ts
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

export function reportWebVitals(onPerfEntry?: (metric: any) => void) {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    getCLS(onPerfEntry);
    getFID(onPerfEntry);
    getFCP(onPerfEntry);
    getLCP(onPerfEntry);
    getTTFB(onPerfEntry);
  }
}

// Uso en _app.tsx
import { reportWebVitals } from '../lib/web-vitals';

export function reportWebVitals(metric) {
  // Enviar a servicio de analytics
  console.log(metric);

  // Enviar a monitoring service
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', metric.name, {
      event_category: 'Web Vitals',
      event_label: metric.id,
      value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
      non_interaction: true,
    });
  }
}
```

#### Error Boundaries

```typescript
// components/ErrorBoundary.tsx
import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error?: Error; resetError: () => void }>;
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to monitoring service
    console.error('Error caught by boundary:', error, errorInfo);

    // Send to error reporting service
    if (typeof window !== 'undefined' && window.Sentry) {
      window.Sentry.captureException(error, {
        contexts: {
          react: {
            componentStack: errorInfo.componentStack,
          },
        },
      });
    }
  }

  resetError = () => {
    this.setState({ hasError: false, error: undefined });
  };

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback;
      return <FallbackComponent error={this.state.error} resetError={this.resetError} />;
    }

    return this.props.children;
  }
}

function DefaultErrorFallback({ error, resetError }: { error?: Error; resetError: () => void }) {
  return (
    <div className="error-boundary">
      <h2>Algo salió mal</h2>
      <p>{error?.message || 'Ha ocurrido un error inesperado'}</p>
      <button onClick={resetError}>Intentar de nuevo</button>
    </div>
  );
}
```

### Escalabilidad Horizontal

#### Micro-frontends Architecture

```typescript
// lib/micro-frontend.ts
interface MicroFrontend {
  name: string;
  host: string;
  remoteEntry: string;
  exposes: string[];
}

class MicroFrontendManager {
  private frontends: Map<string, MicroFrontend> = new Map();

  register(frontend: MicroFrontend) {
    this.frontends.set(frontend.name, frontend);
  }

  async loadComponent(name: string, component: string): Promise<React.ComponentType> {
    const frontend = this.frontends.get(name);
    if (!frontend) throw new Error(`Micro-frontend ${name} not found`);

    // Dynamic import del componente remoto
    const module = await import(/* webpackIgnore: true */ `${frontend.host}${frontend.remoteEntry}`);
    return module[component];
  }
}

// Configuración de micro-frontends
const mfManager = new MicroFrontendManager();

mfManager.register({
  name: 'marketplace',
  host: 'https://marketplace.triboka.com',
  remoteEntry: '/remoteEntry.js',
  exposes: ['./MarketplaceApp', './ProductCard'],
});

mfManager.register({
  name: 'analytics',
  host: 'https://analytics.triboka.com',
  remoteEntry: '/remoteEntry.js',
  exposes: ['./AnalyticsDashboard', './Charts'],
});
```

---

*Estas especificaciones técnicas proporcionan la base sólida para el desarrollo, mantenimiento y escalabilidad del frontend de Triboka Agro, asegurando una plataforma robusta, segura y de alto rendimiento.*
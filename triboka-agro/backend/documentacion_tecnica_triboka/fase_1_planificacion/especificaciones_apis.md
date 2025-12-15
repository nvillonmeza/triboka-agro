# 📋 ESPECIFICACIONES DE APIs - TRIBOKA

## 📊 Estado: PARCIALMENTE IMPLEMENTADO

### ✅ YA IMPLEMENTADO
- Endpoints básicos documentados en código
- Estructura RESTful consistente
- Autenticación JWT implementada
- Respuestas JSON estandarizadas

### 🚧 PENDIENTE PARA COMPLETAR
- Documentación OpenAPI/Swagger completa
- Esquemas JSON detallados
- Ejemplos de requests/responses
- Documentación de errores
- Versionado de APIs

---

## 🔗 ENDPOINTS IMPLEMENTADOS

### **Autenticación (`/api/auth/`)**

#### `POST /api/auth/login`
**Descripción:** Autenticación de usuario
**Autenticación:** No requerida

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response 200:**
```json
{
  "access_token": "string",
  "user": {
    "id": "integer",
    "email": "string",
    "full_name": "string",
    "role": "string",
    "company_id": "integer"
  }
}
```

#### `POST /api/auth/register`
**Descripción:** Registro de nuevo usuario
**Autenticación:** No requerida

#### `GET /api/auth/profile`
**Descripción:** Obtener perfil del usuario autenticado
**Autenticación:** JWT requerido

### **Usuarios (`/api/users`)**

#### `GET /api/users`
**Descripción:** Listar usuarios (admin/operador)
**Autenticación:** JWT requerido

#### `POST /api/users`
**Descripción:** Crear nuevo usuario
**Autenticación:** JWT requerido

#### `PUT /api/users/{id}`
**Descripción:** Actualizar usuario
**Autenticación:** JWT requerido

#### `DELETE /api/users/{id}`
**Descripción:** Eliminar usuario
**Autenticación:** JWT requerido

### **Empresas (`/api/companies`)**

#### `GET /api/companies`
**Descripción:** Listar empresas
**Autenticación:** JWT requerido

#### `POST /api/companies`
**Descripción:** Crear nueva empresa
**Autenticación:** JWT requerido

### **Lotes (`/api/lots`)**

#### `GET /api/lots`
**Descripción:** Listar lotes
**Autenticación:** JWT requerido

#### `POST /api/lots`
**Descripción:** Crear nuevo lote
**Autenticación:** JWT requerido

#### `GET /api/lots/{id}`
**Descripción:** Obtener lote específico
**Autenticación:** JWT requerido

#### `PUT /api/lots/{id}`
**Descripción:** Actualizar lote
**Autenticación:** JWT requerido

### **Contratos (`/api/contracts`)**

#### `GET /api/contracts`
**Descripción:** Listar contratos
**Autenticación:** JWT requerido

#### `POST /api/contracts`
**Descripción:** Crear nuevo contrato
**Autenticación:** JWT requerido

#### `GET /api/contracts/{id}`
**Descripción:** Obtener contrato específico
**Autenticación:** JWT requerido

### **Batches (`/api/batches`)**

#### `GET /api/batches`
**Descripción:** Listar batches
**Autenticación:** JWT requerido

#### `POST /api/batches`
**Descripción:** Crear nuevo batch
**Autenticación:** JWT requerido

### **Deals (`/api/deals`)** ✅ IMPLEMENTADO

#### `GET /api/deals`
**Descripción:** Listar acuerdos comerciales
**Autenticación:** JWT requerido

#### `POST /api/deals`
**Descripción:** Crear nuevo acuerdo
**Autenticación:** JWT requerido

#### `GET /api/deals/{id}`
**Descripción:** Obtener acuerdo específico
**Autenticación:** JWT requerido

---

## 📋 CÓDIGOS DE ERROR ESTÁNDAR

### **4xx - Errores del Cliente**
- `400 Bad Request` - Datos inválidos
- `401 Unauthorized` - Token inválido o expirado
- `403 Forbidden` - Sin permisos suficientes
- `404 Not Found` - Recurso no encontrado
- `422 Unprocessable Entity` - Validación fallida

### **5xx - Errores del Servidor**
- `500 Internal Server Error` - Error interno
- `502 Bad Gateway` - Error de conexión
- `503 Service Unavailable` - Servicio no disponible

### **Formato de Error**
```json
{
  "error": "string",
  "message": "string",
  "details": "object (opcional)"
}
```

---

## 🔐 AUTENTICACIÓN Y AUTORIZACIÓN

### **JWT Token**
- **Header:** `Authorization: Bearer {token}`
- **Expiración:** 24 horas
- **Refresh:** Implementado básico

### **Roles y Permisos**
- `admin`: Acceso completo
- `operator`: Gestión operacional
- `exporter`: Gestión de exportaciones
- `buyer`: Gestión de compras
- `producer`: Acceso limitado a lotes propios

---

## 📊 PAGINACIÓN Y FILTROS

### **Paginación Estándar**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

### **Parámetros de Query**
- `page`: Número de página (default: 1)
- `per_page`: Elementos por página (default: 20, max: 100)
- `sort`: Campo de ordenamiento
- `order`: asc/desc
- `search`: Búsqueda de texto
- `filters`: Filtros específicos (JSON)

---

## 🧪 TESTING DE APIs

### **Entorno de Testing**
- **Base URL:** `http://localhost:5003/api` (desarrollo)
- **Base URL:** `https://app.triboka.com/api` (producción)

### **Herramientas Recomendadas**
- **Postman/Insomnia** para testing manual
- **Swagger UI** para documentación interactiva
- **pytest** para testing automatizado

---

## 📋 PENDIENTE PARA COMPLETAR

### **1. Documentación OpenAPI/Swagger**
- [ ] Crear archivo `swagger.yaml` completo
- [ ] Implementar Swagger UI en `/api/docs`
- [ ] Generar documentación automática desde código

### **2. Esquemas JSON Detallados**
- [ ] Definir schemas para todos los modelos
- [ ] Validación automática de requests
- [ ] Documentación de campos opcionales/obligatorios

### **3. Ejemplos Completos**
- [ ] Request/Response examples para cada endpoint
- [ ] Casos de uso comunes
- [ ] Manejo de errores documentado

### **4. Versionado de APIs**
- [ ] Implementar `/api/v1/` prefix
- [ ] Estrategia de migración entre versiones
- [ ] Deprecation warnings

### **5. Rate Limiting**
- [ ] Implementar límites por usuario/IP
- [ ] Documentación de límites
- [ ] Headers informativos (X-RateLimit-*)

---

**Estado**: 🚧 REQUIERE COMPLETACIÓN PARA FASE 1 FINALIZADA</content>
<parameter name="filePath">/home/rootpanel/web/app.triboka.com/backend/documentacion_tecnica_triboka/fase_1_planificacion/especificaciones_apis.md
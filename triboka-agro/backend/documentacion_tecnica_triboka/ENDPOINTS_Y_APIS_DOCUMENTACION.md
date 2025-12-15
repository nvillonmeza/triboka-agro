# 📋 **DOCUMENTACIÓN DE ENDPOINTS Y APIs - Triboka Ecosistema**

## 📅 **Fecha:** Noviembre 17, 2025
## 🎯 **Estado:** Verificación Completada - Problemas Identificados

---

## 🔍 **RESUMEN EJECUTIVO**

Se realizó verificación completa de conectividad entre los 3 servicios principales. La **arquitectura multi-tenant está correctamente implementada**, pero faltan endpoints críticos de integración.

---

## 🏗️ **ARQUITECTURA MULTI-TENANT CONFIRMADA**

### ✅ **Implementación Correcta**
- Cada empresa tiene `company_id` único
- Filtrado automático en todas las rutas
- API keys únicas por empresa
- Aislamiento completo de datos

### ❌ **Problemas de Integración**
- URLs incorrectas en AgroWeight Cloud
- Endpoints faltantes en Triboka Agro
- Backend cacao no activo en ERP
- Falta autenticación por API key

---

## 📊 **ESTADO ACTUAL DE SERVICIOS**

| Servicio | Puerto | Estado | Endpoints Activos | Problemas |
|----------|--------|--------|-------------------|-----------|
| **Triboka Agro** | `5003` | ✅ ACTIVO | 15+ endpoints | Falta auth API key |
| **Triboka ERP** | `5008` | ✅ ACTIVO | Health check | Endpoints cacao inactivos |
| **Triboka ERP Inventory** | `5006` | ✅ ACTIVO | 10+ endpoints | Error interno en queries |
| **AgroWeight Cloud** | - | 🚧 DESARROLLO | - | URLs mal configuradas |

---

## 🔗 **ENDPOINTS ACTIVOS VERIFICADOS**

### **1. Triboka Agro (Puerto 5003)**

#### ✅ **Endpoints Públicos**
```http
GET /health
GET /api/public/trace/verify/{entity_type}/{entity_id}
```

#### ✅ **Endpoints con JWT**
```http
GET /api/lots
POST /api/lots
GET /api/lots/{uuid}
PUT /api/lots/{uuid}
POST /api/lots/{uuid}/quality-test
GET /api/lots/{uuid}/track
GET /api/lots/stats

GET /api/nfts
GET /api/nfts/{uuid}
POST /api/nfts

POST /api/traceability/events
GET /api/traceability/timeline/{entity_type}/{entity_id}
```

### **2. Triboka ERP (Puerto 5008)**

#### ✅ **Endpoints Activos**
```http
GET /health
```

#### ❌ **Endpoints Inactivos (Backend Cacao)**
```http
POST /api/recepciones
POST /api/recepciones/{id}/liquidacion
POST /api/secado-ciclos
POST /api/silo-movimientos
POST /api/batch
GET /api/precios-qq
GET /api/contratos/{id}
```

### **3. Triboka ERP Inventory (Puerto 5006)**

#### ✅ **Endpoints Activos**
```http
GET /api/inventory/health
GET /api/inventory/products
POST /api/inventory/products
GET /api/inventory/items
POST /api/inventory/items
PUT /api/inventory/items/{id}
DELETE /api/inventory/items/{id}
GET /api/inventory/movements
GET /api/inventory/suppliers
POST /api/inventory/suppliers
```

---

## ⚠️ **ENDPOINTS REQUERIDOS FALTANTES**

### **Para AgroWeight Cloud → Triboka Agro**

```python
# 1. Obtener lote por NFT hash
GET /api/lotes/nft/{nft_hash}
Authorization: Bearer {api_key}
Response: Lote metadata + NFT info

# 2. Registrar evento en lote NFT
POST /api/lotes/{lote_nft_id}/eventos
Authorization: Bearer {api_key}
Body: {"tipo": "recepcion", "peso_kg": 1000, ...}

# 3. Crear NFT de batch final
POST /api/batch-nft
Authorization: Bearer {api_key}
Body: {"batch_code": "BATCH-001", "lotes": [...], ...}
```

### **Para AgroWeight Cloud → Triboka ERP**

```python
# 1. Crear recepción industrial
POST /api/recepciones
Authorization: Bearer {api_key}
Body: {
  "empresa_id": "AGROCROP",
  "lote_nft_id": "NFT123",
  "peso_bruto_kg": 10000,
  "peso_tara_kg": 3000,
  "humedad_porcentaje": 18.5,
  "origen": "camion"
}

# 2. Completar liquidación
POST /api/recepciones/{id}/liquidacion
Authorization: Bearer {api_key}
Body: {
  "peso_final_qq": 140.0,
  "precio_qq": 120.5,
  "total_pagar": 16884
}

# 3. Registrar ciclo de secado
POST /api/secado-ciclos
Authorization: Bearer {api_key}
Body: {
  "recepcion_id": 123,
  "peso_entrada_kg": 7000,
  "peso_salida_kg": 6200,
  "humedad_inicial": 18.5,
  "humedad_final": 7.0
}

# 4. Crear batch industrial
POST /api/batch
Authorization: Bearer {api_key}
Body: {
  "batch_codigo": "BATCH-001",
  "peso_total_kg": 24800,
  "lotes_componentes": [...]
}
```

---

## 🔧 **CONFIGURACIÓN ACTUAL EN AgroWeight Cloud**

### ❌ **URLs Incorrectas (Problema Crítico)**

```dart
// lib/config/app_config.dart - ACTUALMENTE MALO
class AppConfig {
  static const String baseUrl = 'http://erp.triboka.com/api';      // ❌ No existe
  static const String agroApiUrl = 'http://agro.triboka.com/api';  // ❌ No existe
}
```

### ✅ **URLs Correctas Requeridas**

```dart
// lib/config/app_config.dart - DEBE SER
class AppConfig {
  static const String baseUrl = 'http://localhost:5008/api';       // ✅ ERP local
  static const String agroApiUrl = 'http://localhost:5003/api';    // ✅ Agro local
}
```

---

## 🔐 **AUTENTICACIÓN API KEY FALTANTE**

### **Estado Actual**
- Triboka Agro NO valida API keys de empresas
- AgroWeight Cloud envía headers de auth pero no son validados

### **Implementación Requerida**

```python
# En Triboka Agro - Nuevo decorador
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'API key required'}), 401
        
        api_key = auth_header.replace('Bearer ', '')
        company = Company.query.filter_by(api_key=api_key).first()
        
        if not company:
            return jsonify({'error': 'Invalid API key'}), 401
        
        g.company = company
        return f(*args, **kwargs)
    return decorated_function

# Uso en endpoints
@app.route('/api/lotes/nft/<nft_hash>', methods=['GET'])
@require_api_key
def get_lote_nft(nft_hash):
    company = g.company
    # Lógica con company_id filtrado
```

---

## 🧪 **TESTING DE CONECTIVIDAD**

### **Comandos de Verificación**

```bash
# 1. Verificar servicios activos
netstat -tlnp | grep -E "(5003|5006|5008)"

# 2. Health checks
curl -s http://localhost:5003/health
curl -s http://localhost:5006/api/inventory/health
curl -s http://localhost:5008/health

# 3. Verificar trazabilidad pública
curl -s "http://localhost:5003/api/public/trace/verify/lot/TEST-001"

# 4. Verificar endpoints faltantes
curl -X POST http://localhost:5008/api/recepciones \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

---

## 📋 **CHECKLIST DE IMPLEMENTACIÓN**

### **Fase 1: Corregir URLs y Configuración**
- [ ] Actualizar `app_config.dart` con URLs correctas
- [ ] Verificar conectividad desde AgroWeight Cloud

### **Fase 2: Implementar Autenticación API Key**
- [ ] Crear decorador `@require_api_key` en Triboka Agro
- [ ] Aplicar decorador a endpoints de integración

### **Fase 3: Crear Endpoints Faltantes**
- [ ] `GET /api/lotes/nft/{hash}` en Triboka Agro
- [ ] `POST /api/lotes/{id}/eventos` en Triboka Agro
- [ ] `POST /api/batch-nft` en Triboka Agro
- [ ] Activar backend cacao en Triboka ERP

### **Fase 4: Testing Multi-Tenant**
- [ ] Crear empresa de prueba "AgroCrop Ecuador"
- [ ] Crear empresa de prueba "CacaoGlobal Peru"
- [ ] Verificar aislamiento de datos
- [ ] Testing flujo completo con API keys

### **Fase 5: Documentación Final**
- [ ] Documentar todos los endpoints implementados
- [ ] Crear guía de integración para clientes
- [ ] Documentar flujo multi-tenant

---

## 🎯 **PRIORIDADES DE IMPLEMENTACIÓN**

1. **URGENTE:** Corregir URLs en AgroWeight Cloud
2. **URGENTE:** Implementar `@require_api_key` en Triboka Agro
3. **ALTO:** Crear endpoints `/api/lotes/nft/{hash}`
4. **ALTO:** Activar backend cacao en ERP
5. **MEDIO:** Testing multi-tenant completo
6. **BAJO:** Documentación final

---

## 📞 **CONTACTO Y SOPORTE**

**Arquitecto de Solución:** [Tu Nombre]
**Fecha de Verificación:** Noviembre 17, 2025
**Estado:** Problemas identificados, solución planificada

---

*Documento generado automáticamente por verificación de conectividad del ecosistema Triboka.*</content>
<parameter name="filePath">/home/rootpanel/web/app.triboka.com/backend/documentacion_tecnica_triboka/ENDPOINTS_Y_APIS_DOCUMENTACION.md
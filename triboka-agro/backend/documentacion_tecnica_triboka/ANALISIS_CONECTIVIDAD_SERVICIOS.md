# 📊 **ANÁLISIS DE CONECTIVIDAD ENTRE SERVICIOS TRIBOKA**
## *Estado Actual y Problemas Identificados*

**Fecha:** 17 de noviembre de 2025
**Versión:** 1.0
**Autor:** GitHub Copilot - Análisis de Arquitectura

---

## 🎯 **OBJETIVO DEL ANÁLISIS**

Verificar la conectividad y desarrollo de APIs/endpoints que interconectan los 3 servicios principales del ecosistema Triboka:

1. **Triboka ERP** (`web/app.triboka.com/triboka-erp`)
2. **Triboka Agro** (`web/app.triboka.com`)
3. **AgroWeight Cloud** (`web/app.triboka.com/agro_weight_cloud`)

---

## 🔗 **ESTADO ACTUAL DE CONECTIVIDAD**

### **Servicios Activos Identificados**

| Servicio | Puerto | Estado | Endpoints Verificados | Observaciones |
|----------|--------|--------|----------------------|---------------|
| **Triboka Agro** | `5003` | ✅ **ACTIVO** | `/health`, `/api/public/trace/verify/*` | API blockchain completa |
| **Triboka ERP** | `5008` | ✅ **ACTIVO** | `/health` | Backend principal, pero sin endpoints cacao |
| **Triboka ERP - Inventory** | `5006` | ✅ **ACTIVO** | `/api/inventory/health` | Servicio de inventario separado |
| **AgroWeight Cloud** | - | 🚧 **EN DESARROLLO** | - | Flutter app, no expone API |

---

## 📋 **ENDPOINTS IDENTIFICADOS Y FUNCIONALES**

### **1. Triboka Agro (Puerto 5003)**
```bash
✅ GET /health
   Response: {"blockchain":"ready","database":"healthy","service":"Triboka Agro API","status":"ok","timestamp":"2025-11-17T18:32:59.216340","version":"2.0.0"}

✅ GET /api/public/trace/verify/{entity_type}/{entity_id}
   Response: {"error":"Entidad no encontrada o sin trazabilidad"}
   Status: Endpoint existe pero requiere datos reales
```

### **2. Triboka ERP (Puerto 5008)**
```bash
✅ GET /health
   Response: {"database":"connected","service":"Triboka ERP Backend","status":"healthy","version":"1.0.0"}
```

### **3. Triboka ERP - Inventory (Puerto 5006)**
```bash
✅ GET /api/inventory/health
   Response: {"service":"inventory","status":"healthy","timestamp":"2025-11-17T18:33:40.087339"}
```

---

## ⚠️ **PROBLEMAS CRÍTICOS IDENTIFICADOS**

### **1. Endpoints de Cacao del ERP No Disponibles**
- **Archivo:** `triboka-erp/backend/app_cacao.py`
- **Estado:** ❌ No está ejecutándose
- **Impacto:** AgroWeight Cloud no puede enviar recepciones al ERP
- **Endpoints faltantes:**
  - `POST /api/lotes/recepcion`
  - `POST /api/lotes/{id}/secado`
  - `POST /api/lotes/{id}/calidad`
  - `POST /api/lotes/{id}/liquidar`
  - `GET /api/precios/spot`

### **2. URLs de Configuración Incorrectas en AgroWeight Cloud**
**Archivo:** `agro_weight_cloud/lib/config/app_config.dart`

```dart
// ❌ CONFIGURACIÓN ACTUAL (INCORRECTA)
static const String baseUrl = 'http://erp.triboka.com/api';
static const String agroApiUrl = 'http://agro.triboka.com/api';

// ✅ CONFIGURACIÓN CORRECTA PROPUESTA
static const String baseUrl = 'http://localhost:5008';
static const String agroApiUrl = 'http://localhost:5003';
```

### **3. Endpoint de Lotes NFT Requiere Autenticación**
- **Endpoint:** `GET /api/lotes/nft/{hash}`
- **Estado:** ❌ Requiere JWT token
- **Problema:** AgroWeight Cloud no tiene sistema de autenticación con Triboka Agro
- **Solución:** Crear endpoint público o implementar API key

### **4. Error Interno en Servicio de Inventario**
```bash
curl http://localhost:5006/api/inventory/products
Response: {"error":"Error interno del servidor","success":false}
```

---

## 🔄 **FLUJO DE INTEGRACIÓN ACTUAL**

### **Flujo Esperado vs Realidad**

#### **Flujo Esperado (Diseño Original)**
```
AgroWeight Cloud → Triboka Agro (NFT) → Triboka ERP (Recepción)
AgroWeight Cloud → Triboka ERP (Liquidación) → Triboka Agro (Eventos)
```

#### **Flujo Actual (Estado Real)**
```
AgroWeight Cloud → ❌ (URLs incorrectas)
Triboka Agro → ✅ (Parcialmente funcional)
Triboka ERP → ✅ (Health OK, pero endpoints cacao no activos)
```

---

## 📊 **MATRIZ DE CONECTIVIDAD**

| Servicio Origen | Servicio Destino | Endpoint | Estado | Problema |
|----------------|------------------|----------|--------|----------|
| **AgroWeight** | **Triboka Agro** | `/api/lotes/nft/{hash}` | ❌ BLOQUEADO | Requiere autenticación |
| **AgroWeight** | **Triboka ERP** | `/api/lotes/recepcion` | ❌ BLOQUEADO | Servicio no activo |
| **Triboka Agro** | **Triboka ERP** | - | ✅ OK | No aplica |
| **Triboka ERP** | **Triboka Agro** | `/api/lotes/{id}/eventos` | ❌ NO PROBADO | Requiere testing |

---

## 🛠️ **PLAN DE SOLUCIÓN PROPUESTO**

### **FASE 1: Iniciar Servicios Faltantes**
1. **Activar backend de cacao del ERP**
   ```bash
   cd /home/rootpanel/web/app.triboka.com/triboka-erp/backend
   python3 app_cacao.py
   ```

2. **Verificar puerto asignado al servicio de cacao**

### **FASE 2: Corregir Configuración de URLs**
1. **Actualizar `app_config.dart`** con URLs locales correctas
2. **Implementar configuración de producción vs desarrollo**

### **FASE 3: Crear Endpoints Públicos**
1. **Endpoint público para lotes NFT** en Triboka Agro
2. **Sistema de API keys** entre servicios

### **FASE 4: Testing de Integración**
1. **Probar flujo completo** recepción → ERP → trazabilidad
2. **Validar autenticación** entre servicios
3. **Documentar todos los endpoints** funcionales

---

## 📈 **MÉTRICAS DE CONECTIVIDAD**

- **Servicios Activos:** 3/4 (75%)
- **Endpoints Funcionales:** 4/12 (33%)
- **Flujos Operativos:** 0/3 (0%)
- **Tiempo Estimado de Solución:** 2-3 horas

---

## 🎯 **SIGUIENTES PASOS**

1. **Ejecutar FASE 1** - Iniciar servicios faltantes
2. **Documentar endpoints** encontrados
3. **Implementar correcciones** de configuración
4. **Probar conectividad completa**
5. **Actualizar esta documentación** con resultados

---

*Documento generado automáticamente por análisis de arquitectura - GitHub Copilot*</content>
<parameter name="filePath">/home/rootpanel/web/app.triboka.com/backend/documentacion_tecnica_triboka/ANALISIS_CONECTIVIDAD_SERVICIOS.md


# 🌍 **TRIBOKA — ARQUITECTURA UNIFICADA**

### *Sistema Web3 de Trazabilidad + ERP Industrial completo para cacao*

**Incluye toda la lógica, procesos, API, blockchain y arquitectura del frontend.**

---

# 🧩 **0. VISIÓN GLOBAL DEL SISTEMA**


## 🟫 **Triboka ERP**

➡ Plataforma empresarial de exportadoras
➡ Procesos industriales del cacao
➡ Recepción, Calidad, Secado
➡ Mermas, Almacenamiento, Batches
➡ Contratos, Fijaciones, Despachos
➡ Costos y dashboard
➡ Consume API de Triboka Agro
➡ Genera eventos blockchain posteriores



# ⛓️ **2. EVENTOS BLOCKCHAIN (OFICIALES)**

La cadena de trazabilidad completa:

1. `PRODUCER_INIT` — Productor (Agro)
2. `RECEPCION_EXPORTADORA` — ERP
3. `CALIDAD_LABORATORIO` — ERP
4. `SECADO` — ERP
5. `MERMA` — ERP
6. `ALMACENAMIENTO` — ERP
7. `BATCH` — ERP
8. `FIJACION` — ERP
9. `DESPACHO` — ERP
10. `BROKER_DEAL` — Admin (si aplica)

🔹 Todos generan hash + metadata off-chain
🔹 Blockchain ligera (solo hash)
🔹 Metadata detallada almacenada en Triboka Agro

---

# 🔌 **3. INTEGRACIÓN: ERP ↔ TRIBOKA AGRO**

Este es el corazón técnico.

## ✔ 3.1 Qué obtiene el ERP desde Agro

* Datos del lote de origen
* Metadata del productor
* Fotos
* Geolocalización
* Humedad inicial
* Tipo de cacao
* Hash inicial
* Trazabilidad hasta ese momento

## ✔ 3.2 Qué envía el ERP hacia Agro

Cada módulo del ERP crea un evento blockchain:

```
POST /api/lotes/{codigo}/event/{tipo}
```

Payload estandarizado:

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

# 🏭 **4. MÓDULOS DEL ERP**

Toda la lógica industrial completa:

---

## **4.1 Recepción (Acopio)**

Datos:

* Peso bruto
* Tara
* Sacos
* Humedad
* Impurezas
* Peso neto
* Productor importado vía API
* Fotos / evidencia
* QR del lote interno

Blockchain: `RECEPCION_EXPORTADORA`

---

## **4.2 Laboratorio / Calidad**

Incluye:

* Corte
* % fermentación
* % moho
* % violetas
* % impurezas reales
* % humedad final
* Observaciones
* Fotos del análisis

Blockchain: `CALIDAD`

---

## **4.3 Secado**

Lógica:

* Humedad inicial
* Humedad objetivo
* Tipo secado (natural / industrial)
* Peso húmedo
* Peso seco final
* Duración
* Secadora
* Turnos

Cálculos:

```
merma_humedad = (humedad_inicial - humedad_final) % de peso
merma_total = peso_inicial - peso_final
```

Blockchain: `SECADO`

---

## **4.4 Mermas**

Fuentes:

* Humedad
* Impurezas
* Secado
* Industrial

Blockchain: `MERMA`

---

## **4.5 Almacenamiento / Bodegas**

* Movimientos entre bodegas
* Cantidades
* QR tracking
* Auditoría interna

Blockchain: `ALMACENAMIENTO`

---

## **4.6 Batches / Mezclas**

* Mezcla de lotes secos
* Porcentaje por lote
* Peso final
* Clases de cacao
* Lote de exportación

Blockchain: `BATCH`

---

## **4.7 Contratos y Fijaciones**

Sin comercio.

Incluye:

* Volumen TM
* Diferencial
* Spot del día
* Fecha de fijación
* Relación con batch

Blockchain: `FIJACION`

---

## **4.8 Despacho / Exportación**

Incluye:

* Container
* Guía
* Documentos
* Fotos
* Puerto
* Nave
* Cliente

Blockchain: `DESPACHO`

---

# 📦 **5. ARQUITECTURA DEL FRONTEND**

Usando:

* **Next.js 14 (App Router)**
* **TypeScript**
* **Tailwind**
* **shadcn/ui**
* **Zustand**
* **React Query**
* **JWT**

---

## **5.1 Estructura principal del frontend**

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
/hooks
/lib
/providers
/styles
```

---

## **5.2 Sistema de Autenticación**

* **JWT** firmado por backend
* Almacenado en **httpOnly cookie** o localStorage (según diseño)
* Renovación automática
* Roles incluidos en el payload
* Middleware en Next:

```
middleware.ts
```

Rutas protegidas:

* `/erp/**`
* `/admin/**`
* `/productor/**`

---

## **5.3 Sistema de Autorización (roles)**

En cada layout:

```ts
export default async function Layout({children}) {
  const user = await getUser();
  if (!user.roles.includes("calidad")) redirect("/no-permisos");
  return <>{children}</>;
}
```

---

## **5.4 Interfaz ERP (UX)**

### Sidebar dinámico por rol:

* Acopio → Recepción
* Calidad → Laboratorio
* Secado → Mermas / Secado
* Contabilidad → Costos
* Exportación → Contratos / Despachos

### Dashboard:

* KPI Cards
* Gráficos
* Trazabilidad del día
* Notificaciones

### Vistas por módulo:

* Tablas con filtros
* Formularios por pasos (wizard)
* Modales de evidencia
* Carga de fotos
* QR scanner

---

## **5.5 Integración con API de Triboka Agro**

En el módulo:

`/erp/importar-lote`

El usuario ingresa código:

```
1234-5678-ABC
```

Frontend hace:

```
GET https://api.triboka.com/lotes/{codigo}
```

Y muestra:

* Nombre productor
* Finca
* Ubicación
* Humedad
* Peso inicial
* Fotos

Botón:
**"Importar lote al ERP"**

---

## **5.6 Registro de eventos blockchain desde el frontend**

Cada módulo del ERP tiene un botón “Registrar y enviar a blockchain”.

Ejemplo:
En secado:

```
POST /api/lotes/{id}/event/secado
```

Frontend:

* valida datos
* firma local o servidor
* envía al backend
* backend → Triboka Agro → Blockchain

---

# 🗄️ **6. MODELO DE BASE DE DATOS ERP**

Tablas principales:

* `empresas`
* `usuarios`
* `lotes_origen` (provenientes de Agro)
* `lotes_materia_prima`
* `recepciones`
* `calidades`
* `secados`
* `mermas`
* `bodegas`
* `movimientos_bodega`
* `batches`
* `batch_detalles`
* `contratos`
* `fijaciones`
* `despachos`
* `eventos_blockchain`
* `licencias`
* `api_keys`
* `broker_deals`

---

# 🔐 **7. SEGURIDAD**

* API Key por empresa
* JWT con roles
* Logging completo
* Auditoría
* Versionamiento
* Encriptación de evidencia
* Access tokens limitados
* Firma de eventos blockchain

---

# 📊 **8. DASHBOARD CENTRAL (Empresa)**

KPIs:

* Lotes activos
* Peso recibido
* Peso seco producido
* Merma promedio
* Producción diaria
* Batch listos
* Contratos abiertos
* Eventos blockchain emitidos

Gráficos:

* mermas vs tiempo
* secado vs humedad
* mapa de bodegas
* trazabilidad
* lotes por productor




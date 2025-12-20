# Estrategia de Implementación: Backend y Sincronización (VPS)

Este documento detalla los pasos técnicos para construir el Backend en tu VPS (`agro.triboka.com`) y conectar la aplicación móvil Triboka para lograr una arquitectura **Offline-First**.

## 1. Lógica de Negocio: Vitrina Comercial (Ceguera Competitiva)

La sección "General" funciona como una **Vitrina Comercial** dinámica. El backend debe respetar estrictamente estas reglas de visibilidad al servir el feed (`/api/publications/feed`).

### Principio Fundamental
**Ningún usuario puede ver las publicaciones de otros usuarios con su mismo rol.**

| Rol | Publica (Oferta/Demanda) | Ve (Consume) |
| :--- | :--- | :--- |
| **Exportadora** 🌍 | • **Cupos de Compra**: Contratos abiertos.<br>• *No ve cupos de otras exportadoras.* | • **Lotes de Productores**: Cosechas disponibles.<br>• **Lotes de Centros**: Volumen consolidado. |
| **Centro de Acopio** 🏭 | • **Lotes a Venta**: Oferta para exp.<br>• **Ofertas de Precio**: Precios de compra. | • **Cupos de Exportadoras**: Demanda intl.<br>• **Lotes de Productores**: Oferta local. |
| **Productor** 👨‍🌾 | • **Lotes de Cosecha**: Su producción. | • **Ofertas de Centros**: Precios locales.<br>• **Cupos de Exportadoras**: Oportunidades directas. |

---

## 2. Implementación Técnica Inmediata

Pasos prioritarios para habilitar la sincronización de las publicaciones ya existentes en la App.

### A. [VPS] Endpoint de Sincronización (PUSH)
Implementar en `agro.triboka.com` para recibir los datos de Hive.

**POST** `/api/sync/push`
- **Headers**: `Authorization: Bearer <token>`
- **Body JSON**:
  ```json
  {
    "publications": [
      { 
        "id": "LOTE-1783...", 
        "role": "proveedor", 
        "type": "offer", 
        "data": { "volume": 500, "price": 240, ... },
        "created_at": "2024-05-20T10:00:00Z" 
      }
    ]
  }
  ```
- **Lógica Backend**:
  1.  Validar Token.
  2.  Iterar sobre el array `publications`.
  3.  **Upsert**: Si el ID existe, actualizar; si no, insertar.
  4.  Responder `200 OK`.

### B. [Mobile] Actualizar `PublicationService.dart`
Modificar el servicio actual en Flutter para enviar los datos cuando haya conexión.

1.  Añadir método `syncPush()`.
2.  Leer publicaciones locales con `synced = false` (necesita añadir este flag al guardar).
3.  Enviar POST a `AppConstants.baseUrl/api/sync/push`.
4.  Si respuesta es 200, marcar `synced = true` en Hive.

---

## 3. Estrategia de Base de Datos (Sugeryida)

### Tabla: `publications`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | VARCHAR | ID generado por la App (PK) |
| `role` | VARCHAR | 'centro' / 'proveedor' / 'exportadora' |
| `type` | VARCHAR | 'offer' / 'price' / 'demand' |
| `content` | JSONB | Datos flexibles del formulario |
| `user_id` | UUID | Usuario propietario |
| `is_active` | BOOLEAN | Control de estado |


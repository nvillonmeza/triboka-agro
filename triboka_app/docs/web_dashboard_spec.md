# Especificación de Dashboard Web (`agro.triboka.com`)

Este documento detalla la estructura, componentes y lógica necesaria para replicar la experiencia de la App Móvil en la versión Web.

## 1. Diseño General (Global)

La web debe mantener la estética "Premium" de la app pero aprovechando el espacio horizontal.

- **Header Principal**:
  - Saludo: "Hola, [Nombre Usuario]"
  - Rol: Badge con el rol (Exportadora / Centro / Productor)
  - **Ticker de Mercado (Top)**:
    - *Componente*: `MarketWidget`
    - *Datos*: Precio Spot NY (ej. $6319), Diferencia diaria, Estado (Abierto/Cerrado).
    - *Ubicación Web*: Barra superior fija o Card destacada a la izquierda.

---

## 2. Dashboards por Rol (Vistas Específicas)

### A. Dashboard Exportadora 🌍

**Objetivo**: Gestión de compras y visualización de oferta.

1.  **Panel Izquierdo: Mis Cupos (Gestión)**
    - *Acción*: Botón "Publicar Cupo de Compra".
    - *Lista*: Tarjetas de cupos activos publicados por la exportadora.
    - *Datos*: ID Cupo, Volumen Requerido, Precio Ref, Estado.

2.  **Panel Central: Muro de Ofertas (Vitrina)**
    - *Lógica*: Ver publicaciones de **Centros de Acopio** y **Productores**.
    - *Componente*: Grid de `PublicationCard`.
    - *Filtros*: Por Origen (Centro/Productor), Por Variedad.

3.  **Panel Derecho: KPIs**
    - *Gráfico*: Destinos de Exportación (Pie Chart).
    - *Métrica*: Capacidad de Compra disponible (Simulada/Real).

---

### B. Dashboard Centro de Acopio 🏭

**Objetivo**: Intermediación (Compra y Venta).

1.  **Panel Superior: Resumen Operativo**
    - *Cards*: Stock Actual (kg), Dinero en Caja, Despachos del Día.
    - *Alertas*: Alerta de capacidad de bodega (>90%).

2.  **Panel Izquierdo: Gestión Comercial**
    - *Acciones*: "Vender Lote" (Publicar oferta), "Fijar Precio Compra" (Publicar precio día).
    - *Lista*: Mis Lotes Activos / Mis Precios del día.

3.  **Panel Central: Mercado (Vitrina Mixta)**
    - *Lógica*: Ver **Cupos de Exportadoras** (Demanda) y **Lotes de Productores** (Oferta).
    - *Componente*: Feed dividido o etiquetado por "Venta" (Prod) y "Compra" (Exp).

---

### C. Dashboard Productor 👨‍🌾

**Objetivo**: Gestión de cosecha y venta.

1.  **Panel Izquierdo: Mis Lotes**
    - *Acción*: "Registrar Lote" (Nueva Cosecha/Venta).
    - *Lista*: Historial de lotes registrados (En finca, En secado, Vendido).

2.  **Panel Central: Ofertas de Compra (Vitrina)**
    - *Lógica*: Ver **Precios de Centros de Acopio** y **Cupos de Exportadoras**.
    - *Prioridad*: Mostrar mejores precios primero.

3.  **Panel Derecho: Calidad**
    - *Gráfico*: Historial de calidad (Humedad/Fermentación) de últimos lotes.

---

## 3. Componentes Reutilizables (Web)

Para mantener la consistencia con Flutter:

1.  **`PublicationCard` (Web Component)**
    - Encabezado: Tipo (Venta/Compra/Precio), Título.
    - Cuerpo: Autor (Empresa), Detalles (Volumen, Precio), Tags (Certificaciones).
    - Footer: Botón "Contactar" o "Negociar".

2.  **Colores y Estilos**
    - Primario: Verde Esmeralda (`#059669`).
    - Secundario: Verde Claro (`#10B981`).
    - Acento: Ámbar (`#FBBF24`).
    - Tipografía: **Poppins** (Google Fonts).

## 4. Conexión API

El Dashboard Web consumirá los mismos endpoints definidos en la estrategia de sincronización:

- `GET /api/publications/feed?role=[ROL_USUARIO]` -> Para llenar el Muro/Vitrina.
- `GET /api/market/spot` -> Para el Ticker de precios.

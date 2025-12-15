# Lógica de Negocio - Manejo de Precios del Cacao

**Versión:** 1.0  
**Fecha:** Noviembre 11, 2025  
**Sistema:** Triboka - Plataforma de Trazabilidad de Cacao

---

## 📊 RESUMEN EJECUTIVO

Este documento define la lógica de negocio para el manejo de precios del cacao en la plataforma Triboka, incluyendo la estructura de precios, diferenciales de mercado, conversiones de unidades, y la integración con fuentes de datos en tiempo real.

### Diagrama de Flujo de Precios

```
┌─────────────────────────────────────────────────────────────────┐
│           MERCADO INTERNACIONAL (Yahoo Finance CC=F)             │
│                    Precio Spot: $6,833/MT                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ├─────────────────────────────────────┐
                           │                                     │
                           ▼                                     ▼
              ┌────────────────────────┐         ┌────────────────────────┐
              │   EXPORTADORAS         │         │   PRODUCTORES          │
              │   (Venta a clientes)   │         │   (Venta a exportadora)│
              ├────────────────────────┤         ├────────────────────────┤
              │ Diferencial:           │         │ Diferencial:           │
              │ -$1,000 a -$1,200/MT   │         │ -$1,400 a -$1,600/MT   │
              ├────────────────────────┤         ├────────────────────────┤
              │ Precio Venta:          │         │ Precio Compra:         │
              │ $5,733/MT              │         │ $5,333/MT              │
              │ (Spot - $1,100)        │         │ (Spot - $1,500)        │
              └────────────────────────┘         └────────────────────────┘
                           │                                     ▲
                           │                                     │
                           │    ┌─────────────────────┐         │
                           └───▶│  MARGEN: $400/MT    │◀────────┘
                                │  (7.5% aprox.)      │
                                └─────────────────────┘
```

### Datos Clave del Sistema

| Concepto | Valor | Descripción |
|----------|-------|-------------|
| **Fuente Precio Spot** | Yahoo Finance CC=F | ICE Futures U.S. (NYSE) |
| **Actualización** | 5 minutos | Precio en tiempo real |
| **Diferencial Exportadoras** | -$1,000 a -$1,200/MT | Descuento sobre spot para venta |
| **Diferencial Productores** | -$1,400 a -$1,600/MT | Descuento sobre spot para compra |
| **Margen Esperado** | $300 a $600/MT | Diferencia entre compra y venta |
| **Unidad Principal** | Tonelada Métrica (MT) | 1 MT = 1,000 kg |
| **Unidad Local** | Quintal (configurable) | Colombia: 50 kg/qq |
| **Conversión CC=F** | × 1.10231 | Tonelada corta → MT |

---

## 💰 ESTRUCTURA DE PRECIOS

### 1. Precio Spot (Mercado Internacional)

**Fuente de datos:** Yahoo Finance (Ticker: CC=F)  
**Actualización:** Tiempo real (5 minutos)  
**Mercado:** ICE Futures U.S. (New York Board of Trade)

El precio spot representa el precio del cacao en el mercado internacional de futuros y sirve como **referencia base** para todos los cálculos de precios en la plataforma.

#### Características del Ticker CC=F:
- **Exchange:** NYB (New York Board of Trade)
- **Tipo:** FUTURE (Contrato de futuros)
- **Moneda:** USD (Dólares estadounidenses)
- **Unidad original:** USD por tonelada corta (2,000 lbs)

### 2. Diferencial de Mercado

El diferencial es el **descuento o "castigo" que se aplica al precio spot del mercado internacional** para determinar el precio de compra. Este descuento refleja los costos de intermediación, procesamiento y riesgos asumidos por los diferentes actores de la cadena de valor.

#### Cadena de Valor y Diferenciales:

```
Precio Spot (Mercado Internacional)
         ↓
    Diferencial Exportadoras: -$1,000 a -$1,200 USD/MT
         ↓
Precio Venta Exportadoras = Spot - $1,100 (promedio)
         ↓
    Diferencial Productores: -$1,400 a -$1,600 USD/MT
         ↓
Precio Compra Productores = Spot - $1,500 (promedio)
```

**Ejemplo práctico:**
```
Spot del mercado: $6,000/MT

Clientes externos compran a exportadoras:
→ Diferencial: -$1,100/MT
→ Precio venta: $6,000 - $1,100 = $4,900/MT

Exportadoras compran a productores:
→ Diferencial: -$1,500/MT
→ Precio compra: $6,000 - $1,500 = $4,500/MT

Margen exportadora: $4,900 - $4,500 = $400/MT
```

#### Rango Estándar del Diferencial:

| Nivel | Diferencial | Rango USD/MT | Precio si Spot = $6,000 |
|-------|-------------|--------------|-------------------------|
| **Exportadoras** (venta a clientes) | -$1,000 a -$1,200 | Spot - $1,100 | $4,900/MT |
| **Productores** (compra de cacao) | -$1,400 a -$1,600 | Spot - $1,500 | $4,500/MT |

#### Características Clave:

✅ **Fijo en USD (NO porcentual)**
- El diferencial se mantiene en un rango fijo de USD, independiente de las fluctuaciones del precio spot
- No se calcula como porcentaje del spot
- Se mantiene constante en términos nominales

✅ **Ejemplo con diferentes precios spot:**

| Spot/MT | Diferencial | Precio Exportadora | Precio Productor |
|---------|-------------|-------------------|------------------|
| $5,000 | -$1,100 | $3,900 | $3,500 |
| $6,000 | -$1,100 | $4,900 | $4,500 |
| $7,000 | -$1,100 | $5,900 | $5,500 |
| $8,000 | -$1,100 | $6,900 | $6,500 |

*Nota: El diferencial en USD se mantiene constante ($1,100 y $1,500 respectivamente)*

#### Factores que determinan el diferencial:

El diferencial lo determina el **mercado según su oferta y demanda**, pero en términos generales se consideran los siguientes factores:

1. **Condiciones del contrato**
   - Plazo de entrega
   - Volumen comprometido
   - La exportadora va fijando batches para completer el volumen total fijado

2. **Oferta y Demanda**
   - Disponibilidad de cacao en el mercado local
   - Demanda de clientes internacionales
   - Competencia entre exportadoras

3. **Calidad y Origen**
   - Cacao fino de aroma vs. ordinario
   - Certificaciones (Orgánico, Fair Trade, Rainforest)
   - Reputación del origen geográfico 

 

### 3. Clasificación de Estados del Diferencial

El sistema clasifica automáticamente el diferencial según el nivel de la cadena:

#### Para Exportadoras (venta a clientes externos):

| Estado | Rango | Interpretación |
|--------|-------|----------------|
| **Normal** | -$1,200 a -$1,000/MT | Rango esperado del mercado de exportación |
| **Competitivo** | -$1,000 a -$800/MT | Mejor que el estándar (atractivo para clientes) |
| **Alto** | -$800 a $0/MT | Diferencial reducido (menor margen) |
| **Premium** | ≥ $0/MT | Sobre el mercado spot (excepcional) |

#### Para Productores (compra de cacao):

| Estado | Rango | Interpretación |
|--------|-------|----------------|
| **Normal** | -$1,600 a -$1,400/MT | Rango esperado del mercado local |
| **Favorable** | -$1,400 a -$1,200/MT | Mejor precio para productores |
| **Muy Favorable** | -$1,200 a -$1,000/MT | Excelente precio (productores beneficiados) |
| **Excepcional** | > -$1,000/MT | Precio premium (condiciones especiales) |

#### Interpretación del Margen:

```
Margen Exportadora = Diferencial Exportadora - Diferencial Productor

Ejemplo estándar:
Margen = (-$1,100) - (-$1,500) = $400/MT

Escenarios:
- Margen < $300/MT: Bajo (presión competitiva)
- Margen $300-$500/MT: Normal (operación sostenible)
- Margen > $500/MT: Alto (mercado favorable para exportadora)
```

### 4. Precio Fijado (Fixed Price)

Cuando se **fija un precio**, se utiliza la siguiente fórmula:

```
Precio Fijado = Spot del momento - Diferencial estándar

Donde:
- Spot del momento = Precio CC=F en el momento de fijación
- Diferencial estándar = Valor entre -$1,000 y -$1,200 USD/MT
```

**Ejemplo de fijación:**
```
Fecha: 2025-11-11 10:30 AM
Spot del momento: $6,833.22/MT
Diferencial aplicado: -$1,100/MT

Precio Fijado = $6,833.22 - $1,100 = $5,733.22/MT
```

---

## ⚖️ CONVERSIONES DE PESO

### Unidades de Medida

El sistema trabaja con múltiples unidades de medida para adaptarse a diferentes contextos:

1. **Tonelada Métrica (MT)** - Unidad estándar del sistema
   - 1 MT = 1,000 kg
   - 1 MT = 2,204.62 libras
   - Uso: Comercio internacional, contratos de exportación

2. **Tonelada Corta (Short Ton)** - Unidad de Yahoo Finance CC=F
   - 1 Tonelada corta = 2,000 libras
   - 1 Tonelada corta = 907.185 kg
   - Uso: Mercado de futuros estadounidense

3. **Kilogramos (kg)** - Unidad de medida interna del sistema
   - 1 kg = 0.001 MT
   - 1 kg = 2.20462 libras
   - Uso: Registro de lotes, pesaje en finca

4. **Quintales (qq)** - Unidad utilizada en países productores
   - **Valores configurables** (ver sección Configuración)
   - Estándar: 1 quintal = 100 libras = 45.3592 kg
   - Variantes regionales:
     * Colombia: 1 quintal = 50 kg
     * México: 1 quintal = 46 kg
     * Perú: 1 quintal = 46 kg
   - Uso: Compra directa a productores locales

### Conversiones Configurables

Los factores de conversión se definen en el archivo de configuración:

```python
# config.py - Unidades de Peso Configurables

# Quintal (qq) - Configuración por país
QUINTAL_CONFIG = {
    'standard': {
        'kg': 45.3592,          # 100 libras
        'lbs': 100,
        'description': 'Quintal estándar (100 lbs)'
    },
    'colombia': {
        'kg': 50.0,
        'lbs': 110.231,
        'description': 'Quintal colombiano (50 kg)'
    },
    'mexico': {
        'kg': 46.0,
        'lbs': 101.413,
        'description': 'Quintal mexicano (46 kg)'
    },
    'peru': {
        'kg': 46.0,
        'lbs': 101.413,
        'description': 'Quintal peruano (46 kg)'
    }
}

# Selección del tipo de quintal a usar
QUINTAL_TYPE = 'standard'  # Cambiar según el país de operación

# Obtener configuración activa
QUINTAL_TO_KG = QUINTAL_CONFIG[QUINTAL_TYPE]['kg']
QUINTAL_TO_LBS = QUINTAL_CONFIG[QUINTAL_TYPE]['lbs']
```

### Tabla de Conversiones Rápidas

| Desde | A | Factor | Ejemplo |
|-------|---|--------|---------|
| Tonelada corta | MT | × 0.907185 | 1 ton corta = 0.907 MT |
| MT | Tonelada corta | × 1.10231 | 1 MT = 1.102 ton cortas |
| MT | Kilogramos | × 1000 | 1 MT = 1,000 kg |
| Kilogramos | MT | ÷ 1000 | 1,000 kg = 1 MT |
| Quintales (std) | Kilogramos | × 45.3592 | 1 qq = 45.36 kg |
| Quintales (CO) | Kilogramos | × 50 | 1 qq = 50 kg |
| Kilogramos | Quintales (std) | ÷ 45.3592 | 100 kg = 2.20 qq |
| Libras | Kilogramos | × 0.453592 | 100 lbs = 45.36 kg |


### Factor de Conversión

Para convertir precios de tonelada corta (CC=F) a tonelada métrica (MT):

```python
# Factor de conversión
CONVERSION_FACTOR = 2204.62 / 2000.0  # = 1.102310

# Aplicación
precio_mt = precio_ton_corta * CONVERSION_FACTOR

# Ejemplo:
# CC=F = $6,199.00 por tonelada corta
# Precio MT = $6,199.00 × 1.102310 = $6,833.22/MT
```

### Conversión de Kilogramos a Toneladas Métricas

```python
# Fórmula
toneladas_metricas = kilogramos / 1000.0

# Ejemplo de lote:
# Lote: 2,500 kg
# MT = 2,500 / 1,000 = 2.5 MT
```

### Conversión de Quintales a Kilogramos

```python
# Usando configuración
from config import QUINTAL_TO_KG

# Fórmula
kilogramos = quintales * QUINTAL_TO_KG

# Ejemplos según tipo de quintal:

# Quintal estándar (100 lbs = 45.3592 kg)
quintales = 10
kg = 10 * 45.3592 = 453.592 kg

# Quintal colombiano (50 kg)
quintales = 10
kg = 10 * 50 = 500 kg

# Quintal mexicano (46 kg)
quintales = 10
kg = 10 * 46 = 460 kg
```

### Conversión de Quintales a Toneladas Métricas

```python
# Fórmula combinada
toneladas_metricas = (quintales * QUINTAL_TO_KG) / 1000.0

# Ejemplo con quintal estándar:
# Compra: 50 quintales
# kg = 50 × 45.3592 = 2,267.96 kg
# MT = 2,267.96 / 1,000 = 2.268 MT

# Ejemplo con quintal colombiano:
# Compra: 50 quintales
# kg = 50 × 50 = 2,500 kg
# MT = 2,500 / 1,000 = 2.5 MT
```

### Cálculo de Precio Total de Lote

```python
# Fórmula básica
precio_total_lote = precio_por_mt * peso_mt

# Ejemplo con kilogramos:
# Peso del lote: 2,500 kg (2.5 MT)
# Precio/MT: $5,700
# Precio total = $5,700 × 2.5 = $14,250 USD

# Ejemplo con quintales (estándar):
# Peso del lote: 50 quintales
# Conversión: 50 qq × 45.3592 kg = 2,267.96 kg = 2.268 MT
# Precio/MT: $5,700
# Precio total = $5,700 × 2.268 = $12,927.60 USD

# Ejemplo con quintales (Colombia):
# Peso del lote: 50 quintales
# Conversión: 50 qq × 50 kg = 2,500 kg = 2.5 MT
# Precio/MT: $5,700
# Precio total = $5,700 × 2.5 = $14,250 USD
```

### Cálculo de Precio por Quintal

```python
# Fórmula
precio_por_quintal = (precio_por_mt * QUINTAL_TO_KG) / 1000.0

# Ejemplo:
# Precio/MT: $5,700
# Quintal estándar (45.3592 kg):
# Precio/qq = ($5,700 × 45.3592) / 1,000 = $258.55/qq

# Quintal colombiano (50 kg):
# Precio/qq = ($5,700 × 50) / 1,000 = $285/qq

# Verificación:
# 50 qq × $285 = $14,250 (mismo resultado que por MT)
```

---

## 📐 FÓRMULAS Y CÁLCULOS

### 1. Conversión Precio Spot

```python
# Obtener precio de Yahoo Finance
cacao = yf.Ticker("CC=F")
hist = cacao.history(period="5d")
precio_ton_corta = float(hist['Close'].iloc[-1])

# Convertir a USD/MT
precio_spot_mt = precio_ton_corta * (2204.62 / 2000.0)
```

### 2. Cálculo de Diferencial

```python
# Diferencial absoluto
diferencial_usd = precio_contrato_mt - precio_spot_mt

# Diferencial porcentual (solo para reporte)
diferencial_pct = (diferencial_usd / precio_spot_mt) * 100

# Ejemplo:
# Contrato: $5,643/MT
# Spot: $6,833/MT
# Diferencial: $5,643 - $6,833 = -$1,190/MT ✅ (dentro del rango)
# Porcentual: (-$1,190 / $6,833) × 100 = -17.42%
```

### 3. Precio Promedio Ponderado

Para calcular el precio promedio de múltiples lotes:

```python
total_value = 0
total_weight = 0

for lote in lotes:
    peso_mt = lote.weight_kg / 1000.0
    total_value += lote.purchase_price_usd
    total_weight += peso_mt

precio_promedio_mt = total_value / total_weight if total_weight > 0 else 0

# Ejemplo:
# Lote 1: 2.5 MT × $5,700 = $14,250
# Lote 2: 1.8 MT × $5,620 = $10,116
# Total: 4.3 MT, $24,366
# Promedio: $24,366 / 4.3 = $5,666.51/MT
```

### 4. Cambio Diario del Spot

```python
# Obtener precio actual y anterior
precio_actual = float(hist['Close'].iloc[-1])
precio_anterior = float(hist['Close'].iloc[-2])

# Calcular cambio porcentual
cambio_diario_pct = ((precio_actual - precio_anterior) / precio_anterior) * 100

# Ejemplo:
# Anterior: $6,013/ton
# Actual: $6,199/ton
# Cambio: ((6,199 - 6,013) / 6,013) × 100 = +3.09%
```

### 5. Volatilidad Anualizada

```python
# Obtener histórico de 1 año
hist_year = cacao.history(period="1y")

# Calcular retornos diarios
returns = hist_year['Close'].pct_change().dropna()

# Volatilidad anualizada
volatilidad = float(returns.std()) * 100 * (252 ** 0.5)

# Donde:
# - returns.std() = Desviación estándar de retornos diarios
# - 252 = Días de trading en un año
# - Raíz cuadrada de 252 para anualizar
```

---

## 🔄 FLUJO DE DATOS

### Arquitectura de Integración

```
┌─────────────────────────────────────────────────────────────┐
│                    Yahoo Finance (CC=F)                      │
│                  ICE Futures U.S. - NYSE                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ API Call (yfinance)
                         │ Frecuencia: 5 minutos
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend API - Flask (app_web3.py)               │
│                                                              │
│  1. Obtener precio spot (CC=F)                              │
│  2. Convertir tonelada corta → MT                           │
│  3. Consultar lotes en BD (SQLite)                          │
│  4. Calcular precios promedio                               │
│  5. Calcular diferencial                                    │
│  6. Clasificar estado diferencial                           │
│  7. Generar estadísticas mercado                            │
│                                                              │
│  Endpoint: GET /api/market/cacao-prices                     │
│  Auth: JWT Bearer Token                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ JSON Response
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          Frontend Dashboard (dashboard.html)                 │
│                                                              │
│  Visualización:                                             │
│  • 4 Cards de precios (Spot, Contratos, Fijado, Diferencial)│
│  • Resumen de mercado (52 semanas, volatilidad)            │
│  • Actualización automática (AJAX 5 min)                   │
└─────────────────────────────────────────────────────────────┘
```

### Endpoint API: `/api/market/cacao-prices`

**Método:** GET  
**Auth:** JWT Bearer Token  
**Actualización:** Tiempo real

#### Respuesta JSON:

```json
{
  "spot": {
    "price": 6833.22,
    "change": 3.09,
    "currency": "USD",
    "unit": "MT",
    "source": "Yahoo Finance (CC=F)"
  },
  "contracts": {
    "avgPrice": 5657.89,
    "activeCount": 5,
    "totalVolume": 1800.0
  },
  "fixed": {
    "avgPrice": 5657.89,
    "volume": 10.38
  },
  "differential": {
    "value": -1175.33,
    "percent": -17.20,
    "status": "Normal (rango esperado)",
    "explanation": "Diferencial estándar del mercado: -$1000 a -$1200/MT bajo el spot"
  },
  "market": {
    "rangeMin": 6207.11,
    "rangeMax": 14253.97,
    "volatility": 58.38
  },
  "business_logic": {
    "differential_range": {
      "min": -1200,
      "max": -1000,
      "unit": "USD/MT",
      "description": "Rango estándar de diferencial bajo el precio spot"
    },
    "pricing_model": "Diferencial fijo en USD (no porcentual)",
    "factors": [
      "Costos de procesamiento y logística (fijos)",
      "Prima por calidad y origen",
      "Certificaciones (Orgánico, Fair Trade, Rainforest)",
      "Condiciones del contrato (plazo, volumen, pago)"
    ],
    "fixing_logic": "Al fijar precio: Spot del momento - diferencial estándar ($1000-$1200)"
  },
  "data_points": {
    "lots_analyzed": 6,
    "contracts_active": 5,
    "total_fixed_mt": 10.38
  },
  "timestamp": "2025-11-11T15:30:00.000Z",
  "source": "Yahoo Finance (CC=F) + Triboka Database"
}
```

---

## 💾 ESTRUCTURA DE BASE DE DATOS

### Tabla: `producer_lots`

Almacena los lotes de cacao con sus precios y pesos.

#### Campos relevantes:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER | ID único del lote |
| `lot_code` | VARCHAR | Código del lote (ej: LOT-CACAO-20241101-0001) |
| `weight_kg` | DECIMAL | Peso del lote en kilogramos |
| `purchase_price_usd` | DECIMAL | Precio total de compra en USD |
| `status` | VARCHAR | Estado: purchased, batched, in_transit, etc. |
| `quality_score` | DECIMAL | Puntuación de calidad (0-100) |
| `moisture_content` | DECIMAL | Porcentaje de humedad |
| `origin` | VARCHAR | Región/finca de origen |

#### Cálculo de precio por MT:

```sql
SELECT 
    lot_code,
    weight_kg,
    purchase_price_usd,
    (purchase_price_usd / (weight_kg / 1000.0)) AS price_per_mt,
    status
FROM producer_lots
WHERE status IN ('purchased', 'batched')
  AND purchase_price_usd IS NOT NULL
  AND weight_kg > 0;
```

#### Ejemplo de registros:

```
LOT-CACAO-20241101-0001 | 2500 kg | $14,072.63 | $5,629.05/MT | purchased
LOT-CACAO-20241102-0002 | 1800 kg | $10,116.77 | $5,620.43/MT | purchased
LOT-CAFE-20241103-0003  | 3200 kg | $18,035.56 | $5,636.11/MT | batched
```

---

## 📈 ESTADÍSTICAS DE MERCADO

### Rango 52 Semanas

Valores mínimo y máximo del precio spot en el último año:

```python
hist_year = cacao.history(period="1y")

# Mínimo (convertido a MT)
year_low = float(hist_year['Low'].min()) * (2204.62 / 2000.0)

# Máximo (convertido a MT)
year_high = float(hist_year['High'].max()) * (2204.62 / 2000.0)

# Ejemplo actual:
# Mínimo: $6,207.11/MT
# Máximo: $14,253.97/MT
# Rango: $8,046.86/MT (variación significativa)
```

### Volatilidad

Medida de variabilidad del precio:

```python
# Retornos diarios
returns = hist_year['Close'].pct_change().dropna()

# Volatilidad anualizada
volatility = float(returns.std()) * 100 * (252 ** 0.5)

# Interpretación:
# < 20% = Baja volatilidad
# 20-40% = Volatilidad moderada
# > 40% = Alta volatilidad

# Ejemplo actual: 58.38% (muy alta volatilidad)
```

---

## 🛠️ IMPLEMENTACIÓN TÉCNICA

### Dependencias

```python
# requirements.txt
yfinance==0.2.66        # Yahoo Finance API
pandas==2.3.3           # Análisis de datos
numpy==2.3.4            # Cálculos numéricos
Flask==2.3.2            # Backend API
Flask-JWT-Extended      # Autenticación
SQLAlchemy==2.0.19      # ORM Database
```

### Instalación

```bash
# Activar virtual environment
source /home/rootpanel/web/app.triboka.com/.venv/bin/activate

# Instalar yfinance
pip install yfinance

# Verificar instalación
python -c "import yfinance as yf; print(yf.__version__)"
```

### Configuración

```python
# config.py
CACAO_TICKER = "CC=F"
CACAO_UPDATE_INTERVAL = 300  # 5 minutos en segundos

# Diferenciales (USD/MT)
DIFFERENTIAL_EXPORTER_MIN = -1200   # Exportadoras: mínimo
DIFFERENTIAL_EXPORTER_MAX = -1000   # Exportadoras: máximo
DIFFERENTIAL_PRODUCER_MIN = -1600   # Productores: mínimo
DIFFERENTIAL_PRODUCER_MAX = -1400   # Productores: máximo

# Conversiones de peso
CONVERSION_FACTOR = 2204.62 / 2000.0  # Ton corta → MT (1.102310)
MT_TO_KG = 1000.0                      # MT → Kilogramos
KG_TO_MT = 1.0 / 1000.0                # Kilogramos → MT

# Configuración de Quintales por país
QUINTAL_CONFIG = {
    'standard': {
        'kg': 45.3592,
        'lbs': 100,
        'description': 'Quintal estándar (100 lbs)'
    },
    'colombia': {
        'kg': 50.0,
        'lbs': 110.231,
        'description': 'Quintal colombiano (50 kg)'
    },
    'mexico': {
        'kg': 46.0,
        'lbs': 101.413,
        'description': 'Quintal mexicano (46 kg)'
    },
    'peru': {
        'kg': 46.0,
        'lbs': 101.413,
        'description': 'Quintal peruano (46 kg)'
    }
}

# Selección del tipo de quintal (CONFIGURABLE)
QUINTAL_TYPE = 'standard'  # Opciones: standard, colombia, mexico, peru

# Obtener valores activos
QUINTAL_TO_KG = QUINTAL_CONFIG[QUINTAL_TYPE]['kg']
QUINTAL_TO_LBS = QUINTAL_CONFIG[QUINTAL_TYPE]['lbs']
QUINTAL_TO_MT = QUINTAL_TO_KG / 1000.0
```

### Funciones de Conversión Implementadas

```python
# utils/conversions.py

def ton_corta_to_mt(precio_ton_corta):
    """Convertir precio de tonelada corta a tonelada métrica"""
    return precio_ton_corta * (2204.62 / 2000.0)

def kg_to_mt(kilogramos):
    """Convertir kilogramos a toneladas métricas"""
    return kilogramos / 1000.0

def mt_to_kg(toneladas):
    """Convertir toneladas métricas a kilogramos"""
    return toneladas * 1000.0

def quintales_to_kg(quintales, quintal_type='standard'):
    """Convertir quintales a kilogramos según tipo de quintal"""
    from config import QUINTAL_CONFIG
    kg_per_quintal = QUINTAL_CONFIG[quintal_type]['kg']
    return quintales * kg_per_quintal

def quintales_to_mt(quintales, quintal_type='standard'):
    """Convertir quintales a toneladas métricas"""
    kg = quintales_to_kg(quintales, quintal_type)
    return kg_to_mt(kg)

def kg_to_quintales(kilogramos, quintal_type='standard'):
    """Convertir kilogramos a quintales según tipo de quintal"""
    from config import QUINTAL_CONFIG
    kg_per_quintal = QUINTAL_CONFIG[quintal_type]['kg']
    return kilogramos / kg_per_quintal

def precio_mt_to_quintal(precio_mt, quintal_type='standard'):
    """Convertir precio por MT a precio por quintal"""
    from config import QUINTAL_CONFIG
    kg_per_quintal = QUINTAL_CONFIG[quintal_type]['kg']
    return (precio_mt * kg_per_quintal) / 1000.0

# Ejemplo de uso:
# >>> quintales_to_mt(50, 'colombia')
# 2.5
# >>> precio_mt_to_quintal(5700, 'colombia')
# 285.0
```

---

## 🔍 CASOS DE USO

### Caso 1: Compra de Lote a Productor

**Escenario:** Exportadora compra un lote de 50 quintales de cacao a un productor

```
1. Obtener precio spot actual:
   → Yahoo Finance CC=F: $6,833.22/MT

2. Aplicar diferencial para productores:
   → Diferencial productor: -$1,500/MT (rango estándar -$1,400 a -$1,600)
   → Precio compra: $6,833.22 - $1,500 = $5,333.22/MT

3. Convertir peso a MT:
   → Peso: 50 quintales (Colombia: 50 kg/qq)
   → kg = 50 × 50 = 2,500 kg
   → MT = 2,500 / 1,000 = 2.5 MT

4. Calcular precio total:
   → Precio total = 2.5 MT × $5,333.22 = $13,333.05 USD

5. Precio por quintal (para referencia del productor):
   → Precio/qq = $13,333.05 / 50 = $266.66/quintal

6. Registrar en BD:
   INSERT INTO producer_lots (
       lot_code, weight_kg, purchase_price_usd, 
       purchase_price_per_mt, differential_applied, status
   ) VALUES (
       'LOT-CACAO-20251111-0007', 
       2500, 
       13333.05,
       5333.22,
       -1500,
       'purchased'
   );
```

### Caso 2: Venta a Cliente Externo (Exportación)

**Escenario:** Exportadora vende 10 MT de cacao a cliente internacional

```
1. Obtener precio spot actual:
   → Yahoo Finance CC=F: $6,833.22/MT

2. Aplicar diferencial para exportación:
   → Diferencial exportadora: -$1,100/MT (rango estándar -$1,000 a -$1,200)
   → Precio venta: $6,833.22 - $1,100 = $5,733.22/MT

3. Calcular precio total:
   → Volumen: 10 MT
   → Precio total = 10 MT × $5,733.22 = $57,332.20 USD

4. Calcular margen (si se compró a productores):
   → Precio compra promedio: $5,333.22/MT
   → Precio venta: $5,733.22/MT
   → Margen = $5,733.22 - $5,333.22 = $400/MT
   → Margen total = 10 MT × $400 = $4,000 USD
   → Margen %: ($400 / $5,333.22) × 100 = 7.5%

5. Registrar contrato:
   INSERT INTO export_contracts (
       contract_code, volume_mt, price_per_mt, 
       total_value_usd, differential_applied, status
   ) VALUES (
       'EXP-2025-001', 
       10.0, 
       5733.22,
       57332.20,
       -1100,
       'active'
   );
```

### Caso 3: Fijación de Precio con Batches

**Escenario:** Cliente fija precio para 20 MT, exportadora completa con batches

```
1. Cliente solicita fijación:
   → Timestamp: 2025-11-11 14:30:00
   → Spot del momento: $6,833.22/MT
   → Diferencial negociado: -$1,050/MT (mejor que estándar)
   → Precio fijado: $6,833.22 - $1,050 = $5,783.22/MT
   → Volumen total: 20 MT

2. Exportadora crea batches para completar:
   
   Batch 1 (LOT-CACAO-20241101-0001):
   → Peso: 2.5 MT
   → Status: batched → fixed
   → Precio fijado: 2.5 × $5,783.22 = $14,458.05
   
   Batch 2 (LOT-CACAO-20241102-0002):
   → Peso: 1.8 MT
   → Status: batched → fixed
   → Precio fijado: 1.8 × $5,783.22 = $10,409.80
   
   [... continuar hasta completar 20 MT]

3. Actualizar registros:
   UPDATE producer_lots
   SET fixed_price_usd = (weight_kg / 1000.0) * 5783.22,
       fixed_date = '2025-11-11 14:30:00',
       status = 'fixed',
       contract_id = 'EXP-2025-001'
   WHERE lot_code IN ('LOT-CACAO-20241101-0001', 'LOT-CACAO-20241102-0002', ...);

4. Actualizar contrato:
   UPDATE export_contracts
   SET batches_completed = 8,
       total_mt_batched = 20.0,
       batching_complete = TRUE
   WHERE contract_code = 'EXP-2025-001';
```

### Caso 4: Análisis de Margen de Operación

**Escenario:** Evaluar rentabilidad de operación completa

```
1. Datos de mercado:
   → Precio spot: $6,833.22/MT
   → Diferencial exportadora: -$1,100/MT → Venta: $5,733.22/MT
   → Diferencial productor: -$1,500/MT → Compra: $5,333.22/MT

2. Volumen operado:
   → Comprado a productores: 100 MT
   → Vendido a clientes: 95 MT (5 MT en inventario)

3. Cálculo financiero:
   
   Ingresos (ventas):
   → 95 MT × $5,733.22 = $544,655.90
   
   Costos (compras):
   → 100 MT × $5,333.22 = $533,322.00
   
   Margen bruto:
   → $544,655.90 - $533,322.00 = $11,333.90
   → Margen/MT vendida: $11,333.90 / 95 = $119.30/MT
   
   Valor inventario:
   → 5 MT × $5,333.22 = $26,666.10 (costo de compra)

4. Análisis:
   → Margen operativo: 2.1% sobre ventas
   → Margen teórico (diferencial): $400/MT
   → Margen real: $119.30/MT (afectado por inventario)
   → Rotación: 95% del volumen vendido
```

---

## 📊 DASHBOARD - VISUALIZACIÓN

### Área de Precios del Cacao

El dashboard muestra 4 cards principales:

#### 1. Precio Spot
- **Valor:** Precio actual en USD/MT
- **Indicador:** Cambio diario en porcentaje (↑ verde / ↓ rojo)
- **Fuente:** Yahoo Finance (CC=F)
- **Color:** Gradiente marrón (#8B4513)

#### 2. Contratos Activos
- **Valor:** Precio promedio de lotes purchased/batched
- **Contador:** Número de contratos activos
- **Volumen:** Total en toneladas métricas
- **Color:** Gradiente cobre (#B87333)

#### 3. Precio Fijado
- **Valor:** Precio promedio de lotes con precio fijado
- **Volumen:** MT con precio fijado
- **Color:** Gradiente dorado (#DAA520)

#### 4. Diferencial
- **Valor:** Diferencia en USD/MT
- **Porcentaje:** Diferencial porcentual vs spot
- **Estado:** Clasificación (Normal, Bajo, Favorable, Premium)
- **Color:** Gradiente verde oliva (#6B8E23)

### Resumen de Mercado

- **Rango 52 semanas:** Mínimo - Máximo
- **Volatilidad:** Porcentaje anualizado
- **Fuente de datos:** Yahoo Finance (CC=F)
- **Lotes analizados:** Contador de lotes en BD

---

## 🔐 SEGURIDAD Y VALIDACIÓN

### Validación de Datos

```python
# Validar precio spot
if spot_price <= 0 or spot_price > 50000:
    logger.warning("Precio spot fuera de rango esperado")
    spot_price = 3250.0  # Fallback

# Validar diferencial
if differential < -3000 or differential > 1000:
    logger.warning("Diferencial anómalo detectado")
    # Investigar causa

# Validar peso
if weight_kg <= 0 or weight_kg > 100000:
    raise ValueError("Peso del lote inválido")
```

### Manejo de Errores

```python
try:
    cacao = yf.Ticker("CC=F")
    hist = cacao.history(period="5d")
except Exception as e:
    logger.error(f"Error Yahoo Finance: {e}")
    # Usar precio fallback o caché
    spot_price = get_cached_price() or 3250.0
```

---

## 📚 REFERENCIAS

### Fuentes de Datos

- **Yahoo Finance:** https://finance.yahoo.com/quote/CC=F
- **ICE Futures U.S.:** https://www.theice.com/products/7
- **World Cocoa Foundation:** https://www.worldcocoafoundation.org/

### Documentación Técnica

- **yfinance GitHub:** https://github.com/ranaroussi/yfinance
- **Pandas Documentation:** https://pandas.pydata.org/docs/
- **Flask Documentation:** https://flask.palletsprojects.com/

### Mercados de Cacao

- **ICCO (International Cocoa Organization):** https://www.icco.org/
- **Cocoa Barometer:** https://cocoabarometer.org/

---

## 📝 HISTORIAL DE CAMBIOS

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2025-11-11 | Documento inicial con lógica de negocio completa |
| 1.1 | 2025-11-11 | Actualización con correcciones:<br>• Clarificación de diferenciales (exportadoras vs productores)<br>• Adición de quintales configurables por país<br>• Nuevos casos de uso con batches y margen<br>• Funciones de conversión implementadas |

---

## 👥 CONTACTO Y SOPORTE

Para preguntas sobre la lógica de negocio del cacao:

- **Email técnico:** dev@triboka.com
- **Documentación:** https://docs.triboka.com
- **Sistema:** https://app.triboka.com

---

**© 2025 Triboka - Plataforma de Trazabilidad de Cacao con Blockchain**


Dashboard exportador

ok en cuanto a seccion la seccion empresas no deberia estar aqui sino solo en admin y operadores

me falta la seccion donde se registrara se gestionara o se integrara apis para el tema de la exportacion o consideras que eso debe ser parte del ERP 

dentro del panel de exportador tengo una seccion contratos aqui muestra el resumen de lo que hay en la seccion en el sidebar contratos ok en este caso deberia mostrar un resumen de los contratos activos y un boton para crear nuevo contrato Luego en la seccion contratos si deberia estar toda la gestion de contratos exportacion y ahi si deberia estar la parte de integracion con apis externas para el tema de exportacion

los batches creados no tienen trazabilidad y asi mismo choca el estado con los botones de trazabilidad y ver detalle

al crear un nuevo batch me sale erros mostrando los batches disponibles

y en contratos no se dejan visualizar 

la logica aqui es que exportadora debe poder visualizar a todos los productores y sus lotes todos los registrados en el sistema poder categorizarlo por ubicacion por ejemplo y de alguna manera levantar una oferta para hacer un contrato de compra con ciertos lotes seleccionados por ejemplo esto debe quedar bien definido y pienso que deberiamos reestructura por ejemplo la seccion del sidebar lotes que aqui se muestren todo los lotes de todos los usuarios registrados y poder categorizarlos y filtarlos y desde aqui mismo desde los lotes definir la menera en crear contratos con los productores y las acciones que se ejecuten como exportadora se reflejen en en lso dashboard de los productores tambien, y podria ser que en el panel de exportador en la seccion lotes disponibles solo se vean los disponibles de los productores con los que ya hay convenio o contratos establecidos asi me parece que deberia ser la logica, tambien esta informacion de productores debe estar disponible para el ERP para la seccion proveedores

pero es porque companie lista las empresas registrada no los productores eso no esta programado para listarse ni quiero que se liste /lotes solo debe mostrar los lotes de todos los productores no listar a los productores 

sudo systemctl restart triboka-frontend
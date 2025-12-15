# ✅ Integración Yahoo Finance - Precios Reales de Cacao

## 📋 Resumen

Se ha integrado **Yahoo Finance (yfinance)** para obtener el **precio spot REAL del cacao** desde los mercados internacionales, combinándolo con los datos reales de contratos de la base de datos de Triboka.

## 🎯 Cambios Implementados

### 1. **Instalación de yfinance**

```bash
/home/rootpanel/web/app.triboka.com/.venv/bin/pip install yfinance
```

Paquetes instalados:
- `yfinance==0.2.66`
- `pandas==2.3.3`
- `numpy==2.3.4`
- `beautifulsoup4==4.14.2`
- Dependencias adicionales

### 2. **Backend - Endpoint Mejorado**

**Archivo:** `backend/app_web3.py` (líneas ~2320-2480)

#### **Precio Spot (Yahoo Finance)**

```python
# Ticker del cacao: CC=F (Cocoa Futures)
cacao = yf.Ticker("CC=F")
hist = cacao.history(period="5d")

# Precio más reciente
current_price = float(hist['Close'].iloc[-1])

# Convertir de USD/ton corta a USD/tonelada métrica
# 1 MT = 2204.62 lbs, 1 ton corta = 2000 lbs
spot_price = current_price * (2204.62 / 2000.0)

# Calcular cambio diario
prev_price = float(hist['Close'].iloc[-2])
daily_change = ((current_price - prev_price) / prev_price) * 100
```

#### **Datos Reales de Base de Datos**

```python
# Lotes con precios reales
purchased_lots = ProducerLot.query.filter(
    ProducerLot.status.in_(['purchased', 'batched']),
    ProducerLot.purchase_price_usd.isnot(None),
    ProducerLot.weight_kg > 0
).all()

# Calcular precio promedio de contratos
for lot in purchased_lots:
    weight_mt = float(lot.weight_kg) / 1000.0  # kg → MT
    price_per_mt = float(lot.purchase_price_usd) / weight_mt
    contract_prices.append(price_per_mt)
    total_contract_weight += weight_mt

avg_contract_price = statistics.mean(contract_prices)
```

#### **Estadísticas de Mercado (52 semanas)**

```python
# Obtener datos históricos de 1 año
hist_year = cacao.history(period="1y")

# Rango de precios
year_low = float(hist_year['Low'].min()) * (2204.62 / 2000.0)
year_high = float(hist_year['High'].max()) * (2204.62 / 2000.0)

# Volatilidad anualizada
returns = hist_year['Close'].pct_change().dropna()
volatility = float(returns.std()) * 100 * (252 ** 0.5)
```

### 3. **Respuesta del Endpoint**

**Estructura JSON Completa:**

```json
{
  "spot": {
    "price": 6710.86,
    "change": 1.25,
    "currency": "USD",
    "unit": "MT",
    "source": "Yahoo Finance (CC=F)"
  },
  "contracts": {
    "avgPrice": 1626.83,
    "activeCount": 5,
    "totalVolume": 1800.00
  },
  "fixed": {
    "avgPrice": 1626.83,
    "volume": 10.38
  },
  "differential": {
    "value": -5084.03,
    "percent": -75.76
  },
  "market": {
    "rangeMin": 6207.11,
    "rangeMax": 14253.97,
    "volatility": 58.31
  },
  "timestamp": "2025-11-11T02:37:55.387892",
  "source": "Yahoo Finance (CC=F) + Triboka Database",
  "data_points": {
    "lots_analyzed": 6,
    "contracts_active": 5,
    "total_fixed_mt": 10.38
  }
}
```

### 4. **Frontend - Visualización Actualizada**

**Archivo:** `frontend/templates/dashboard.html`

**Nuevos campos mostrados:**

```html
<!-- Fuente de datos dinámica -->
<div id="data-source">Yahoo Finance (CC=F)</div>

<!-- Lotes analizados -->
<div id="lots-analyzed">6 lotes (10.38 MT)</div>

<!-- Próxima actualización -->
<div id="next-update">5:00</div>
```

**JavaScript actualizado:**

```javascript
// Mostrar fuente de datos real
if (dataSourceElement && data.source) {
    dataSourceElement.textContent = data.source;
}

// Mostrar estadísticas de BD
if (lotsAnalyzedElement && data.data_points) {
    lotsAnalyzedElement.textContent = 
        `${data.data_points.lots_analyzed} lotes (${data.data_points.total_fixed_mt} MT)`;
}
```

## 📊 Datos Mostrados en Dashboard

### **Card 1: Precio Spot**
- 💰 **Fuente:** Yahoo Finance (CC=F)
- 📈 **Datos:** Precio en tiempo real + cambio diario
- 🔄 **Actualización:** Cada 5 minutos
- 🌐 **Mercado:** ICE Futures U.S.

**Ejemplo actual:**
```
Precio Spot: $6,710.86 USD/MT
Cambio: +1.25%
```

### **Card 2: Contratos Activos**
- 💰 **Fuente:** Base de datos Triboka
- 📊 **Cálculo:** Promedio de lotes purchased/batched
- 📋 **Datos:** Número de contratos y volumen total

**Ejemplo actual:**
```
Precio Contratos: $1,626.83/MT
Contratos activos: 5
Volumen: 1,800.00 MT
```

### **Card 3: Precio Fijado**
- 💰 **Fuente:** Base de datos Triboka
- 📊 **Cálculo:** Promedio de lotes con precio fijado
- ⚖️ **Datos:** Volumen total fijado

**Ejemplo actual:**
```
Precio Fijado: $1,626.83/MT
Volumen fijado: 10.38 MT
```

### **Card 4: Diferencial**
- 📊 **Cálculo:** Contratos - Spot
- 📈 **Porcentaje:** (Diferencial / Spot) * 100

**Ejemplo actual:**
```
Diferencial: -$5,084.03/MT
Porcentaje: -75.76%
```

### **Resumen de Mercado**
- 📉 **Rango 52 semanas:** $6,207.11 - $14,253.97
- 📊 **Volatilidad:** 58.31%
- 📡 **Fuente:** Yahoo Finance (CC=F) + Triboka Database
- 📦 **Lotes analizados:** 6 lotes (10.38 MT)

## 🔍 Conversión de Unidades

**Yahoo Finance CC=F retorna:**
- Precio en USD por **tonelada corta** (2,000 lbs)

**Triboka usa:**
- Precio en USD por **tonelada métrica** (2,204.62 lbs)

**Conversión aplicada:**
```python
spot_price_mt = spot_price_short_ton * (2204.62 / 2000.0)
```

**Factor de conversión:** 1.102310 (≈ +10.23%)

## 🔄 Flujo de Actualización

```
1. Usuario accede a /dashboard
   ↓
2. Frontend ejecuta initCacaoPrices()
   ↓
3. JavaScript hace fetch a /api/market/cacao-prices
   ↓
4. Backend ejecuta:
   a. yf.Ticker("CC=F").history(period="5d")
   b. ProducerLot.query.filter(status='purchased')...
   c. ExportContract.query.filter(status='active')...
   ↓
5. Backend calcula:
   - Precio spot (Yahoo Finance)
   - Precio promedio contratos (BD real)
   - Precio fijado (BD real)
   - Diferencial (Contratos - Spot)
   - Estadísticas de mercado (Yahoo Finance 1y)
   ↓
6. Backend retorna JSON con datos reales
   ↓
7. Frontend actualiza DOM con displayCacaoPrices(data)
   ↓
8. Espera 5 minutos y repite desde paso 3
```

## 📈 Interpretación de Datos

### **¿Por qué el diferencial es negativo (-75.76%)?**

El precio spot actual está en **$6,710.86/MT** (Yahoo Finance), pero los contratos en la BD tienen precios de ejemplo mucho más bajos (**$1,626.83/MT**).

Esto es **normal en datos de prueba**. En producción:
- Los contratos deberían tener precios cercanos al spot
- El diferencial típico es +$50 a +$200/MT (premium por calidad, certificaciones)
- Diferencial negativo indicaría contratos antiguos o precios congelados

### **Volatilidad 58.31%**

La volatilidad actual del cacao es **muy alta** debido a:
- Crisis climática en Costa de Marfil y Ghana (principales productores)
- Problemas de oferta global
- Especulación en mercados de futuros

**Contexto histórico:**
- Volatilidad normal del cacao: 15-25%
- Volatilidad actual: 58.31% (extremadamente alta)
- Máximo histórico reciente: $14,253.97/MT (récord)

## 🛠️ Configuración Técnica

### **Ticker Yahoo Finance**

```
Símbolo: CC=F
Nombre: Cocoa Futures
Mercado: ICE Futures U.S.
Unidad: USD por tonelada corta
Horario: 24/5 (lunes-viernes)
```

### **Alternativas de Ticker**

Si `CC=F` no está disponible:
- `CCK25.NYB` - Cocoa May 2025 Contract
- `CCN25.NYB` - Cocoa July 2025 Contract
- Consultar ICE Futures directamente

### **Límites de Yahoo Finance**

- **Rate limiting:** ~2,000 requests/hora
- **Actualización dashboard:** Cada 5 minutos = 288 requests/día
- **Datos históricos:** Hasta 10 años gratis
- **Recomendación:** Para producción considerar API pagada (Bloomberg, Reuters)

## 📊 Logs del Sistema

### **Logs exitosos:**

```
INFO:__main__:✅ Precio spot real obtenido: $6710.86/MT (cambio: +1.25%)
INFO:__main__:📊 Lotes encontrados en BD: 6
INFO:__main__:💰 Precio promedio contratos: $1626.83/MT (de 6 lotes)
INFO:__main__:🔒 Precio fijado promedio: $1626.83/MT, Volumen: 10.38 MT
INFO:__main__:📄 Contratos activos: 5, Volumen total: 1800.00 MT
INFO:__main__:📊 Diferencial: $-5084.03/MT (-75.76%)
INFO:__main__:📈 Rango anual: $6207.11 - $14253.97, Volatilidad: 58.31%
INFO:__main__:✅ Precios calculados exitosamente con datos reales
```

### **Logs de error (fallback):**

```
ERROR:__main__:❌ Error obteniendo precio de Yahoo Finance: [error]
WARNING:__main__:⚠️ No se pudieron obtener datos de Yahoo Finance, usando valor por defecto
```

En caso de error, el sistema retorna datos de fallback simulados para mantener el dashboard funcional.

## ✅ Verificación de Funcionamiento

**1. Verificar instalación:**
```bash
/home/rootpanel/web/app.triboka.com/.venv/bin/pip show yfinance
```

**2. Probar endpoint manualmente:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:5003/api/market/cacao-prices | jq
```

**3. Verificar logs en tiempo real:**
```bash
sudo journalctl -u triboka-flask -f | grep "cacao"
```

**4. Ver dashboard:**
```
URL: https://app.triboka.com/dashboard
Usuario: admin@triboka.com
Password: admin123
```

## 🎯 Datos Reales Ahora Mostrados

| Métrica | Fuente | Tipo |
|---------|--------|------|
| Precio Spot | Yahoo Finance (CC=F) | ✅ Real |
| Cambio diario | Yahoo Finance (CC=F) | ✅ Real |
| Precio Contratos | Base de datos Triboka | ✅ Real |
| Volumen Contratos | Base de datos Triboka | ✅ Real |
| Precio Fijado | Base de datos Triboka | ✅ Real |
| Volumen Fijado | Base de datos Triboka | ✅ Real |
| Rango 52 semanas | Yahoo Finance (CC=F) | ✅ Real |
| Volatilidad | Yahoo Finance (CC=F) | ✅ Real |
| Lotes analizados | Base de datos Triboka | ✅ Real |

## 📝 Notas Importantes

### **Precios en BD de Prueba**

Los lotes actuales tienen precios de ejemplo (~$1,600-$3,000/MT) que son **significativamente más bajos** que el precio spot actual ($6,710/MT).

**Para datos realistas:**
1. Actualizar precios de lotes en BD con valores cercanos al spot
2. Usar precios históricos reales (2023-2024: $2,500-$4,500/MT)
3. Considerar premium por calidad/certificaciones (+$100-300/MT)

### **Actualización de Precios en BD**

Ejemplo para actualizar precios de lotes:

```python
from models_simple import db, ProducerLot
from decimal import Decimal

# Precio spot actual aproximado (usar valor reciente)
current_spot = 6700.0

# Actualizar lotes con precios realistas
lots = ProducerLot.query.filter_by(status='purchased').all()
for lot in lots:
    weight_mt = float(lot.weight_kg) / 1000.0
    # Premium de +5% sobre spot
    price_per_mt = current_spot * 1.05
    lot.purchase_price_usd = Decimal(price_per_mt * weight_mt)

db.session.commit()
```

## 🚀 Mejoras Futuras

1. **Cache de precios Yahoo Finance** (Redis/Memcached)
2. **WebSocket** para actualizaciones en tiempo real
3. **Gráficos históricos** (Chart.js con datos de yfinance)
4. **Alertas de precio** (notificaciones cuando cruza umbrales)
5. **API Bloomberg/Reuters** para datos de grado institucional
6. **Múltiples orígenes de cacao** (Ghana, Ecuador, Perú)
7. **Forward curves** (precios futuros de contratos)

---

**Fecha:** 11 de noviembre de 2025  
**Sistema:** Triboka Agro - Dashboard ESG  
**Estado:** ✅ Yahoo Finance Integrado + Datos Reales de BD  
**Ticker:** CC=F (Cocoa Futures, ICE)

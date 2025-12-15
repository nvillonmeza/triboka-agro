"""
Configuración de precios y conversiones de cacao
Triboka - Plataforma de Trazabilidad
"""

# =====================================
# CONFIGURACIÓN DE MERCADO
# =====================================

# Ticker de Yahoo Finance para precio spot
CACAO_TICKER = "CC=F"  # Cocoa Futures, ICE Futures U.S.

# Intervalo de actualización de precios (segundos)
CACAO_UPDATE_INTERVAL = 300  # 5 minutos

# =====================================
# DIFERENCIALES DE MERCADO (USD/MT)
# =====================================

# Diferencial para exportadoras (venta a clientes internacionales)
DIFFERENTIAL_EXPORTER_MIN = -1200   # Mínimo: -$1,200/MT
DIFFERENTIAL_EXPORTER_MAX = -1000   # Máximo: -$1,000/MT
DIFFERENTIAL_EXPORTER_DEFAULT = -1100  # Por defecto: -$1,100/MT

# Diferencial para productores (compra local)
DIFFERENTIAL_PRODUCER_MIN = -1600   # Mínimo: -$1,600/MT
DIFFERENTIAL_PRODUCER_MAX = -1400   # Máximo: -$1,400/MT
DIFFERENTIAL_PRODUCER_DEFAULT = -1500  # Por defecto: -$1,500/MT

# Margen esperado (diferencia entre compra y venta)
EXPECTED_MARGIN_MIN = 300   # Mínimo: $300/MT
EXPECTED_MARGIN_MAX = 600   # Máximo: $600/MT
EXPECTED_MARGIN_DEFAULT = 400  # Por defecto: $400/MT

# =====================================
# CONVERSIONES DE PESO
# =====================================

# Conversión tonelada corta → tonelada métrica
# Yahoo Finance CC=F usa toneladas cortas (2,000 lbs)
# Sistema usa toneladas métricas (1,000 kg = 2,204.62 lbs)
CONVERSION_FACTOR_TON_TO_MT = 2204.62 / 2000.0  # = 1.102310

# Conversiones básicas
MT_TO_KG = 1000.0           # 1 tonelada métrica = 1,000 kg
KG_TO_MT = 1.0 / 1000.0     # 1 kg = 0.001 MT
LBS_TO_KG = 0.453592        # 1 libra = 0.453592 kg
KG_TO_LBS = 2.20462         # 1 kg = 2.20462 libras

# =====================================
# CONFIGURACIÓN DE QUINTALES
# =====================================

# Configuración por país/región
# Permite adaptar el sistema a diferentes estándares locales
QUINTAL_CONFIG = {
    'standard': {
        'kg': 45.3592,
        'lbs': 100,
        'description': 'Quintal estándar internacional (100 lbs)',
        'region': 'Internacional'
    },
    'colombia': {
        'kg': 50.0,
        'lbs': 110.231,
        'description': 'Quintal colombiano (50 kg)',
        'region': 'Colombia'
    },
    'mexico': {
        'kg': 46.0,
        'lbs': 101.413,
        'description': 'Quintal mexicano (46 kg)',
        'region': 'México'
    },
    'peru': {
        'kg': 46.0,
        'lbs': 101.413,
        'description': 'Quintal peruano (46 kg)',
        'region': 'Perú'
    },
    'ecuador': {
        'kg': 45.36,
        'lbs': 100,
        'description': 'Quintal ecuatoriano (100 lbs)',
        'region': 'Ecuador'
    },
    'venezuela': {
        'kg': 46.0,
        'lbs': 101.413,
        'description': 'Quintal venezolano (46 kg)',
        'region': 'Venezuela'
    }
}

# =====================================
# SELECCIÓN ACTIVA
# =====================================

# CONFIGURAR AQUÍ EL TIPO DE QUINTAL A USAR
# Opciones: 'standard', 'colombia', 'mexico', 'peru', 'ecuador', 'venezuela'
QUINTAL_TYPE = 'colombia'  # ⬅️ CAMBIAR SEGÚN EL PAÍS DE OPERACIÓN

# =====================================
# VALORES DERIVADOS (NO MODIFICAR)
# =====================================

# Obtener configuración activa
QUINTAL_TO_KG = QUINTAL_CONFIG[QUINTAL_TYPE]['kg']
QUINTAL_TO_LBS = QUINTAL_CONFIG[QUINTAL_TYPE]['lbs']
QUINTAL_TO_MT = QUINTAL_TO_KG / 1000.0
QUINTAL_DESCRIPTION = QUINTAL_CONFIG[QUINTAL_TYPE]['description']
QUINTAL_REGION = QUINTAL_CONFIG[QUINTAL_TYPE]['region']

# =====================================
# VALIDACIONES
# =====================================

# Rangos válidos para validación de datos
PRICE_SPOT_MIN = 1000.0      # USD/MT mínimo esperado
PRICE_SPOT_MAX = 20000.0     # USD/MT máximo esperado
WEIGHT_LOT_MIN = 1.0         # kg mínimo por lote
WEIGHT_LOT_MAX = 100000.0    # kg máximo por lote
QUALITY_SCORE_MIN = 0.0      # Puntuación mínima de calidad
QUALITY_SCORE_MAX = 100.0    # Puntuación máxima de calidad
MOISTURE_MIN = 0.0           # % humedad mínimo
MOISTURE_MAX = 15.0          # % humedad máximo (estándar: 7-8%)

# =====================================
# FUNCIONES DE CONVERSIÓN
# =====================================

def ton_corta_to_mt(precio_ton_corta):
    """Convertir precio de tonelada corta (CC=F) a tonelada métrica"""
    return precio_ton_corta * CONVERSION_FACTOR_TON_TO_MT

def kg_to_mt(kilogramos):
    """Convertir kilogramos a toneladas métricas"""
    return kilogramos * KG_TO_MT

def mt_to_kg(toneladas):
    """Convertir toneladas métricas a kilogramos"""
    return toneladas * MT_TO_KG

def quintales_to_kg(quintales, quintal_type=None):
    """Convertir quintales a kilogramos"""
    if quintal_type is None:
        quintal_type = QUINTAL_TYPE
    kg_per_quintal = QUINTAL_CONFIG[quintal_type]['kg']
    return quintales * kg_per_quintal

def quintales_to_mt(quintales, quintal_type=None):
    """Convertir quintales a toneladas métricas"""
    kg = quintales_to_kg(quintales, quintal_type)
    return kg_to_mt(kg)

def kg_to_quintales(kilogramos, quintal_type=None):
    """Convertir kilogramos a quintales"""
    if quintal_type is None:
        quintal_type = QUINTAL_TYPE
    kg_per_quintal = QUINTAL_CONFIG[quintal_type]['kg']
    return kilogramos / kg_per_quintal

def mt_to_quintales(toneladas, quintal_type=None):
    """Convertir toneladas métricas a quintales"""
    kg = mt_to_kg(toneladas)
    return kg_to_quintales(kg, quintal_type)

def precio_mt_to_quintal(precio_mt, quintal_type=None):
    """Convertir precio por MT a precio por quintal"""
    if quintal_type is None:
        quintal_type = QUINTAL_TYPE
    kg_per_quintal = QUINTAL_CONFIG[quintal_type]['kg']
    return (precio_mt * kg_per_quintal) / 1000.0

def precio_quintal_to_mt(precio_quintal, quintal_type=None):
    """Convertir precio por quintal a precio por MT"""
    if quintal_type is None:
        quintal_type = QUINTAL_TYPE
    kg_per_quintal = QUINTAL_CONFIG[quintal_type]['kg']
    return (precio_quintal * 1000.0) / kg_per_quintal

def calcular_diferencial(precio_compra_mt, precio_spot_mt):
    """Calcular diferencial entre precio de compra y spot"""
    return precio_compra_mt - precio_spot_mt

def calcular_margen(precio_venta_mt, precio_compra_mt):
    """Calcular margen entre precio de venta y compra"""
    return precio_venta_mt - precio_compra_mt

def calcular_margen_porcentual(precio_venta_mt, precio_compra_mt):
    """Calcular margen porcentual"""
    margen = calcular_margen(precio_venta_mt, precio_compra_mt)
    return (margen / precio_compra_mt) * 100.0 if precio_compra_mt > 0 else 0.0

def validar_precio_spot(precio):
    """Validar que el precio spot esté en rango esperado"""
    return PRICE_SPOT_MIN <= precio <= PRICE_SPOT_MAX

def validar_peso_lote(peso_kg):
    """Validar que el peso del lote esté en rango válido"""
    return WEIGHT_LOT_MIN <= peso_kg <= WEIGHT_LOT_MAX

def validar_diferencial_exportadora(diferencial):
    """Validar que el diferencial de exportadora esté en rango"""
    return DIFFERENTIAL_EXPORTER_MIN <= diferencial <= DIFFERENTIAL_EXPORTER_MAX

def validar_diferencial_productor(diferencial):
    """Validar que el diferencial de productor esté en rango"""
    return DIFFERENTIAL_PRODUCER_MIN <= diferencial <= DIFFERENTIAL_PRODUCER_MAX

# =====================================
# INFORMACIÓN DEL SISTEMA
# =====================================

def get_system_config():
    """Obtener configuración actual del sistema"""
    return {
        'ticker': CACAO_TICKER,
        'update_interval': CACAO_UPDATE_INTERVAL,
        'differential_exporter': {
            'min': DIFFERENTIAL_EXPORTER_MIN,
            'max': DIFFERENTIAL_EXPORTER_MAX,
            'default': DIFFERENTIAL_EXPORTER_DEFAULT
        },
        'differential_producer': {
            'min': DIFFERENTIAL_PRODUCER_MIN,
            'max': DIFFERENTIAL_PRODUCER_MAX,
            'default': DIFFERENTIAL_PRODUCER_DEFAULT
        },
        'quintal': {
            'type': QUINTAL_TYPE,
            'kg': QUINTAL_TO_KG,
            'lbs': QUINTAL_TO_LBS,
            'description': QUINTAL_DESCRIPTION,
            'region': QUINTAL_REGION
        },
        'conversions': {
            'ton_to_mt': CONVERSION_FACTOR_TON_TO_MT,
            'mt_to_kg': MT_TO_KG,
            'kg_to_mt': KG_TO_MT
        }
    }

# =====================================
# EJEMPLO DE USO
# =====================================

if __name__ == '__main__':
    import json
    
    print("="*70)
    print("CONFIGURACIÓN DE CACAO - TRIBOKA")
    print("="*70)
    print()
    
    config = get_system_config()
    print(json.dumps(config, indent=2))
    print()
    
    print("Ejemplos de conversión:")
    print(f"50 quintales ({QUINTAL_REGION}) = {quintales_to_kg(50):.2f} kg = {quintales_to_mt(50):.3f} MT")
    print(f"2,500 kg = {kg_to_quintales(2500):.2f} quintales")
    print(f"Precio $5,700/MT = ${precio_mt_to_quintal(5700):.2f}/quintal")
    print()
    
    print("Ejemplo de diferencial:")
    spot = 6833.22
    precio_exportadora = spot + DIFFERENTIAL_EXPORTER_DEFAULT
    precio_productor = spot + DIFFERENTIAL_PRODUCER_DEFAULT
    margen = calcular_margen(precio_exportadora, precio_productor)
    margen_pct = calcular_margen_porcentual(precio_exportadora, precio_productor)
    
    print(f"Spot: ${spot:.2f}/MT")
    print(f"Precio exportadora: ${precio_exportadora:.2f}/MT (diferencial: ${DIFFERENTIAL_EXPORTER_DEFAULT}/MT)")
    print(f"Precio productor: ${precio_productor:.2f}/MT (diferencial: ${DIFFERENTIAL_PRODUCER_DEFAULT}/MT)")
    print(f"Margen: ${margen:.2f}/MT ({margen_pct:.2f}%)")
    print()

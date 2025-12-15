#!/bin/bash

# 🧪 Test Automatizado del Flujo Blockchain End-to-End
# Versión: 1.0
# Fecha: 2025-11-07

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# URLs de los servicios
AGRO_URL="http://localhost:5003"
ERP_URL="http://localhost:5007"
FRONTEND_URL="http://localhost:5051"

# Credenciales
EMAIL="admin@triboka.com"
PASSWORD="admin123"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}     🧪 TEST FLUJO BLOCKCHAIN END-TO-END                  ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Función para imprimir pasos
print_step() {
    echo ""
    echo -e "${YELLOW}▶ $1${NC}"
    echo ""
}

# Función para verificar respuesta
check_response() {
    if echo "$1" | grep -q "error"; then
        echo -e "${RED}✗ Error en la respuesta${NC}"
        echo "$1"
        exit 1
    else
        echo -e "${GREEN}✓ Éxito${NC}"
    fi
}

# 1. Verificar servicios
print_step "1️⃣  Verificando servicios activos..."

echo "Triboka Agro (5003):"
AGRO_HEALTH=$(curl -s "$AGRO_URL/health" || echo '{"error":"No responde"}')
if echo "$AGRO_HEALTH" | grep -q '"status":"ok"'; then
    echo -e "${GREEN}✓ Triboka Agro OK${NC}"
else
    echo -e "${RED}✗ Triboka Agro no responde${NC}"
    exit 1
fi

echo ""
echo "ERP Backend (5007):"
ERP_HEALTH=$(curl -s "$ERP_URL/api/health" || echo '{"error":"No responde"}')
if echo "$ERP_HEALTH" | grep -q '"status":"healthy"'; then
    echo -e "${GREEN}✓ ERP Backend OK${NC}"
else
    echo -e "${RED}✗ ERP Backend no responde${NC}"
    exit 1
fi

# 2. Login en Triboka Agro
print_step "2️⃣  Login en Triboka Agro..."

AGRO_LOGIN=$(curl -s -X POST "$AGRO_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

check_response "$AGRO_LOGIN"

TOKEN_AGRO=$(echo "$AGRO_LOGIN" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "Token Agro: ${TOKEN_AGRO:0:20}..."

# 3. Login en ERP
print_step "3️⃣  Login en ERP..."

ERP_LOGIN=$(curl -s -X POST "$ERP_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

check_response "$ERP_LOGIN"

TOKEN_ERP=$(echo "$ERP_LOGIN" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "Token ERP: ${TOKEN_ERP:0:20}..."

# 4. Listar lotes disponibles en Agro
print_step "4️⃣  Listando lotes disponibles en Triboka Agro..."

LOTS=$(curl -s "$AGRO_URL/api/lots?status=available" \
    -H "Authorization: Bearer $TOKEN_AGRO")

check_response "$LOTS"

NUM_LOTS=$(echo "$LOTS" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('lots', [])))" 2>/dev/null || echo "0")
echo "Lotes disponibles: $NUM_LOTS"

# 5. Importar lotes a ERP
print_step "5️⃣  Importando lotes a ERP..."

IMPORT_RESULT=$(curl -s -X POST "$ERP_URL/api/agro/lotes/importar" \
    -H "Authorization: Bearer $TOKEN_ERP" \
    -H "Content-Type: application/json" \
    -d '{"filters": {"estado": "disponible"}}')

check_response "$IMPORT_RESULT"

IMPORTED=$(echo "$IMPORT_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('lotes_importados', 0))" 2>/dev/null || echo "0")
echo "Lotes importados: $IMPORTED"

# 6. Listar lotes en ERP
print_step "6️⃣  Listando lotes en ERP..."

ERP_LOTS=$(curl -s "$ERP_URL/api/lotes?estado=almacenado" \
    -H "Authorization: Bearer $TOKEN_ERP")

check_response "$ERP_LOTS"

# Extraer ID del primer lote
LOTE_ID=$(echo "$ERP_LOTS" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['lotes'][0]['id'] if data.get('lotes') else '')" 2>/dev/null || echo "")

if [ -z "$LOTE_ID" ]; then
    echo -e "${RED}✗ No hay lotes disponibles para crear batch${NC}"
    exit 1
fi

echo "Lote ID seleccionado: $LOTE_ID"

# 7. Listar clientes
print_step "7️⃣  Listando clientes en ERP..."

CLIENTES=$(curl -s "$ERP_URL/api/clientes" \
    -H "Authorization: Bearer $TOKEN_ERP")

check_response "$CLIENTES"

# Extraer ID del primer cliente
CLIENTE_ID=$(echo "$CLIENTES" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['clientes'][0]['id'] if data.get('clientes') else '')" 2>/dev/null || echo "")

if [ -z "$CLIENTE_ID" ]; then
    echo -e "${RED}✗ No hay clientes disponibles${NC}"
    exit 1
fi

echo "Cliente ID seleccionado: $CLIENTE_ID"

# 8. Crear batch en ERP
print_step "8️⃣  Creando batch de exportación en ERP..."

BATCH_CODE="BATCH-TEST-$(date +%Y%m%d-%H%M%S)"
FECHA_EMBARQUE=$(date -d "+30 days" +%Y-%m-%d)

BATCH_CREATE=$(curl -s -X POST "$ERP_URL/api/batches/crear" \
    -H "Authorization: Bearer $TOKEN_ERP" \
    -H "Content-Type: application/json" \
    -d "{
        \"lote_ids\": [$LOTE_ID],
        \"cliente_id\": $CLIENTE_ID,
        \"tipo_operacion\": \"exportacion\",
        \"bl_number\": \"TEST$(date +%Y%m%d)\",
        \"naviera\": \"Test Shipping Line\",
        \"numero_contenedor\": \"TESTCONT$(date +%H%M%S)\",
        \"pais_destino\": \"Estados Unidos\",
        \"puerto_salida\": \"Puerto Cortés, Honduras\",
        \"puerto_destino\": \"Miami, USA\",
        \"fecha_embarque\": \"$FECHA_EMBARQUE\",
        \"incoterm\": \"FOB\",
        \"valor_comercial_usd\": 50000
    }")

check_response "$BATCH_CREATE"

BATCH_ID=$(echo "$BATCH_CREATE" | python3 -c "import sys, json; print(json.load(sys.stdin)['batch']['id'])" 2>/dev/null || echo "")

if [ -z "$BATCH_ID" ]; then
    echo -e "${RED}✗ No se pudo crear el batch${NC}"
    exit 1
fi

echo "Batch creado: ID $BATCH_ID"
echo "Código: $BATCH_CODE"

# 9. Enviar batch a blockchain
print_step "9️⃣  Enviando batch a blockchain (generando NFT)..."

BLOCKCHAIN_RESULT=$(curl -s -X POST "$ERP_URL/api/batches/$BATCH_ID/enviar-blockchain" \
    -H "Authorization: Bearer $TOKEN_ERP" \
    -H "Content-Type: application/json")

check_response "$BLOCKCHAIN_RESULT"

# Extraer información del NFT
NFT_TOKEN_ID=$(echo "$BLOCKCHAIN_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('nft', {}).get('token_id', ''))" 2>/dev/null || echo "")
NFT_CONTRACT=$(echo "$BLOCKCHAIN_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('nft', {}).get('contract_address', ''))" 2>/dev/null || echo "")
NFT_OPENSEA=$(echo "$BLOCKCHAIN_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('nft', {}).get('opensea_url', ''))" 2>/dev/null || echo "")
BLOCKCHAIN_HASH=$(echo "$BLOCKCHAIN_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('batch', {}).get('hash_blockchain', ''))" 2>/dev/null || echo "")

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}                    ✓ NFT GENERADO                        ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Token ID:         $NFT_TOKEN_ID"
echo "Contract:         $NFT_CONTRACT"
echo "Blockchain Hash:  $BLOCKCHAIN_HASH"
echo "OpenSea URL:      $NFT_OPENSEA"
echo ""

# 10. Verificar batch con metadata completa
print_step "🔟 Verificando batch con metadata completa..."

BATCH_DETAIL=$(curl -s "$ERP_URL/api/batches/$BATCH_ID" \
    -H "Authorization: Bearer $TOKEN_ERP")

check_response "$BATCH_DETAIL"

# Verificar que tenga NFT
HAS_NFT=$(echo "$BATCH_DETAIL" | python3 -c "import sys, json; data = json.load(sys.stdin); print('yes' if data.get('batch', {}).get('nft_token_id') else 'no')" 2>/dev/null || echo "no")

if [ "$HAS_NFT" = "yes" ]; then
    echo -e "${GREEN}✓ Batch tiene NFT asociado${NC}"
else
    echo -e "${RED}✗ Batch no tiene NFT${NC}"
    exit 1
fi

# Verificar que tenga metadata completa
HAS_METADATA=$(echo "$BATCH_DETAIL" | python3 -c "import sys, json; data = json.load(sys.stdin); print('yes' if data.get('batch', {}).get('metadata_completa') else 'no')" 2>/dev/null || echo "no")

if [ "$HAS_METADATA" = "yes" ]; then
    echo -e "${GREEN}✓ Batch tiene metadata completa${NC}"
else
    echo -e "${RED}✗ Batch no tiene metadata completa${NC}"
    exit 1
fi

# Resumen Final
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}              🎉 TEST COMPLETADO EXITOSAMENTE             ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}✓${NC} Servicios verificados"
echo -e "${GREEN}✓${NC} Login en ambos sistemas"
echo -e "${GREEN}✓${NC} Lotes importados desde Triboka Agro"
echo -e "${GREEN}✓${NC} Batch creado en ERP"
echo -e "${GREEN}✓${NC} NFT generado en blockchain"
echo -e "${GREEN}✓${NC} Metadata completa preservada"
echo ""
echo "Batch ID:     $BATCH_ID"
echo "Batch Code:   $BATCH_CODE"
echo "NFT Token:    $NFT_TOKEN_ID"
echo "OpenSea:      $NFT_OPENSEA"
echo ""
echo -e "${YELLOW}Ver en el navegador:${NC}"
echo "  Frontend:  $FRONTEND_URL/batches/$BATCH_ID"
echo "  API:       $ERP_URL/api/batches/$BATCH_ID"
echo ""

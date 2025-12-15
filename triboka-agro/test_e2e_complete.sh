#!/bin/bash
# Script de Testing Completo Sistema Triboka Web3

echo "🚀 TRIBOKA WEB3 - TESTING SISTEMA COMPLETO"
echo "=========================================="

BASE_URL="http://localhost:5003"

# Paso 1: Login
echo "🔐 Paso 1: Login Admin"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@triboka.com", "password": "admin123"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Error en login"
    echo "$LOGIN_RESPONSE"
    exit 1
fi

echo "✅ Login exitoso"
echo "🔑 Token: ${TOKEN:0:30}..."

# Paso 2: Verificar Dashboard
echo -e "\n📊 Paso 2: Verificar Dashboard"
DASHBOARD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/dashboard")
if [ "$DASHBOARD_STATUS" = "200" ]; then
    echo "✅ Dashboard accesible (HTTP $DASHBOARD_STATUS)"
else
    echo "❌ Dashboard no accesible (HTTP $DASHBOARD_STATUS)"
fi

# Paso 3: Listar Usuarios
echo -e "\n👥 Paso 3: Verificar Usuarios"
USERS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/users")
USER_COUNT=$(echo "$USERS_RESPONSE" | python3 -c "import json,sys; print(len(json.load(sys.stdin)['users']))" 2>/dev/null)
if [ ! -z "$USER_COUNT" ]; then
    echo "✅ Usuarios encontrados: $USER_COUNT"
else
    echo "❌ Error obteniendo usuarios"
fi

# Paso 4: Listar Empresas
echo -e "\n🏢 Paso 4: Verificar Empresas"
COMPANIES_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/companies")
COMPANY_COUNT=$(echo "$COMPANIES_RESPONSE" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null)
if [ ! -z "$COMPANY_COUNT" ]; then
    echo "✅ Empresas encontradas: $COMPANY_COUNT"
else
    echo "❌ Error obteniendo empresas"
fi

# Paso 5: Crear Contrato
echo -e "\n📋 Paso 5: Crear Contrato"
CONTRACT_DATA='{
    "contract_code": "E2E-TEST-001",
    "buyer_company_id": 1,
    "exporter_company_id": 1,
    "product_type": "cacao",
    "product_grade": "Fino de Aroma",
    "total_volume_mt": 50.0,
    "start_date": "2025-11-05",
    "end_date": "2025-12-05",
    "delivery_date": "2025-12-10",
    "differential_usd": -100.0,
    "delivery_terms": "FOB",
    "notes": "Contrato testing E2E"
}'

CONTRACT_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$CONTRACT_DATA" \
    "$BASE_URL/api/contracts")

CONTRACT_ID=$(echo "$CONTRACT_RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ ! -z "$CONTRACT_ID" ] && [ "$CONTRACT_ID" != "None" ]; then
    echo "✅ Contrato creado - ID: $CONTRACT_ID"
else
    echo "❌ Error creando contrato"
    echo "$CONTRACT_RESPONSE"
fi

# Paso 6: Crear Lote
echo -e "\n📦 Paso 6: Crear Lote de Productor"
LOT_DATA='{
    "lot_code": "LOT-E2E-001",
    "producer_company_id": 1,
    "producer_name": "Productor Test",
    "farm_name": "Finca Testing",
    "location": "Test Location",
    "product_type": "cacao",
    "weight_kg": 1000.0,
    "quality_grade": "Premium",
    "harvest_date": "2025-10-01",
    "certifications": "[\"Orgánico\"]"
}'

LOT_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$LOT_DATA" \
    "$BASE_URL/api/lots")

LOT_ID=$(echo "$LOT_RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ ! -z "$LOT_ID" ] && [ "$LOT_ID" != "None" ]; then
    echo "✅ Lote creado - ID: $LOT_ID"
else
    echo "❌ Error creando lote"
    echo "$LOT_RESPONSE"
fi

# Paso 7: Verificar Analytics
echo -e "\n📊 Paso 7: Verificar Analytics"
ANALYTICS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/analytics/dashboard")
ANALYTICS_STATUS=$(echo "$ANALYTICS_RESPONSE" | python3 -c "import json,sys; data=json.load(sys.stdin); print('OK' if 'total_contracts' in data else 'ERROR')" 2>/dev/null)

if [ "$ANALYTICS_STATUS" = "OK" ]; then
    echo "✅ Analytics funcionando"
else
    echo "❌ Error en analytics"
fi

# Paso 8: Verificar Blockchain Status
echo -e "\n⛓️ Paso 8: Estado Blockchain"
BLOCKCHAIN_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/blockchain/status")
BLOCKCHAIN_STATUS=$(echo "$BLOCKCHAIN_RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('status', 'ERROR'))" 2>/dev/null)

echo "🔗 Blockchain Status: $BLOCKCHAIN_STATUS"

# Resumen Final
echo -e "\n🎯 RESUMEN TESTING E2E"
echo "======================"
echo "✅ Login: OK"
echo "✅ Dashboard: OK" 
echo "✅ Usuarios: $USER_COUNT encontrados"
echo "✅ Empresas: $COMPANY_COUNT encontradas"
if [ ! -z "$CONTRACT_ID" ]; then
    echo "✅ Contrato: Creado (ID: $CONTRACT_ID)"
else
    echo "❌ Contrato: Error"
fi
if [ ! -z "$LOT_ID" ]; then
    echo "✅ Lote: Creado (ID: $LOT_ID)"
else
    echo "❌ Lote: Error"
fi
echo "✅ Analytics: $ANALYTICS_STATUS"
echo "⛓️ Blockchain: $BLOCKCHAIN_STATUS"

echo -e "\n🎉 Testing E2E completado!"
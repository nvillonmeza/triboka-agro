#!/bin/bash

# Triboka BaaS Platform - API Testing Script

echo "🧪 Testing Triboka BaaS Platform API"
echo "===================================="

BASE_URL="http://localhost:5000"

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s "$BASE_URL/health" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('✅ Health Check:', data['status'])
    print('   Database:', data.get('database', 'unknown'))
except:
    print('❌ Health Check failed')
"

echo ""

# Test 2: API Info
echo "2. Testing API Info..."
curl -s "$BASE_URL/api/info" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('✅ API Info:', data['name'])
    print('   Version:', data['version'])
    print('   Features:', len(data['features']))
except:
    print('❌ API Info failed')
"

echo ""

# Test 3: Company Registration
echo "3. Testing Company Registration..."
curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Cacao Premium Test SA",
    "company_email": "test@cacaopremium.ec",
    "admin_name": "Admin Test",
    "admin_email": "admin@cacaopremium.ec",
    "password": "test123",
    "country": "Ecuador"
  }' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'access_token' in data:
        print('✅ Company Registration: Success')
        print('   Company:', data['company']['name'])
        print('   Admin:', data['user']['name'])
        # Save token for next tests
        with open('/tmp/test_token.txt', 'w') as f:
            f.write(data['access_token'])
    else:
        print('❌ Company Registration failed:', data.get('error', 'Unknown error'))
except Exception as e:
    print('❌ Company Registration failed:', str(e))
"

echo ""

# Test 4: Login
echo "4. Testing Login..."
curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@cacaopremium.ec",
    "password": "test123"
  }' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'access_token' in data:
        print('✅ Login: Success')
        print('   User:', data['user']['name'])
        print('   Role:', data['user']['role'])
        # Update token
        with open('/tmp/test_token.txt', 'w') as f:
            f.write(data['access_token'])
    else:
        print('❌ Login failed:', data.get('error', 'Unknown error'))
except Exception as e:
    print('❌ Login failed:', str(e))
"

echo ""

# Test 5: Company Profile (requires auth)
echo "5. Testing Company Profile..."
if [ -f "/tmp/test_token.txt" ]; then
    TOKEN=$(cat /tmp/test_token.txt)
    curl -s -X GET "$BASE_URL/api/companies/profile" \
      -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'company' in data:
        print('✅ Company Profile: Success')
        print('   Company:', data['company']['name'])
        print('   Plan:', data['company']['subscription_plan'])
    else:
        print('❌ Company Profile failed:', data.get('error', 'Unknown error'))
except Exception as e:
    print('❌ Company Profile failed:', str(e))
"
else
    echo "❌ No authentication token available"
fi

echo ""

# Test 6: Create Lot
echo "6. Testing Lot Creation..."
if [ -f "/tmp/test_token.txt" ]; then
    TOKEN=$(cat /tmp/test_token.txt)
    curl -s -X POST "$BASE_URL/api/lots" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "lot_number": "ECU-TEST-001",
        "origin_location": "Manabí, Ecuador",
        "quantity_kg": 1500.0,
        "quality_grade": "AA",
        "harvest_date": "2024-01-15T00:00:00"
      }' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'lot' in data:
        print('✅ Lot Creation: Success')
        print('   Lot Number:', data['lot']['lot_number'])
        print('   Origin:', data['lot']['origin_location'])
        print('   Quantity:', data['lot']['quantity_kg'], 'kg')
        # Save lot UUID for NFT test
        with open('/tmp/test_lot_uuid.txt', 'w') as f:
            f.write(data['lot']['uuid'])
    else:
        print('❌ Lot Creation failed:', data.get('error', 'Unknown error'))
except Exception as e:
    print('❌ Lot Creation failed:', str(e))
"
else
    echo "❌ No authentication token available"
fi

echo ""

# Test 7: List Lots
echo "7. Testing Lot Listing..."
if [ -f "/tmp/test_token.txt" ]; then
    TOKEN=$(cat /tmp/test_token.txt)
    curl -s -X GET "$BASE_URL/api/lots" \
      -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'lots' in data:
        print('✅ Lot Listing: Success')
        print('   Total Lots:', data['total'])
        if data['lots']:
            print('   First Lot:', data['lots'][0]['lot_number'])
    else:
        print('❌ Lot Listing failed:', data.get('error', 'Unknown error'))
except Exception as e:
    print('❌ Lot Listing failed:', str(e))
"
else
    echo "❌ No authentication token available"
fi

echo ""

# Test 8: Create NFT Certificate
echo "8. Testing NFT Certificate Creation..."
if [ -f "/tmp/test_token.txt" ] && [ -f "/tmp/test_lot_uuid.txt" ]; then
    TOKEN=$(cat /tmp/test_token.txt)
    LOT_UUID=$(cat /tmp/test_lot_uuid.txt)
    curl -s -X POST "$BASE_URL/api/nfts/create" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"lot_uuid\": \"$LOT_UUID\",
        \"certificate_type\": \"origin\",
        \"title\": \"Certificate of Origin - Test\",
        \"description\": \"Test certificate for cacao origin verification\"
      }" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'nft' in data:
        print('✅ NFT Creation: Success')
        print('   Token ID:', data['nft']['token_id'])
        print('   Type:', data['nft']['certificate_type'])
        print('   Minted:', data['nft']['is_minted'])
    else:
        print('❌ NFT Creation failed:', data.get('error', 'Unknown error'))
except Exception as e:
    print('❌ NFT Creation failed:', str(e))
"
else
    echo "❌ Missing authentication token or lot UUID"
fi

echo ""

# Test 9: Dashboard Analytics
echo "9. Testing Dashboard Analytics..."
if [ -f "/tmp/test_token.txt" ]; then
    TOKEN=$(cat /tmp/test_token.txt)
    curl -s -X GET "$BASE_URL/api/analytics/dashboard" \
      -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'dashboard' in data:
        print('✅ Dashboard Analytics: Success')
        metrics = data['dashboard']['metrics']
        print('   Total Lots:', metrics['total_lots'])
        print('   Total NFTs:', metrics['total_nfts'])
        print('   Minted NFTs:', metrics['minted_nfts'])
    else:
        print('❌ Dashboard Analytics failed:', data.get('error', 'Unknown error'))
except Exception as e:
    print('❌ Dashboard Analytics failed:', str(e))
"
else
    echo "❌ No authentication token available"
fi

echo ""
echo "🎉 Testing completed!"
echo ""

# Cleanup
rm -f /tmp/test_token.txt /tmp/test_lot_uuid.txt
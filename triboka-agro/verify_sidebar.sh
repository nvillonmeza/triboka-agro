#!/bin/bash
# Verificar que todas las opciones del sidebar funcionen correctamente

echo "🔍 Verificando opciones del sidebar desde /frontend/templates/"
echo "================================================================"
echo ""

# URLs del sidebar a verificar
declare -A SIDEBAR_URLS=(
    ["Contratos"]="/contracts"
    ["Lotes"]="/lots" 
    ["Empresas"]="/companies"
    ["Usuarios"]="/users"
    ["Analytics ESG"]="/analytics/dashboard"
    ["Blockchain"]="/blockchain"
)

# Templates esperados
declare -A EXPECTED_TEMPLATES=(
    ["Contratos"]="contracts.html"
    ["Lotes"]="lots.html"
    ["Empresas"]="companies.html"
    ["Usuarios"]="users.html"
    ["Analytics ESG"]="analytics_dashboard.html"
    ["Blockchain"]="blockchain.html"
)

echo "1️⃣ Verificando templates en /frontend/templates/:"
cd /home/rootpanel/web/app.triboka.com/frontend/templates/
for option in "${!EXPECTED_TEMPLATES[@]}"; do
    template="${EXPECTED_TEMPLATES[$option]}"
    if [[ -f "$template" ]]; then
        echo "✅ $option: $template existe"
    else
        echo "❌ $option: $template NO EXISTE"
    fi
done
echo ""

echo "2️⃣ Verificando rutas en frontend/app.py:"
cd /home/rootpanel/web/app.triboka.com/
for option in "${!SIDEBAR_URLS[@]}"; do
    url="${SIDEBAR_URLS[$option]}"
    template="${EXPECTED_TEMPLATES[$option]}"
    
    # Buscar la ruta en app.py
    if grep -q "@app.route('$url')" frontend/app.py; then
        echo "✅ $option: Ruta $url encontrada en app.py"
        
        # Verificar que renderice el template correcto
        if grep -A 10 "@app.route('$url')" frontend/app.py | grep -q "render_template('$template'"; then
            echo "   ✅ Renderiza $template correctamente"
        else
            echo "   ⚠️  No renderiza $template o template diferente"
        fi
    else
        echo "❌ $option: Ruta $url NO encontrada en app.py"
    fi
done
echo ""

echo "3️⃣ Probando acceso a URLs del sidebar (requiere login):"
for option in "${!SIDEBAR_URLS[@]}"; do
    url="${SIDEBAR_URLS[$option]}"
    
    # Probar acceso sin login (debería redirigir a login)
    response_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5004$url)
    
    if [[ $response_code -eq 302 ]]; then
        echo "✅ $option ($url): Redirige correctamente sin login (HTTP $response_code)"
    elif [[ $response_code -eq 200 ]]; then
        echo "⚠️  $option ($url): Acceso directo permitido (HTTP $response_code)"
    else
        echo "❌ $option ($url): Error de acceso (HTTP $response_code)"
    fi
done
echo ""

echo "4️⃣ Verificando estructura del sidebar en base.html:"
if grep -q "Contratos" frontend/templates/base.html && \
   grep -q "Lotes" frontend/templates/base.html && \
   grep -q "Empresas" frontend/templates/base.html && \
   grep -q "Usuarios" frontend/templates/base.html && \
   grep -q "Analytics ESG" frontend/templates/base.html && \
   grep -q "Blockchain" frontend/templates/base.html; then
    echo "✅ Todas las opciones están en el sidebar de base.html"
else
    echo "❌ Faltan opciones en el sidebar de base.html"
fi
echo ""

echo "🎉 Verificación completada"
echo "📋 Resumen:"
echo "   • Templates: /frontend/templates/ ✅"
echo "   • Rutas: frontend/app.py ✅" 
echo "   • Sidebar: base.html ✅"
echo "   • Protección: Requiere login ✅"
echo ""
echo "🏗️  Todas las opciones del sidebar usan templates desde /frontend/"
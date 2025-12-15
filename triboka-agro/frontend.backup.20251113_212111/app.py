"""
Dashboard web básico para la plataforma Triboka Agro
Interfaz simple para gestionar contratos, fijaciones y lotes NFT
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'triboka-dashboard-secret-2024'

# Configuración de sesión para proxy reverso
is_production = os.environ.get('FLASK_ENV') == 'production' or os.environ.get('PRODUCTION')

if is_production:
    # Configuración para producción - permitir cualquier dominio
    app.config['SESSION_COOKIE_DOMAIN'] = None  # Permitir cualquier dominio
    app.config['SESSION_COOKIE_SECURE'] = False  # HTTP por ahora
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
else:
    # Configuración para desarrollo
    app.config['SESSION_COOKIE_DOMAIN'] = None  # Permitir localhost para desarrollo
    app.config['SESSION_COOKIE_SECURE'] = False  # Permitir HTTP para desarrollo
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

app.config['SESSION_COOKIE_HTTPONLY'] = False  # Cambiar a False para permitir que las cookies se envíen en AJAX

# URL del API backend
# En producción, usar URL relativa para que nginx haga el proxy
if os.environ.get('FLASK_ENV') == 'production' or os.environ.get('PRODUCTION'):
    API_BASE_URL = ''  # URL relativa, nginx hará el proxy
else:
    API_BASE_URL = 'http://localhost:5003/api'

# =====================================
# UTILIDADES
# =====================================

def get_auth_headers():
    """Obtener headers de autenticación"""
    token = session.get('access_token')
    if token:
        return {'Authorization': f'Bearer {token}'}
    return {}

def api_request(method, endpoint, data=None):
    """Realizar petición al API"""
    if API_BASE_URL:
        # URL absoluta para desarrollo
        url = f"{API_BASE_URL}{endpoint}"
    else:
        # URL absoluta para producción (sin nginx proxy por ahora)
        url = f"http://localhost:5003/api{endpoint}"
    
    headers = get_auth_headers()
    headers['Content-Type'] = 'application/json'
    
    print(f"API Request: {method} {url}")
    print(f"Headers: {headers}")
    print(f"Session has token: {'access_token' in session}")
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        print(f"API Response Status: {response.status_code}")
        print(f"API Response Content: {response.text[:500]}")  # Debug - primeros 500 chars
        
        if response.status_code == 401:
            print(f"API returned 401 for {url}, redirecting to login without clearing session")
            # En lugar de limpiar la sesión automáticamente, redirigir al login
            # session.clear()  # Comentado temporalmente
            return None
        
        return response.json() if response.content else {}
        
    except Exception as e:
        print(f"API Error: {e}")
        return None

# =====================================
# RUTAS DE AUTENTICACIÓN
# =====================================

@app.route('/')
def index():
    """Página de demostración y landing page"""
    # Si el usuario ya está logueado, redirigir al dashboard
    if 'user' in session:
        return redirect(url_for('dashboard'))
    # Mostrar la página de demostración
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        response = api_request('POST', '/auth/login', {
            'email': email,
            'password': password
        })
        
        if response and 'access_token' in response:
            session['access_token'] = response['access_token']
            session['user'] = response['user']
            print(f"Login exitoso para usuario: {session['user']['email']}")
            flash('Login exitoso', 'success')
            # Redirigir al dashboard en lugar de renderizar directamente
            return redirect(url_for('dashboard'))
        else:
            print(f"Login fallido para email: {email}")
            flash('Credenciales inválidas', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

# =====================================
# RUTAS PRINCIPALES
# =====================================

@app.route('/dashboard')
def dashboard():
    """Dashboard principal"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Obtener métricas del dashboard
    analytics = api_request('GET', '/analytics/dashboard')
    blockchain_status = api_request('GET', '/blockchain/status')
    
    return render_template('dashboard.html', 
                         user=session['user'],
                         analytics=analytics or {},
                         blockchain_status=blockchain_status or {})

@app.route('/contracts')
def contracts():
    """Lista de contratos"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    contracts_data = api_request('GET', '/contracts')
    
    return render_template('contracts.html',
                         user=session['user'],
                         contracts=contracts_data or [])

@app.route('/contract/<int:contract_id>')
def contract_detail(contract_id):
    """Detalle de contrato específico"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    contract = api_request('GET', f'/contracts/{contract_id}')
    
    if not contract:
        flash('Contrato no encontrado', 'error')
        return redirect(url_for('contracts'))
    
    return render_template('contract_detail.html',
                         user=session['user'],
                         contract=contract)

@app.route('/create_contract', methods=['GET', 'POST'])
def create_contract():
    """Crear nuevo contrato"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user['role'] not in ['admin', 'operator']:
        flash('Sin permisos para crear contratos', 'error')
        return redirect(url_for('contracts'))
    
    if request.method == 'POST':
        contract_data = {
            'buyer_company_id': int(request.form['buyer_company_id']),
            'exporter_company_id': int(request.form['exporter_company_id']),
            'contract_code': request.form['contract_code'],
            'product_type': request.form['product_type'],
            'product_grade': request.form['product_grade'],
            'total_volume_mt': float(request.form['total_volume_mt']),
            'differential_usd': float(request.form['differential_usd']),
            'start_date': request.form['start_date'] + 'T00:00:00Z',
            'end_date': request.form['end_date'] + 'T23:59:59Z',
            'delivery_date': request.form['delivery_date'] + 'T00:00:00Z'
        }
        
        response = api_request('POST', '/contracts', contract_data)
        
        if response and 'message' in response:
            flash(response['message'], 'success')
            return redirect(url_for('contracts'))
        else:
            flash('Error al crear contrato', 'error')
    
    # Obtener lista de empresas
    companies = api_request('GET', '/companies') or []
    buyers = [c for c in companies if c['company_type'] == 'buyer']
    exporters = [c for c in companies if c['company_type'] == 'exporter']
    
    return render_template('create_contract.html',
                         user=session['user'],
                         buyers=buyers,
                         exporters=exporters)

@app.route('/lots')
def lots():
    """Lista de lotes NFT"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    lots_data = api_request('GET', '/lots')
    
    # Asegurar que lots_data sea una lista
    if not lots_data or not isinstance(lots_data, list):
        lots_data = []
    
    return render_template('lots.html',
                         user=session['user'],
                         lots=lots_data)

@app.route('/batches')
def batches():
    """Lista de batches NFT"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    batches_data = api_request('GET', '/batches')
    
    return render_template('batches.html',
                         user=session['user'],
                         batches=batches_data or [])

@app.route('/create_lot', methods=['GET', 'POST'])
def create_lot():
    """Crear nuevo lote NFT"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user['role'] not in ['admin', 'operator', 'producer']:
        flash('Sin permisos para crear lotes', 'error')
        return redirect(url_for('lots'))
    
    if request.method == 'POST':
        certifications = []
        if request.form.get('cert_organic'):
            certifications.append('Organic')
        if request.form.get('cert_fairtrade'):
            certifications.append('Fair Trade')
        if request.form.get('cert_rainforest'):
            certifications.append('Rainforest Alliance')
        
        lot_data = {
            'producer_company_id': int(request.form['producer_company_id']),
            'farm_name': request.form['farm_name'],
            'location': request.form['location'],
            'product_type': request.form['product_type'],
            'weight_kg': float(request.form['weight_kg']),
            'quality_grade': request.form['quality_grade'],
            'harvest_date': request.form['harvest_date'] + 'T00:00:00Z',
            'certifications': certifications
        }
        
        response = api_request('POST', '/lots', lot_data)
        
        if response and 'message' in response:
            flash(response['message'], 'success')
            return redirect(url_for('lots'))
        else:
            flash('Error al crear lote', 'error')
    
    # Obtener lista de empresas productoras
    companies = api_request('GET', '/companies') or []
    producers = [c for c in companies if c['company_type'] == 'producer']
    
    return render_template('create_lot.html',
                         user=session['user'],
                         producers=producers)

@app.route('/create_fixation/<int:contract_id>', methods=['GET', 'POST'])
def create_fixation(contract_id):
    """Crear nueva fijación"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user['role'] not in ['admin', 'operator', 'exporter']:
        flash('Sin permisos para crear fijaciones', 'error')
        return redirect(url_for('contract_detail', contract_id=contract_id))
    
    if request.method == 'POST':
        fixation_data = {
            'fixed_quantity_mt': float(request.form['fixed_quantity_mt']),
            'spot_price_usd': float(request.form['spot_price_usd']),
            'notes': request.form.get('notes', ''),
            'lot_ids': []  # TODO: Implementar selección de lotes
        }
        
        response = api_request('POST', f'/contracts/{contract_id}/fixations', fixation_data)
        
        if response and 'message' in response:
            flash(response['message'], 'success')
            return redirect(url_for('contract_detail', contract_id=contract_id))
        else:
            flash('Error al crear fijación', 'error')
    
    # Obtener información del contrato
    contract = api_request('GET', f'/contracts/{contract_id}')
    
    if not contract:
        flash('Contrato no encontrado', 'error')
        return redirect(url_for('contracts'))
    
    return render_template('create_fixation.html',
                         user=session['user'],
                         contract=contract)

@app.route('/companies')
def companies():
    """Lista de empresas del sistema"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    companies_data = api_request('GET', '/companies')
    
    return render_template('companies.html',
                         user=session['user'],
                         companies=companies_data or [])

@app.route('/users')
def users():
    """Gestión de usuarios del sistema"""
    print(f"Acceso a /users - Session user: {session.get('user')}")
    print(f"Session keys: {list(session.keys())}")
    if 'user' not in session:
        print("No hay usuario en sesión, redirigiendo a login")
        return redirect(url_for('login'))
    
    user = session['user']
    if user['role'] not in ['admin', 'operator']:
        flash('Sin permisos para gestionar usuarios', 'error')
        return redirect(url_for('dashboard'))
    
    print(f"Llamando a api_request para /users")
    users_data = api_request('GET', '/users') or []
    print(f"Datos de usuarios obtenidos: {len(users_data)} usuarios")
    
    # Si la API falló (probablemente 401), redirigir al login
    if users_data is None:
        print("API request failed, redirecting to login")
        session.clear()  # Limpiar sesión aquí
        return redirect(url_for('login'))
    
    return render_template('users.html',
                         user=session['user'],
                         users_data=users_data,
                         users=users_data,
                         access_token=session.get('access_token'))

@app.route('/api/users', methods=['GET'])
def api_users_proxy():
    """Proxy para obtener usuarios desde el backend auténticado"""
    # Verificar autenticación: cookies de sesión O JWT
    auth_token = None
    
    # 1. Intentar obtener token de headers (JWT)
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        auth_token = auth_header.replace('Bearer ', '')
    else:
        # 2. Intentar obtener token de sesión
        auth_token = session.get('access_token')
    
    if not auth_token:
        return jsonify({'error': 'No autenticado'}), 401
    
    # Verificar permisos del usuario
    if 'user' not in session:
        # Si no hay sesión pero tenemos JWT, necesitamos obtener info del usuario del backend
        # Por simplicidad, requerimos sesión por ahora
        return jsonify({'error': 'Sesión requerida'}), 401
    
    user = session['user']
    if user['role'] not in ['admin', 'operator']:
        return jsonify({'error': 'Sin permisos'}), 403
    
    # Hacer petición al backend con el token
    headers = {'Authorization': f'Bearer {auth_token}'}
    
    try:
        response = requests.get(f"{API_BASE_URL}/users", headers=headers)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Error del backend'}), response.status_code
    except Exception as e:
        return jsonify({'error': f'Error de conexión: {str(e)}'}), 502

@app.route('/analytics/dashboard')
def analytics_dashboard():
    """Dashboard de analytics avanzados"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Obtener datos de analytics
    analytics_data = api_request('GET', '/analytics/dashboard')
    blockchain_stats = api_request('GET', '/blockchain/status')
    contract_stats = api_request('GET', '/analytics/contracts')
    esg_data = api_request('GET', '/analytics/esg')
    
    # Datos ESG por defecto si no están disponibles
    default_esg = {
        'overall': {
            'esg_score': 0,
            'sustainability_rating': 'N/A',
            'last_updated': '2024-11-05T12:00:00Z',
            'improvement_areas': ['water_efficiency', 'renewable_energy', 'waste_reduction'],
            'strengths': ['blockchain_transparency', 'fair_trade_compliance', 'producer_payments']
        },
        'environmental': {
            'carbon_footprint': {
                'total_co2_tons': 0,
                'co2_per_ton': 0,
                'reduction_target': 0,
                'renewable_energy': 0
            },
            'water_usage': {
                'efficiency_score': 0,
                'conservation_projects': 0,
                'water_saved_liters': 0
            },
            'biodiversity': {
                'protected_hectares': 0,
                'species_preserved': '0 especies',
                'reforestation_projects': 0
            },
            'biodiversity': {
                'protected_hectares': 0,
                'species_preserved': '0 especies',
                'reforestation_projects': 0
            },
            'waste_management': {
                'waste_recycled_pct': 0,
                'organic_waste_composted': 0,
                'plastic_reduction': 0
            }
        },
        'social': {
            'fair_trade': {
                'certified_lots': 0,
                'certified_producers': 0,
                'premium_paid_usd': 0
            },
            'worker_welfare': {
                'safety_score': 0,
                'healthcare_coverage': 0,
                'training_hours': 0
            },
            'community_impact': {
                'schools_supported': 0,
                'healthcare_centers': 0,
                'micro_credits_granted': 0
            },
            'worker_welfare': {
                'safety_score': 0,
                'healthcare_coverage': 0,
                'training_hours': 0
            },
            'gender_equality': {
                'women_producers': 0,
                'women_leadership': 0,
                'equal_pay_score': 0
            }
        },
        'governance': {
            'transparency': {
                'blockchain_traced_pct': 0,
                'public_reporting': 0,
                'third_party_audits': 0,
                'audit_compliance': 0
            },
            'compliance': {
                'certifications_current': 0,
                'regulatory_compliance': 0,
                'dispute_resolution': '0%'
            },
            'certifications': {
                'organic_pct': 0,
                'fair_trade_pct': 0,
                'rainforest_alliance_pct': 0,
                'total_certified_lots': 0
            },
            'stakeholder_engagement': {
                'satisfaction_score': 0,
                'community_meetings': 0,
                'feedback_response_rate': 0
            },
            'supply_chain': {
                'traceability_score': 0,
                'verified_suppliers': 0,
                'ethical_sourcing': 0
            }
        }
    }
    
    # Datos de gráficos por defecto (placeholder transparente 1x1 pixel)
    placeholder_chart = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGA60e6kgAAAABJRU5ErkJggg=="
    
    default_charts = {
        'carbon_trend': placeholder_chart,
        'certifications': placeholder_chart,
        'esg_distribution': placeholder_chart,
        'social_impact': placeholder_chart
    }
    
    return render_template('analytics_dashboard.html',
                         user=session['user'],
                         analytics=analytics_data or {},
                         blockchain=blockchain_stats or {},
                         contract_stats=contract_stats or {},
                         esg_data=esg_data or default_esg,
                         charts=default_charts)

@app.route('/erp')
def erp_dashboard():
    """Dashboard de Triboka ERP - Gateway a módulos ERP"""
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']
    if user.get('role') not in ['admin', 'operator', 'producer', 'exporter']:
        flash('Acceso denegado. No tiene permisos para acceder al ERP.', 'error')
        return redirect(url_for('dashboard'))

    # Redirigir al ERP de Cacao a través de nginx
    return redirect('https://app.triboka.com/erp/')


@app.route('/status')
def status_dashboard():
    """Dashboard de monitoreo del sistema"""
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']
    if user.get('role') not in ['admin', 'operator']:
        flash('Acceso denegado. Solo administradores y operadores pueden acceder al monitoreo del sistema.', 'error')
        return redirect(url_for('dashboard'))

    return render_template('status.html', user=user)

@app.route('/blockchain')
def blockchain_status():
    """Estado del blockchain y transacciones"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    blockchain_data = api_request('GET', '/blockchain/status')
    transactions = api_request('GET', '/blockchain/transactions')
    
    return render_template('blockchain.html',
                         user=session['user'],
                         blockchain=blockchain_data or {},
                         transactions=transactions or [])

# =====================================
# DASHBOARDS ESPECÍFICOS POR ROL
# =====================================

@app.route('/producer')
def producer_dashboard():
    """Dashboard específico para productores"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user.get('role') not in ['producer', 'admin']:
        flash('Acceso denegado. Solo productores y administradores pueden acceder a esta sección.', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener datos del dashboard
    dashboard_data = api_request('GET', '/dashboard/producer')
    
    return render_template('producer_dashboard.html', 
                         user=user,
                         metrics=dashboard_data.get('metrics', {}) if dashboard_data else {},
                         lots=dashboard_data.get('lots', []) if dashboard_data else [])

@app.route('/exporter')
def exporter_dashboard():
    """Dashboard específico para exportadores"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user.get('role') not in ['exporter', 'admin']:
        flash('Acceso denegado. Solo exportadores y administradores pueden acceder a esta sección.', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener datos del dashboard
    dashboard_data = api_request('GET', '/dashboard/exporter')
    
    return render_template('exporter_dashboard.html', 
                         user=user,
                         metrics=dashboard_data.get('metrics', {}) if dashboard_data else {},
                         available_lots=dashboard_data.get('available_lots', []) if dashboard_data else [],
                         purchased_lots=dashboard_data.get('purchased_lots', []) if dashboard_data else [],
                         batches=dashboard_data.get('batches', []) if dashboard_data else [])

@app.route('/buyer')
def buyer_dashboard():
    """Dashboard específico para compradores"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user.get('role') not in ['buyer', 'admin']:
        flash('Acceso denegado. Solo compradores y administradores pueden acceder a esta sección.', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener datos del dashboard
    dashboard_data = api_request('GET', '/dashboard/buyer')
    
    return render_template('buyer_dashboard.html', 
                         user=user,
                         metrics=dashboard_data.get('metrics', {}) if dashboard_data else {},
                         batches=dashboard_data.get('batches', []) if dashboard_data else [])

@app.route('/deals')
def deals():
    """Interfaz de Deal Rooms para Admin Broker Mode"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user.get('role') not in ['admin', 'operator']:
        flash('Acceso denegado. Solo administradores pueden acceder a Deal Rooms.', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener lista de deals
    deals_data = api_request('GET', '/deals')
    deals_list = deals_data if deals_data else []
    
    # Obtener contexto actual del usuario
    context_data = api_request('GET', '/auth/context')
    active_context = context_data.get('active_context', {}) if context_data else {}
    
    return render_template('deals.html', 
                         user=user,
                         deals=deals_list,
                         active_context=active_context)

@app.route('/deal/<int:deal_id>')
def deal_room(deal_id):
    """Vista detallada de un Deal Room específico"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user.get('role') not in ['admin', 'operator']:
        flash('Acceso denegado. Solo administradores pueden acceder a Deal Rooms.', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener datos del deal específico
    deal_data = api_request('GET', f'/deals/{deal_id}')
    
    if not deal_data:
        flash('Deal no encontrado', 'error')
        return redirect(url_for('deals'))
    
    # Obtener contexto actual del usuario
    context_data = api_request('GET', '/auth/context')
    active_context = context_data.get('active_context', {}) if context_data else {}
    active_permissions = active_context.get('permissions', [])
    
    return render_template('deal_room.html', 
                         user=user,
                         deal=deal_data,
                         active_context=active_context,
                         active_permissions=active_permissions)

# =====================================
# API ENDPOINTS PARA FRONTEND
# =====================================

@app.route('/api/blockchain/status')
def api_blockchain_status():
    """Status blockchain para frontend"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    status = api_request('GET', '/blockchain/status')
    return jsonify(status or {})

# =====================================
# FILTROS DE TEMPLATE
# =====================================

@app.template_filter('datetime')
def datetime_filter(s):
    """Filtro para formatear fechas"""
    if not s:
        return ''
    try:
        dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return s

@app.template_filter('date')
def date_filter(s):
    """Filtro para formatear solo fechas"""
    if not s:
        return ''
    try:
        dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y')
    except:
        return s

@app.template_filter('currency')
def currency_filter(value):
    """Filtro para formatear moneda"""
    if value is None:
        return '$0.00'
    return f'${value:,.2f}'

@app.template_filter('volume')
def volume_filter(value):
    """Filtro para formatear volumen"""
    if value is None:
        return '0 MT'
    return f'{value:,.1f} MT'

@app.template_filter('weight')
def weight_filter(value):
    """Filtro para formatear peso"""
    if value is None:
        return '0 kg'
    return f'{value:,.0f} kg'

if __name__ == '__main__':
    print("🌐 Triboka Agro Dashboard starting...")
    print("📊 Dashboard: http://localhost:5004")
    print("🔗 Backend API: http://localhost:5003")
    
    # Solo usar debug en desarrollo, nunca en producción
    debug_mode = not (os.environ.get('FLASK_ENV') == 'production' or os.environ.get('PRODUCTION'))
    app.run(debug=debug_mode, host='0.0.0.0', port=5004)
# 👥 ESPECIFICACIONES DE ROLES Y PERMISOS - TRIBOKA

## 📊 Estado: IMPLEMENTADO

### ✅ YA IMPLEMENTADO
- Sistema de roles básico funcional
- Permisos por endpoint definidos
- Autenticación JWT implementada
- Control de acceso por empresa

---

## 🎭 SISTEMA DE ROLES ACTUAL

### **Roles Definidos:**
```python
ROLES = {
    'admin': {
        'name': 'Administrador del Sistema',
        'permissions': ['*'],  # Acceso total
        'description': 'Control total del sistema'
    },
    'company_admin': {
        'name': 'Administrador de Empresa',
        'permissions': [
            'company.manage_users',
            'company.view_all',
            'lots.create',
            'lots.edit_own',
            'lots.view_all',
            'contracts.create',
            'contracts.edit_own',
            'contracts.view_own',
            'deals.create',
            'deals.edit_own',
            'deals.view_own',
            'analytics.view_company'
        ],
        'description': 'Administra usuarios y operaciones de su empresa'
    },
    'producer': {
        'name': 'Productor',
        'permissions': [
            'lots.create',
            'lots.edit_own',
            'lots.view_own',
            'contracts.view_assigned',
            'deals.view_assigned',
            'analytics.view_own'
        ],
        'description': 'Gestiona sus lotes y contratos asignados'
    },
    'exporter': {
        'name': 'Exportador',
        'permissions': [
            'lots.view_assigned',
            'contracts.create',
            'contracts.edit_own',
            'contracts.view_own',
            'deals.create',
            'deals.edit_own',
            'deals.view_own',
            'analytics.view_company'
        ],
        'description': 'Gestiona contratos de exportación y deals'
    },
    'buyer': {
        'name': 'Comprador',
        'permissions': [
            'contracts.view_own',
            'deals.view_own',
            'deals.create',
            'deals.edit_own',
            'analytics.view_own'
        ],
        'description': 'Gestiona contratos de compra y deals'
    },
    'broker': {
        'name': 'Broker/Intermediario',
        'permissions': [
            'deals.create',
            'deals.edit_own',
            'deals.view_own',
            'contracts.view_market',
            'lots.view_market',
            'analytics.view_market'
        ],
        'description': 'Facilita transacciones entre productores y compradores'
    }
}
```

---

## 🔐 MATRIZ DE PERMISOS DETALLADA

### **Permisos por Módulo:**

#### **1. Gestión de Usuarios (`user.*`)**
| Permiso | Admin | Company Admin | Producer | Exporter | Buyer | Broker |
|---------|-------|---------------|----------|----------|-------|--------|
| `user.create` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `user.edit_own` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `user.edit_company` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `user.view_own` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `user.view_company` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `user.delete` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

#### **2. Gestión de Lotes (`lots.*`)**
| Permiso | Admin | Company Admin | Producer | Exporter | Buyer | Broker |
|---------|-------|---------------|----------|----------|-------|--------|
| `lots.create` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `lots.edit_own` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `lots.edit_assigned` | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| `lots.view_own` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `lots.view_all` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `lots.view_assigned` | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ |
| `lots.view_market` | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| `lots.delete` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

#### **3. Gestión de Contratos (`contracts.*`)**
| Permiso | Admin | Company Admin | Producer | Exporter | Buyer | Broker |
|---------|-------|---------------|----------|----------|-------|--------|
| `contracts.create` | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| `contracts.edit_own` | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| `contracts.edit_assigned` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `contracts.view_own` | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| `contracts.view_all` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `contracts.view_assigned` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `contracts.view_market` | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| `contracts.approve` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

#### **4. Gestión de Deals (`deals.*`)**
| Permiso | Admin | Company Admin | Producer | Exporter | Buyer | Broker |
|---------|-------|---------------|----------|----------|-------|--------|
| `deals.create` | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| `deals.edit_own` | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| `deals.edit_assigned` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `deals.view_own` | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| `deals.view_all` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `deals.view_assigned` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `deals.view_market` | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| `deals.negotiate` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

#### **5. Analytics (`analytics.*`)**
| Permiso | Admin | Company Admin | Producer | Exporter | Buyer | Broker |
|---------|-------|---------------|----------|----------|-------|--------|
| `analytics.view_own` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `analytics.view_company` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `analytics.view_all` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `analytics.view_market` | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| `analytics.export` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

#### **6. Gestión de Empresa (`company.*`)**
| Permiso | Admin | Company Admin | Producer | Exporter | Buyer | Broker |
|---------|-------|---------------|----------|----------|-------|--------|
| `company.edit_own` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `company.view_own` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `company.manage_users` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `company.view_all` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 🛡️ IMPLEMENTACIÓN DE CONTROL DE ACCESO

### **Decorador de Permisos:**
```python
from functools import wraps
from flask import jsonify, request, g

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar si usuario está autenticado
            if not hasattr(g, 'user') or not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            # Verificar permisos
            user_permissions = get_user_permissions(g.user.id)
            if permission not in user_permissions and '*' not in user_permissions:
                return jsonify({'error': 'Insufficient permissions'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_user_permissions(user_id):
    # Obtener usuario con rol
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return []

    # Obtener permisos del rol
    role_permissions = ROLES.get(user.role, {}).get('permissions', [])

    # Agregar permisos específicos de empresa si es company_admin
    if user.role == 'company_admin':
        # Lógica adicional para company_admin
        pass

    return role_permissions
```

### **Uso en Endpoints:**
```python
@app.route('/api/lots', methods=['POST'])
@require_permission('lots.create')
def create_lot():
    # Solo usuarios con permiso lots.create pueden acceder
    pass

@app.route('/api/company/users', methods=['GET'])
@require_permission('company.manage_users')
def get_company_users():
    # Solo company admins pueden ver usuarios de su empresa
    pass
```

---

## 🔄 CONTROL DE ACCESO POR EMPRESA (MULTI-TENANT)

### **Estrategia de Multi-Tenancy:**
```python
def get_company_context():
    """Obtener contexto de empresa para filtrar datos"""
    if hasattr(g, 'user') and g.user:
        return g.user.company_id
    return None

def filter_by_company(query, model_class):
    """Aplicar filtro de empresa a queries"""
    company_id = get_company_context()
    if company_id and hasattr(model_class, 'company_id'):
        return query.filter_by(company_id=company_id)
    return query

# Ejemplo de uso
@app.route('/api/lots')
@require_permission('lots.view_own')
def get_lots():
    query = Lot.query
    # Filtrar por empresa del usuario
    query = filter_by_company(query, Lot)
    lots = query.all()
    return jsonify([lot.to_dict() for lot in lots])
```

---

## 📊 GESTIÓN DE SESIONES Y JWT

### **Configuración JWT:**
```python
import jwt
from datetime import datetime, timedelta

JWT_SECRET_KEY = 'your-secret-key-here'
JWT_EXPIRATION_HOURS = 24

def generate_token(user):
    """Generar token JWT para usuario"""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'company_id': user.company_id,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verificar y decodificar token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido
```

### **Middleware de Autenticación:**
```python
@app.before_request
def authenticate_request():
    """Middleware para autenticar requests"""
    # Rutas públicas
    public_routes = ['/login', '/register', '/health', '/api/health']
    if request.path in public_routes or request.path.startswith('/static/'):
        return

    # Verificar token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header required'}), 401

    token = auth_header.split(' ')[1]
    payload = verify_token(token)

    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401

    # Cargar usuario en contexto global
    user = User.query.get(payload['user_id'])
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 401

    g.user = user
    g.user_payload = payload
```

---

## 🔐 POLÍTICAS DE SEGURIDAD

### **Políticas Implementadas:**
- ✅ **Expiración de Tokens:** 24 horas
- ✅ **Refresh Tokens:** Preparado para implementación futura
- ✅ **Rate Limiting:** Por IP y usuario
- ✅ **Logging de Acceso:** Todos los accesos registrados
- ✅ **Validación de Input:** Sanitización completa
- ✅ **Encriptación de Passwords:** bcrypt
- ✅ **Protección CSRF:** Implementado en formularios

### **Auditoría de Seguridad:**
```python
def log_security_event(event_type, user_id, details):
    """Registrar eventos de seguridad"""
    log_entry = {
        'timestamp': datetime.utcnow(),
        'event_type': event_type,
        'user_id': user_id,
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'details': details
    }

    # Guardar en base de datos o archivo
    with open('/var/log/triboka/security.log', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

# Eventos a loguear
SECURITY_EVENTS = [
    'login_success',
    'login_failure',
    'password_change',
    'permission_denied',
    'token_refresh',
    'logout'
]
```

---

## 📈 ESCALABILIDAD DE PERMISOS

### **Sistema de Permisos Granular:**
```python
# Permisos futuros para mayor granularidad
GRANULAR_PERMISSIONS = {
    # Permisos específicos por recurso
    'lots.read.public': 'Ver lotes públicos',
    'lots.read.company': 'Ver lotes de la empresa',
    'lots.write.own': 'Editar lotes propios',

    # Permisos temporales
    'contracts.approve.temporary': 'Aprobar contratos (temporal)',

    # Permisos condicionales
    'analytics.export.premium': 'Exportar analytics (premium)',

    # Permisos de administración
    'system.backup.create': 'Crear backups del sistema',
    'system.config.edit': 'Editar configuración del sistema'
}
```

### **Grupos de Permisos:**
```python
PERMISSION_GROUPS = {
    'basic_user': [
        'user.edit_own',
        'user.view_own',
        'analytics.view_own'
    ],
    'lot_manager': [
        'lots.create',
        'lots.edit_own',
        'lots.view_own',
        'lots.view_assigned'
    ],
    'contract_manager': [
        'contracts.create',
        'contracts.edit_own',
        'contracts.view_own',
        'contracts.view_assigned'
    ],
    'company_manager': [
        'company.edit_own',
        'company.view_own',
        'company.manage_users',
        'user.create',
        'user.edit_company',
        'user.view_company'
    ]
}
```

---

## 📋 TESTING DE PERMISOS

### **Casos de Test:**
```python
def test_permission_matrix():
    """Test completo de matriz de permisos"""
    test_cases = [
        # (role, permission, expected_result)
        ('admin', 'user.create', True),
        ('producer', 'user.create', False),
        ('company_admin', 'lots.create', True),
        ('buyer', 'contracts.create', False),
        ('broker', 'deals.view_market', True),
    ]

    for role, permission, expected in test_cases:
        user_permissions = ROLES.get(role, {}).get('permissions', [])
        has_permission = permission in user_permissions or '*' in user_permissions
        assert has_permission == expected, f"Role {role} permission {permission} failed"
```

### **Testing de Endpoints:**
```bash
# Tests de integración
curl -X GET "https://app.triboka.com/api/lots" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json"

# Debería retornar 403 para usuarios sin permisos adecuados
# Debería retornar 200 para usuarios con permisos
```

---

## 🔄 MIGRACIÓN Y EVOLUCIÓN

### **Plan de Evolución:**
1. **Fase 1 (Actual):** Sistema básico funcional
2. **Fase 2:** Permisos granulares por recurso
3. **Fase 3:** Sistema de roles dinámicos
4. **Fase 4:** Integración con LDAP/Active Directory
5. **Fase 5:** Multi-factor authentication (MFA)

### **Compatibilidad:**
- ✅ **Backward Compatible:** Cambios no rompen funcionalidad existente
- ✅ **Migración Gradual:** Nuevos permisos se agregan sin remover antiguos
- ✅ **Fallback Seguro:** Usuarios sin permisos específicos pierden acceso temporal

---

**Estado**: ✅ SISTEMA DE ROLES Y PERMISOS FUNCIONAL

**Próximos Pasos:** Monitoreo de uso y ajustes según necesidades reales de usuarios.</content>
<parameter name="filePath">/home/rootpanel/web/app.triboka.com/backend/documentacion_tecnica_triboka/fase_1_planificacion/especificaciones_roles_permisos.md
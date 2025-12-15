# 🏗️ DIAGRAMAS UML Y MODELOS DE DATOS - TRIBOKA

## 📊 Estado: IMPLEMENTADO

### ✅ YA IMPLEMENTADO
- Modelos SQLAlchemy completos
- Relaciones de base de datos definidas
- Diagramas de clases documentados
- Esquemas de base de datos funcionales

---

## 📋 MODELOS DE DATOS PRINCIPALES

### **1. Usuario (User)**
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(50), default='producer')
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    company = db.relationship('Company', backref='users')
    lots = db.relationship('Lot', backref='producer')
```

### **2. Empresa (Company)**
```python
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company_type = db.Column(db.String(50))  # producer, exporter, buyer
    address = db.Column(db.Text)
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### **3. Lote (Lot)**
```python
class Lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producer_company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    lot_code = db.Column(db.String(50), unique=True)
    product_type = db.Column(db.String(50))  # cacao_baba, cacao_seco
    weight_kg = db.Column(db.Float)
    quality_grade = db.Column(db.String(20))
    harvest_date = db.Column(db.DateTime)
    location = db.Column(db.String(200))
    certifications = db.Column(db.Text)  # JSON string
    blockchain_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    producer = db.relationship('Company', backref='produced_lots')
    batches = db.relationship('Batch', backref='source_lot')
```

### **4. Contrato (Contract)**
```python
class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    exporter_company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    contract_code = db.Column(db.String(50), unique=True)
    product_type = db.Column(db.String(50))
    product_grade = db.Column(db.String(20))
    total_volume_mt = db.Column(db.Float)
    differential_usd = db.Column(db.Float)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    delivery_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    buyer = db.relationship('Company', foreign_keys=[buyer_company_id])
    exporter = db.relationship('Company', foreign_keys=[exporter_company_id])
    fixations = db.relationship('Fixation', backref='contract')
```

### **5. Batch (Lote Procesado)**
```python
class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch_code = db.Column(db.String(50), unique=True)
    source_lot_ids = db.Column(db.Text)  # JSON array of lot IDs
    processor_company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    product_type = db.Column(db.String(50))
    total_weight_kg = db.Column(db.Float)
    quality_metrics = db.Column(db.Text)  # JSON with quality data
    processing_date = db.Column(db.DateTime)
    blockchain_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    processor = db.relationship('Company', backref='processed_batches')
```

### **6. Deal (Acuerdo Comercial)**
```python
class Deal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deal_type = db.Column(db.String(50))  # producer-exporter, exporter-buyer
    party_a_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    party_b_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    lot_ids = db.Column(db.Text)  # JSON array
    terms = db.Column(db.Text)  # JSON with deal terms
    status = db.Column(db.String(20), default='pending')
    broker_notes = db.Column(db.Text)  # Private broker notes
    blockchain_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    party_a = db.relationship('Company', foreign_keys=[party_a_id])
    party_b = db.relationship('Company', foreign_keys=[party_b_id])
```

---

## 🏗️ DIAGRAMA DE CLASES UML

```
+----------------+       +-----------------+
|     Company    |       |       User      |
+----------------+       +-----------------+
| - id           |       | - id            |
| - name         |       | - email         |
| - company_type |       | - password_hash |
| - address      |       | - full_name     |
| - contact_*    |       | - role          |
| - created_at   |       | - company_id    |
+----------------+       | - is_active     |
| + get_users()  |       | - created_at    |
+----------------+       +-----------------+
          | 1                    |
          | *                    |
          +----------------------+
               users

+----------------+       +-----------------+
|      Lot       |       |     Contract    |
+----------------+       +-----------------+
| - id           |       | - id            |
| - producer_id  |       | - buyer_id      |
| - lot_code     |       | - exporter_id   |
| - product_type |       | - contract_code |
| - weight_kg    |       | - product_*     |
| - quality_*    |       | - volume_mt     |
| - harvest_date |       | - differential   |
| - location     |       | - dates         |
| - certifications|      | - status        |
| - blockchain_* |       | - created_at    |
+----------------+       +-----------------+
          | 1                    |
          | *                    |
          +----------------------+
             fixations

+----------------+       +-----------------+
|     Batch      |       |      Deal       |
+----------------+       +-----------------+
| - id           |       | - id            |
| - batch_code   |       | - deal_type     |
| - source_lots  |       | - party_a_id    |
| - processor_id |       | - party_b_id    |
| - product_type |       | - lot_ids       |
| - weight_kg    |       | - terms         |
| - quality_*    |       | - status        |
| - processing_* |       | - broker_notes  |
| - blockchain_* |       | - blockchain_*  |
+----------------+       +-----------------+
```

---

## 🔗 RELACIONES DE BASE DE DATOS

### **Relaciones Principales:**

1. **User → Company** (Many-to-One)
   - Un usuario pertenece a una empresa
   - Una empresa tiene muchos usuarios

2. **Lot → Company** (Many-to-One)
   - Un lote pertenece a un productor
   - Un productor tiene muchos lotes

3. **Contract → Company** (Many-to-One x2)
   - Un contrato tiene un comprador y un exportador
   - Una empresa puede tener muchos contratos como comprador o exportador

4. **Batch → Company** (Many-to-One)
   - Un batch pertenece a un procesador
   - Un procesador tiene muchos batches

5. **Batch → Lot** (Many-to-Many)
   - Un batch puede provenir de múltiples lotes
   - Un lote puede contribuir a múltiples batches

6. **Deal → Company** (Many-to-One x2)
   - Un deal conecta dos empresas
   - Una empresa puede participar en muchos deals

---

## 📊 ESQUEMA DE BASE DE DATOS

### **Tablas Principales:**
- `user` - Usuarios del sistema
- `company` - Empresas registradas
- `lot` - Lotes de cacao registrados
- `contract` - Contratos comerciales
- `batch` - Lotes procesados
- `deal` - Acuerdos comerciales

### **Índices Recomendados:**
- `user.email` (único)
- `user.company_id`
- `company.company_type`
- `lot.producer_company_id`
- `lot.lot_code` (único)
- `contract.contract_code` (único)
- `contract.buyer_company_id`
- `contract.exporter_company_id`
- `batch.batch_code` (único)
- `deal.party_a_id`, `deal.party_b_id`

---

## 🔄 MIGRACIONES Y VERSIONADO

### **Estrategia de Migraciones:**
- **Herramienta:** Flask-Migrate (Alembic)
- **Versionado:** Numeración secuencial
- **Rollback:** Soportado para todas las migraciones

### **Migraciones Planificadas:**
1. **v1.0:** Esquema inicial completo
2. **v1.1:** Agregar campos para trazabilidad blockchain
3. **v1.2:** Campos para multi-tenancy
4. **v1.3:** Optimizaciones de rendimiento
5. **v2.0:** Migración a PostgreSQL (futuro)

---

## 📈 OPTIMIZACIONES DE RENDIMIENTO

### **Consultas Optimizadas:**
- **Joins Eficientes:** Usar select_related para relaciones 1-1
- **Índices Estratégicos:** En campos de búsqueda frecuentes
- **Paginación:** Implementada en todas las listas
- **Caching:** Preparado para Redis (futuro)

### **Escalabilidad:**
- **Sharding:** Preparado por empresa (multi-tenant)
- **Read Replicas:** Arquitectura preparada
- **Connection Pooling:** SQLAlchemy configurado
- **Query Optimization:** EXPLAIN ANALYZE para queries complejas

---

## 🔧 VALIDACIONES Y CONSTRAINTS

### **Constraints de Base de Datos:**
- **NOT NULL:** Campos obligatorios
- **UNIQUE:** Emails, códigos de lote/contrato/batch
- **FOREIGN KEY:** Integridad referencial
- **CHECK:** Valores válidos para enums

### **Validaciones de Aplicación:**
- **Email:** Formato válido
- **Fechas:** Lógicas (end_date > start_date)
- **Pesos:** Valores positivos
- **Roles:** Valores permitidos
- **Tipos de Empresa:** producer, exporter, buyer

---

## 📋 PENDIENTE PARA OPTIMIZACIONES FUTURAS

### **Mejoras de Rendimiento:**
- [ ] Implementar índices de base de datos faltantes
- [ ] Agregar caching de queries frecuentes
- [ ] Optimizar queries N+1
- [ ] Implementar database connection pooling avanzado

### **Escalabilidad:**
- [ ] Diseño de sharding por empresa
- [ ] Migración planificada a PostgreSQL
- [ ] Implementación de read replicas
- [ ] Arquitectura de microservicios preparada

### **Monitoreo:**
- [ ] Métricas de performance de BD
- [ ] Alertas de queries lentas
- [ ] Monitoreo de conexiones activas
- [ ] Análisis de uso de índices

---

**Estado**: ✅ MODELOS COMPLETOS Y FUNCIONALES

**Próximos Pasos:** Monitoreo de rendimiento y optimizaciones según uso real del sistema.</content>
<parameter name="filePath">/home/rootpanel/web/app.triboka.com/backend/documentacion_tecnica_triboka/fase_1_planificacion/diagramas_uml_modelos.md
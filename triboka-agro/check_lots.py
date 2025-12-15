#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/rootpanel/web/app.triboka.com/backend')

from models.models import db, Lot, Company, User
from config.config import Config
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Contar lotes totales
    total_lots = Lot.query.count()
    print(f"Total de lotes en DB: {total_lots}")
    
    # Contar por status
    available = Lot.query.filter_by(status='available').count()
    purchased = Lot.query.filter_by(status='purchased').count()
    batched = Lot.query.filter_by(status='batched').count()
    
    print(f"  - Disponibles: {available}")
    print(f"  - Comprados: {purchased}")
    print(f"  - En batch: {batched}")
    
    # Mostrar todos los lotes
    print(f"\nTodos los lotes ({total_lots}):")
    lots = Lot.query.all()
    for lot in lots:
        producer = Company.query.get(lot.producer_company_id)
        print(f"  - ID: {lot.id} | Código: {lot.lot_code} | Productor: {producer.name if producer else 'N/A'} | Status: {lot.status} | Peso: {lot.weight_kg}kg | Ubicación: {lot.location}")
    
    # Verificar usuarios
    print("\n\nUsuarios registrados:")
    users = User.query.all()
    for user in users:
        company = Company.query.get(user.company_id) if user.company_id else None
        print(f"  - ID: {user.id} | Email: {user.email} | Role: {user.role} | Company: {company.name if company else 'N/A'}")

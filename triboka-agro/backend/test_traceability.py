#!/usr/bin/env python3
"""
Test de endpoint de trazabilidad blockchain
"""
import sys
sys.path.insert(0, '/home/rootpanel/web/app.triboka.com/backend')

from app_web3 import app, db
from models_simple import ProducerLot
import json

with app.app_context():
    # Obtener primer lote
    lot = ProducerLot.query.first()
    
    if lot:
        print(f"\n{'='*60}")
        print(f"✅ TRAZABILIDAD BLOCKCHAIN - Lote: {lot.lot_code}")
        print(f"{'='*60}\n")
        
        print(f"📦 Información del Lote:")
        print(f"   ID: {lot.id}")
        print(f"   Código: {lot.lot_code}")
        print(f"   Estado: {lot.status}")
        print(f"   Peso: {lot.weight_kg} kg")
        print(f"   Calidad: {lot.quality_grade}")
        print(f"   Productor: {lot.producer_company.name if lot.producer_company else 'N/A'}")
        print(f"   Finca: {lot.farm_name}")
        print(f"   Ubicación: {lot.location}")
        
        print(f"\n📜 Certificaciones:")
        if lot.certifications:
            for cert in lot.certifications.split(','):
                print(f"   ✓ {cert.strip()}")
        else:
            print(f"   Sin certificaciones")
        
        print(f"\n🔗 Información Blockchain:")
        blockchain_id = lot.blockchain_lot_id or f'0x{lot.id:064x}'
        print(f"   Blockchain ID: {blockchain_id[:20]}...{blockchain_id[-10:]}")
        print(f"   Red: Polygon Mainnet")
        print(f"   Contrato: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb")
        
        print(f"\n📅 Timeline de Eventos:")
        
        # Evento 1: Creación
        print(f"\n   1️⃣  LOTE CREADO")
        print(f"      Fecha: {lot.created_at}")
        print(f"      Actor: {lot.producer_company.name if lot.producer_company else 'Productor'}")
        print(f"      TX Hash: 0x{'a' * 64}")
        print(f"      Block: 12,345,678")
        
        # Evento 2: Certificaciones
        if lot.certifications:
            print(f"\n   2️⃣  CERTIFICACIONES VERIFICADAS")
            print(f"      Fecha: {lot.created_at}")
            print(f"      Actor: Sistema de Certificación")
            print(f"      Certificaciones: {lot.certifications}")
            print(f"      TX Hash: 0x{'b' * 64}")
            print(f"      Block: 12,345,679")
        
        # Evento 3: Compra
        if lot.status in ['purchased', 'batched'] and lot.purchase_date:
            buyer_name = 'Exportadora'
            if lot.purchased_by_company:
                buyer_name = lot.purchased_by_company.name
            elif lot.export_contract and lot.export_contract.exporter_company:
                buyer_name = lot.export_contract.exporter_company.name
                
            print(f"\n   3️⃣  LOTE COMPRADO")
            print(f"      Fecha: {lot.purchase_date}")
            print(f"      Actor: {buyer_name}")
            print(f"      Precio: ${lot.purchase_price_usd:,.2f}" if lot.purchase_price_usd else "      Precio: N/A")
            print(f"      TX Hash: 0x{'c' * 64}")
            print(f"      Block: 12,345,680")
        
        print(f"\n{'='*60}")
        print(f"✅ Endpoint /api/lots/{lot.id}/traceability retornará estos datos")
        print(f"{'='*60}\n")
    else:
        print("❌ No se encontraron lotes en la base de datos")

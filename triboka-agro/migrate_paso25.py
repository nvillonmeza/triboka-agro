#!/usr/bin/env python3
"""
Triboka Agro - Migración de Base de Datos Paso 2.5
Agrega índices de rendimiento para tablas DID y TraceEvent
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Aplica migración para agregar índices de rendimiento"""

    db_path = 'database/triboka.db'

    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada. Ejecuta init_database.py primero.")
        return

    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("🔄 Aplicando migración de índices de rendimiento...")

    try:
        # Crear tablas nuevas si no existen
        print("📋 Creando tablas DID y TraceEvent...")

        # Tabla DigitalIdentity
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS digital_identities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                did TEXT NOT NULL UNIQUE,
                user_id INTEGER,
                company_id INTEGER,
                kyc_status TEXT DEFAULT 'pending',
                blockchain_address TEXT,
                reputation_score REAL DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        ''')

        # Tabla DigitalSignature
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS digital_signatures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signer_did TEXT NOT NULL,
                signer_id INTEGER,
                signer_name TEXT,
                document_type TEXT NOT NULL,
                document_id TEXT NOT NULL,
                document_hash TEXT NOT NULL,
                signature TEXT NOT NULL,
                signature_algorithm TEXT DEFAULT 'RSA-SHA256',
                public_key TEXT,
                blockchain_tx_hash TEXT,
                blockchain_timestamp TIMESTAMP,
                status TEXT DEFAULT 'valid',
                revocation_reason TEXT,
                signed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (signer_id) REFERENCES users (id)
            )
        ''')

        # Tabla KYCDocument
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kyc_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                did_id INTEGER NOT NULL,
                document_type TEXT NOT NULL,
                document_number TEXT NOT NULL,
                issuing_country TEXT,
                issuing_authority TEXT,
                document_hash TEXT NOT NULL,
                verification_hash TEXT,
                file_path TEXT,
                issued_at DATE,
                expires_at DATE,
                verification_status TEXT DEFAULT 'pending',
                verified_by INTEGER,
                verified_at TIMESTAMP,
                verification_notes TEXT,
                blockchain_tx_hash TEXT,
                blockchain_timestamp TIMESTAMP,
                is_primary INTEGER DEFAULT 0,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (did_id) REFERENCES digital_identities (id),
                FOREIGN KEY (verified_by) REFERENCES users (id)
            )
        ''')

        # Tabla TraceEvent
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trace_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                location TEXT,
                actor_id INTEGER,
                actor_name TEXT,
                event_data TEXT,
                measurements TEXT,
                blockchain_tx_hash TEXT,
                blockchain_block_number INTEGER,
                blockchain_timestamp TIMESTAMP,
                digital_signature_id INTEGER,
                status TEXT DEFAULT 'active',
                is_public INTEGER DEFAULT 1,
                tags TEXT,
                event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (actor_id) REFERENCES users (id),
                FOREIGN KEY (digital_signature_id) REFERENCES digital_signatures (id)
            )
        ''')

        # Tabla TraceTimeline
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trace_timelines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                parent_event_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                total_events INTEGER DEFAULT 0,
                completed_events INTEGER DEFAULT 0,
                blockchain_events INTEGER DEFAULT 0,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                estimated_completion TIMESTAMP,
                tags TEXT,
                custom_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_event_id) REFERENCES trace_events (id)
            )
        ''')

        print("✅ Tablas DID y TraceEvent creadas")

        # Crear índices para optimización de rendimiento
        print("⚡ Creando índices de rendimiento...")

        # Índices para DigitalIdentity
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_identities_did ON digital_identities(did)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_identities_user_id ON digital_identities(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_identities_company_id ON digital_identities(company_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_identities_kyc_status ON digital_identities(kyc_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_identities_blockchain_address ON digital_identities(blockchain_address)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_identities_reputation_score ON digital_identities(reputation_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_identities_is_active ON digital_identities(is_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_identities_created_at ON digital_identities(created_at)')

        # Índices para DigitalSignature
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_signatures_signer_did ON digital_signatures(signer_did)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_signatures_signer_id ON digital_signatures(signer_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_signatures_document_type ON digital_signatures(document_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_signatures_document_id ON digital_signatures(document_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_signatures_document_hash ON digital_signatures(document_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_signatures_blockchain_tx_hash ON digital_signatures(blockchain_tx_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_signatures_blockchain_timestamp ON digital_signatures(blockchain_timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_signatures_status ON digital_signatures(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_signatures_signed_at ON digital_signatures(signed_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_signatures_expires_at ON digital_signatures(expires_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digital_signatures_created_at ON digital_signatures(created_at)')

        # Índices para KYCDocument
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kyc_documents_did_id ON kyc_documents(did_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kyc_documents_document_type ON kyc_documents(document_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kyc_documents_document_number ON kyc_documents(document_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kyc_documents_issuing_country ON kyc_documents(issuing_country)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kyc_documents_document_hash ON kyc_documents(document_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kyc_documents_verification_hash ON kyc_documents(verification_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kyc_documents_issued_at ON kyc_documents(issued_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kyc_documents_expires_at ON kyc_documents(expires_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kyc_documents_verification_status ON kyc_documents(verification_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kyc_documents_verified_by ON kyc_documents(verified_by)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kyc_documents_verified_at ON kyc_documents(verified_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kyc_documents_blockchain_tx_hash ON kyc_documents(blockchain_tx_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kyc_documents_blockchain_timestamp ON kyc_documents(blockchain_timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kyc_documents_is_primary ON kyc_documents(is_primary)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kyc_documents_created_at ON kyc_documents(created_at)')

        # Índices para TraceEvent
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_events_event_type ON trace_events(event_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_events_entity_type ON trace_events(entity_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_events_entity_id ON trace_events(entity_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_events_location ON trace_events(location)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_events_actor_id ON trace_events(actor_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_events_blockchain_tx_hash ON trace_events(blockchain_tx_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_events_blockchain_block_number ON trace_events(blockchain_block_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_events_blockchain_timestamp ON trace_events(blockchain_timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_events_digital_signature_id ON trace_events(digital_signature_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_events_status ON trace_events(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_events_is_public ON trace_events(is_public)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_events_event_timestamp ON trace_events(event_timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_events_created_at ON trace_events(created_at)')

        # Índices para TraceTimeline
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_timelines_entity_type ON trace_timelines(entity_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_timelines_entity_id ON trace_timelines(entity_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_timelines_parent_event_id ON trace_timelines(parent_event_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_timelines_status ON trace_timelines(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_timelines_total_events ON trace_timelines(total_events)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_timelines_completed_events ON trace_timelines(completed_events)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_timelines_blockchain_events ON trace_timelines(blockchain_events)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_timelines_started_at ON trace_timelines(started_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_timelines_completed_at ON trace_timelines(completed_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_timelines_estimated_completion ON trace_timelines(estimated_completion)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_timelines_created_at ON trace_timelines(created_at)')

        print("✅ Índices de rendimiento creados")

        # Insertar datos de prueba para DID
        print("📊 Insertando datos de prueba DID...")

        # Digital Identities de prueba
        did_data = [
            ('did:triboka:001', 1, 1, 'verified', '0x742d35Cc6634C0532925a3b844Bc454e4438f44e', 95.5, 1),
            ('did:triboka:002', 2, 1, 'verified', '0x8ba1f109551bD432803012645ac136ddd64DBA72', 88.2, 1),
            ('did:triboka:003', 3, 2, 'pending', '0x1234567890123456789012345678901234567890', 0.0, 1),
            ('did:triboka:004', 4, 4, 'verified', '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd', 92.1, 1),
            ('did:triboka:005', 5, 5, 'verified', '0xfedcba0987654321fedcba0987654321fedcba09', 91.8, 1)
        ]

        cursor.executemany('''
            INSERT OR IGNORE INTO digital_identities (did, user_id, company_id, kyc_status, blockchain_address, reputation_score, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', did_data)

        # Eventos de trazabilidad de prueba
        trace_events_data = [
            ('lot_creation', 'lot', 'LOT-2025-001', 'Creación de Lote', 'Lote de cacao premium creado', 'Finca La Esperanza', 2, 'Juan Productor', '{"quality": "A+", "quantity": 500}', '{"humidity": 7.2, "temperature": 25.5}', None, None, None, None, 'active', 1, '["premium", "organic"]', '2024-12-15 08:00:00'),
            ('reception', 'lot', 'LOT-2025-001', 'Recepción en Planta', 'Lote recibido para procesamiento', 'Planta Triboka', 5, 'Carlos Procesador', '{"reception_time": "2024-12-16T10:30:00"}', '{"weight": 498.5}', None, None, None, None, 'active', 1, '["processing"]', '2024-12-16 10:30:00'),
            ('drying', 'lot', 'LOT-2025-001', 'Proceso de Secado', 'Secado natural completado', 'Secadero Triboka', 5, 'Carlos Procesador', '{"drying_method": "natural", "duration_hours": 72}', '{"final_humidity": 6.8}', None, None, None, None, 'active', 1, '["processing", "quality"]', '2024-12-19 14:00:00'),
            ('contract_signing', 'contract', '1', 'Firma de Contrato', 'Contrato de suministro firmado digitalmente', 'Bogotá', 3, 'María Exportadora', '{"contract_value": 4500, "buyer": "Chocolates Premium EU"}', None, None, None, None, None, 'active', 1, '["legal", "blockchain"]', '2024-12-20 09:00:00')
        ]

        cursor.executemany('''
            INSERT OR IGNORE INTO trace_events (event_type, entity_type, entity_id, title, description, location, actor_id, actor_name, event_data, measurements, blockchain_tx_hash, blockchain_block_number, blockchain_timestamp, digital_signature_id, status, is_public, tags, event_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', trace_events_data)

        # Confirmar cambios
        conn.commit()

        # Verificar índices creados
        print("\n📈 Verificando migración:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        indices = cursor.fetchall()
        print(f"   ✅ Índices creados: {len(indices)}")

        # Verificar datos insertados
        tables = ['digital_identities', 'digital_signatures', 'kyc_documents', 'trace_events', 'trace_timelines']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   ✅ {table}: {count} registros")

        conn.close()

        print("\n🎉 Migración Paso 2.5 completada exitosamente!")
        print("📊 Base de datos optimizada para trazabilidad DID y blockchain")

    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        conn.rollback()
        conn.close()
        return False

    return True

if __name__ == "__main__":
    migrate_database()
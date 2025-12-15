from flask import Flask, request as flask_request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_jwt_extended import decode_token, JWTManager
import json
import sqlite3
from datetime import datetime
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5004", "http://localhost:5003", "http://127.0.0.1:5004", "http://127.0.0.1:5003", "https://app.triboka.com"], logger=True, engineio_logger=True)

# Store active connections
active_connections = {}

class NotificationManager:
    def __init__(self):
        self.db_path = 'instance/triboka_production.db'
        self.init_notification_tables()
    
    def init_notification_tables(self):
        """Inicializar tablas de notificaciones"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT NOT NULL DEFAULT 'info',
                category TEXT NOT NULL DEFAULT 'system',
                data JSON,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                priority INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_notification_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                notification_type TEXT NOT NULL,
                enabled BOOLEAN DEFAULT TRUE,
                push_enabled BOOLEAN DEFAULT TRUE,
                email_enabled BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, notification_type)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS internal_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER NOT NULL,
                to_user_id INTEGER NOT NULL,
                subject TEXT,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                parent_message_id INTEGER,
                FOREIGN KEY (from_user_id) REFERENCES users(id),
                FOREIGN KEY (to_user_id) REFERENCES users(id),
                FOREIGN KEY (parent_message_id) REFERENCES internal_messages(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_notification(self, user_id, title, message, notification_type='info', 
                          category='system', data=None, priority=1, expires_hours=24):
        """Crear nueva notificación"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        expires_at = datetime.now() if expires_hours else None
        if expires_hours:
            expires_at = datetime.now().replace(hour=datetime.now().hour + expires_hours)
        
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, type, category, data, priority, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, title, message, notification_type, category, 
              json.dumps(data) if data else None, priority, expires_at))
        
        notification_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Enviar notificación en tiempo real
        self.send_realtime_notification(user_id, {
            'id': notification_id,
            'title': title,
            'message': message,
            'type': notification_type,
            'category': category,
            'data': data,
            'priority': priority,
            'created_at': datetime.now().isoformat()
        })
        
        return notification_id
    
    def send_realtime_notification(self, user_id, notification_data):
        """Enviar notificación en tiempo real via WebSocket"""
        room = f"user_{user_id}"
        socketio.emit('new_notification', notification_data, room=room)
    
    def get_user_notifications(self, user_id, limit=50, unread_only=False):
        """Obtener notificaciones del usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, title, message, type, category, data, is_read, created_at, priority
            FROM notifications 
            WHERE user_id = ? AND (expires_at IS NULL OR expires_at > datetime('now'))
        '''
        
        if unread_only:
            query += ' AND is_read = FALSE'
        
        query += ' ORDER BY priority DESC, created_at DESC LIMIT ?'
        
        cursor.execute(query, (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        
        notifications = []
        for row in rows:
            notifications.append({
                'id': row[0],
                'title': row[1],
                'message': row[2],
                'type': row[3],
                'category': row[4],
                'data': json.loads(row[5]) if row[5] else None,
                'is_read': bool(row[6]),
                'created_at': row[7],
                'priority': row[8]
            })
        
        return notifications
    
    def mark_as_read(self, notification_id, user_id):
        """Marcar notificación como leída"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE notifications 
            SET is_read = TRUE 
            WHERE id = ? AND user_id = ?
        ''', (notification_id, user_id))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0

notification_manager = NotificationManager()

@socketio.on('connect')
def handle_connect(auth):
    """Manejar conexión WebSocket"""
    try:
        print(f"🔌 Nueva conexión WebSocket - Auth: {auth}")
        
        # Para desarrollo, permitir conexiones sin autenticación
        # TODO: Habilitar autenticación en producción
        user_id = 1  # Usuario por defecto para pruebas
        
        if auth and 'token' in auth:
            try:
                token = auth['token']
                decoded_token = decode_token(token)
                user_id = decoded_token['sub']
                print(f"✅ Token válido para usuario {user_id}")
            except Exception as e:
                print(f"⚠️ Token inválido, usando usuario por defecto: {e}")
        
        # Unirse a sala personal del usuario
        join_room(f"user_{user_id}")
        active_connections[flask_request.sid] = user_id
        
        print(f"✅ Usuario {user_id} conectado (SID: {flask_request.sid})")
        
        # Enviar notificaciones pendientes (vacías por ahora)
        emit('pending_notifications', [])
        
        return True
    except Exception as e:
        print(f"❌ Error en conexión: {e}")
        return False

@socketio.on('disconnect')
def handle_disconnect():
    """Manejar desconexión WebSocket"""
    if flask_request.sid in active_connections:
        user_id = active_connections[flask_request.sid]
        leave_room(f"user_{user_id}")
        del active_connections[flask_request.sid]
        print(f"Usuario {user_id} desconectado")

@socketio.on('mark_notification_read')
def handle_mark_read(data):
    """Marcar notificación como leída"""
    try:
        user_id = active_connections.get(flask_request.sid)
        if not user_id:
            return
        
        notification_id = data.get('notification_id')
        if notification_manager.mark_as_read(notification_id, user_id):
            emit('notification_marked_read', {'notification_id': notification_id})
    except Exception as e:
        print(f"Error marcando notificación: {e}")

@socketio.on('get_notifications')
def handle_get_notifications(data):
    """Obtener notificaciones del usuario"""
    try:
        user_id = active_connections.get(flask_request.sid)
        if not user_id:
            return
        
        limit = data.get('limit', 50)
        unread_only = data.get('unread_only', False)
        
        notifications = notification_manager.get_user_notifications(user_id, limit, unread_only)
        emit('notifications_list', notifications)
    except Exception as e:
        print(f"Error obteniendo notificaciones: {e}")

@socketio.on('send_internal_message')
def handle_internal_message(data):
    """Enviar mensaje interno entre usuarios"""
    try:
        from_user_id = active_connections.get(flask_request.sid)
        if not from_user_id:
            return
        
        to_user_id = data.get('to_user_id')
        subject = data.get('subject', '')
        message = data.get('message')
        
        if not to_user_id or not message:
            emit('message_error', {'error': 'Datos incompletos'})
            return
        
        # Guardar mensaje en base de datos
        conn = sqlite3.connect(notification_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO internal_messages (from_user_id, to_user_id, subject, message)
            VALUES (?, ?, ?, ?)
        ''', (from_user_id, to_user_id, subject, message))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Crear notificación para el destinatario
        notification_manager.create_notification(
            to_user_id,
            f"Nuevo mensaje: {subject}" if subject else "Nuevo mensaje interno",
            f"Mensaje de {data.get('from_name', 'Usuario')}: {message[:100]}...",
            'message',
            'messages',
            {'message_id': message_id, 'from_user_id': from_user_id}
        )
        
        emit('message_sent', {'message_id': message_id})
        
    except Exception as e:
        print(f"Error enviando mensaje: {e}")
        emit('message_error', {'error': str(e)})

# Función para generar notificaciones automáticas del sistema
def generate_system_notifications():
    """Generar notificaciones automáticas basadas en eventos del sistema"""
    while True:
        try:
            conn = sqlite3.connect(notification_manager.db_path)
            cursor = conn.cursor()
            
            # Verificar contratos próximos a vencer
            cursor.execute('''
                SELECT c.id, c.contract_code, c.delivery_date, u.id as user_id, u.name
                FROM export_contracts c
                JOIN users u ON u.company_id = c.exporter_company_id
                WHERE c.delivery_date <= datetime('now', '+5 days')
                AND c.status = 'active'
                AND c.id NOT IN (
                    SELECT CAST(json_extract(data, '$.contract_id') AS INTEGER)
                    FROM notifications 
                    WHERE category = 'contract_expiry' 
                    AND created_at > datetime('now', '-1 day')
                )
            ''')
            
            expiring_contracts = cursor.fetchall()
            
            for contract in expiring_contracts:
                days_left = (datetime.fromisoformat(contract[2]) - datetime.now()).days
                notification_manager.create_notification(
                    contract[3],  # user_id
                    f"Contrato próximo a vencer: {contract[1]}",
                    f"El contrato {contract[1]} vence en {days_left} días. Revisa el estado de las fijaciones.",
                    'warning',
                    'contract_expiry',
                    {'contract_id': contract[0], 'days_left': days_left},
                    priority=3
                )
            
            # Verificar lotes no asignados por mucho tiempo
            cursor.execute('''
                SELECT pl.id, pl.lot_code, u.id as user_id, u.name
                FROM producer_lots pl
                JOIN users u ON u.company_id = pl.producer_company_id
                WHERE pl.status = 'available'
                AND pl.created_at <= datetime('now', '-7 days')
                AND pl.id NOT IN (
                    SELECT CAST(json_extract(data, '$.lot_id') AS INTEGER)
                    FROM notifications 
                    WHERE category = 'lot_unassigned' 
                    AND created_at > datetime('now', '-3 days')
                )
            ''')
            
            unassigned_lots = cursor.fetchall()
            
            for lot in unassigned_lots:
                notification_manager.create_notification(
                    lot[2],  # user_id
                    f"Lote sin asignar: {lot[1]}",
                    f"El lote {lot[1]} lleva más de 7 días sin ser asignado a un contrato.",
                    'info',
                    'lot_unassigned',
                    {'lot_id': lot[0]},
                    priority=2
                )
            
            conn.close()
            
        except Exception as e:
            print(f"Error generando notificaciones automáticas: {e}")
        
        # Esperar 1 hora antes de la próxima verificación
        time.sleep(3600)

# Iniciar hilo para notificaciones automáticas
notification_thread = threading.Thread(target=generate_system_notifications, daemon=True)
notification_thread.start()

if __name__ == '__main__':
    print("🔔 Servidor de Notificaciones iniciado en puerto 5005")
    socketio.run(app, host='0.0.0.0', port=5005, debug=False, allow_unsafe_werkzeug=True)
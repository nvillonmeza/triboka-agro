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
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id TEXT NOT NULL,
                sender_id INTEGER NOT NULL,
                content TEXT,
                message_type TEXT DEFAULT 'text',
                metadata JSON,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_chat_message(self, room_id, sender_id, content, message_type='text', metadata=None):
        """Crear nuevo mensaje de chat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_messages (room_id, sender_id, content, message_type, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (room_id, sender_id, content, message_type, json.dumps(metadata) if metadata else None))
        
        message_id = cursor.lastrowid
        
        # Obtener fecha de creación
        cursor.execute('SELECT created_at FROM chat_messages WHERE id = ?', (message_id,))
        created_at = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        message_data = {
            'id': message_id,
            'room_id': room_id,
            'sender_id': sender_id,
            'content': content,
            'message_type': message_type,
            'metadata': metadata,
            'is_read': False,
            'created_at': created_at
        }
        
        # Emitir a la sala
        socketio.emit('new_chat_message', message_data, room=room_id)
        
        return message_data

    def get_chat_history(self, room_id, limit=50, offset=0):
        """Obtener historial de chat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.id, m.room_id, m.sender_id, m.content, m.message_type, m.metadata, m.is_read, m.created_at, u.name
            FROM chat_messages m
            LEFT JOIN users u ON m.sender_id = u.id
            WHERE m.room_id = ?
            ORDER BY m.created_at DESC
            LIMIT ? OFFSET ?
        ''', (room_id, limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            messages.append({
                'id': row[0],
                'room_id': row[1],
                'sender_id': row[2],
                'content': row[3],
                'message_type': row[4],
                'metadata': json.loads(row[5]) if row[5] else None,
                'is_read': bool(row[6]),
                'created_at': row[7],
                'sender_name': row[8]
            })
        
        return messages

    def mark_chat_read(self, room_id, user_id):
        """Marcar mensajes de una sala como leídos (excepto los propios)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE chat_messages 
            SET is_read = TRUE 
            WHERE room_id = ? AND sender_id != ? AND is_read = FALSE
        ''', (room_id, user_id))
        
        updated = cursor.rowcount
        conn.commit()
        conn.close()
        return updated

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

# --- Chat Events ---

@socketio.on('join_chat')
def handle_join_chat(data):
    """Unirse a una sala de chat"""
    room_id = data.get('room_id')
    if room_id:
        join_room(room_id)
        print(f"Usuario {active_connections.get(flask_request.sid)} se unió a sala {room_id}")
        emit('chat_joined', {'room_id': room_id})

@socketio.on('leave_chat')
def handle_leave_chat(data):
    """Salir de una sala de chat"""
    room_id = data.get('room_id')
    if room_id:
        leave_room(room_id)
        print(f"Usuario {active_connections.get(flask_request.sid)} salió de sala {room_id}")

@socketio.on('send_chat_message')
def handle_send_chat_message(data):
    """Enviar mensaje de chat"""
    try:
        sender_id = active_connections.get(flask_request.sid)
        if not sender_id:
            return
        
        room_id = data.get('room_id')
        content = data.get('content')
        message_type = data.get('type', 'text')
        metadata = data.get('metadata')
        
        if not room_id or not content:
            return
            
        notification_manager.create_chat_message(room_id, sender_id, content, message_type, metadata)
        
    except Exception as e:
        print(f"Error enviando mensaje chat: {e}")
        emit('error', {'message': str(e)})

@socketio.on('typing')
def handle_typing(data):
    """Indicador de escribiendo"""
    room_id = data.get('room_id')
    is_typing = data.get('is_typing', False)
    user_id = active_connections.get(flask_request.sid)
    
    if room_id and user_id:
        socketio.emit('user_typing', {
            'room_id': room_id,
            'user_id': user_id,
            'is_typing': is_typing
        }, room=room_id, include_self=False)

@socketio.on('get_chat_history')
def handle_get_chat_history(data):
    """Obtener historial"""
    room_id = data.get('room_id')
    limit = data.get('limit', 50)
    offset = data.get('offset', 0)
    
    if room_id:
        messages = notification_manager.get_chat_history(room_id, limit, offset)
        emit('chat_history', {'room_id': room_id, 'messages': messages})

@socketio.on('mark_chat_read')
def handle_mark_chat_read(data):
    """Marcar leídos"""
    room_id = data.get('room_id')
    user_id = active_connections.get(flask_request.sid)
    
    if room_id and user_id:
        count = notification_manager.mark_chat_read(room_id, user_id)
        if count > 0:
            socketio.emit('messages_read', {'room_id': room_id, 'user_id': user_id}, room=room_id)

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
Excelente 🔥 — lo que estás planteando es un módulo de mensajería interna profesional, al estilo ERP colaborativo, donde los socios, proveedores, centros y exportadoras puedan comunicarse directamente entre sí solo si tienen una relación contractual o comercial vigente.
Te dejo un documento completo para tu siguiente archivo: chat.md.

⸻

💬 Módulo: Chat de Comunicación Interna

📘 Descripción general

El módulo Chat tiene como objetivo facilitar la comunicación directa entre socios vinculados (proveedores, centros de acopio y exportadoras) que mantienen contratos activos o relaciones comerciales dentro del sistema.

Permite coordinar precios, fijaciones de lotes, tiempos de entrega y resolver incidencias sin salir del entorno de la app.
Cada chat es privado entre los participantes vinculados por contrato.

⸻

🧭 Estructura funcional

1. Tipos de conversación

Tipo de chat	Participantes	Descripción
Proveedor ↔ Centro	Un proveedor y un centro de acopio	Comunicación sobre entregas, humedad, peso, recepción o pago.
Centro ↔ Exportadora	Un centro y una exportadora	Negociación de precios, fijaciones de lote, programación de embarques.
Proveedor ↔ Exportadora	Comunicación directa (cuando el proveedor trabaja sin centro)	Fijación directa de precios o entregas programadas.
Interno (admin)	Administrador con cualquier usuario	Mensajes de soporte, alertas o instrucciones globales.


⸻

🧩 Reglas de visibilidad
	•	Solo se puede abrir chat con socios con contratos activos o recientes (últimos 90 días).
	•	No se permiten chats abiertos sin relación comercial.
	•	Cada conversación incluye historial de mensajes, archivos adjuntos y estado en línea.

⸻

🧱 Estructura técnica (Flutter)

🔹 Modelo de datos

class ChatMessage {
  final String id;
  final String senderId;
  final String receiverId;
  final String message;
  final DateTime timestamp;
  final bool isRead;

  ChatMessage({
    required this.id,
    required this.senderId,
    required this.receiverId,
    required this.message,
    required this.timestamp,
    this.isRead = false,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) => ChatMessage(
        id: json['id'],
        senderId: json['sender_id'],
        receiverId: json['receiver_id'],
        message: json['message'],
        timestamp: DateTime.parse(json['timestamp']),
        isRead: json['is_read'] ?? false,
      );
}


⸻

🔹 UI general

Estructura principal del módulo:

ChatPage
 ├─ Lista de contactos con los que existe relación contractual
 ├─ Barra de búsqueda y filtro (por rol o contrato)
 └─ ChatView (pantalla de conversación)
      ├─ Mensajes ordenados por fecha
      ├─ Campo de texto + botón enviar
      └─ Adjuntar archivos o documentos PDF/imagen


⸻

🔹 Ejemplo de pantalla de chat (Flutter)

class ChatScreen extends StatefulWidget {
  final String partnerName;
  final String partnerRole;

  const ChatScreen({required this.partnerName, required this.partnerRole});

  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final List<Map<String, String>> messages = [];
  final TextEditingController controller = TextEditingController();

  void sendMessage() {
    if (controller.text.trim().isEmpty) return;
    setState(() {
      messages.add({"me": controller.text.trim()});
      controller.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            CircleAvatar(child: Text(widget.partnerName[0])),
            SizedBox(width: 8),
            Text(widget.partnerName),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final msg = messages[index];
                final isMe = msg.containsKey("me");
                return Align(
                  alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: isMe ? Colors.green[100] : Colors.grey[200],
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(isMe ? msg["me"]! : msg["other"]!),
                  ),
                );
              },
            ),
          ),
          Container(
            padding: const EdgeInsets.all(8),
            color: Colors.grey[100],
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: controller,
                    decoration: InputDecoration(
                      hintText: "Escribe un mensaje...",
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(20),
                        borderSide: BorderSide.none,
                      ),
                      filled: true,
                      fillColor: Colors.white,
                    ),
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.send, color: Colors.green),
                  onPressed: sendMessage,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}


⸻

⚙️ Backend sugerido

El backend manejará:
	•	SocketIO o Firebase Realtime Database (para mensajes en tiempo real).
	•	Autenticación JWT para asegurar que solo los socios válidos puedan enviar mensajes.
	•	Estructura de tablas:

usuarios
 ├─ id
 ├─ nombre
 ├─ rol (proveedor / centro / exportadora)

chats
 ├─ id
 ├─ usuario1_id
 ├─ usuario2_id
 ├─ contrato_id (opcional)

mensajes
 ├─ id
 ├─ chat_id
 ├─ sender_id
 ├─ texto
 ├─ timestamp
 ├─ leido (boolean)
 ├─ adjunto_url (opcional)


⸻

🔒 Seguridad y permisos
	•	Solo se puede iniciar chat si existe un contrato confirmado entre ambas partes.
	•	Los mensajes se encriptan en tránsito (HTTPS + WebSocket seguro).
	•	Las conversaciones se eliminan al finalizar un contrato si así se define en políticas de empresa.

⸻

🎨 UX recomendada
	•	Bubble chat estilo WhatsApp Business / Telegram pero adaptado al branding cacao (tonos verde y marrón).
	•	Mostrar foto o logo de empresa en el avatar.
	•	Notificación visual (badge) en el ícono del menú inferior cuando hay mensajes nuevos.
	•	Al abrir un contrato, un botón “Abrir chat con socio” conecta directamente con la conversación.

⸻

🚀 Próximos pasos sugeridos
	1.	Crear modelo ChatMessage y ChatUser.
	2.	Implementar lista de socios filtrada por contrato activo.
	3.	Integrar Firebase o Socket.IO con backend Flask o Node.js.
	4.	Implementar notificaciones push (FCM).
	5.	Guardar historial local con Hive o sqflite.
	6.	Añadir envío de archivos (PDF, imágenes, tickets).
	7.	Mostrar último mensaje en la lista de chats.

⸻

📁 Estructura de archivos recomendada

lib/
├─ pages/
│  ├─ chat_list_page.dart       # lista de chats activos
│  └─ chat_screen.dart          # pantalla de conversación
├─ models/
│  ├─ chat_message.dart
│  └─ chat_user.dart
├─ services/
│  ├─ chat_service.dart         # conexión API / Socket
│  └─ notification_service.dart
└─ widgets/
   └─ message_bubble.dart


⸻


import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../utils/constants.dart';
import '../services/notification_service.dart';

class ChatPage extends StatefulWidget {
  const ChatPage({super.key});

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final List<Map<String, dynamic>> _chats = [
    {
      'nombre': 'Agroarriba S.A.',
      'rol': 'Exportadora',
      'ultimoMensaje': 'Confirmamos recepción del lote',
      'tiempo': '2 min',
      'noLeidos': 2,
      'avatar': 'A',
      'color': Colors.blue,
    },
    {
      'nombre': 'Centro Norte',
      'rol': 'Centro de Acopio',
      'ultimoMensaje': 'Listo para entrega mañana',
      'tiempo': '1 h',
      'noLeidos': 0,
      'avatar': 'CN',
      'color': Colors.green,
    },
    {
      'nombre': 'Juan Pérez',
      'rol': 'Proveedor',
      'ultimoMensaje': 'Humedad en 7.8%, ok?',
      'tiempo': '3 h',
      'noLeidos': 1,
      'avatar': 'JP',
      'color': Colors.orange,
    },
    {
      'nombre': 'Ecuacacao',
      'rol': 'Exportadora',
      'ultimoMensaje': 'Precio fijado para diciembre',
      'tiempo': '1 día',
      'noLeidos': 0,
      'avatar': 'E',
      'color': Colors.purple,
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppConstants.backgroundLight,
      appBar: AppBar(
        title: const Text('Chat'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              // TODO: Implementar búsqueda
            },
          ),
          Consumer<NotificationService>(
            builder: (context, notificationService, child) {
              return IconButton(
                icon: const Icon(Icons.notifications_active),
                onPressed: () => _simularMensajesEntrantes(notificationService),
                tooltip: 'Simular mensajes entrantes',
              );
            },
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Header con información
            Container(
              width: double.infinity,
              margin: const EdgeInsets.all(AppConstants.defaultPadding),
              padding: const EdgeInsets.all(AppConstants.defaultPadding),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [
                    AppConstants.primaryColor,
                    AppConstants.secondaryColor,
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(
                        Icons.chat_bubble,
                        color: Colors.white,
                        size: 24,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Comunicación con socios',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Solo con contratos activos o relaciones comerciales vigentes',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.9),
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
            
            // Lista de chats
            Expanded(
              child: _chats.isEmpty
                  ? const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.chat_bubble_outline,
                            size: 64,
                            color: AppConstants.textSecondary,
                          ),
                          SizedBox(height: 16),
                          Text(
                            'No hay conversaciones activas',
                            style: TextStyle(
                              color: AppConstants.textSecondary,
                              fontSize: 16,
                            ),
                          ),
                          SizedBox(height: 8),
                          Text(
                            'Los chats aparecen cuando tienes\ncontratos activos con socios',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: AppConstants.textSecondary,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.symmetric(
                        horizontal: AppConstants.defaultPadding,
                      ),
                      itemCount: _chats.length,
                      itemBuilder: (context, index) {
                        final chat = _chats[index];
                        return _buildChatItem(chat);
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChatItem(Map<String, dynamic> chat) {
    return Container(
      margin: const EdgeInsets.only(bottom: AppConstants.smallPadding),
      child: Material(
        color: AppConstants.cardWhite,
        borderRadius: BorderRadius.circular(AppConstants.borderRadius),
        elevation: 2,
        shadowColor: Colors.black12,
        child: InkWell(
          borderRadius: BorderRadius.circular(AppConstants.borderRadius),
          onTap: () {
            _openChatDetail(chat);
          },
          child: Padding(
            padding: const EdgeInsets.all(AppConstants.defaultPadding),
            child: Row(
              children: [
                // Avatar
                CircleAvatar(
                  radius: 24,
                  backgroundColor: chat['color'],
                  child: Text(
                    chat['avatar'],
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                ),
                
                const SizedBox(width: AppConstants.defaultPadding),
                
                // Información del chat
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            chat['nombre'],
                            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                              fontWeight: FontWeight.w600,
                              color: AppConstants.textPrimary,
                            ),
                          ),
                          Text(
                            chat['tiempo'],
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: AppConstants.textSecondary,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 2),
                      Text(
                        chat['rol'],
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: chat['color'],
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              chat['ultimoMensaje'],
                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: AppConstants.textSecondary,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          if (chat['noLeidos'] > 0)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                color: AppConstants.primaryColor,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Text(
                                '${chat['noLeidos']}',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _openChatDetail(Map<String, dynamic> chat) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => ChatDetailPage(chat: chat),
      ),
    );
  }

  void _simularMensajesEntrantes(NotificationService notificationService) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('💬 Simulador de Chat'),
        content: const Text(
          'Esto simulará mensajes entrantes de diferentes socios comerciales:\n\n'
          '• Mensajes de proveedores\n'
          '• Consultas de exportadoras\n'
          '• Notificaciones de centros de acopio\n\n'
          'Las notificaciones aparecerán en la consola de debug.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.of(context).pop();
              
              // Simular mensajes entrantes
              notificationService.notificarNuevoMensaje(
                'Carlos Mendoza', 
                '¿Cuál es el precio actual del cacao?'
              );
              
              Future.delayed(const Duration(seconds: 3), () {
                notificationService.notificarNuevoMensaje(
                  'SUMAQAO S.A.C.', 
                  'Necesitamos confirmar la orden de 1500 TM'
                );
              });
              
              Future.delayed(const Duration(seconds: 6), () {
                notificationService.notificarNuevoMensaje(
                  'Centro Huánuco', 
                  'Stock actualizado: 1,250 kg disponibles'
                );
              });
              
              Future.delayed(const Duration(seconds: 9), () {
                notificationService.notificarNuevoMensaje(
                  'María Gonzales', 
                  'La entrega estará lista mañana temprano'
                );
              });

              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('💬 Simulación de chat iniciada - Revisa la consola'),
                  backgroundColor: AppConstants.primaryColor,
                  duration: Duration(seconds: 3),
                ),
              );
            },
            child: const Text('Iniciar Simulación'),
          ),
        ],
      ),
    );
  }
}

class ChatDetailPage extends StatefulWidget {
  final Map<String, dynamic> chat;

  const ChatDetailPage({super.key, required this.chat});

  @override
  State<ChatDetailPage> createState() => _ChatDetailPageState();
}

class _ChatDetailPageState extends State<ChatDetailPage> {
  final TextEditingController _messageController = TextEditingController();
  final List<Map<String, dynamic>> _messages = [
    {
      'texto': '¡Hola! ¿Cómo va el secado del lote?',
      'esMio': false,
      'tiempo': '10:30',
    },
    {
      'texto': 'Muy bien, la humedad está bajando. Creo que estará listo para mañana.',
      'esMio': true,
      'tiempo': '10:32',
    },
    {
      'texto': 'Perfecto. ¿Podrías confirmar el peso final cuando esté listo?',
      'esMio': false,
      'tiempo': '10:35',
    },
    {
      'texto': 'Por supuesto. Te envío las fotos también.',
      'esMio': true,
      'tiempo': '10:37',
    },
  ];

  void _sendMessage() {
    if (_messageController.text.trim().isEmpty) return;

    setState(() {
      _messages.add({
        'texto': _messageController.text.trim(),
        'esMio': true,
        'tiempo': '${DateTime.now().hour}:${DateTime.now().minute.toString().padLeft(2, '0')}',
      });
      _messageController.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            CircleAvatar(
              radius: 16,
              backgroundColor: widget.chat['color'],
              child: Text(
                widget.chat['avatar'],
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.chat['nombre'],
                  style: const TextStyle(fontSize: 16),
                ),
                Text(
                  widget.chat['rol'],
                  style: TextStyle(
                    fontSize: 12,
                    color: widget.chat['color'],
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.more_vert),
            onPressed: () {
              // TODO: Opciones del chat
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Lista de mensajes
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(AppConstants.defaultPadding),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                return _buildMessageBubble(message);
              },
            ),
          ),
          
          // Campo de entrada de mensaje
          Container(
            padding: const EdgeInsets.all(AppConstants.defaultPadding),
            decoration: const BoxDecoration(
              color: AppConstants.cardWhite,
              border: Border(
                top: BorderSide(color: Colors.grey, width: 0.2),
              ),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: InputDecoration(
                      hintText: 'Escribe un mensaje...',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(20),
                        borderSide: BorderSide.none,
                      ),
                      filled: true,
                      fillColor: AppConstants.backgroundLight,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 8,
                      ),
                    ),
                    maxLines: null,
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 8),
                Material(
                  color: AppConstants.primaryColor,
                  borderRadius: BorderRadius.circular(20),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(20),
                    onTap: _sendMessage,
                    child: const Padding(
                      padding: EdgeInsets.all(12),
                      child: Icon(
                        Icons.send,
                        color: Colors.white,
                        size: 20,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(Map<String, dynamic> message) {
    final bool esMio = message['esMio'];
    
    return Align(
      alignment: esMio ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        decoration: BoxDecoration(
          color: esMio 
              ? AppConstants.primaryColor.withOpacity(0.1)
              : AppConstants.cardWhite,
          borderRadius: BorderRadius.circular(12),
          border: esMio 
              ? Border.all(color: AppConstants.primaryColor.withOpacity(0.3))
              : Border.all(color: Colors.grey.shade300),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              message['texto'],
              style: TextStyle(
                color: esMio 
                    ? AppConstants.primaryColor.withOpacity(0.9)
                    : AppConstants.textPrimary,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              message['tiempo'],
              style: TextStyle(
                color: AppConstants.textSecondary,
                fontSize: 11,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
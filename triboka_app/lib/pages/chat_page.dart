import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../utils/constants.dart';
import '../services/notification_service.dart';
import '../services/chat_service.dart';

import '../widgets/simulation_banner.dart';

class ChatPage extends StatefulWidget {
  const ChatPage({super.key});

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  // Datos hardcoded para la lista de chats (simulando contratos activos)
  final List<Map<String, dynamic>> _chats = [
    {
      'room_id': 'contract_101',
      'nombre': 'Agroarriba S.A.',
      'rol': 'Exportadora',
      'ultimoMensaje': 'Confirmamos recepción del lote',
      'tiempo': '2 min',
      'noLeidos': 2,
      'avatar': 'A',
      'color': Colors.blue,
    },
    {
      'room_id': 'contract_102',
      'nombre': 'Centro Norte',
      'rol': 'Centro de Acopio',
      'ultimoMensaje': 'Listo para entrega mañana',
      'tiempo': '1 h',
      'noLeidos': 0,
      'avatar': 'CN',
      'color': Colors.green,
    },
    {
      'room_id': 'contract_103',
      'nombre': 'Juan Pérez',
      'rol': 'Proveedor',
      'ultimoMensaje': 'Humedad en 7.8%, ok?',
      'tiempo': '3 h',
      'noLeidos': 1,
      'avatar': 'JP',
      'color': Colors.orange,
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
          Consumer<ChatService>(builder: (context, chatService, _) {
            return Container(
              margin: const EdgeInsets.only(right: 16),
              child: Icon(
                Icons.circle, 
                size: 12,
                color: chatService.isConnected ? Colors.greenAccent : Colors.redAccent,
              ),
            );
          })
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Simulation Banner
            Consumer<ChatService>(builder: (context, chat, _) {
              return SimulationBanner(isVisible: chat.isSimulated);
            }),
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
              child: ListView.builder(
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
                      Text(
                        chat['ultimoMensaje'],
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: AppConstants.textSecondary,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
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
}

class ChatDetailPage extends StatefulWidget {
  final Map<String, dynamic> chat;

  const ChatDetailPage({super.key, required this.chat});

  @override
  State<ChatDetailPage> createState() => _ChatDetailPageState();
}

class _ChatDetailPageState extends State<ChatDetailPage> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    // Unirse a la sala al iniciar
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<ChatService>(context, listen: false).joinChat(widget.chat['room_id']);
    });
  }

  @override
  void dispose() {
    // Salir de la sala al cerrar (opcional, joinChat maneja el cambio)
    super.dispose();
  }

  void _sendMessage() {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;

    final chatService = Provider.of<ChatService>(context, listen: false);
    chatService.sendMessage(text);
    _messageController.clear();
    
    // Scroll al final
    _scrollToBottom();
  }
  
  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        0.0, // ListView invertido, 0 es el final
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
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
                Consumer<ChatService>(
                  builder: (context, chat, _) {
                     return chat.isTyping 
                       ? const Text(
                           'Escribiendo...',
                           style: TextStyle(
                             fontSize: 12,
                             color: AppConstants.primaryColor,
                             fontStyle: FontStyle.italic,
                           ),
                         )
                       : Text(
                           widget.chat['rol'],
                           style: TextStyle(
                             fontSize: 12,
                             color: widget.chat['color'],
                             fontWeight: FontWeight.w500,
                           ),
                         );
                  }
                ),
              ],
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          // Lista de mensajes (Conectada a ChatService)
          Expanded(
            child: Consumer<ChatService>(
              builder: (context, chatService, child) {
                final messages = chatService.messages;
                
                if (messages.isEmpty) {
                  return const Center(child: Text('Inicia la conversación'));
                }
                
                return ListView.builder(
                  controller: _scrollController,
                  reverse: true, // Mensajes nuevos abajo
                  padding: const EdgeInsets.all(AppConstants.defaultPadding),
                  itemCount: messages.length,
                  itemBuilder: (context, index) {
                    final message = messages[index];
                    // Determinar si es mi mensaje (por ahora sender_id = 1 es mi usuario mock)
                    final esMio = message['sender_id'] == 1; 
                    return _buildMessageBubble(message, esMio);
                  },
                );
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
                    onChanged: (val) {
                      // TODO: Implementar lógica de typing debounce
                    },
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

  Widget _buildMessageBubble(Map<String, dynamic> message, bool esMio) {
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
              message['content'] ?? '',
              style: TextStyle(
                color: esMio 
                    ? AppConstants.primaryColor.withOpacity(0.9)
                    : AppConstants.textPrimary,
                fontSize: 14,
              ),
            ),
            // const SizedBox(height: 4),
            // Text(
            //   message['created_at'] ?? '', // Formatear hora
            //   style: TextStyle(
            //     color: AppConstants.textSecondary,
            //     fontSize: 11,
            //   ),
            // ),
          ],
        ),
      ),
    );
  }
}
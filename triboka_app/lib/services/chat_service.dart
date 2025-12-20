import 'dart:async';
import 'package:flutter/material.dart';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import '../utils/constants.dart';

class ChatService extends ChangeNotifier {
  IO.Socket? _socket;
  bool _isConnected = false;
  bool _isSimulated = false; // New flag
  String _currentRoom = '';
  List<Map<String, dynamic>> _conversations = []; // Local storage of chats
  List<Map<String, dynamic>> _messages = [];
  Map<String, bool> _typingUsers = {};
  
  // Getters
  bool get isConnected => _isConnected;
  bool get isSimulated => _isSimulated;
  List<Map<String, dynamic>> get messages => _messages;
  List<Map<String, dynamic>> get conversations => _conversations;
  bool get isTyping => _typingUsers.isNotEmpty;

  // Inicializar servicio
  void initService() {
    // Production URL from constants
    final String socketUrl = 'https://api.triboka.com:443/chat'; 
    
    _socket = IO.io(socketUrl, IO.OptionBuilder()
      .setTransports(['websocket'])
      .disableAutoConnect()
      .setExtraHeaders({'token': 'dev_token'}) // TODO: Implementar JWT real
      .build()
    );

    _socket?.onConnect((_) {
      print('✅ Conectado al servidor de chat');
      _isConnected = true;
      notifyListeners();
    });

    _socket?.onDisconnect((_) {
      print('❌ Desconectado del servidor de chat');
      _isConnected = false;
      notifyListeners();
    });
    
    _socket?.on('connect_error', (data) => print('⚠️ Error de conexión: $data'));

    // Listeners de Chat
    _socket?.on('chat_joined', (data) {
      print('🚪 Unido a sala: ${data['room_id']}');
    });

    _socket?.on('new_chat_message', (data) {
      if (data['room_id'] == _currentRoom) {
        _messages.insert(0, data); // Insertar al inicio (nuevo mensaje)
        notifyListeners();
      }
      // Update snippet in conversation list
      final index = _conversations.indexWhere((c) => c['room_id'] == data['room_id']);
      if (index != -1) {
        _conversations[index]['ultimoMensaje'] = data['content'];
        _conversations[index]['tiempo'] = 'Ahora';
        notifyListeners();
      }
    });

    _socket?.on('chat_history', (data) {
      if (data['room_id'] == _currentRoom) {
        final List<dynamic> history = data['messages'];
        _messages = List<Map<String, dynamic>>.from(history);
        notifyListeners();
      }
    });
    
    _socket?.on('user_typing', (data) {
      if (data['room_id'] == _currentRoom) {
        final userId = data['user_id'].toString();
        final isTyping = data['is_typing'] as bool;
        
        if (isTyping) {
          _typingUsers[userId] = true;
        } else {
          _typingUsers.remove(userId);
        }
        notifyListeners();
      }
    });

    _socket?.connect();
    
    // DEMO: Disabled for Production
    /*
    Future.delayed(const Duration(seconds: 2), () {
      if (!_isConnected) {
        print('⚠️ Servidor no encontrado, activando modo SIMULACIÓN para demo.');
        _isConnected = true; 
        _isSimulated = true; 
        notifyListeners();
      }
    });
    */
  }

  // Start or Get Chat
  Map<String, dynamic> startChat(String authorName, String publicationTitle, String role) {
    // Generate a pseudo-unique ID for this interaction
    final roomId = 'chat_${authorName.replaceAll(' ', '')}_${DateTime.now().millisecondsSinceEpoch}';
    
    // Check if we already have a chat with this author (Simplification)
    final existingIndex = _conversations.indexWhere((c) => c['nombre'] == authorName);
    
    if (existingIndex != -1) {
      return _conversations[existingIndex];
    }

    // Create new chat
    final newChat = {
      'room_id': roomId,
      'nombre': authorName,
      'rol': role.toUpperCase(),
      'ultimoMensaje': 'Interés en: $publicationTitle',
      'tiempo': 'Nuevo',
      'noLeidos': 0,
      'avatar': authorName.isNotEmpty ? authorName[0].toUpperCase() : '?',
      'color': Colors.blueAccent, // Pick random color in real app
    };
    
    _conversations.insert(0, newChat);
    notifyListeners();
    return newChat;
  }

  // Métodos públicos
  void joinChat(String roomId) {
    if (_currentRoom == roomId) return;
    
    if (_currentRoom.isNotEmpty) {
      leaveChat(_currentRoom);
    }
    
    _currentRoom = roomId;
    _messages.clear();
    notifyListeners();
    
    if (_socket?.connected == true) {
      _socket?.emit('join_chat', {'room_id': roomId});
      getHistory(roomId);
    }
  }
  
  void _loadMockHistory() async {
    // Disabled
  }

  void leaveChat(String roomId) {
    _socket?.emit('leave_chat', {'room_id': roomId});
    _currentRoom = '';
    _messages.clear();
    notifyListeners();
  }

  void sendMessage(String content, {String type = 'text', Map<String, dynamic>? metadata}) {
    if (_currentRoom.isEmpty || content.isEmpty) return;
    
    if (_socket?.connected == true) {
      _socket?.emit('send_chat_message', {
        'room_id': _currentRoom,
        'content': content,
        'type': type,
        'metadata': metadata
      });
    } else {
      // Offline / Simulated Send
      // Just echo locally so user sees their message
      final msg = {'sender_id': 1, 'content': content, 'created_at': DateTime.now().toString()};
      _messages.insert(0, msg);
      
      // Update last message in conversation list
      final index = _conversations.indexWhere((c) => c['room_id'] == _currentRoom);
      if (index != -1) {
        _conversations[index]['ultimoMensaje'] = content;
        _conversations[index]['tiempo'] = 'Ahora';
      }
      notifyListeners();
      
      // Auto-reply DISABLED for Production
    }
  }

  void sendTyping(bool isTyping) {
    if (_currentRoom.isEmpty) return;
    
    _socket?.emit('typing', {
      'room_id': _currentRoom,
      'is_typing': isTyping
    });
  }

  void getHistory(String roomId, {int limit = 50, int offset = 0}) {
    _socket?.emit('get_chat_history', {
      'room_id': roomId,
      'limit': limit,
      'offset': offset
    });
  }
  
  @override
  void dispose() {
    _socket?.disconnect();
    _socket?.dispose();
    super.dispose();
  }
}

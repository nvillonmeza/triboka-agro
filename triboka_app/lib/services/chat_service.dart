import 'dart:async';
import 'package:flutter/material.dart';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import '../utils/constants.dart';

class ChatService extends ChangeNotifier {
  IO.Socket? _socket;
  bool _isConnected = false;
  bool _isSimulated = false; // New flag
  String _currentRoom = '';
  List<Map<String, dynamic>> _messages = [];
  Map<String, bool> _typingUsers = {};
  
  // Getters
  bool get isConnected => _isConnected;
  bool get isSimulated => _isSimulated;
  List<Map<String, dynamic>> get messages => _messages;
  bool get isTyping => _typingUsers.isNotEmpty;

  // Inicializar servicio
  void initService() {
    // Production URL from constants
    final String socketUrl = AppConstants.chatSocketUrl; 
    
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
    
    // DEMO: If connection fails after 2 seconds, switch to mock mode
    Future.delayed(const Duration(seconds: 2), () {
      if (!_isConnected) {
        print('⚠️ Servidor no encontrado, activando modo SIMULACIÓN para demo.');
        // _isConnected stays false for real socket, but we treat service as "Usable"
        _isConnected = true; 
        _isSimulated = true; // Mark as simulated
        notifyListeners();
      }
    });
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
    } else {
       // Mock History for Demo
       _loadMockHistory();
    }
  }
  
  void _loadMockHistory() async {
    await Future.delayed(const Duration(milliseconds: 500));
    _messages = [
      {'sender_id': 2, 'content': 'Hola, ¿cómo va el envío?', 'created_at': DateTime.now().subtract(const Duration(minutes: 5)).toString()},
      {'sender_id': 1, 'content': 'Todo bien, saliendo mañana.', 'created_at': DateTime.now().subtract(const Duration(minutes: 2)).toString()},
    ];
    notifyListeners();
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
      // Mock Send
      final msg = {'sender_id': 1, 'content': content, 'created_at': DateTime.now().toString()};
      _messages.insert(0, msg);
      notifyListeners();
      
      // Auto-reply simulation
      Future.delayed(const Duration(seconds: 2), () {
        if (_currentRoom.isNotEmpty) {
           final reply = {'sender_id': 2, 'content': 'Entendido, gracias por la info.', 'created_at': DateTime.now().toString()};
           _messages.insert(0, reply);
           notifyListeners();
        }
      });
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

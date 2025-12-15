import 'package:flutter/foundation.dart';
import 'package:hive_flutter/hive_flutter.dart';

class User {
  final String id;
  final String name;
  final String email;
  final String role; // 'proveedor', 'centro', 'exportadora'
  final String? avatarUrl;

  User({
    required this.id,
    required this.name,
    required this.email,
    required this.role,
    this.avatarUrl,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      name: json['name'],
      email: json['email'],
      role: json['role'],
      avatarUrl: json['avatarUrl'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'role': role,
      'avatarUrl': avatarUrl,
    };
  }
}

class AuthService extends ChangeNotifier {
  User? _currentUser;
  bool _isLoading = false;
  
  // Hive box name
  static const String _authBoxName = 'auth_session';

  User? get currentUser => _currentUser;
  bool get isLoggedIn => _currentUser != null;
  bool get isLoading => _isLoading;
  String get currentRole => _currentUser?.role ?? 'guest';

  Future<void> initService() async {
    await _loadSession();
  }

  Future<void> _loadSession() async {
    try {
      final box = await Hive.openBox(_authBoxName);
      final userMap = box.get('user');
      
      if (userMap != null) {
        _currentUser = User.fromJson(Map<String, dynamic>.from(userMap));
        notifyListeners();
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error loading session: $e');
      }
    }
  }

  Future<bool> login(String email, String password, String role) async {
    _isLoading = true;
    notifyListeners();

    // Simulate API delay
    await Future.delayed(const Duration(seconds: 2));

    try {
      // Mock validation logic
      if (password == '123456') {
        // Create user based on role
        final newUser = User(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          name: _getNameForRole(role),
          email: email,
          role: role,
          avatarUrl: 'https://i.pravatar.cc/150?u=$email',
        );

        // Save session
        final box = await Hive.openBox(_authBoxName);
        await box.put('user', newUser.toJson());

        _currentUser = newUser;
        return true;
      } else {
        throw Exception('Contraseña incorrecta');
      }
    } catch (e) {
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    _isLoading = true;
    notifyListeners(); // Notify to show loading if needed

    try {
      final box = await Hive.openBox(_authBoxName);
      await box.delete('user');
      _currentUser = null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  String _getNameForRole(String role) {
    switch (role) {
      case 'proveedor': return 'Juan Agricultor';
      case 'centro': return 'Centro de Acopio El Triunfo';
      case 'exportadora': return 'Ecuador Cocoa Exports';
      default: return 'Usuario Demo';
    }
  }
}

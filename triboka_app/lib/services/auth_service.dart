// lib/services/auth_service.dart
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../config/api_config.dart';
import '../models/user.dart';

class AuthService extends ChangeNotifier {
  static const String _tokenKey = 'auth_token';
  static const String _userKey = 'user_data';

  bool _isLoading = false;
  bool get isLoading => _isLoading;
  bool get isLoggedIn => _currentUser != null;

  User? _currentUser;
  User? get currentUser => _currentUser;

  // For compatibility with SyncService
  Future<String?> getAccessToken() async {
    return getToken();
  }

  /// Inicializa el servicio checkeando sesión
  Future<void> initService() async {
    final userMap = await getUser();
    if (userMap != null) {
      // Intentar construir un objeto User si es posible, o usar el map. 
      // Por compatibilidad con la app existente que usa User object:
      try {
         // Asegurar que el map tiene los campos requeridos por User.fromMap
         // Si el backend devuelve campos distintos, mapearlos aquí.
         _currentUser = User.fromMap(userMap);
      } catch (e) {
        debugPrint('Error parsing user from cache: $e');
      }
    }
    notifyListeners();
  }

  /// Wrapper para compatibilidad con UI existente
  Future<bool> loginWithPassword(String email, String password, [String? role]) async {
    _setLoading(true);
    final result = await login(email, password);
    _setLoading(false);
    return result['success'] == true;
  }

  /// Login con email y password
  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.loginEndpoint}'),
        headers: ApiConfig.headers,
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      ).timeout(ApiConfig.connectionTimeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        
        // --- VALIDACIÓN DE LICENCIA (Ecosistema Consolidado) ---
        if (data['license'] != null) {
          final license = data['license'];
          if (license['status'] != 'active') {
            return {
              'success': false,
              'error': 'Licencia inactiva o expirada. Contacte soporte.',
            };
          }
          // Opcional: Guardar fecha de expiración
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString('license_expiration', license['expiration'] ?? '');
        }
        // --------------------------------------------------------

        // Guardar token y usuario
        if (data['access_token'] != null) {
           await _saveToken(data['access_token']);
        }
        if (data['user'] != null) {
           await _saveUser(data['user']);
           try {
             _currentUser = User.fromMap(data['user']);
           } catch (e) {
             debugPrint('Error creating User object: $e');
           }
        }
        
        notifyListeners();
        return {
          'success': true,
          'data': data,
        };
      } else {
        final error = jsonDecode(response.body);
        return {
          'success': false,
          'error': error['error'] ?? 'Error al iniciar sesión',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Error de conexión: ${e.toString()}',
      };
    }
  }

  /// Registrar nuevo usuario
  Future<Map<String, dynamic>> register({
    required String name,
    required String email,
    required String password,
    required String role,
    String? company,
  }) async {
    _setLoading(true);
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.registerEndpoint}'),
        headers: ApiConfig.headers,
        body: jsonEncode({
          'name': name,
          'email': email,
          'password': password,
          'role': role,
          if (company != null) 'company_name': company,
        }),
      ).timeout(ApiConfig.connectionTimeout);

      if (response.statusCode == 201 || response.statusCode == 200) {
        final data = jsonDecode(response.body);
        
        if (data['access_token'] != null) {
          await _saveToken(data['access_token']);
        }
        if (data['user'] != null) {
          await _saveUser(data['user']);
          try {
             _currentUser = User.fromMap(data['user']);
           } catch (e) {
             debugPrint('Error creating User object: $e');
           }
        }
        
        notifyListeners();
        _setLoading(false);
        return {
          'success': true,
          'data': data,
        };
      } else {
        final error = jsonDecode(response.body);
        _setLoading(false);
        return {
          'success': false,
          'error': error['error'] ?? 'Error al registrarse',
        };
      }
    } catch (e) {
      _setLoading(false);
      return {
        'success': false,
        'error': 'Error de conexión: ${e.toString()}',
      };
    }
  }

  /// Obtener perfil del usuario
  Future<Map<String, dynamic>> getProfile() async {
    try {
      final token = await getToken();
      if (token == null) {
        return {
          'success': false,
          'error': 'No hay sesión activa',
        };
      }

      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.profileEndpoint}'),
        headers: ApiConfig.headersWithAuth(token),
      ).timeout(ApiConfig.connectionTimeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await _saveUser(data);
        try {
             _currentUser = User.fromMap(data);
        } catch (e) {debugPrint('Error parsing user: $e');}
        
        notifyListeners();
        return {
          'success': true,
          'data': data,
        };
      } else {
        return {
          'success': false,
          'error': 'Error al obtener perfil',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Error de conexión: ${e.toString()}',
      };
    }
  }

  /// Cerrar sesión
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_userKey);
    _currentUser = null;
    notifyListeners();
  }

  /// Verificar si hay sesión activa
  Future<bool> isAuthenticated() async {
    final token = await getToken();
    return token != null;
  }

  /// Obtener token guardado
  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  /// Obtener usuario guardado
  Future<Map<String, dynamic>?> getUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userJson = prefs.getString(_userKey);
    if (userJson != null) {
      return jsonDecode(userJson);
    }
    return null;
  }

  // Métodos privados
  Future<void> _saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  Future<void> _saveUser(Map<String, dynamic> user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userKey, jsonEncode(user));
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}

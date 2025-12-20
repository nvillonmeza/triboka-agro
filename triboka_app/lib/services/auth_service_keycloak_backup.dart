import 'package:flutter/foundation.dart';
import 'package:flutter_appauth/flutter_appauth.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/user.dart';
import '../utils/constants.dart';

class AuthService extends ChangeNotifier {
  final FlutterAppAuth _appAuth = const FlutterAppAuth();
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  
  // Keycloak Configuration
  static const String _keycloakUrl = 'https://auth.triboka.com';
  static const String _realm = 'triboka';
  static const String _clientId = 'triboka-mobile';
  static const String _redirectUrl = 'triboka://callback';
  static const String _issuer = '$_keycloakUrl/realms/$_realm';
  static const String _discoveryUrl = '$_issuer/.well-known/openid-configuration';
  
  // State for UI
  bool _isLoading = false;
  User? _currentUser;
  
  bool get isLoading => _isLoading;
  User? get currentUser => _currentUser;
  bool get isLoggedIn => _currentUser != null;
  String get currentRole => _currentUser?.role ?? 'invitado';

  // ... (initService, login, loginWithPassword methods remain same)

  // Native Registration calling Backend Proxy
  Future<bool> register(String email, String password, String firstName, String lastName, String role, {String? location, String? productType}) async {
    _setLoading(true);
    try {
      final response = await http.post(
        Uri.parse('${AppConstants.baseUrl}/api/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
          'firstName': firstName,
          'lastName': lastName,
          'role': role,
          'location': location,
          'productType': productType
        }),
      );

      if (response.statusCode == 201) {
        // Registration successful
        // Optionally auto-login here or just return true to let UI redirect to login
        _setLoading(false);
        return true;
      } else {
        debugPrint('Registration failed: ${response.body}');
        // We could decode error message here to show to user
      }
    } catch (e) {
      debugPrint('Registration error: $e');
    }
    _setLoading(false);
     return false;
  }
  
  // ... (rest of methods)

  // ... imports

  /// Inicializa el servicio y restaura la sesión si es posible
  Future<void> initService() async {
    // 1. Try to load cached user (Offline support)
    await _loadCachedUser();
    
    // 2. Check token validity (Online support)
    final hasValidToken = await _checkSession();
    if (hasValidToken && _currentUser == null) {
      // If we have valid token but no user loaded (edge case), fetch from server
      await _loadUserInfo();
    } 
    // If token is invalid/expired but we have a user, we stay logged in (Offline Mode)
    // In a real scenario, we might want to flag this as "offline_session" to UI.
  }

  // Login con OAuth 2.0 / OIDC (Standard Flow)
  Future<bool> login() async {
    _setLoading(true);
    try {
      final AuthorizationTokenResponse? result = await _appAuth.authorizeAndExchangeCode(
        AuthorizationTokenRequest(
          _clientId,
          _redirectUrl,
          discoveryUrl: _discoveryUrl,
          scopes: ['openid', 'profile', 'email', 'roles', 'offline_access'],
        ),
      );

      if (result != null) {
        await _storeTokens(result.accessToken!, result.refreshToken, result.idToken);
        await _loadUserInfo(); // This now also caches the user
        _setLoading(false);
        return true;
      }
    } catch (e) {
      debugPrint('Login Standard Flow error: $e');
    }
    _setLoading(false);
    return false;
  }

  // Login con Username/Password (Direct Access Grants)
  Future<bool> loginWithPassword(String username, String password, [String? role]) async {
    _setLoading(true);
    
    // MOCK / DEMO MODE for 'admin@triboka.com'
    if (username == 'admin@triboka.com' && password == '123456') {
      await Future.delayed(const Duration(seconds: 1));
      _currentUser = User(
        id: 'mock_user_admin',
        name: 'Administrador Demo',
        email: username,
        role: role ?? 'admin',
        createdAt: DateTime.now(),
      );
      // Cache this mock user too for offline demo
      await _cacheUser(_currentUser!);
      
      _setLoading(false);
      notifyListeners();
      return true;
    }

    try {
      final response = await http.post(
        Uri.parse('$_issuer/protocol/openid-connect/token'),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'client_id': _clientId,
          'username': username,
          'password': password,
          'grant_type': 'password',
          'scope': 'openid profile email roles offline_access',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        await _storeTokens(data['access_token'], data['refresh_token'], data['id_token']);
        await _loadUserInfo(); // Fetches and caches user
        
        _setLoading(false);
        return true;
      } else {
        debugPrint('Login Direct Grant failed: ${response.body}');
      }
    } catch (e) {
      debugPrint('Login Direct Grant error: $e');
    }
    _setLoading(false);
    return false;
  }
  
  // Wrapper for UI compatibility
  Future<bool> loginLegacy(String email, String password, String role) async {
    return loginWithPassword(email, password, role);
  }

  Future<void> _storeTokens(String accessToken, String? refreshToken, String? idToken) async {
    await _secureStorage.write(key: 'access_token', value: accessToken);
    if (refreshToken != null) {
      await _secureStorage.write(key: 'refresh_token', value: refreshToken);
    }
    if (idToken != null) {
      await _secureStorage.write(key: 'id_token', value: idToken);
    }
  }

  Future<String?> getAccessToken() async {
    return await _secureStorage.read(key: 'access_token');
  }

  Future<bool> _checkSession() async {
    final token = await getAccessToken();
    if (token == null) return false;
    
    try {
      // Decode locally to check expiration
      final parts = token.split('.');
      if (parts.length != 3) return false;
      
      final payload = json.decode(utf8.decode(base64Url.decode(base64Url.normalize(parts[1]))));
      final exp = payload['exp'];
      final now = DateTime.now().millisecondsSinceEpoch ~/ 1000;
      
      return exp > now;
    } catch (e) {
      return false;
    }
  }

  Future<void> _loadUserInfo() async {
    final token = await getAccessToken();
    if (token == null) return;

    try {
      final response = await http.get(
        Uri.parse('$_issuer/protocol/openid-connect/userinfo'),
        headers: {'Authorization': 'Bearer $token'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final newUser = User(
          id: data['sub'] ?? 'unknown',
          name: data['name'] ?? data['preferred_username'] ?? 'Usuario',
          email: data['email'] ?? '',
          role: 'user', // We would parse roles here
          createdAt: DateTime.now(),
        );
        _currentUser = newUser;
        await _cacheUser(newUser); // Save for offline
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error getting user info: $e');
      // If network fails but we had a cached user, we might want to keep using it
      // or check if _currentUser is already set from initService.
    }
  }
  
  Future<void> _cacheUser(User user) async {
    final userMap = user.toMap();
    await _secureStorage.write(key: 'cached_user', value: json.encode(userMap));
  }
  
  Future<void> _loadCachedUser() async {
    try {
      final userJson = await _secureStorage.read(key: 'cached_user');
      if (userJson != null) {
        final userMap = json.decode(userJson);
        _currentUser = User.fromMap(userMap);
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error loading cached user: $e');
    }
  }

  Future<void> logout() async {
    await _secureStorage.deleteAll(); // Clears cached_user too
    _currentUser = null;
    notifyListeners();
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}

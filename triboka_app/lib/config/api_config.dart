// lib/config/api_config.dart
class ApiConfig {
  // URL base del API
  static const String baseUrl = 'https://agro.triboka.com/api';
  
  // Endpoints principales
  static const String loginEndpoint = '/auth/login';
  static const String registerEndpoint = '/auth/register';
  static const String profileEndpoint = '/auth/profile';
  static const String lotsEndpoint = '/lots';
  static const String contractsEndpoint = '/contracts';
  static const String companiesEndpoint = '/companies';
  
  // Configuración de timeouts
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  
  // Headers comunes
  static Map<String, String> get headers => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  
  // Headers con autenticación
  static Map<String, String> headersWithAuth(String token) => {
    ...headers,
    'Authorization': 'Bearer $token',
  };
}

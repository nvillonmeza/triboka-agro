import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../utils/constants.dart';

class ApiClient {
  static const String _baseUrl = 'https://agro.triboka.com/api';
  final _storage = const FlutterSecureStorage();

  Future<Map<String, String>> _getHeaders() async {
    final token = await _storage.read(key: 'auth_token');
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  Future<dynamic> get(String endpoint) async {
    final url = Uri.parse('$_baseUrl$endpoint');
    try {
      final headers = await _getHeaders();
      final response = await http.get(url, headers: headers);
      return _handleResponse(response);
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  Future<dynamic> post(String endpoint, dynamic body) async {
    final url = Uri.parse('$_baseUrl$endpoint');
    try {
      final headers = await _getHeaders();
      final response = await http.post(
        url, 
        headers: headers, 
        body: jsonEncode(body),
      );
      return _handleResponse(response);
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  Future<dynamic> put(String endpoint, dynamic body) async {
    final url = Uri.parse('$_baseUrl$endpoint');
    try {
      final headers = await _getHeaders();
      final response = await http.put(
        url, 
        headers: headers, 
        body: jsonEncode(body),
      );
      return _handleResponse(response);
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  dynamic _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isEmpty) return {};
      return jsonDecode(response.body);
    } else if (response.statusCode == 401) {
      throw Exception('Unauthorized'); // Debería disparar logout
    } else {
      throw Exception('Error ${response.statusCode}: ${response.body}');
    }
  }
}


import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart'; // Make sure this exists or use Constants
import '../utils/constants.dart';
import 'auth_service.dart';

class SupportService {
  final AuthService _authService;

  SupportService(this._authService);

  /// Crea un ticket de soporte en el sistema centralizado
  Future<Map<String, dynamic>> createTicket({
    required String subject,
    required String description,
    String priority = 'medium',
  }) async {
    final token = await _authService.getToken();
    if (token == null) return {'success': false, 'error': 'No auth token'};

    try {
      final response = await http.post(
        Uri.parse('${AppConstants.baseUrl}/api/support/tickets'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'subject': subject,
          'description': description,
          'priority': priority,
          'source': 'mobile_app',
        }),
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      } else {
        return {'success': false, 'error': 'Error al crear ticket'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Error de conexión: $e'};
    }
  }
}

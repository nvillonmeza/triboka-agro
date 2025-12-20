// lib/tests/connectivity_test.dart
import 'package:http/http.dart' as http;

Future<void> testBackendConnection() async {
  try {
    print('🔍 Probando conexión con backend...');
    
    final response = await http.get(
      Uri.parse('https://agro.triboka.com/api/health'),
    ).timeout(Duration(seconds: 10));
    
    print('✅ Respuesta recibida: ${response.statusCode}');
    print('📦 Cuerpo: ${response.body}');
    
    if (response.statusCode == 200) {
      print('✅ Backend accesible correctamente');
    }
  } catch (e) {
    print('❌ Error de conexión: $e');
  }
}

void main() async {
  await testBackendConnection();
}

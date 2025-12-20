import 'package:hive_flutter/hive_flutter.dart';
import 'dart:async';

class PublicationService {
  static const String _boxName = 'vitrina_publications';

  /// Guarda una nueva publicación en la base de datos local (Hive)
  Future<void> createPublication(Map<String, dynamic> data) async {
    final box = await Hive.openBox(_boxName);
    
    // Usamos el ID de la data como key, o generamos uno si no existe
    final String key = data['id'] ?? DateTime.now().millisecondsSinceEpoch.toString();
    
    await box.put(key, data);
    print('✅ Publication saved to Hive DB: $key');
  }

  /// Recupera todas las publicaciones
  Future<List<Map<String, dynamic>>> getAllPublications() async {
    final box = await Hive.openBox(_boxName);
    return box.values.map((e) => Map<String, dynamic>.from(e)).toList();
  }

  /// Recupera publicaciones filtradas por visibilidad (Role Based)
  Future<List<Map<String, dynamic>>> getFeedForRole(String userRole) async {
    final all = await getAllPublications();
    
    return all.where((pub) {
      final pubRole = pub['role']; // Rol del que publicó
      
      // Lógica de Ceguera Competitiva (Replicada del Frontend)
      if (userRole == 'exportadora') {
        return pubRole == 'centro' || pubRole == 'proveedor'; 
      } else if (userRole == 'centro') {
        return pubRole == 'exportadora' || pubRole == 'proveedor';
      } else if (userRole == 'proveedor') {
        return pubRole == 'centro' || pubRole == 'exportadora';
      }
      return true; // Admin/Invitado ve todo (opcional)
    }).toList();
  }

  Future<void> deletePublication(String id) async {
    final box = await Hive.openBox(_boxName);
    await box.delete(id);
  }

  // --- Sincronización API (Futuro) ---
  /*
  Future<void> syncPush(String token) async {
    // 1. Obtener no sincronizados
    // 2. POST /api/sync/push
    // 3. Update 'synced' = true
    print('Syncing to agro.triboka.com...');
  }
  */
}

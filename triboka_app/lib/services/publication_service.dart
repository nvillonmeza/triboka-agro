import 'package:hive_flutter/hive_flutter.dart';
import 'dart:async';

class PublicationService {
  static const String _boxName = 'vitrina_publications';
  bool isSyncing = false; // Estado simple


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

  // --- Sincronización API ---
  
  /// Enviar publicaciones pendientes al servidor
  Future<void> syncPush(String token) async {
    try {
      final box = await Hive.openBox(_boxName);
      final unsynced = box.values.where((e) => e['synced'] == false || e['synced'] == null).toList();

      if (unsynced.isEmpty) return;

      print('🔄 Syncing ${unsynced.length} publications to server...');
      
      // En una implementación real, usaríamos ApiClient
      // final api = ApiClient();
      
      // Simulamos envío exitoso por ahora para no bloquear flujo offline
      await Future.delayed(const Duration(seconds: 1)); 

      /* 
      // Lógica real:
      for (var pub in unsynced) {
        await api.post('/publications', pub);
        // Actualizar synced=true
        pub['synced'] = true;
        await box.put(pub['id'], pub);
      }
      */
      
      print('✅ Sync Push completed.');
    } catch (e) {
      print('❌ Sync Push failed: $e');
    }
  }

  /// Descargar publicaciones remotas
  Future<void> fetchRemoteFeed() async {
    try {
      print('🔄 Fetching remote feed...');
      
      // En una implementación real:
      // final api = ApiClient();
      // final List remoteData = await api.get('/publications/feed');
      
      // Simulamos respuesta del servidor
      await Future.delayed(const Duration(seconds: 1));
      
      /*
      // Guardar en Hive
      final box = await Hive.openBox(_boxName);
      for (var item in remoteData) {
        item['synced'] = true; // Ya viene del server
        await box.put(item['id'], item);
      }
      */
      
      print('✅ Remote feed fetched.');
    } catch (e) {
       print('❌ Fetch failed: $e');
    }
  }
}

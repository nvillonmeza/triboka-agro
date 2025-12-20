import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:provider/provider.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'publication_service.dart';
import 'auth_service.dart';

class SyncManager {
  final PublicationService _publicationService = PublicationService();
  Timer? _timer;
  bool _isSyncing = false;
  
  // Singleton pattern
  static final SyncManager _instance = SyncManager._internal();
  factory SyncManager() => _instance;
  SyncManager._internal();

  void startSyncLoop() {
    print('🚀 SyncManager started');
    // Sincronizar al inicio
    _runSync();
    
    // Y cada 5 minutos
    _timer = Timer.periodic(const Duration(minutes: 5), (timer) {
      _runSync();
    });
  }

  void stopSyncLoop() {
    _timer?.cancel();
    print('🛑 SyncManager stopped');
  }

  Future<void> triggerManualSync() async {
    print('👆 Manual Sync Triggered');
    await _runSync();
  }

  Future<void> _runSync() async {
    if (_isSyncing) return;
    
    // Verificar conectividad
    final connectivityResult = await Connectivity().checkConnectivity();
    if (connectivityResult == ConnectivityResult.none) {
      print('⚠️ No internet connection. Skipping sync.');
      return;
    }

    _isSyncing = true;
    try {
      // 1. Push pending data (Upload)
      // Necesitamos el token, pero PublicationService puede manejarlo o se lo pasamos
      // Por simplicidad, asumimos que PublicationService o ApiClient se encargan del storage
      await _publicationService.syncPush('dummy_token');

      // 2. Pull remote data (Download)
      await _publicationService.fetchRemoteFeed();

    } catch (e) {
      print('❌ Sync Error: $e');
    } finally {
      _isSyncing = false;
    }
  }
}

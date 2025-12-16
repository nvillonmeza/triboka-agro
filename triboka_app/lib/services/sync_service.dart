import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:hive/hive.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'auth_service.dart';
import '../utils/constants.dart';
import '../models/contract_model.dart';

class SyncService {
  final AuthService _authService;
  // Use AppConstants for URL
  
  SyncService(this._authService) {
    _initConnectivityMonitor();
  }

  void _initConnectivityMonitor() {
    Connectivity().onConnectivityChanged.listen((ConnectivityResult result) {
      if (result != ConnectivityResult.none) {
        syncPendingTransactions();
      }
    });
  }

  /// Sincroniza datos estáticos (Pull) y cola de transacciones (Push)
  Future<void> performFullSync() async {
    await syncStaticData();
    await syncPendingTransactions();
  }

  /// Descarga actualizaciones desde el servidor (Pull)
  Future<void> syncStaticData() async {
    final token = await _authService.getAccessToken(); // Changed to matches AuthService method
    if (token == null) return;

    final lastSyncBox = await Hive.openBox('sync_meta');
    final lastSync = lastSyncBox.get('last_sync_timestamp', defaultValue: 0);

    try {
      final response = await http.get(
        Uri.parse('${AppConstants.baseUrl}/api/sync/delta?last_sync=$lastSync'),
        headers: {'Authorization': 'Bearer $token'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        await _processServerUpdates(data);
        
        // Actualizar timestamp
        await lastSyncBox.put('last_sync_timestamp', DateTime.now().millisecondsSinceEpoch);
      }
    } catch (e) {
      print('Error syncing static data: $e');
    }
  }

  Future<void> _processServerUpdates(Map<String, dynamic> data) async {
    // 1. Process Contracts
    if (data.containsKey('contracts')) {
      final box = Hive.box<ExportContract>('contracts');
      final List contractsData = data['contracts'];
      
      for (var json in contractsData) {
        final serverContract = ExportContract.fromJson(json);
        
        // Conflict Resolution Strategy: SERVER WINS
        // If we have a local version, we overwrite it regardless of its local state
        // because the server is the source of truth for "synced" status.
        // Exception: If local is 'created' (new ID pending), logic might differ, 
        // but here ID match implies server knows about it.
        
        // Ensure status is synced
        serverContract.syncStatus = 'synced';
        serverContract.lastUpdatedLocal = DateTime.now().millisecondsSinceEpoch;
        
        await box.put(serverContract.id, serverContract);
      }
    }
    
    // 2. Process Fixations
    /*
    if (data.containsKey('fixations')) {
      final box = Hive.box<Fixation>('fixations');
      // ... similar logic
    }
    */
    
    // 3. Process Companies
    /*
    if (data.containsKey('companies')) {
       final box = Hive.box<Company>('companies');
       // ... similar logic
    }
    */
  }

  /// Envía transacciones pendientes al servidor (Push)
  Future<void> syncPendingTransactions() async {
    final connectivityResult = await Connectivity().checkConnectivity();
    if (connectivityResult == ConnectivityResult.none) return;

    final token = await _authService.getAccessToken(); 
    if (token == null) return;

    await _syncContracts(token);
    // await _syncFixations(token); // Future implementation
  }

  Future<void> _syncContracts(String token) async {
    if (!Hive.isBoxOpen('contracts')) return;
    final box = Hive.box<ExportContract>('contracts');
    
    // Find unsynced items
    final unsynced = box.values.where((c) => c.syncStatus != 'synced').toList();
    
    for (var contract in unsynced) {
      bool success = false;
      
      if (contract.syncStatus == 'created') {
        success = await _postContract(contract, token);
      } else if (contract.syncStatus == 'updated') {
        success = await _putContract(contract, token);
      }

      if (success) {
        contract.syncStatus = 'synced';
        contract.save(); // HiveObject save
      }
    }
  }

  Future<bool> _postContract(ExportContract contract, String token) async {
    try {
      final response = await http.post(
        Uri.parse('${AppConstants.baseUrl}/api/contracts'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: json.encode(contract.toJson()),
      );
      return response.statusCode >= 200 && response.statusCode < 300;
    } catch (e) {
      print('Error posting contract: $e');
      return false;
    }
  }
  
  Future<bool> _putContract(ExportContract contract, String token) async {
     // Similar logic for PUT
     return true; // Placeholder
  }

  // Deprecated generic queue methods - Keeping for reference or removal
  /*
  Future<void> queueTransaction(...) async { ... }
  */
}

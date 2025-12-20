import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:hive_flutter/hive_flutter.dart';
import '../utils/constants.dart';

import '../models/contract_model.dart';
import '../services/platform_service.dart'; // Para info de debug si needed

class ContractService extends ChangeNotifier {
  bool _isLoading = false;
  String? _error;
  List<ExportContract> _contracts = [];
  
  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  List<ExportContract> get contracts => _contracts;
  bool _isSimulated = false;
  bool get isSimulated => _isSimulated;

  // Base URL from Config
  String get _baseUrl => AppConstants.baseUrl; 

  // Mock method for generating contracts
  List<ExportContract> _generateMockContracts() {
    return [
      ExportContract(
        id: 101,
        contractCode: 'CTR-2025-001',
        buyerCompanyId: 2,
        exporterCompanyId: 1,
        productType: 'Cacao Fino de Aroma',
        productGrade: 'Grado 1',
        totalVolumeMt: 50.0,
        differentialUsd: 250.0,
        status: 'active',
        createdByUserId: 1,
        startDate: DateTime.now().subtract(const Duration(days: 5)),
        endDate: DateTime.now().add(const Duration(days: 25)),
        fixations: [
          Fixation(id: 1, exportContractId: 101, fixedQuantityMt: 10.0, spotPriceUsd: 3200.0, totalValueUsd: 32000.0, fixationDate: DateTime.now().subtract(const Duration(days: 2)))
        ]
      ),
      ExportContract(
        id: 102,
        contractCode: 'CTR-2025-002',
        buyerCompanyId: 3,
        exporterCompanyId: 1,
        productType: 'Cacao CCN51',
        productGrade: 'Grado 2',
        totalVolumeMt: 100.0,
        differentialUsd: 150.0,
        status: 'draft',
        createdByUserId: 1,
        startDate: DateTime.now(),
        endDate: DateTime.now().add(const Duration(days: 60)),
      ),
    ];
  }

  // Headers con Auth (Mock por el momento o implementar JWT real)
  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer mocking_token_for_dev', // TODO: Integrar con AuthService
  };

  Future<void> initService() async {
    await _loadFromCache();
  }

  Future<void> _loadFromCache() async {
    try {
      final box = Hive.box<ExportContract>('contracts');
      if (box.isNotEmpty) {
        _contracts = box.values.toList();
        // Sort by CreatedAt desc
        _contracts.sort((a, b) => (b.createdAt ?? DateTime.now()).compareTo(a.createdAt ?? DateTime.now()));
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error loading contracts cache: $e');
    }
  }

  Future<void> _saveToCache() async {
    try {
      final box = Hive.box<ExportContract>('contracts');
      // Save all current contracts to box
      for (var contract in _contracts) {
        await box.put(contract.id, contract); 
      }
    } catch (e) {
      debugPrint('Error saving contracts cache: $e');
    }
  }

  /// Cargar lista de contratos
  Future<void> fetchContracts({int page = 1, String? status}) async {
    _isLoading = true;
    _error = null;
    _isSimulated = false; // Reset
    notifyListeners();

    try {
      final queryParams = {
        'page': page.toString(),
        if (status != null) 'status': status,
      };
      
      final uri = Uri.parse('$_baseUrl/contracts').replace(queryParameters: queryParams);
      
      // Try Real Network Call
      try {
           // Uncomment when backend ready
           /* 
           final response = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 3));
           if (response.statusCode == 200) {
              final List data = json.decode(response.body)['contracts'];
              final fetched = data.map((json) => ExportContract.fromJson(json)).toList();
              
              // Clear local cache or Merge? Strategy: Merge/Update
              final box = Hive.box<ExportContract>('contracts');
              for(var c in fetched) {
                 c.syncStatus = 'synced';
                 await box.put(c.id, c);
              }
              await _loadFromCache(); // Reload from updated cache
              return; 
           }
           */
          throw Exception('Backend not ready'); // Force catch for now
      } catch (networkError) {
          debugPrint('⚠️ ContractService: Network failed ($networkError). Switching to SIMULATION.');
          _isSimulated = true;
          
          await Future.delayed(const Duration(milliseconds: 500));
          
          // 1. Load what we have
          await _loadFromCache();
          
          // 2. Mock seeding DISABLED for Production
          /*
          if (_contracts.isEmpty) {
             debugPrint('Seeding Mock Data into Hive...');
             final mocks = _generateMockContracts();
             final box = Hive.box<ExportContract>('contracts');
             for(var c in mocks) {
               await box.put(c.id, c);
             }
             await _loadFromCache();
          }
          */
      }
    } catch (e) {
      _error = 'Error crítico: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Crear nuevo contrato
  Future<ExportContract?> createContract(Map<String, dynamic> contractData) async {
    _isLoading = true;
    notifyListeners();

    try {
      // Logic: Create Local Object -> Save to Hive (status=created) -> Try Network -> Update id/status if success
      
      final newContract = ExportContract(
        id: DateTime.now().millisecondsSinceEpoch, // Temporary ID
        contractCode: contractData['contract_code'] ?? 'CTR-NEW-${DateTime.now().minute}',
        buyerCompanyId: 2, 
        exporterCompanyId: 1, 
        productType: contractData['product_type'], 
        productGrade: contractData['product_grade'], 
        totalVolumeMt: contractData['total_volume_mt'], 
        differentialUsd: contractData['differential_usd'], 
        status: 'draft', 
        createdByUserId: 1,
        startDate: DateTime.parse(contractData['start_date']),
        endDate: DateTime.parse(contractData['end_date']),
        syncStatus: 'created', // Pending Sync
        lastUpdatedLocal: DateTime.now().millisecondsSinceEpoch,
      );

      // Save Local
      final box = Hive.box<ExportContract>('contracts');
      await box.put(newContract.id, newContract);
      _contracts.insert(0, newContract);
      
      // Try Network (Mocked for now)
      try {
         // await http.post(...)
         // If success: newContract.syncStatus = 'synced'; box.put(newContract.id, newContract);
         
         // Mock Network Delay
         await Future.delayed(const Duration(seconds: 1));
         // Assume success for demo
         newContract.syncStatus = 'synced';
         newContract.save(); // HiveObject extension method!
         
      } catch (e) {
         // Keep as 'created' for SyncService to pick up later
         debugPrint('Network failed, kept as pending sync: $e');
      }

      _isLoading = false;
      notifyListeners();
      return newContract;

    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  // Método auxiliar para actualizar fijaciones localmente (usado por FijacionService)
  Future<void> addFixationLocal(int contractId, Fixation fixation) async {
    final index = _contracts.indexWhere((c) => c.id == contractId);
    if (index != -1) {
      var contract = _contracts[index];
      
      // Crear nueva lista de fijaciones
      List<Fixation> newFixations = List.from(contract.fixations ?? []);
      newFixations.add(fixation);
      
      // Actualizar volumen fijado
      double newFixedVolume = contract.fixedVolumeMt + fixation.fixedQuantityMt;
      
      // Actualizar estado si se completó
      String newStatus = contract.status;
      if (newFixedVolume >= contract.totalVolumeMt) {
        newStatus = 'completed';
      }

      // Reemplazar contrato
      final updatedContract = ExportContract(
        id: contract.id,
        contractCode: contract.contractCode,
        buyerCompanyId: contract.buyerCompanyId,
        exporterCompanyId: contract.exporterCompanyId,
        productType: contract.productType,
        productGrade: contract.productGrade,
        totalVolumeMt: contract.totalVolumeMt,
        fixedVolumeMt: newFixedVolume,
        differentialUsd: contract.differentialUsd,
        startDate: contract.startDate,
        endDate: contract.endDate,
        deliveryDate: contract.deliveryDate,
        status: newStatus,
        blockchainContractId: contract.blockchainContractId,
        createdByUserId: contract.createdByUserId,
        createdAt: contract.createdAt,
        updatedAt: DateTime.now(),
        buyerCompany: contract.buyerCompany,
        exporterCompany: contract.exporterCompany,
        fixations: newFixations,
        syncStatus: 'updated', // Pending Sync
        lastUpdatedLocal: DateTime.now().millisecondsSinceEpoch,
      );
      
      // Persist Update
      final box = Hive.box<ExportContract>('contracts');
      await box.put(updatedContract.id, updatedContract);
      
      _contracts[index] = updatedContract;
      notifyListeners();
    }
  }


}

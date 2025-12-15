import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:hive_flutter/hive_flutter.dart';
import '../utils/constants.dart';
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
  String get _baseUrl => ApiConfig.apiBaseUrl; 

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
          Fixation(id: 1, contractId: 101, fixedQuantityMt: 10.0, spotPriceUsd: 3200.0, fixationDate: DateTime.now().subtract(const Duration(days: 2)), status: 'confirmed')
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
      final box = await Hive.openBox('contracts_cache');
      final List<dynamic>? cachedList = box.get('all_contracts');
      
      if (cachedList != null) {
        _contracts = cachedList.map((e) => ExportContract.fromJson(Map<String, dynamic>.from(e))).toList();
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error loading contracts cache: $e');
    }
  }

  Future<void> _saveToCache() async {
    try {
      final box = await Hive.openBox('contracts_cache');
      final jsonList = _contracts.map((e) => e.toJson()).toList();
      await box.put('all_contracts', jsonList);
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
          // final response = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 3));
          // if (response.statusCode == 200) { ... _saveToCache(); return; }
          throw Exception('Backend not ready'); // Force catch for now
      } catch (networkError) {
          debugPrint('⚠️ ContractService: Network failed ($networkError). Switching to SIMULATION.');
          _isSimulated = true;
          
          // Fallback to Mock Data logic
          await Future.delayed(const Duration(milliseconds: 500));
          
          // 1. Try Cache First for offline feel
          await _loadFromCache();
          
          // 2. If Cache empty, generate Mock
          if (_contracts.isEmpty) {
             _contracts = _generateMockContracts();
             await _saveToCache();
          }
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
      // Llamada real
      /*
      final response = await http.post(
        Uri.parse('$_baseUrl/contracts'),
        headers: _headers,
        body: json.encode(contractData),
      );

      if (response.statusCode == 201) {
        final data = json.decode(response.body);
        final newContract = ExportContract.fromJson(data['contract']);
        _contracts.insert(0, newContract);
        await _saveToCache(); // Update cache
        notifyListeners();
        return newContract;
      }
      */
      
      // MOCK CREATION
      await Future.delayed(const Duration(seconds: 2));
      final newMock = ExportContract(
        id: DateTime.now().millisecondsSinceEpoch, 
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
      );
      _contracts.insert(0, newMock);
      await _saveToCache(); // Update cache

      
      _isLoading = false;
      notifyListeners();
      return newMock;

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
      } else if (newFixedVolume > 0 && newStatus == 'active') {
        // Podríamos tener un estado 'partially_fixed' si el backend lo soporta
      }

      // Reemplazar contrato en la lista con la versión actualizada
      _contracts[index] = ExportContract(
        id: contract.id,
        contractCode: contract.contractCode,
        buyerCompanyId: contract.buyerCompanyId,
        exporterCompanyId: contract.exporterCompanyId,
        productType: contract.productType,
        productGrade: contract.productGrade,
        totalVolumeMt: contract.totalVolumeMt,
        fixedVolumeMt: newFixedVolume, // Actualizado
        differentialUsd: contract.differentialUsd,
        startDate: contract.startDate,
        endDate: contract.endDate,
        deliveryDate: contract.deliveryDate,
        status: newStatus, // Actualizado
        blockchainContractId: contract.blockchainContractId,
        createdByUserId: contract.createdByUserId,
        createdAt: contract.createdAt,
        updatedAt: DateTime.now(),
        buyerCompany: contract.buyerCompany,
        exporterCompany: contract.exporterCompany,
        fixations: newFixations, // Actualizado
      );
      
      notifyListeners();
    }
  }

  /// Mock helper para desarrollo UI
  List<ExportContract> _generateMockContracts() {
    return [
      ExportContract(
        id: 1,
        contractCode: 'CTR-2025-AGRO-001',
        buyerCompanyId: 10,
        exporterCompanyId: 1,
        productType: 'Cacao',
        productGrade: 'Grado 1',
        totalVolumeMt: 500.0,
        fixedVolumeMt: 100.0,
        differentialUsd: 250.0,
        startDate: DateTime.now().subtract(const Duration(days: 10)),
        endDate: DateTime.now().add(const Duration(days: 300)),
        status: 'active',
        createdByUserId: 1,
        buyerCompany: Company(id: 10, name: 'Chocolate Global Inc', country: 'USA'),
        exporterCompany: Company(id: 1, name: 'Triboka Agro', country: 'Ecuador'),
      ),
      ExportContract(
        id: 2,
        contractCode: 'CTR-2025-AGRO-002',
        buyerCompanyId: 12,
        exporterCompanyId: 1,
        productType: 'Café',
        productGrade: 'Arábica',
        totalVolumeMt: 1200.0,
        fixedVolumeMt: 0.0,
        differentialUsd: 150.0,
        startDate: DateTime.now(),
        endDate: DateTime.now().add(const Duration(days: 180)),
        status: 'draft',
        createdByUserId: 1,
        buyerCompany: Company(id: 12, name: 'EuroCoffee Ltd', country: 'Germany'),
        exporterCompany: Company(id: 1, name: 'Triboka Agro', country: 'Ecuador'),
      ),
    ];
  }
}

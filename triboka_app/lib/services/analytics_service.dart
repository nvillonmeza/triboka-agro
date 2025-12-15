import 'dart:io'; 
import 'package:flutter/foundation.dart';
import '../utils/constants.dart';

class AnalyticsData {
  // Common
  final double stockKg;
  final int activeContracts;
  
  // Proveedor Specific
  final double qualityScore; // 0-100
  final double dryingProgress; // 0-100
  final String nextDelivery;
  
  // Centro Specific
  final int partnerCount;
  final double capacityOccupied; // 0-100
  final int pendingShipments;
  final String location;

  AnalyticsData({
    this.stockKg = 0,
    this.activeContracts = 0,
    this.qualityScore = 0,
    this.dryingProgress = 0,
    this.nextDelivery = '',
    this.partnerCount = 0,
    this.capacityOccupied = 0,
    this.pendingShipments = 0,
    this.location = '',
  });
}

class AnalyticsService extends ChangeNotifier {
  AnalyticsData? _metrics;
  bool _isLoading = false;
  bool _isSimulated = false; // New flag

  AnalyticsData? get metrics => _metrics;
  bool get isLoading => _isLoading;
  bool get isSimulated => _isSimulated;

  // Simulate fetching data based on role
  Future<void> fetchMetrics(String role) async {
    _isLoading = true;
    _isSimulated = false; // Reset initially
    notifyListeners();

    try {
       // Try Real API Call
       // final response = await http.get(Uri.parse('${ApiConfig.analyticsEndpoint}/$role'));
       
       // Force error for demo until backend is live
       throw const SocketException('Simulated Network Error'); 
       
    } catch (e) {
      // Fallback to simulation
      _isSimulated = true;
      debugPrint('⚠️ AnalyticsService: Connection failed, using SIMULATED data. Error: $e');
      
      // Simulate network delay for Mock
      await Future.delayed(const Duration(milliseconds: 800));

      // Simulate backend response based on role
      switch (role) {
        case 'proveedor':
          _metrics = AnalyticsData(
            stockKg: 2450.5,
            activeContracts: 3,
            qualityScore: 85.0, // A+
            dryingProgress: 65.0,
            nextDelivery: '15 Dic - Centro A',
          );
          break;
        case 'centro':
          _metrics = AnalyticsData(
            stockKg: 14550.0,
            partnerCount: 42,
            capacityOccupied: 78.5,
            pendingShipments: 5,
            location: 'El Triunfo',
          );
          break;
        case 'exportadora':
          _metrics = AnalyticsData(
            activeContracts: 12,
            pendingShipments: 3, 
          );
          break;
        default:
          _metrics = AnalyticsData();
      }
    }

    _isLoading = false;
    notifyListeners();
  }
}

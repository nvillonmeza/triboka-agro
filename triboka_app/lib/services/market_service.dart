import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';

class MarketData {
  final double price;
  final double change;
  final double changePercent;
  final double dayHigh;
  final double dayLow;
  final DateTime timestamp;
  final bool isMarketOpen;
  final bool isOffline; // New field

  MarketData({
    required this.price,
    required this.change,
    required this.changePercent,
    required this.dayHigh,
    required this.dayLow,
    required this.timestamp,
    required this.isMarketOpen,
    this.isOffline = false,
  });
}

class MarketService extends ChangeNotifier {
  // Yahoo Finance Ticker for Cocoa Futures
  static const String _ticker = 'CC=F';
  
  MarketData? _currentData;
  List<double> _intradayPoints = [];
  bool _isLoading = false;
  String? _error;

  MarketData? get currentData => _currentData;
  List<double> get intradayPoints => _intradayPoints;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // ICE Futures U.S. Cocoa Hours (ET)
  // Open: 04:45 AM ET
  // Close: 01:30 PM ET (13:30)
  bool get isMarketOpen {
    final now = DateTime.now().toUtc().subtract(const Duration(hours: 5)); // To ET (approx)
    // Simple check: Mon-Fri
    if (now.weekday > 5) return false;
    
    final start = DateTime(now.year, now.month, now.day, 4, 45);
    final end = DateTime(now.year, now.month, now.day, 13, 30);
    
    return now.isAfter(start) && now.isBefore(end);
  }

  Future<void> initService() async {
    await fetchData();
  }

  Future<void> fetchData() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // 1. Fetch Snapshot
      final url = Uri.parse('https://query1.finance.yahoo.com/v8/finance/chart/$_ticker?interval=5m&range=1d');
      if (kDebugMode) {
        print('Fetching market data from: $url');
      }
      
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final json = jsonDecode(response.body);
        final result = json['chart']['result'][0];
        final meta = result['meta'];
        final quote = result['indicators']['quote'][0];

        final currentPrice = meta['regularMarketPrice']?.toDouble() ?? 0.0;
        final previousClose = meta['chartPreviousClose']?.toDouble() ?? 0.0;
        
        // Extract intraday series
        final List<dynamic> closes = quote['close'] ?? [];
        _intradayPoints = closes
            .where((e) => e != null)
            .map((e) => (e as num).toDouble())
            .toList();

        _currentData = MarketData(
          price: currentPrice,
          change: currentPrice - previousClose,
          changePercent: ((currentPrice - previousClose) / previousClose) * 100,
          dayHigh: meta['regularMarketDayHigh']?.toDouble() ?? currentPrice,
          dayLow: meta['regularMarketDayLow']?.toDouble() ?? currentPrice,
          timestamp: DateTime.fromMillisecondsSinceEpoch(meta['regularMarketTime'] * 1000),
          isMarketOpen: isMarketOpen, 
          isOffline: false,
        );
      } else {
        throw Exception('Failed to load market data: ${response.statusCode}');
      }
    } catch (e) {
      _error = e.toString();
      if (kDebugMode) {
        print('Error fetching market data: $e');
      }
      // Fallback to simulation if network fails
      _generateSimulation();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void _generateSimulation() {
    // Generate realistic Cocoa price simulation aligned with user expectation (~2450)
    final basePrice = 2450.0;
    final now = DateTime.now();
    final randomRaw = (now.millisecondsSinceEpoch % 100) / 100.0;
    final volatility = 15.0; // Lower volatility for stability
    
    final currentPrice = basePrice + (randomRaw * volatility * (randomRaw > 0.5 ? 1 : -1));
    
    _currentData = MarketData(
      price: currentPrice,
      change: currentPrice - basePrice,
      changePercent: ((currentPrice - basePrice) / basePrice) * 100,
      dayHigh: basePrice + 50,
      dayLow: basePrice - 50,
      timestamp: now,
      isMarketOpen: isMarketOpen,
      isOffline: true,
    );
    
    // Simulate chart points
    _intradayPoints = List.generate(20, (i) => basePrice + (i * 2) - 20);
  }
}

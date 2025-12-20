import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';
import 'dart:math';

class MarketData {
  final double price;
  final double change;
  final double changePercent;
  final double dayHigh;
  final double dayLow;
  final double open;
  final DateTime timestamp;
  final bool isMarketOpen;
  final bool isOffline;

  MarketData({
    required this.price,
    required this.change,
    required this.changePercent,
    required this.dayHigh,
    required this.dayLow,
    required this.open,
    required this.timestamp,
    required this.isMarketOpen,
    this.isOffline = false,
  });
}

class MarketService extends ChangeNotifier {
  // Stooq Ticker for Cocoa Futures
  static const String _ticker = 'cc.f';
  
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
      // Fetch from Stooq (CSV format)
      // f=sd2t2ohlc&h&e=csv -> Symbol, Date, Time, Open, High, Low, Close
      final url = Uri.parse('https://stooq.com/q/l/?s=$_ticker&f=sd2t2ohlc&h&e=csv');
      
      if (kDebugMode) {
        print('Fetching market data from: $url');
      }
      
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final csvData = response.body;
        _parseStooqData(csvData);
      } else {
        throw Exception('Failed to load market data: ${response.statusCode}');
      }
    } catch (e) {
      _error = e.toString();
      if (kDebugMode) {
        print('Error fetching market data: $e');
      }
      // Only simulate if we really have no data yet
      if (_currentData == null) {
         _generateSimulationFallback();
      }
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void _parseStooqData(String csv) {
    try {
      final lines = const LineSplitter().convert(csv);
      if (lines.length < 2) throw Exception('Invalid CSV format');
      
      // Header: Symbol,Date,Time,Open,High,Low,Close
      // Data: CC.F,2025-12-16,19:29:55,5935.5,6047,5866,5998
      final values = lines[1].split(',');
      if (values.length < 7) throw Exception('Insufficient data columns');

      final dateStr = values[1]; // 2025-12-16
      final timeStr = values[2]; // 19:29:55
      final open = double.tryParse(values[3]) ?? 0.0;
      final high = double.tryParse(values[4]) ?? 0.0;
      final low = double.tryParse(values[5]) ?? 0.0;
      final price = double.tryParse(values[6]) ?? 0.0; // Close is current price

      final dateTime = DateTime.parse('$dateStr $timeStr');
      
      // Calculate change (using Open as previous ref since we don't have prev close in this short format)
      // Ideally we'd need prev close, but Open is a decent approximation for intraday change
      final change = price - open;
      final changePercent = open != 0 ? (change / open) * 100 : 0.0;

      _currentData = MarketData(
        price: price,
        change: change,
        changePercent: changePercent,
        dayHigh: high,
        dayLow: low,
        open: open,
        timestamp: dateTime,
        isMarketOpen: isMarketOpen,
        isOffline: false,
      );

      _generateRealisticIntradayChart(open, high, low, price);

    } catch (e) {
      debugPrint('Error parsing CSV: $e');
      throw e;
    }
  }

  void _generateRealisticIntradayChart(double open, double high, double low, double close) {
    // Generate ~20 points curve that respects O, H, L, C
    // This is a "pseudo-real" chart because we don't have the minute-by-minute data
    // but we know the boundaries.
    
    final points = <double>[];
    final random = Random();
    final steps = 20;

    // Start at Open
    points.add(open);

    // We need to hit High and Low somewhere in the middle
    // Simple strategy: Divide into 3 sections: Open->High/Low->Low/High->Close
    // This is a naive approximation but better than random noise.
    
    // Determine trend
    bool hitHighFirst = random.nextBool();
    
    for (int i = 1; i < steps - 1; i++) {
       // Interpolate loosely towards targets
       // For now, just Brownian motion constrained by High/Low
       double prev = points.last;
       double drift = (close - open) / steps;
       double shock = (high - low) * 0.1 * (random.nextDouble() - 0.5);
       
       double next = prev + drift + shock;
       
       // Clamp
       if (next > high) next = high;
       if (next < low) next = low;
       
       points.add(next);
    }

    // Force High and Low to be present if they haven't been hit? 
    // Ideally yes, but for UI visual it's okay if it's close.
    // Let's inject High and Low at random indices to guarantee range usage
    int highIdx = 2 + random.nextInt(6);
    int lowIdx = 10 + random.nextInt(6);
    
    if (highIdx < points.length) points[highIdx] = high;
    if (lowIdx < points.length) points[lowIdx] = low;

    // End at Close
    points.add(close);

    _intradayPoints = points;
  }

  void _generateSimulationFallback() {
    // Generate realistic Cocoa price simulation aligned with current market (~6000)
    final basePrice = 6000.0;
    final now = DateTime.now();
    final random = Random();
    
    final currentPrice = basePrice + (random.nextDouble() * 100 - 50);
    
    _currentData = MarketData(
      price: currentPrice,
      change: currentPrice - basePrice,
      changePercent: ((currentPrice - basePrice) / basePrice) * 100,
      dayHigh: basePrice + 50,
      dayLow: basePrice - 50,
      open: basePrice,
      timestamp: now,
      isMarketOpen: isMarketOpen,
      isOffline: true,
    );
    
    _intradayPoints = List.generate(20, (i) => basePrice + (i * 2) - 20);
  }
}

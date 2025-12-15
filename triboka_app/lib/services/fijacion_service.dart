import 'dart:async';
import 'package:flutter/material.dart';
import '../models/contract_model.dart';
import 'contract_service.dart';

// Mantenemos los enums útiles
enum MetodoComunicacion { mensaje, correo, llamada, todas }

/// Servicio para gestionar la simulación de mercado y operaciones de fijación
class FijacionService extends ChangeNotifier {
  // Estado del Mercado (Simulación)
  double _precioNYActual = 2450.0; 
  bool _mercadoAbierto = false;
  bool _modoSimulacion = false;
  
  // Cache local de fijaciones recientes (adicionales a las que vienen en el contrato)
  // Esto es útil para mostrar historial inmediato antes de recargar del backend
  final List<Fixation> _fixationsLocales = [];

  // Getters
  double get precioNYActual => _precioNYActual;
  bool get mercadoAbierto => _mercadoAbierto;
  bool get modoSimulacion => _modoSimulacion;

  FijacionService() {
    _checkMarketHours();
    // Timer para actualizar precio en tiempo real (Simulación de Live Market)
    Timer.periodic(const Duration(seconds: 3), (_) {
      if (_mercadoAbierto) _simularVariacionPrecio();
    });
  }

  void _checkMarketHours() {
    final now = DateTime.now();
    final hour = now.hour;
    // Mercado abierto check simple (05:00 - 11:00)
    _mercadoAbierto = (now.weekday >= 1 && now.weekday <= 5) && (hour >= 5 && hour < 11);
    notifyListeners();
  }

  void _simularVariacionPrecio() {
    // Variación aleatoria entre -2 y +2
    final variacion = (DateTime.now().millisecond % 5) - 2.0;
    _precioNYActual += variacion;
    // Mantener en rango realista
    if (_precioNYActual < 2000) _precioNYActual = 2000;
    if (_precioNYActual > 5000) _precioNYActual = 5000;
    notifyListeners();
  }

  // Simulación manual para demos
  void simularEstadoMercado() {
    _mercadoAbierto = !_mercadoAbierto;
    _modoSimulacion = true;
    notifyListeners();
  }

  String get estadoMercadoTexto {
    if (!_mercadoAbierto) return 'CERRADO (Abre 05:00)';
    if (_modoSimulacion) return 'ABIERTO (SIMULADO)';
    return 'ABIERTO';
  }

  /// Ejecutar una fijación de precio
  /// Retorna el objeto Fixation creado si es exitoso
  Future<Fixation?> realizarFijacion({
    required ExportContract contract,
    required double cantidadMt,
    required ContractService contractService,
  }) async {
    if (!_mercadoAbierto) {
      throw Exception('El mercado está cerrado actualmente.');
    }

    double pendiente = contract.totalVolumeMt - contract.fixedVolumeMt;
    if (cantidadMt > pendiente) {
      throw Exception('La cantidad excede el volumen pendiente (${pendiente} MT).');
    }

    try {
      // 1. Preparar datos de la fijación
      final precioSpot = _precioNYActual;
      final precioFinal = precioSpot + contract.differentialUsd;
      final totalValue = precioFinal * cantidadMt;

      // 2. Crear objeto Fixation (Simulamos respuesta del backend)
      final nuevaFijacion = Fixation(
        id: DateTime.now().millisecondsSinceEpoch,
        exportContractId: contract.id,
        fixedQuantityMt: cantidadMt,
        spotPriceUsd: precioSpot,
        totalValueUsd: totalValue,
        fixationDate: DateTime.now(),
        notes: 'Fijación Mobile App - Mercado $_precioNYActual',
      );

      // 3. Actualizar contrato a través del ContractService
      // En un app real, llamaríamos a un endpoint de fijación específico
      // Aquí simulamos actualizando el contrato localmente
      await contractService.addFixationLocal(contract.id, nuevaFijacion);
      
      _fixationsLocales.insert(0, nuevaFijacion);
      notifyListeners();
      
      return nuevaFijacion;

    } catch (e) {
      debugPrint('Error en fijación: $e');
      rethrow;
    }
  }

  /// Calcular valor estimado de un contrato con el precio actual
  double calcularValorEstimado(ExportContract contract) {
    double pendiente = contract.totalVolumeMt - contract.fixedVolumeMt;
    if (pendiente <= 0) return 0;
    return (precioNYActual + contract.differentialUsd) * pendiente;
  }
}
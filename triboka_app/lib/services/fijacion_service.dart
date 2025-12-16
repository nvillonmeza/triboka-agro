import 'dart:async';
import 'package:flutter/material.dart';
import '../models/contract_model.dart';
import 'contract_service.dart';
import 'market_service.dart';

// Mantenemos los enums útiles
enum MetodoComunicacion { mensaje, correo, llamada, todas }

/// Servicio para gestionar la simulación de mercado y operaciones de fijación
class FijacionService extends ChangeNotifier {
  // Estado (Hereda precio de MarketService)
  final MarketService _marketService; // Injected dependency
  
  // Cache local de fijaciones recientes (adicionales a las que vienen en el contrato)
  final List<Fixation> _fixationsLocales = [];

  // Getters
  // Use MarketService's price if available, else fallback safely
  double get precioNYActual => _marketService.currentData?.price ?? 2450.0;
  bool get mercadoAbierto => _marketService.isMarketOpen;
  bool get modoSimulacion => _marketService.currentData?.isOffline ?? true;

  FijacionService(this._marketService); // Constructor injection

  // DEPRECATED: Internal simulation logic removed in favor of Centralized MarketService
  /*
  void _simularVariacionPrecio() { ... }
  */

  // Simulación manual para demos (Toggle simulated state in MarketService if needed, or just keep local toggle for UI testing?)
  void simularEstadoMercado() {
     // Maybe notify MarketService or just ignore for now as we want centralization
     notifyListeners();
  }

  String get estadoMercadoTexto {
    if (!mercadoAbierto) return 'CERRADO (Abre 05:00)';
    if (modoSimulacion) return 'ABIERTO (SIMULADO)';
    return 'ABIERTO';
  }

  /// Ejecutar una fijación de precio
  /// Retorna el objeto Fixation creado si es exitoso
  Future<Fixation?> realizarFijacion({
    required ExportContract contract,
    required double cantidadMt,
    required ContractService contractService,
  }) async {
    if (!mercadoAbierto) {
      throw Exception('El mercado está cerrado actualmente.');
    }

    double pendiente = contract.totalVolumeMt - contract.fixedVolumeMt;
    if (cantidadMt > pendiente) {
      throw Exception('La cantidad excede el volumen pendiente (${pendiente} MT).');
    }

    try {
      // 1. Preparar datos de la fijación
      final precioSpot = precioNYActual; // Uses getter
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
        notes: 'Fijación Mobile App - Mercado $precioSpot',
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
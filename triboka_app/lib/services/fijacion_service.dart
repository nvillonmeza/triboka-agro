import 'dart:async';
import 'package:flutter/material.dart';

enum EstadoContrato { pendiente, fijado, vencido, parcialmenteFijado, semiFijado }
enum TipoFijacion { productoraExportadora, exportadoraCliente, precioSpot }
enum MetodoComunicacion { mensaje, correo, llamada, todas }

class Contrato {
  final String id;
  final String nombreContraparte;
  final String tipoContraparte; // 'proveedor', 'exportadora', 'cliente'
  final double cantidad; // en TM
  final double cantidadFijada; // en TM
  final double diferencial; // diferencial acordado en USD/TM
  final DateTime fechaCreacion;
  final DateTime fechaLimite;
  final EstadoContrato estado;
  final double? precioFijado; // precio NY al momento de fijación
  final DateTime? fechaFijacion;
  final List<OperacionFijacion> fijaciones;
  
  // Propiedades para semi-fijado
  final DateTime? fechaSemiFijacion; // cuando se inició el semi-fijado
  final double? porcentajeAnticipo; // % del anticipo (60-70%)
  final double? valorAnticipo; // valor del anticipo pagado
  final double? precioSemiFijado; // precio de referencia al momento del semi-fijado

  Contrato({
    required this.id,
    required this.nombreContraparte,
    required this.tipoContraparte,
    required this.cantidad,
    this.cantidadFijada = 0,
    required this.diferencial,
    required this.fechaCreacion,
    required this.fechaLimite,
    required this.estado,
    this.precioFijado,
    this.fechaFijacion,
    this.fijaciones = const [],
    this.fechaSemiFijacion,
    this.porcentajeAnticipo,
    this.valorAnticipo,
    this.precioSemiFijado,
  });

  double get cantidadPendiente => cantidad - cantidadFijada;
  double get porcentajeFijado => (cantidadFijada / cantidad) * 100;
  bool get puedeSerFijado => estado == EstadoContrato.pendiente || estado == EstadoContrato.parcialmenteFijado || estado == EstadoContrato.semiFijado;
  
  // Métodos para semi-fijado
  bool get esSemiFijado => estado == EstadoContrato.semiFijado;
  bool get venceSemiFijado {
    if (fechaSemiFijacion == null) return false;
    final ahora = DateTime.now();
    final diasTranscurridos = ahora.difference(fechaSemiFijacion!).inDays;
    return diasTranscurridos >= 7;
  }
  
  int get diasRestantesSemiFijado {
    if (fechaSemiFijacion == null) return 0;
    final ahora = DateTime.now();
    final diasTranscurridos = ahora.difference(fechaSemiFijacion!).inDays;
    return 7 - diasTranscurridos;
  }
  
  double calcularDiferenciaSemiFijado(double precioActual) {
    if (precioSemiFijado == null) return 0.0;
    return precioActual - precioSemiFijado!;
  }
  
  Color get colorEstado {
    switch (estado) {
      case EstadoContrato.pendiente:
        return Colors.orange;
      case EstadoContrato.fijado:
        return Colors.green;
      case EstadoContrato.vencido:
        return Colors.red;
      case EstadoContrato.parcialmenteFijado:
        return Colors.blue;
      case EstadoContrato.semiFijado:
        return Colors.purple;
    }
  }

  String get estadoTexto {
    switch (estado) {
      case EstadoContrato.pendiente:
        return 'Pendiente';
      case EstadoContrato.fijado:
        return 'Fijado';
      case EstadoContrato.vencido:
        return 'Vencido';
      case EstadoContrato.parcialmenteFijado:
        return 'Parcialmente Fijado';
      case EstadoContrato.semiFijado:
        return 'Semi-Fijado';
    }
  }

  double calcularValorEstimado(double precioNY) {
    return (precioNY + diferencial) * cantidadPendiente;
  }

  double calcularValorFijado() {
    if (precioFijado == null) return 0;
    return (precioFijado! + diferencial) * cantidadFijada;
  }
}

class ReporteAcuerdo {
  final String nombreContraparte;
  final String tipoContraparte;
  final String rolUsuario; // quien está fijando
  final String direccionContraparte;
  final String contactoContraparte;

  ReporteAcuerdo({
    required this.nombreContraparte,
    required this.tipoContraparte,
    required this.rolUsuario,
    this.direccionContraparte = '',
    this.contactoContraparte = '',
  });
}

class OperacionFijacion {
  final String id;
  final String contratoId;
  final double cantidad; // en TM
  final double precioSpot; // precio NY/ICE al momento de fijación
  final double diferencial; // diferencial pactado
  final double valorTotal;
  final DateTime fechaHora;
  final TipoFijacion tipo;
  final List<MetodoComunicacion> metodosUsados;
  final String? observaciones;
  final String ordenFijacion; // número de orden única
  final ReporteAcuerdo acuerdo;

  OperacionFijacion({
    required this.id,
    required this.contratoId,
    required this.cantidad,
    required this.precioSpot,
    required this.diferencial,
    required this.valorTotal,
    required this.fechaHora,
    required this.tipo,
    required this.metodosUsados,
    required this.ordenFijacion,
    required this.acuerdo,
    this.observaciones,
  });

  // Precio final por TM (Spot + Diferencial)
  double get precioFinal => precioSpot + diferencial;
  
  // Precio por quintal (1 TM = 10 qq aproximadamente)
  double get precioPorQuintal => precioFinal / 10;
  
  // Cantidad en quintales
  double get cantidadQuintales => cantidad * 10;
  
  // Información completa del acuerdo
  String get detalleCompleto {
    return '''
REPORTE DE FIJACIÓN
==================
Orden: $ordenFijacion
Fecha/Hora: ${fechaHora.day}/${fechaHora.month}/${fechaHora.year} ${fechaHora.hour}:${fechaHora.minute.toString().padLeft(2, '0')}

PARTES DEL ACUERDO:
${acuerdo.rolUsuario}: Usuario actual
${acuerdo.tipoContraparte}: ${acuerdo.nombreContraparte}

DETALLES COMERCIALES:
Cantidad: ${cantidad.toStringAsFixed(2)} TM (${cantidadQuintales.toStringAsFixed(1)} qq)
Precio Spot (NY): \$${precioSpot.toStringAsFixed(2)}/TM
Diferencial Pactado: \$${diferencial.toStringAsFixed(2)}/TM
Precio Final: \$${precioFinal.toStringAsFixed(2)}/TM
Precio por Quintal: \$${precioPorQuintal.toStringAsFixed(2)}/qq
Valor Total: \$${valorTotal.toStringAsFixed(2)}

COMUNICACIÓN:
${metodosUsados.map((m) => _getMetodoTexto(m)).join(', ')}

${observaciones != null ? 'OBSERVACIONES:\n$observaciones' : ''}
''';
  }
  
  String _getMetodoTexto(MetodoComunicacion metodo) {
    switch (metodo) {
      case MetodoComunicacion.mensaje:
        return 'Mensaje';
      case MetodoComunicacion.correo:
        return 'Correo';
      case MetodoComunicacion.llamada:
        return 'Llamada';
      case MetodoComunicacion.todas:
        return 'Todos los métodos';
    }
  }
}

class FijacionService extends ChangeNotifier {
  List<Contrato> _contratos = [];
  List<OperacionFijacion> _historialFijaciones = [];
  double _precioNYActual = 2450.0; // Mock precio NY actual
  bool _mercadoAbierto = false;
  bool _modoSimulacion = false; // Para indicar si estamos en modo simulación
  
  // Timer para procesar vencimientos automáticos
  Timer? _timerVencimientos;

  List<Contrato> get contratos => _contratos;
  List<OperacionFijacion> get historialFijaciones => _historialFijaciones;
  double get precioNYActual => _precioNYActual;
  bool get mercadoAbierto => _mercadoAbierto;
  bool get modoSimulacion => _modoSimulacion;

  FijacionService() {
    _initializeMockData();
    _checkMarketHours();
    _iniciarTimerVencimientos();
  }

  void _initializeMockData() {
    final now = DateTime.now();
    
    _contratos = [
      Contrato(
        id: 'CON001',
        nombreContraparte: 'Agroarriba S.A.',
        tipoContraparte: 'exportadora',
        cantidad: 50.0,
        cantidadFijada: 25.0,
        diferencial: 150.0,
        fechaCreacion: now.subtract(const Duration(days: 30)),
        fechaLimite: now.add(const Duration(days: 15)),
        estado: EstadoContrato.parcialmenteFijado,
        fijaciones: [],
      ),
      Contrato(
        id: 'CON002',
        nombreContraparte: 'SUMAQAO S.A.C.',
        tipoContraparte: 'exportadora',
        cantidad: 75.0,
        cantidadFijada: 0,
        diferencial: 200.0,
        fechaCreacion: now.subtract(const Duration(days: 15)),
        fechaLimite: now.add(const Duration(days: 30)),
        estado: EstadoContrato.pendiente,
        fijaciones: [],
      ),
      Contrato(
        id: 'CON003',
        nombreContraparte: 'Carlos Mendoza',
        tipoContraparte: 'proveedor',
        cantidad: 25.0,
        cantidadFijada: 25.0,
        diferencial: 100.0,
        fechaCreacion: now.subtract(const Duration(days: 45)),
        fechaLimite: now.subtract(const Duration(days: 5)),
        estado: EstadoContrato.fijado,
        precioFijado: 2380.0,
        fechaFijacion: now.subtract(const Duration(days: 10)),
        fijaciones: [],
      ),
      Contrato(
        id: 'CON004',
        nombreContraparte: 'Ecuacacao Export',
        tipoContraparte: 'exportadora',
        cantidad: 100.0,
        cantidadFijada: 0,
        diferencial: 175.0,
        fechaCreacion: now.subtract(const Duration(days: 5)),
        fechaLimite: now.add(const Duration(days: 45)),
        estado: EstadoContrato.pendiente,
        fijaciones: [],
      ),
    ];

    // Mock de historial de fijaciones
    _historialFijaciones = [
      OperacionFijacion(
        id: 'FIJ001',
        contratoId: 'CON001',
        cantidad: 25.0,
        precioSpot: 2380.0,
        diferencial: 150.0,
        valorTotal: 63250.0, // (2380 + 150) * 25
        fechaHora: now.subtract(const Duration(days: 10, hours: 2)),
        tipo: TipoFijacion.productoraExportadora,
        metodosUsados: [MetodoComunicacion.correo, MetodoComunicacion.mensaje],
        ordenFijacion: 'ORD-FIJ-001',
        acuerdo: ReporteAcuerdo(
          nombreContraparte: 'Agroarriba S.A.',
          tipoContraparte: 'Exportadora',
          rolUsuario: 'Centro de Acopio',
          direccionContraparte: 'Av. Industrial 123, Lima',
          contactoContraparte: 'contacto@agroarriba.com',
        ),
        observaciones: 'Fijación parcial según acuerdo previo',
      ),
      OperacionFijacion(
        id: 'FIJ002',
        contratoId: 'CON003',
        cantidad: 25.0,
        precioSpot: 2420.0,
        diferencial: 100.0,
        valorTotal: 63000.0, // (2420 + 100) * 25
        fechaHora: now.subtract(const Duration(days: 15, hours: 3)),
        tipo: TipoFijacion.productoraExportadora,
        metodosUsados: [MetodoComunicacion.llamada],
        ordenFijacion: 'ORD-FIJ-002',
        acuerdo: ReporteAcuerdo(
          nombreContraparte: 'Carlos Mendoza',
          tipoContraparte: 'Proveedor',
          rolUsuario: 'Centro de Acopio',
          direccionContraparte: 'Km 45 Carretera Central, Huancayo',
          contactoContraparte: '+51 987 654 321',
        ),
        observaciones: 'Fijación completa - Contrato finalizado',
      ),
      OperacionFijacion(
        id: 'FIJ003',
        contratoId: 'CON002',
        cantidad: 35.0,
        precioSpot: 2450.0,
        diferencial: 200.0,
        valorTotal: 92750.0, // (2450 + 200) * 35
        fechaHora: now.subtract(const Duration(days: 5, hours: 1)),
        tipo: TipoFijacion.exportadoraCliente,
        metodosUsados: [MetodoComunicacion.correo, MetodoComunicacion.llamada],
        ordenFijacion: 'ORD-FIJ-003',
        acuerdo: ReporteAcuerdo(
          nombreContraparte: 'SUMAQAO S.A.C.',
          tipoContraparte: 'Exportadora',
          rolUsuario: 'Centro de Acopio',
          direccionContraparte: 'Jr. Comercio 456, Cusco',
          contactoContraparte: 'ventas@sumaqao.com',
        ),
        observaciones: 'Primera fijación parcial del contrato',
      ),
      OperacionFijacion(
        id: 'FIJ004',
        contratoId: 'CON004',
        cantidad: 50.0,
        precioSpot: 2480.0,
        diferencial: 175.0,
        valorTotal: 132750.0, // (2480 + 175) * 50
        fechaHora: now.subtract(const Duration(days: 2, hours: 4)),
        tipo: TipoFijacion.precioSpot,
        metodosUsados: [MetodoComunicacion.todas],
        ordenFijacion: 'ORD-FIJ-004',
        acuerdo: ReporteAcuerdo(
          nombreContraparte: 'Ecuacacao Export',
          tipoContraparte: 'Exportadora Internacional',
          rolUsuario: 'Centro de Acopio',
          direccionContraparte: 'Av. Exportadores 789, Guayaquil, Ecuador',
          contactoContraparte: 'operaciones@ecuacacao.ec',
        ),
        observaciones: 'Fijación urgente por volatilidad del mercado',
      ),
      OperacionFijacion(
        id: 'FIJ005',
        contratoId: 'CON001',
        cantidad: 15.0,
        precioSpot: 2500.0,
        diferencial: 150.0,
        valorTotal: 39750.0, // (2500 + 150) * 15
        fechaHora: now.subtract(const Duration(hours: 6)),
        tipo: TipoFijacion.productoraExportadora,
        metodosUsados: [MetodoComunicacion.mensaje, MetodoComunicacion.correo],
        ordenFijacion: 'ORD-FIJ-005',
        acuerdo: ReporteAcuerdo(
          nombreContraparte: 'Agroarriba S.A.',
          tipoContraparte: 'Exportadora',
          rolUsuario: 'Centro de Acopio',
          direccionContraparte: 'Av. Industrial 123, Lima',
          contactoContraparte: 'contacto@agroarriba.com',
        ),
        observaciones: 'Segunda fijación del contrato - Precio favorable',
      ),
    ];
  }

  void _checkMarketHours() {
    final now = DateTime.now();
    final hour = now.hour;
    
    // Mercado abierto de 5:00 AM a 11:00 AM, lunes a viernes
    _mercadoAbierto = (now.weekday >= 1 && now.weekday <= 5) && 
                     (hour >= 5 && hour < 11);
    
    notifyListeners();
  }

  Future<bool> ejecutarFijacion({
    required String contratoId,
    required double cantidad,
    required List<MetodoComunicacion> metodos,
    String? observaciones,
  }) async {
    if (!_mercadoAbierto) {
      throw Exception('El mercado está cerrado. Horario: 5:00 AM - 11:00 AM');
    }

    final contrato = _contratos.firstWhere((c) => c.id == contratoId);
    
    if (!contrato.puedeSerFijado) {
      throw Exception('Este contrato no puede ser fijado');
    }

    if (cantidad > contrato.cantidadPendiente) {
      throw Exception('La cantidad excede lo pendiente de fijar');
    }

    // Simular variación del precio NY (±$5)
    _precioNYActual += (DateTime.now().millisecond % 11 - 5);

    final valorTotal = (_precioNYActual + contrato.diferencial) * cantidad;

    // Generar número de orden único
    final ordenFijacion = 'ORD-FIJ-${DateTime.now().millisecondsSinceEpoch}';

    // Crear operación de fijación
    final operacion = OperacionFijacion(
      id: 'FIJ${DateTime.now().millisecondsSinceEpoch}',
      contratoId: contratoId,
      cantidad: cantidad,
      precioSpot: _precioNYActual,
      diferencial: contrato.diferencial,
      valorTotal: valorTotal,
      fechaHora: DateTime.now(),
      tipo: TipoFijacion.productoraExportadora,
      metodosUsados: metodos,
      ordenFijacion: ordenFijacion,
      acuerdo: ReporteAcuerdo(
        nombreContraparte: contrato.nombreContraparte,
        tipoContraparte: contrato.tipoContraparte,
        rolUsuario: 'Centro de Acopio', // Este debería venir del usuario actual
        direccionContraparte: 'Dirección no disponible',
        contactoContraparte: 'Contacto no disponible',
      ),
      observaciones: observaciones,
    );

    _historialFijaciones.insert(0, operacion);

    // Actualizar contrato
    final index = _contratos.indexWhere((c) => c.id == contratoId);
    final contratoActualizado = Contrato(
      id: contrato.id,
      nombreContraparte: contrato.nombreContraparte,
      tipoContraparte: contrato.tipoContraparte,
      cantidad: contrato.cantidad,
      cantidadFijada: contrato.cantidadFijada + cantidad,
      diferencial: contrato.diferencial,
      fechaCreacion: contrato.fechaCreacion,
      fechaLimite: contrato.fechaLimite,
      estado: (contrato.cantidadFijada + cantidad >= contrato.cantidad) 
          ? EstadoContrato.fijado 
          : EstadoContrato.parcialmenteFijado,
      precioFijado: contrato.precioFijado ?? _precioNYActual,
      fechaFijacion: contrato.fechaFijacion ?? DateTime.now(),
      fijaciones: [...contrato.fijaciones, operacion],
    );

    _contratos[index] = contratoActualizado;

    // Simular envío de notificaciones
    await _enviarNotificaciones(metodos, operacion, contratoActualizado);

    notifyListeners();
    return true;
  }

  Future<void> _enviarNotificaciones(
    List<MetodoComunicacion> metodos,
    OperacionFijacion operacion,
    Contrato contrato,
  ) async {
    // Simular delay de envío
    await Future.delayed(const Duration(milliseconds: 500));
    
    for (final metodo in metodos) {
      switch (metodo) {
        case MetodoComunicacion.mensaje:
          debugPrint('📱 Mensaje enviado: Fijación ${operacion.id} completada');
          break;
        case MetodoComunicacion.correo:
          debugPrint('📧 Correo enviado: Confirmación fijación ${operacion.cantidad} TM');
          break;
        case MetodoComunicacion.llamada:
          debugPrint('☎️ Llamada programada para confirmación');
          break;
        case MetodoComunicacion.todas:
          debugPrint('🔔 Todas las notificaciones enviadas');
          break;
      }
    }
  }

  void actualizarPrecioNY(double nuevoPrecio) {
    _precioNYActual = nuevoPrecio;
    notifyListeners();
  }

  List<Contrato> getContratosPorEstado(EstadoContrato estado) {
    return _contratos.where((c) => c.estado == estado).toList();
  }

  double get valorTotalPendiente {
    return _contratos
        .where((c) => c.puedeSerFijado)
        .fold(0.0, (sum, c) => sum + c.calcularValorEstimado(_precioNYActual));
  }

  int get totalContratosPendientes {
    return _contratos.where((c) => c.puedeSerFijado).length;
  }

  String get estadoMercado {
    String estado;
    if (_mercadoAbierto) {
      final now = DateTime.now();
      final minutosRestantes = (11 * 60) - (now.hour * 60 + now.minute);
      estado = minutosRestantes > 0 && !_modoSimulacion 
        ? 'Abierto - $minutosRestantes min restantes'
        : 'Abierto';
    } else {
      estado = 'Cerrado - Abre a las 5:00 AM';
    }
    
    return _modoSimulacion ? '$estado (SIMULADO)' : estado;
  }

  // Método para simular el estado del mercado (solo para desarrollo/testing)
  void simularEstadoMercado() {
    _mercadoAbierto = !_mercadoAbierto;
    _modoSimulacion = true; // Activar modo simulación
    
    // Simular cambio de precio cuando cambia el estado
    if (_mercadoAbierto) {
      // Al abrir el mercado, simular ligero incremento (+/- $15)
      _precioNYActual += (DateTime.now().millisecond % 30 - 15);
    } else {
      // Al cerrar el mercado, simular estabilización (+/- $8)
      _precioNYActual += (DateTime.now().millisecond % 16 - 8);
    }
    
    // Asegurar que el precio no sea negativo
    if (_precioNYActual < 2000) _precioNYActual = 2000;
    if (_precioNYActual > 3000) _precioNYActual = 3000;
    
    notifyListeners();
  }
  
  // Método para resetear el mercado a estado automático
  void resetearMercadoAutomatico() {
    _modoSimulacion = false; // Desactivar modo simulación
    _checkMarketHours();
  }

  // Convertir contrato existente a semi-fijado con anticipo
  Future<bool> crearSemiFijado({
    required String contratoId,
    required double porcentajeAnticipo, // 60-70%
  }) async {
    final contrato = _contratos.firstWhere((c) => c.id == contratoId);
    
    if (contrato.estado != EstadoContrato.pendiente) {
      throw Exception('Solo se puede semi-fijar contratos pendientes');
    }

    // Calcular valores del anticipo
    final valorContrato = (precioNYActual + contrato.diferencial) * contrato.cantidad;
    final valorAnticipo = valorContrato * (porcentajeAnticipo / 100);

    // Crear nuevo contrato con estado semi-fijado
    final contratoSemiFijado = Contrato(
      id: contrato.id,
      nombreContraparte: contrato.nombreContraparte,
      tipoContraparte: contrato.tipoContraparte,
      cantidad: contrato.cantidad,
      cantidadFijada: contrato.cantidadFijada,
      diferencial: contrato.diferencial,
      fechaCreacion: contrato.fechaCreacion,
      fechaLimite: contrato.fechaLimite,
      estado: EstadoContrato.semiFijado,
      precioFijado: contrato.precioFijado,
      fechaFijacion: contrato.fechaFijacion,
      fijaciones: contrato.fijaciones,
      fechaSemiFijacion: DateTime.now(),
      porcentajeAnticipo: porcentajeAnticipo,
      valorAnticipo: valorAnticipo,
      precioSemiFijado: precioNYActual,
    );

    // Actualizar en la lista
    final index = _contratos.indexWhere((c) => c.id == contratoId);
    _contratos[index] = contratoSemiFijado;
    
    notifyListeners();
    return true;
  }

  // Procesar vencimientos automáticos de semi-fijados
  void procesarVencimientosSemiFijados() {
    for (int i = 0; i < _contratos.length; i++) {
      final contrato = _contratos[i];
      
      if (contrato.esSemiFijado && contrato.venceSemiFijado) {
        // Liquidar automáticamente
        _liquidarSemiFijadoVencido(contrato);
      }
    }
  }

  void _liquidarSemiFijadoVencido(Contrato contrato) {
    // Calcular diferencia entre precio actual y precio semi-fijado
    final diferenciaPrecio = calcularDiferenciaSemiFijado(contrato);
    final precioFinalVencimiento = precioNYActual + contrato.diferencial;
    
    // Crear operación de fijación automática
    final operacionAutomatica = OperacionFijacion(
      id: 'AUTO-${DateTime.now().millisecondsSinceEpoch}',
      contratoId: contrato.id,
      cantidad: contrato.cantidad,
      precioSpot: precioNYActual,
      diferencial: contrato.diferencial,
      valorTotal: precioFinalVencimiento * contrato.cantidad,
      fechaHora: DateTime.now(),
      tipo: TipoFijacion.precioSpot,
      metodosUsados: [MetodoComunicacion.todas],
      ordenFijacion: 'AUTO-VENC-${DateTime.now().millisecondsSinceEpoch}',
      acuerdo: ReporteAcuerdo(
        nombreContraparte: contrato.nombreContraparte,
        tipoContraparte: contrato.tipoContraparte,
        rolUsuario: 'Sistema Automático',
        direccionContraparte: '',
        contactoContraparte: '',
      ),
      observaciones: 'Liquidación automática por vencimiento de semi-fijado. '
                    'Diferencia: \$${diferenciaPrecio.toStringAsFixed(2)}/TM '
                    '${diferenciaPrecio >= 0 ? "(A favor)" : "(En contra)"}',
    );

    // Crear contrato fijado
    final contratoFijado = Contrato(
      id: contrato.id,
      nombreContraparte: contrato.nombreContraparte,
      tipoContraparte: contrato.tipoContraparte,
      cantidad: contrato.cantidad,
      cantidadFijada: contrato.cantidad,
      diferencial: contrato.diferencial,
      fechaCreacion: contrato.fechaCreacion,
      fechaLimite: contrato.fechaLimite,
      estado: EstadoContrato.fijado,
      precioFijado: precioNYActual,
      fechaFijacion: DateTime.now(),
      fijaciones: [...contrato.fijaciones, operacionAutomatica],
      fechaSemiFijacion: contrato.fechaSemiFijacion,
      porcentajeAnticipo: contrato.porcentajeAnticipo,
      valorAnticipo: contrato.valorAnticipo,
      precioSemiFijado: contrato.precioSemiFijado,
    );

    // Actualizar en la lista
    final index = _contratos.indexWhere((c) => c.id == contrato.id);
    _contratos[index] = contratoFijado;
    
    // Agregar al historial
    _historialFijaciones.insert(0, operacionAutomatica);
    
    notifyListeners();
  }

  // Inicializar timer para verificar vencimientos automáticos cada hora
  void _iniciarTimerVencimientos() {
    // Verificar vencimientos cada hora (en producción podría ser cada 10 minutos)
    _timerVencimientos = Timer.periodic(const Duration(hours: 1), (timer) {
      procesarVencimientosSemiFijados();
    });
    
    // Verificar inmediatamente al iniciar
    procesarVencimientosSemiFijados();
  }

  // Detener el timer cuando el servicio se destruya
  void dispose() {
    _timerVencimientos?.cancel();
    super.dispose();
  }

  double calcularDiferenciaSemiFijado(Contrato contrato) {
    if (!contrato.esSemiFijado || contrato.precioSemiFijado == null) return 0.0;
    return precioNYActual - contrato.precioSemiFijado!;
  }
}
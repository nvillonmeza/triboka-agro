import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

/// Servicio para manejar todas las notificaciones de TRIBOKA
class NotificationService extends ChangeNotifier {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  // Estados de configuración de notificaciones
  bool _notificacionesActivas = true;
  bool _notificacionesChat = true;
  bool _notificacionesAperturaMercado = true;
  bool _notificacionesCierreMercado = true;
  bool _notificacionesOrdenes = true;
  bool _notificacionesConfirmacionOrdenes = true;
  bool _notificacionesPrecios = false;
  
  // Configuraciones de horarios
  TimeOfDay _horarioApertura = const TimeOfDay(hour: 8, minute: 0);
  TimeOfDay _horarioCierre = const TimeOfDay(hour: 17, minute: 0);
  double _umbralCambioPrecio = 2.0;

  // Getters
  bool get notificacionesActivas => _notificacionesActivas;
  bool get notificacionesChat => _notificacionesChat;
  bool get notificacionesAperturaMercado => _notificacionesAperturaMercado;
  bool get notificacionesCierreMercado => _notificacionesCierreMercado;
  bool get notificacionesOrdenes => _notificacionesOrdenes;
  bool get notificacionesConfirmacionOrdenes => _notificacionesConfirmacionOrdenes;
  bool get notificacionesPrecios => _notificacionesPrecios;
  TimeOfDay get horarioApertura => _horarioApertura;
  TimeOfDay get horarioCierre => _horarioCierre;
  double get umbralCambioPrecio => _umbralCambioPrecio;

  // Setters
  void setNotificacionesActivas(bool value) {
    _notificacionesActivas = value;
    notifyListeners();
  }

  void setNotificacionesChat(bool value) {
    _notificacionesChat = value;
    notifyListeners();
  }

  void setNotificacionesAperturaMercado(bool value) {
    _notificacionesAperturaMercado = value;
    notifyListeners();
  }

  void setNotificacionesCierreMercado(bool value) {
    _notificacionesCierreMercado = value;
    notifyListeners();
  }

  void setNotificacionesOrdenes(bool value) {
    _notificacionesOrdenes = value;
    notifyListeners();
  }

  void setNotificacionesConfirmacionOrdenes(bool value) {
    _notificacionesConfirmacionOrdenes = value;
    notifyListeners();
  }

  void setNotificacionesPrecios(bool value) {
    _notificacionesPrecios = value;
    notifyListeners();
  }

  void setHorarioApertura(TimeOfDay horario) {
    _horarioApertura = horario;
    notifyListeners();
  }

  void setHorarioCierre(TimeOfDay horario) {
    _horarioCierre = horario;
    notifyListeners();
  }

  void setUmbralCambioPrecio(double umbral) {
    _umbralCambioPrecio = umbral;
    notifyListeners();
  }

  /// Envía notificación de nuevo mensaje en chat
  void notificarNuevoMensaje(String remitente, String mensaje) {
    if (!_notificacionesActivas || !_notificacionesChat) return;
    
    _mostrarNotificacion(
      titulo: 'Nuevo mensaje de $remitente',
      mensaje: mensaje,
      icono: Icons.chat_bubble,
      tipo: TipoNotificacion.chat,
    );
  }

  /// Envía notificación de apertura del mercado
  void notificarAperturaMercado(double precioActual) {
    if (!_notificacionesActivas || !_notificacionesAperturaMercado) return;
    
    _mostrarNotificacion(
      titulo: '🔔 ¡Mercado NY Abierto!',
      mensaje: 'Precio actual del cacao: \$${precioActual.toStringAsFixed(0)}/TM',
      icono: Icons.trending_up,
      tipo: TipoNotificacion.mercado,
    );
  }

  /// Envía notificación de cierre del mercado
  void notificarCierreMercado(double precioFinal, double cambio) {
    if (!_notificacionesActivas || !_notificacionesCierreMercado) return;
    
    String cambioTexto = cambio >= 0 ? '+${cambio.toStringAsFixed(1)}%' : '${cambio.toStringAsFixed(1)}%';
    
    _mostrarNotificacion(
      titulo: '🔔 Mercado NY Cerrado',
      mensaje: 'Precio final: \$${precioFinal.toStringAsFixed(0)}/TM ($cambioTexto)',
      icono: Icons.trending_down,
      tipo: TipoNotificacion.mercado,
    );
  }

  /// Envía notificación de nueva orden fijada
  void notificarNuevaOrden(String exportadora, double cantidad, double precio) {
    if (!_notificacionesActivas || !_notificacionesOrdenes) return;
    
    _mostrarNotificacion(
      titulo: '📋 Nueva orden fijada',
      mensaje: '$exportadora: ${cantidad.toStringAsFixed(0)} TM a \$${precio.toStringAsFixed(0)}/TM',
      icono: Icons.assignment,
      tipo: TipoNotificacion.orden,
    );
  }

  /// Envía notificación de confirmación de orden
  void notificarConfirmacionOrden(String numeroOrden, String estado) {
    if (!_notificacionesActivas || !_notificacionesConfirmacionOrdenes) return;
    
    _mostrarNotificacion(
      titulo: '✅ Orden confirmada',
      mensaje: 'Orden #$numeroOrden ha sido $estado',
      icono: Icons.check_circle,
      tipo: TipoNotificacion.confirmacion,
    );
  }

  /// Envía notificación de cambio significativo de precio
  void notificarCambioPrecio(double precioAnterior, double precioActual) {
    if (!_notificacionesActivas || !_notificacionesPrecios) return;
    
    double cambio = ((precioActual - precioAnterior) / precioAnterior) * 100;
    
    if (cambio.abs() >= _umbralCambioPrecio) {
      String direccion = cambio > 0 ? '📈' : '📉';
      String cambioTexto = cambio >= 0 ? '+${cambio.toStringAsFixed(1)}%' : '${cambio.toStringAsFixed(1)}%';
      
      _mostrarNotificacion(
        titulo: '$direccion Cambio de precio significativo',
        mensaje: 'Cacao NY: \$${precioActual.toStringAsFixed(0)}/TM ($cambioTexto)',
        icono: Icons.price_change,
        tipo: TipoNotificacion.precio,
      );
    }
  }

  /// Programa notificaciones automáticas del mercado
  void programarNotificacionesMercado() {
    if (!_notificacionesActivas) return;
    
    // TODO: Implementar programación real con WorkManager o similar
    // Por ahora, solo simulamos la funcionalidad
    debugPrint('Programando notificaciones para:');
    debugPrint('- Apertura: ${_horarioApertura.format(_getContext())} EST');
    debugPrint('- Cierre: ${_horarioCierre.format(_getContext())} EST');
  }

  /// Muestra una notificación local
  void _mostrarNotificacion({
    required String titulo,
    required String mensaje,
    required IconData icono,
    required TipoNotificacion tipo,
  }) {
    // TODO: Implementar notificaciones push reales con Firebase
    // Por ahora, mostramos en consola para debugging
    debugPrint('🔔 NOTIFICACIÓN [$tipo]: $titulo - $mensaje');
    
    // En un escenario real, aquí usaríamos Firebase Messaging
    // firebase_messaging.FirebaseMessaging.instance.requestPermission();
  }

  /// Obtiene el contexto actual (simulado)
  BuildContext _getContext() {
    // En implementación real, necesitaríamos acceso al contexto
    // Por ahora retornamos un contexto simulado
    throw UnimplementedError('Contexto no disponible en esta simulación');
  }

  /// Testea todas las notificaciones
  void testearNotificaciones() {
    notificarNuevoMensaje('Carlos Mendoza', '¿Cuál es el precio actual?');
    
    Future.delayed(const Duration(seconds: 2), () {
      notificarAperturaMercado(6319.0);
    });
    
    Future.delayed(const Duration(seconds: 4), () {
      notificarNuevaOrden('SUMAQAO S.A.C.', 1500.0, 6320.0);
    });
    
    Future.delayed(const Duration(seconds: 6), () {
      notificarCambioPrecio(6319.0, 6450.0);
    });
    
    Future.delayed(const Duration(seconds: 8), () {
      notificarCierreMercado(6435.0, 1.8);
    });
    
    Future.delayed(const Duration(seconds: 10), () {
      notificarConfirmacionOrden('ORD-2024-001', 'confirmada');
    });
  }
}

/// Tipos de notificación disponibles
enum TipoNotificacion {
  chat,
  mercado,
  orden,
  confirmacion,
  precio,
}
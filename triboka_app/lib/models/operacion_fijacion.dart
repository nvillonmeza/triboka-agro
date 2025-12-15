class ReporteAcuerdo {
  final String nombreContraparte;
  final String tipoOperacion; // 'compra' o 'venta'
  final String producto;
  final String ubicacion;
  final String condicionesEntrega;
  final String formaPago;

  ReporteAcuerdo({
    required this.nombreContraparte,
    required this.tipoOperacion,
    required this.producto,
    required this.ubicacion,
    required this.condicionesEntrega,
    required this.formaPago,
  });
}

class OperacionFijacion {
  final String id;
  final String ordenFijacion; // Número único de la orden de fijación
  final double cantidad; // En toneladas métricas
  final double precioSpot; // Precio NY/Chicago en $/TM (antes precioNY)
  final double diferencial; // Diferencial pactado en $/TM
  final DateTime fechaHora;
  final String metodoComunicacion; // 'mensaje', 'email', 'llamada', 'todos'
  final String? observaciones;
  final ReporteAcuerdo acuerdo; // Información completa del acuerdo

  OperacionFijacion({
    required this.id,
    required this.ordenFijacion,
    required this.cantidad,
    required this.precioSpot,
    required this.diferencial,
    required this.fechaHora,
    required this.metodoComunicacion,
    this.observaciones,
    required this.acuerdo,
  });

  // Cálculos derivados
  double get precioFinal => precioSpot + diferencial;
  double get valorTotal => precioFinal * cantidad;
  double get precioPorQuintal => precioFinal / 21.772; // 1 TM = 21.772 quintales
  double get cantidadQuintales => cantidad * 21.772;

  // Método para generar reporte completo del acuerdo
  String detalleCompleto() {
    final buffer = StringBuffer();
    
    buffer.writeln('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    buffer.writeln('              REPORTE DE FIJACIÓN DETALLADO');
    buffer.writeln('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    buffer.writeln();
    
    // Información general
    buffer.writeln('📋 INFORMACIÓN GENERAL');
    buffer.writeln('─────────────────────────────────────────────────');
    buffer.writeln('Orden de Fijación: $ordenFijacion');
    buffer.writeln('Fecha y Hora: ${_formatearFechaHora(fechaHora)}');
    buffer.writeln('Contrato ID: $id');
    buffer.writeln();
    
    // Partes del acuerdo
    buffer.writeln('🤝 PARTES DEL ACUERDO');
    buffer.writeln('─────────────────────────────────────────────────');
    buffer.writeln('Contraparte: ${acuerdo.nombreContraparte}');
    buffer.writeln('Tipo de Operación: ${acuerdo.tipoOperacion.toUpperCase()}');
    buffer.writeln('Producto: ${acuerdo.producto}');
    buffer.writeln('Ubicación: ${acuerdo.ubicacion}');
    buffer.writeln();
    
    // Detalles comerciales
    buffer.writeln('💰 DETALLES COMERCIALES');
    buffer.writeln('─────────────────────────────────────────────────');
    buffer.writeln('Cantidad: ${cantidad.toStringAsFixed(2)} TM (${cantidadQuintales.toStringAsFixed(1)} qq)');
    buffer.writeln('Precio Spot (NY): \$${precioSpot.toStringAsFixed(2)} / TM');
    buffer.writeln('Diferencial Pactado: ${diferencial >= 0 ? '+' : ''}\$${diferencial.toStringAsFixed(2)} / TM');
    buffer.writeln('Precio Final: \$${precioFinal.toStringAsFixed(2)} / TM');
    buffer.writeln('Precio por Quintal: \$${precioPorQuintal.toStringAsFixed(2)} / qq');
    buffer.writeln();
    
    // Cálculo del valor total
    buffer.writeln('📊 CÁLCULO DEL VALOR TOTAL');
    buffer.writeln('─────────────────────────────────────────────────');
    buffer.writeln('Fórmula: Precio Final × Cantidad = Valor Total');
    buffer.writeln('Cálculo: \$${precioFinal.toStringAsFixed(2)} × ${cantidad.toStringAsFixed(2)} TM');
    buffer.writeln('VALOR TOTAL: \$${valorTotal.toStringAsFixed(2)}');
    buffer.writeln();
    
    // Términos y condiciones
    buffer.writeln('📋 TÉRMINOS Y CONDICIONES');
    buffer.writeln('─────────────────────────────────────────────────');
    buffer.writeln('Condiciones de Entrega: ${acuerdo.condicionesEntrega}');
    buffer.writeln('Forma de Pago: ${acuerdo.formaPago}');
    buffer.writeln('Método de Comunicación: ${_formatearMetodoComunicacion(metodoComunicacion)}');
    buffer.writeln();
    
    // Observaciones
    if (observaciones != null && observaciones!.isNotEmpty) {
      buffer.writeln('📝 OBSERVACIONES');
      buffer.writeln('─────────────────────────────────────────────────');
      buffer.writeln(observaciones!);
      buffer.writeln();
    }
    
    buffer.writeln('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    buffer.writeln('Reporte generado el ${_formatearFechaHora(DateTime.now())}');
    buffer.writeln('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    return buffer.toString();
  }

  String _formatearFechaHora(DateTime fecha) {
    return '${fecha.day.toString().padLeft(2, '0')}/${fecha.month.toString().padLeft(2, '0')}/${fecha.year} '
           '${fecha.hour.toString().padLeft(2, '0')}:${fecha.minute.toString().padLeft(2, '0')}';
  }

  String _formatearMetodoComunicacion(String metodo) {
    switch (metodo) {
      case 'mensaje':
        return 'Mensaje de texto';
      case 'email':
        return 'Correo electrónico';
      case 'llamada':
        return 'Llamada telefónica';
      case 'todos':
        return 'Todos los métodos';
      default:
        return metodo;
    }
  }
}
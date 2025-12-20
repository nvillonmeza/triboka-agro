import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/fijacion_service.dart';
import '../models/operacion_fijacion.dart';
import '../utils/constants.dart';

class ReporteDetallePage extends StatelessWidget {
  final OperacionFijacion fijacion;

  const ReporteDetallePage({
    Key? key,
    required this.fijacion,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppConstants.backgroundColor,
      appBar: AppBar(
        title: const Text(
          'Reporte de Fijación',
          style: TextStyle(
            fontWeight: FontWeight.w600,
            color: AppConstants.textPrimary,
          ),
        ),
        backgroundColor: AppConstants.cardWhite,
        elevation: 0,
        iconTheme: const IconThemeData(color: AppConstants.textPrimary),
        systemOverlayStyle: SystemUiOverlayStyle.dark,
        actions: [
          IconButton(
            onPressed: () => _compartirReporte(context),
            icon: const Icon(Icons.share),
            tooltip: 'Compartir reporte',
          ),
          IconButton(
            onPressed: () => _exportarPDF(context),
            icon: const Icon(Icons.download),
            tooltip: 'Exportar PDF',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppConstants.defaultPadding),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header del reporte
            _buildHeaderCard(context),
            const SizedBox(height: AppConstants.defaultPadding),
            
            // Resumen ejecutivo
            _buildResumenEjecutivo(context),
            const SizedBox(height: AppConstants.defaultPadding),
            
            // Información del contrato
            _buildContratoCard(context),
            const SizedBox(height: AppConstants.defaultPadding),
            
            // Detalles de precios
            _buildPreciosCard(context),
            const SizedBox(height: AppConstants.defaultPadding),
            
            // Información del acuerdo
            _buildAcuerdoCard(context),
            const SizedBox(height: AppConstants.defaultPadding),
            
            // Cálculos detallados
            _buildCalculosCard(context),
            const SizedBox(height: AppConstants.defaultPadding),
            
            // Observaciones
            if (fijacion.observaciones != null && fijacion.observaciones!.isNotEmpty)
              _buildObservacionesCard(context),
            
            const SizedBox(height: 80), // Espacio para el botón flotante
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _compartirReporte(context),
        backgroundColor: AppConstants.primaryColor,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.share),
        label: const Text('Compartir'),
      ),
    );
  }

  Widget _buildResumenEjecutivo(BuildContext context) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppConstants.primaryColor.withOpacity(0.1),
            AppConstants.secondaryColor.withOpacity(0.05),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
        border: Border.all(
          color: AppConstants.primaryColor.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(AppConstants.defaultPadding * 1.5),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.summarize,
                  color: AppConstants.primaryColor,
                  size: 24,
                ),
                const SizedBox(width: 8),
                Text(
                  'RESUMEN EJECUTIVO',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppConstants.primaryColor,
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Información clave en formato de grid
            Row(
              children: [
                Expanded(
                  child: _buildResumenItem(
                    context,
                    'CANTIDAD',
                    '${fijacion.cantidad.toStringAsFixed(2)} TM',
                    Icons.scale,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildResumenItem(
                    context,
                    'PRECIO FINAL',
                    '\$${fijacion.precioFinal.toStringAsFixed(2)}/TM',
                    Icons.attach_money,
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 12),
            
            Row(
              children: [
                Expanded(
                  child: _buildResumenItem(
                    context,
                    'VALOR TOTAL',
                    '\$${fijacion.valorTotal.toStringAsFixed(2)}',
                    Icons.account_balance_wallet,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildResumenItem(
                    context,
                    'DIFERENCIAL',
                    '${fijacion.diferencial >= 0 ? '+' : ''}\$${fijacion.diferencial.toStringAsFixed(2)}/TM',
                    Icons.trending_up,
                    valueColor: fijacion.diferencial >= 0 ? Colors.green : Colors.red,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResumenItem(
    BuildContext context,
    String label,
    String value,
    IconData icon, {
    Color? valueColor,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppConstants.cardWhite,
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Icon(
            icon,
            color: AppConstants.primaryColor,
            size: 20,
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: AppConstants.textSecondary,
              fontWeight: FontWeight.w500,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              color: valueColor ?? AppConstants.textPrimary,
              fontWeight: FontWeight.w600,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildHeaderCard(BuildContext context) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: AppConstants.cardWhite,
        borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(AppConstants.defaultPadding * 1.5),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // Logo o icono
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppConstants.primaryColor.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.description,
                size: 40,
                color: AppConstants.primaryColor,
              ),
            ),
            
            const SizedBox(height: 16),
            
            Text(
              'REPORTE DE FIJACIÓN',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: AppConstants.textPrimary,
              ),
              textAlign: TextAlign.center,
            ),
            
            const SizedBox(height: 8),
            
            Text(
              'Orden Nº ${fijacion.ordenFijacion}',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: AppConstants.primaryColor,
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
            
            const SizedBox(height: 16),
            
            // Fecha y hora
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: AppConstants.backgroundColor,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                '${_formatFecha(fijacion.fechaHora)} - ${_formatHora(fijacion.fechaHora)}',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w500,
                  color: AppConstants.textSecondary,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildContratoCard(BuildContext context) {
    return _buildSectionCard(
      context,
      'INFORMACIÓN DEL CONTRATO',
      Icons.assignment,
      [
        _buildDetailRow('Contrato ID', fijacion.id),
        _buildDetailRow('Operación ID', fijacion.ordenFijacion),
        _buildDetailRow('Contraparte', fijacion.acuerdo.nombreContraparte),
        _buildDetailRow('Tipo Contraparte', fijacion.acuerdo.tipoOperacion.toUpperCase()),
        _buildDetailRow('Rol Usuario', 'Usuario'), // Fixed hardcoded access
        if (fijacion.acuerdo.ubicacion.isNotEmpty)
          _buildDetailRow('Ubicación', fijacion.acuerdo.ubicacion),
        // contact info not available in current model
      ],
    );
  }

  Widget _buildPreciosCard(BuildContext context) {
    return _buildSectionCard(
      context,
      'DETALLES DE PRECIOS',
      Icons.trending_up,
      [
        _buildDetailRow(
          'Precio Spot (NY)',
          '\$${fijacion.precioSpot.toStringAsFixed(2)} / TM',
          isHighlight: true,
        ),
        _buildDetailRow(
          'Diferencial Pactado',
          '${fijacion.diferencial >= 0 ? '+' : ''}\$${fijacion.diferencial.toStringAsFixed(2)} / TM',
          valueColor: fijacion.diferencial >= 0 ? Colors.green : Colors.red,
        ),
        _buildDetailRow(
          'Precio Final',
          '\$${fijacion.precioFinal.toStringAsFixed(2)} / TM',
          isHighlight: true,
        ),
        _buildDetailRow(
          'Precio por Quintal',
          '\$${fijacion.precioPorQuintal.toStringAsFixed(2)} / qq',
        ),
      ],
    );
  }

  Widget _buildAcuerdoCard(BuildContext context) {
    return _buildSectionCard(
      context,
      'TÉRMINOS DEL ACUERDO',
      Icons.handshake,
      [
        _buildDetailRow('Cantidad en TM', '${fijacion.cantidad.toStringAsFixed(2)} TM'),
        _buildDetailRow('Cantidad en Quintales', '${fijacion.cantidadQuintales.toStringAsFixed(1)} qq'),
        _buildDetailRow('Métodos de Comunicación', _formatearMetodoComunicacion(fijacion.metodoComunicacion)),
      ],
    );
  }

  Widget _buildCalculosCard(BuildContext context) {
    final valorTotalFormateado = '\$${fijacion.valorTotal.toStringAsFixed(2)}';
    
    return _buildSectionCard(
      context,
      'CÁLCULOS DETALLADOS',
      Icons.calculate,
      [
        // Fórmula de cálculo
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppConstants.backgroundColor,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Cálculo del Valor Total:',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: AppConstants.textPrimary,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Precio Final × Cantidad = Valor Total',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontFamily: 'monospace',
                  color: AppConstants.textSecondary,
                ),
              ),
              Text(
                '\$${fijacion.precioFinal.toStringAsFixed(2)} × ${fijacion.cantidad.toStringAsFixed(2)} TM = $valorTotalFormateado',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontFamily: 'monospace',
                  fontWeight: FontWeight.w500,
                  color: AppConstants.textPrimary,
                ),
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 16),
        
        // Valor total destacado
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppConstants.primaryColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: AppConstants.primaryColor.withOpacity(0.3)),
          ),
          child: Column(
            children: [
              Text(
                'VALOR TOTAL DE LA OPERACIÓN',
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                  color: AppConstants.primaryColor,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                valorTotalFormateado,
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppConstants.primaryColor,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildObservacionesCard(BuildContext context) {
    return _buildSectionCard(
      context,
      'OBSERVACIONES',
      Icons.note,
      [
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppConstants.backgroundColor,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            fijacion.observaciones!,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: AppConstants.textSecondary,
              height: 1.5,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSectionCard(BuildContext context, String title, IconData icon, List<Widget> children) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: AppConstants.cardWhite,
        borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(AppConstants.defaultPadding),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header de la sección
            Row(
              children: [
                Icon(icon, color: AppConstants.primaryColor, size: 20),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                    color: AppConstants.textPrimary,
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Contenido de la sección
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value, {bool isHighlight = false, Color? valueColor}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            flex: 2,
            child: Text(
              label,
              style: TextStyle(
                color: AppConstants.textSecondary,
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Expanded(
            flex: 3,
            child: Text(
              value,
              style: TextStyle(
                color: valueColor ?? (isHighlight ? AppConstants.primaryColor : AppConstants.textPrimary),
                fontSize: 14,
                fontWeight: isHighlight ? FontWeight.w600 : FontWeight.w500,
              ),
              textAlign: TextAlign.end,
            ),
          ),
        ],
      ),
    );
  }

  String _formatFecha(DateTime fecha) {
    const meses = [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];
    
    return '${fecha.day} de ${meses[fecha.month - 1]} de ${fecha.year}';
  }

  String _formatHora(DateTime fecha) {
    return '${fecha.hour.toString().padLeft(2, '0')}:${fecha.minute.toString().padLeft(2, '0')}';
  }

  /* REMOVED: TipoFijacion enum is not defined in the model currently.
  String _formatTipoFijacion(TipoFijacion tipo) {
    switch (tipo) {
      case TipoFijacion.productoraExportadora:
        return 'Productora → Exportadora';
      case TipoFijacion.exportadoraCliente:
        return 'Exportadora → Cliente';
      case TipoFijacion.precioSpot:
        return 'Precio Spot';
    }
  }
  */

  /* REMOVED: Mismatch with model which has String, not List<Enum>
  String _formatMetodosComunicacion(List<MetodoComunicacion> metodos) {
    return metodos.map((metodo) {
      switch (metodo) {
        case MetodoComunicacion.mensaje:
          return 'Mensaje';
        case MetodoComunicacion.correo:
          return 'Correo';
        case MetodoComunicacion.llamada:
          return 'Llamada';
        case MetodoComunicacion.todas:
          return 'Todos';
      }
    }).join(', ');
  }
  */

  String _formatearMetodoComunicacion(String metodo) {
     if (metodo == 'mensaje') return 'Mensaje';
     if (metodo == 'correo') return 'Correo';
     if (metodo == 'llamada') return 'Llamada';
     if (metodo == 'todos') return 'Todos';
     return metodo;
  }

  void _compartirReporte(BuildContext context) {
    // Generar texto del reporte
    // Generar texto del reporte
    final reporteTexto = fijacion.detalleCompleto();
    
    // Mostrar opciones de compartir
    showModalBottomSheet(
      context: context,
      builder: (BuildContext context) {
        return Container(
          padding: const EdgeInsets.all(AppConstants.defaultPadding),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Compartir Reporte',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 20),
              
              ListTile(
                leading: const Icon(Icons.copy),
                title: const Text('Copiar al portapapeles'),
                onTap: () {
                  Clipboard.setData(ClipboardData(text: reporteTexto));
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Reporte copiado al portapapeles')),
                  );
                },
              ),
              
              ListTile(
                leading: const Icon(Icons.email),
                title: const Text('Enviar por email'),
                onTap: () {
                  Navigator.pop(context);
                  _enviarPorEmail(context, reporteTexto);
                },
              ),
              
              ListTile(
                leading: const Icon(Icons.message),
                title: const Text('Compartir como mensaje'),
                onTap: () {
                  Navigator.pop(context);
                  _compartirMensaje(context, reporteTexto);
                },
              ),
            ],
          ),
        );
      },
    );
  }

  void _exportarPDF(BuildContext context) {
    // Implementar exportación a PDF
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Funcionalidad de exportar PDF próximamente disponible'),
        backgroundColor: AppConstants.primaryColor,
      ),
    );
  }

  void _enviarPorEmail(BuildContext context, String contenido) {
    // Implementar envío por email
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Abriendo cliente de email...'),
        backgroundColor: AppConstants.primaryColor,
      ),
    );
  }

  void _compartirMensaje(BuildContext context, String contenido) {
    // Implementar compartir como mensaje
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Abriendo aplicación de mensajes...'),
        backgroundColor: AppConstants.primaryColor,
      ),
    );
  }
}
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../utils/constants.dart';
import '../services/fijacion_service.dart';
import 'reporte_detalle_page.dart';

class GestionPage extends StatefulWidget {
  const GestionPage({super.key});

  @override
  State<GestionPage> createState() => _GestionPageState();
}

class _GestionPageState extends State<GestionPage> with TickerProviderStateMixin {
  String _rolActual = 'centro'; // Mock: centro, proveedor, exportadora
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppConstants.backgroundLight,
      appBar: AppBar(
        title: const Text('Gestión'),
        centerTitle: true,
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.swap_horiz),
            tooltip: 'Cambiar rol (Demo)',
            onSelected: (String value) {
              setState(() {
                _rolActual = value;
              });
            },
            itemBuilder: (BuildContext context) => [
              const PopupMenuItem(
                value: 'proveedor',
                child: Text('👨‍🌾 Proveedor'),
              ),
              const PopupMenuItem(
                value: 'centro',
                child: Text('🏠 Centro de Acopio'),
              ),
              const PopupMenuItem(
                value: 'exportadora',
                child: Text('🚢 Exportadora'),
              ),
            ],
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(
              icon: Icon(Icons.business),
              text: 'General',
            ),
            Tab(
              icon: Icon(Icons.assignment),
              text: 'Contratos',
            ),
            Tab(
              icon: Icon(Icons.trending_up),
              text: 'Fijaciones',
            ),
          ],
        ),
      ),
      body: Consumer<FijacionService>(
        builder: (context, fijacionService, child) {
          return TabBarView(
            controller: _tabController,
            children: [
              _buildGeneralTab(_rolActual, fijacionService),
              _buildContratosTab(fijacionService),
              _buildFijacionesTab(fijacionService),
            ],
          );
        },
      ),
    );
  }

  Widget _buildGeneralTab(String rol, FijacionService fijacionService) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppConstants.defaultPadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header con información del rol
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(AppConstants.largePadding),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: _getGradientColors(rol),
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      _getRolIcon(rol),
                      color: Colors.white,
                      size: 28,
                    ),
                    const SizedBox(width: 12),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _getRolTitle(rol),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 20,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        Text(
                          _getRolDescription(rol),
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.9),
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
          
          const SizedBox(height: AppConstants.largePadding),
          
          // Panel de estado del mercado (solo para exportadoras)
          if (rol == 'exportadora') ...[
            _buildMarketStatusPanel(fijacionService),
            const SizedBox(height: AppConstants.largePadding),
          ],
          
          // Métricas principales según el rol
          Text(
            'Métricas principales',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
              color: AppConstants.textPrimary,
            ),
          ),
          
          const SizedBox(height: AppConstants.defaultPadding),
          
          // Grid de cards con métricas
          GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 3,
            crossAxisSpacing: AppConstants.smallPadding,
            mainAxisSpacing: AppConstants.smallPadding,
            childAspectRatio: 0.9,
            children: _buildMetricCards(rol, fijacionService),
          ),
          
          const SizedBox(height: AppConstants.largePadding),
          
          // Detalles específicos del rol
          _buildRoleDetails(rol),
        ],
      ),
    );
  }

  List<Color> _getGradientColors(String rol) {
    switch (rol) {
      case 'proveedor':
        return [Colors.green.shade600, Colors.green.shade400];
      case 'exportadora':
        return [Colors.blue.shade600, Colors.blue.shade400];
      default: // centro
        return [AppConstants.primaryColor, AppConstants.secondaryColor];
    }
  }

  IconData _getRolIcon(String rol) {
    switch (rol) {
      case 'proveedor':  
        return Icons.agriculture;
      case 'exportadora':
        return Icons.local_shipping;
      default: // centro
        return Icons.home_work;
    }
  }

  String _getRolTitle(String rol) {
    switch (rol) {
      case 'proveedor':
        return 'Proveedor';
      case 'exportadora':
        return 'Exportadora';
      default: // centro
        return 'Centro de Acopio';
    }
  }

  String _getRolDescription(String rol) {
    switch (rol) {
      case 'proveedor':
        return 'Gestiona tu producción y entregas';
      case 'exportadora':
        return 'Coordina contratos y exportaciones';
      default: // centro
        return 'Administra ubicación y relaciones';
    }
  }

  List<Widget> _buildMetricCards(String rol, FijacionService fijacionService) {
    switch (rol) {
      case 'proveedor':
        return [
          _buildMetricCard('Stock declarado', '2,450 kg', Icons.inventory_2, Colors.green),
          _buildMetricCard('Proceso secado', '65%', Icons.schedule, Colors.orange),
          _buildMetricCard('Contratos activos', '${fijacionService.contratos.length}', Icons.assignment, Colors.blue),
        ];
      case 'exportadora':
        return [
          _buildMetricCard('Contratos activos', '${fijacionService.totalContratosPendientes}', Icons.assignment, Colors.blue),
          _buildMetricCard('Precio NY', '\$${fijacionService.precioNYActual.toStringAsFixed(0)}', Icons.trending_up, Colors.green),
          _buildMetricCard('Mercado', fijacionService.mercadoAbierto ? 'Abierto' : 'Cerrado', Icons.schedule, fijacionService.mercadoAbierto ? Colors.green : Colors.red),
        ];
      default: // centro
        return [
          _buildMetricCard('Ubicación', 'El Triunfo', Icons.location_on, Colors.red),
          _buildMetricCard('Stock actual', '4,550 kg', Icons.inventory, Colors.green),
          _buildMetricCard('Proveedores', '12', Icons.people, Colors.blue),
        ];
    }
  }

  Widget _buildMetricCard(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(AppConstants.smallPadding),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(AppConstants.borderRadius),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 11,
              color: color,
              fontWeight: FontWeight.w500,
            ),
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 14,
              color: color,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildRoleDetails(String rol) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppConstants.defaultPadding),
      decoration: BoxDecoration(
        color: AppConstants.cardWhite,
        borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
        boxShadow: const [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 8,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Detalles de gestión',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
              color: AppConstants.textPrimary,
            ),
          ),
          const SizedBox(height: AppConstants.defaultPadding),
          ..._getRoleDetailItems(rol),
        ],
      ),
    );
  }

  List<Widget> _getRoleDetailItems(String rol) {
    switch (rol) {
      case 'proveedor':
        return [
          _buildDetailItem('Próxima entrega', 'Centro Norte - 25/Oct/2025'),
          _buildDetailItem('Tiempo restante secado', '3 días estimados'),
          _buildDetailItem('Estado del contrato', 'Activo'),
        ];
      case 'exportadora':
        return [
          _buildDetailItem('Entregas en tránsito', '5 lotes programados'),
          _buildDetailItem('Próximas recepciones', '2 centros confirmados'),
          _buildDetailItem('Estado general', 'En proceso'),
        ];
      default: // centro
        return [
          _buildDetailItem('Contratos con exportadoras', 'Agroarriba, Ecuacacao'),
          _buildDetailItem('Humedad promedio almacenada', '7.8%'),
          _buildDetailItem('Capacidad ocupada', '78% de capacidad total'),
        ];
    }
  }

  Widget _buildDetailItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            flex: 2,
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w500,
                color: AppConstants.textPrimary,
              ),
            ),
          ),
          Expanded(
            flex: 3,
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: AppConstants.textSecondary,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMarketStatusPanel(FijacionService service) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.all(AppConstants.defaultPadding),
      padding: const EdgeInsets.all(AppConstants.defaultPadding),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: service.mercadoAbierto
              ? [Colors.green.shade600, Colors.green.shade400]
              : [Colors.red.shade600, Colors.red.shade400],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Flexible(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                  Row(
                    children: [
                      Icon(
                        service.mercadoAbierto ? Icons.schedule : Icons.schedule_send,
                        color: Colors.white,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Flexible(
                        child: Text(
                          service.estadoMercado,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Precio NY: \$${service.precioNYActual.toStringAsFixed(0)}/TM',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.9),
                      fontSize: 14,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    '${service.totalContratosPendientes}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    'Contratos pendientes',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.9),
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ],
          ),
          
          // Botones de simulación (solo para desarrollo)
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                flex: 2,
                child: OutlinedButton.icon(
                  onPressed: () {
                    service.simularEstadoMercado();
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(
                          service.mercadoAbierto 
                            ? 'Mercado simulado como ABIERTO' 
                            : 'Mercado simulado como CERRADO',
                        ),
                        backgroundColor: service.mercadoAbierto 
                          ? Colors.green 
                          : Colors.red,
                        duration: const Duration(seconds: 2),
                      ),
                    );
                  },
                  icon: Icon(
                    service.mercadoAbierto ? Icons.pause_circle : Icons.play_circle,
                    color: Colors.white,
                    size: 16,
                  ),
                  label: Text(
                    service.mercadoAbierto ? 'Simular Cierre' : 'Simular Apertura',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                    ),
                  ),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Colors.white, width: 1.5),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 8),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                flex: 1,
                child: OutlinedButton.icon(
                  onPressed: () {
                    service.resetearMercadoAutomatico();
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Mercado restablecido a estado automático'),
                        backgroundColor: Colors.blue,
                        duration: Duration(seconds: 2),
                      ),
                    );
                  },
                  icon: const Icon(
                    Icons.refresh,
                    color: Colors.white,
                    size: 16,
                  ),
                  label: const Text(
                    'Auto',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                    ),
                  ),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Colors.white, width: 1.5),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 8),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildContratosTab(FijacionService service) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppConstants.defaultPadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Contratos Activos',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
              color: AppConstants.textPrimary,
            ),
          ),
          const SizedBox(height: AppConstants.defaultPadding),
          
          ...service.contratos.map((contrato) => _buildContratoCard(contrato, service)),
        ],
      ),
    );
  }

  Widget _buildContratoCard(Contrato contrato, FijacionService service) {
    return Container(
      margin: const EdgeInsets.only(bottom: AppConstants.defaultPadding),
      child: Material(
        color: AppConstants.cardWhite,
        borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
        elevation: 3,
        shadowColor: Colors.black12,
        child: Padding(
          padding: const EdgeInsets.all(AppConstants.defaultPadding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header del contrato
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          contrato.nombreContraparte,
                          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.w600,
                            color: AppConstants.textPrimary,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          contrato.id,
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: AppConstants.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: contrato.colorEstado.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: contrato.colorEstado.withOpacity(0.3)),
                    ),
                    child: Text(
                      contrato.estadoTexto,
                      style: TextStyle(
                        color: contrato.colorEstado,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: AppConstants.defaultPadding),
              
              // Detalles del contrato
              _buildContractDetail('Cantidad Total', '${contrato.cantidad.toStringAsFixed(1)} TM'),
              _buildContractDetail('Cantidad Fijada', '${contrato.cantidadFijada.toStringAsFixed(1)} TM'),
              _buildContractDetail('Pendiente', '${contrato.cantidadPendiente.toStringAsFixed(1)} TM'),
              _buildContractDetail('Diferencial', '\$${contrato.diferencial.toStringAsFixed(0)}/TM'),
              _buildContractDetail('Valor Estimado', '\$${contrato.calcularValorEstimado(service.precioNYActual).toStringAsFixed(0)}'),
              
              if (contrato.cantidadFijada > 0 && contrato.precioFijado != null) ...[
                const Divider(),
                _buildContractDetail('Precio Fijado', '\$${(contrato.precioFijado! + contrato.diferencial).toStringAsFixed(0)}/TM'),
                _buildContractDetail('Valor Fijado', '\$${contrato.calcularValorFijado().toStringAsFixed(0)}'),
              ],
              
              // Progreso de fijación
              if (contrato.porcentajeFijado > 0) ...[
                const SizedBox(height: AppConstants.defaultPadding),
                Row(
                  children: [
                    Expanded(
                      child: LinearProgressIndicator(
                        value: contrato.porcentajeFijado / 100,
                        backgroundColor: Colors.grey.shade300,
                        valueColor: AlwaysStoppedAnimation<Color>(contrato.colorEstado),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '${contrato.porcentajeFijado.toStringAsFixed(1)}%',
                      style: TextStyle(
                        color: contrato.colorEstado,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ],
              
              // Botón de fijación
              if (contrato.puedeSerFijado && service.mercadoAbierto) ...[
                const SizedBox(height: AppConstants.defaultPadding),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () => _mostrarDialogoFijacion(contrato, service),
                    icon: const Icon(Icons.trending_up),
                    label: const Text('Realizar Fijación'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppConstants.primaryColor,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildContractDetail(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: AppConstants.textSecondary,
            ),
          ),
          Text(
            value,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w500,
              color: AppConstants.textPrimary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFijacionesTab(FijacionService service) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppConstants.defaultPadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Panel de estado del mercado
          _buildMarketStatusPanel(service),
          const SizedBox(height: AppConstants.largePadding),
          
          // Historial de fijaciones
          Text(
            'Historial de Fijaciones',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
              color: AppConstants.textPrimary,
            ),
          ),
          const SizedBox(height: AppConstants.defaultPadding),
          
          if (service.historialFijaciones.isEmpty)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(AppConstants.largePadding),
              decoration: BoxDecoration(
                color: AppConstants.cardWhite,
                borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
                border: Border.all(color: Colors.grey.shade300),
              ),
              child: Column(
                children: [
                  Icon(
                    Icons.history,  
                    size: 48,
                    color: AppConstants.textSecondary,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'No hay fijaciones registradas',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      color: AppConstants.textSecondary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Las operaciones de fijación aparecerán aquí',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppConstants.textSecondary,
                    ),
                  ),
                ],
              ),
            )
          else
            ...service.historialFijaciones.map((fijacion) => _buildHistorialCard(fijacion)),
        ],
      ),
    );
  }



  Widget _buildHistorialCard(OperacionFijacion fijacion) {
    return Container(
      margin: const EdgeInsets.only(bottom: AppConstants.defaultPadding),
      child: Material(
        color: AppConstants.cardWhite,
        borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
        elevation: 2,
        shadowColor: Colors.black12,
        child: Padding(
          padding: const EdgeInsets.all(AppConstants.defaultPadding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header con botón de reporte
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Orden: ${fijacion.ordenFijacion}',
                          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.w600,
                            color: AppConstants.textPrimary,
                          ),
                        ),
                        Text(
                          '${fijacion.fechaHora.day}/${fijacion.fechaHora.month}/${fijacion.fechaHora.year} ${fijacion.fechaHora.hour}:${fijacion.fechaHora.minute.toString().padLeft(2, '0')}',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: AppConstants.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    onPressed: () => _mostrarReporteDetallado(fijacion),
                    icon: const Icon(Icons.description),
                    tooltip: 'Ver reporte completo',
                    style: IconButton.styleFrom(
                      backgroundColor: AppConstants.primaryColor.withOpacity(0.1),
                      foregroundColor: AppConstants.primaryColor,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 8),
              
              // Detalles resumidos
              _buildContractDetail('Contraparte', fijacion.acuerdo.nombreContraparte),
              _buildContractDetail('Cantidad', '${fijacion.cantidad.toStringAsFixed(2)} TM (${fijacion.cantidadQuintales.toStringAsFixed(1)} qq)'),
              _buildContractDetail('Precio Spot', '\$${fijacion.precioSpot.toStringAsFixed(2)}/TM'),
              _buildContractDetail('Diferencial', '\$${fijacion.diferencial.toStringAsFixed(2)}/TM'),
              _buildContractDetail('Precio Final', '\$${fijacion.precioFinal.toStringAsFixed(2)}/TM'),
              _buildContractDetail('Precio por qq', '\$${fijacion.precioPorQuintal.toStringAsFixed(2)}/qq'),
              _buildContractDetail('Valor Total', '\$${fijacion.valorTotal.toStringAsFixed(2)}'),
              
              if (fijacion.observaciones != null) ...[
                const SizedBox(height: 8),
                Text(
                  fijacion.observaciones!,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppConstants.textSecondary,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
              
              // Botón de reporte completo
              const SizedBox(height: AppConstants.defaultPadding),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () => _mostrarReporteDetallado(fijacion),
                  icon: const Icon(Icons.picture_as_pdf),
                  label: const Text('Generar Reporte Completo'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: AppConstants.primaryColor,
                    side: BorderSide(color: AppConstants.primaryColor),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _mostrarReporteDetallado(OperacionFijacion fijacion) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => ReporteDetallePage(fijacion: fijacion),
      ),
    );
  }

  void _mostrarDialogoFijacion(Contrato contrato, FijacionService service) {
    showDialog(
      context: context,
      builder: (context) => FijacionDialog(
        contrato: contrato,
        service: service,
      ),
    );
  }
}

class FijacionDialog extends StatefulWidget {
  final Contrato contrato;
  final FijacionService service;

  const FijacionDialog({
    super.key,
    required this.contrato,
    required this.service,
  });

  @override
  State<FijacionDialog> createState() => _FijacionDialogState();
}

class _FijacionDialogState extends State<FijacionDialog> {
  final TextEditingController _cantidadController = TextEditingController();
  final TextEditingController _observacionesController = TextEditingController();
  final Set<MetodoComunicacion> _metodosSeleccionados = {};
  bool _isLoading = false;
  bool _esSemiFijado = false;
  double _porcentajeAnticipo = 60.0;

  @override
  void initState() {
    super.initState();
    _cantidadController.text = widget.contrato.cantidadPendiente.toString();
  }

  @override
  Widget build(BuildContext context) {
    final cantidad = double.tryParse(_cantidadController.text) ?? 0;
    final valorEstimado = (widget.service.precioNYActual + widget.contrato.diferencial) * cantidad;

    return AlertDialog(
      title: const Text('💰 Operación de Fijación'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Contrato: ${widget.contrato.nombreContraparte}',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 16),
            
            // Información del precio
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Precios Actuales',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w600,
                      color: Colors.blue.shade700,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Precio NY:'),
                      Text('\$${widget.service.precioNYActual.toStringAsFixed(0)}/TM'),
                    ],
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Diferencial:'),
                      Text('\$${widget.contrato.diferencial.toStringAsFixed(0)}/TM'),
                    ],
                  ),
                  const Divider(),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Precio Final:',
                        style: TextStyle(fontWeight: FontWeight.w600),
                      ),
                      Text(
                        '\$${(widget.service.precioNYActual + widget.contrato.diferencial).toStringAsFixed(0)}/TM',
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          color: Colors.green.shade700,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Cantidad a fijar
            TextField(
              controller: _cantidadController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: 'Cantidad a fijar (TM)',
                hintText: 'Máximo: ${widget.contrato.cantidadPendiente} TM',
                border: const OutlineInputBorder(),
                suffixText: 'TM',
              ),
              onChanged: (_) => setState(() {}),
            ),
            
            const SizedBox(height: 16),
            
            // Valor estimado
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.green.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.green.shade200),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Valor Total Estimado:',
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                      color: Colors.green.shade700,
                    ),
                  ),
                  Text(
                    '\$${valorEstimado.toStringAsFixed(0)}',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: Colors.green.shade700,
                    ),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Opción Semi-Fijado
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.purple.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.purple.shade200),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Checkbox(
                        value: _esSemiFijado,
                        onChanged: (value) {
                          setState(() {
                            _esSemiFijado = value ?? false;
                          });
                        },
                        activeColor: Colors.purple.shade600,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Fijación Semi-Fijada',
                              style: TextStyle(
                                fontWeight: FontWeight.w600,
                                color: Colors.purple.shade700,
                              ),
                            ),
                            Text(
                              'Anticipo con 7 días para fijar precio final',
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.purple.shade600,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  
                  if (_esSemiFijado) ...[
                    const SizedBox(height: 12),
                    Text(
                      'Porcentaje de Anticipo: ${_porcentajeAnticipo.toInt()}%',
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        color: Colors.purple.shade700,
                      ),
                    ),
                    Slider(
                      value: _porcentajeAnticipo,
                      min: 60,
                      max: 70,
                      divisions: 10,
                      label: '${_porcentajeAnticipo.toInt()}%',
                      activeColor: Colors.purple.shade600,
                      onChanged: (value) {
                        setState(() {
                          _porcentajeAnticipo = value;
                        });
                      },
                    ),
                    
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.purple.shade100,
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(color: Colors.purple.shade300),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Anticipo: \$${(valorEstimado * _porcentajeAnticipo / 100).toStringAsFixed(0)}',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.purple.shade800,
                            ),
                          ),
                          Text(
                            'Saldo: \$${(valorEstimado * (100 - _porcentajeAnticipo) / 100).toStringAsFixed(0)}',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.purple.shade700,
                            ),
                          ),
                        ],
                      ),
                    ),
                    
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.orange.shade50,
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(color: Colors.orange.shade300),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.schedule, color: Colors.orange.shade600, size: 16),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'Plazo máximo: 7 días para liquidación automática',
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w500,
                                color: Colors.orange.shade800,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Métodos de comunicación
            Text(
              'Métodos de Comunicación:',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            
            Wrap(
              spacing: 8,
              children: [
                _buildMetodoChip(MetodoComunicacion.mensaje, '📱 Mensaje'),
                _buildMetodoChip(MetodoComunicacion.correo, '📧 Correo'),
                _buildMetodoChip(MetodoComunicacion.llamada, '☎️ Llamada'),
                _buildMetodoChip(MetodoComunicacion.todas, '🔔 Todas'),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Observaciones
            TextField(
              controller: _observacionesController,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'Observaciones (opcional)',
                hintText: 'Ingresa comentarios adicionales...',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: _isLoading ? null : () => Navigator.of(context).pop(),
          child: const Text('Cancelar'),
        ),
        ElevatedButton(
          onPressed: _canExecute() && !_isLoading ? _ejecutarFijacion : null,
          style: ElevatedButton.styleFrom(
            backgroundColor: _esSemiFijado ? Colors.purple.shade600 : AppConstants.primaryColor,
            foregroundColor: Colors.white,
          ),
          child: _isLoading
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : Text(_esSemiFijado ? 'Crear Semi-Fijado' : 'Fijar'),
        ),
      ],
    );
  }

  Widget _buildMetodoChip(MetodoComunicacion metodo, String label) {
    final isSelected = _metodosSeleccionados.contains(metodo);
    
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        setState(() {
          if (metodo == MetodoComunicacion.todas) {
            if (selected) {
              _metodosSeleccionados.clear();
              _metodosSeleccionados.add(MetodoComunicacion.todas);
            } else {
              _metodosSeleccionados.remove(MetodoComunicacion.todas);
            }
          } else {
            _metodosSeleccionados.remove(MetodoComunicacion.todas);
            if (selected) {
              _metodosSeleccionados.add(metodo);
            } else {
              _metodosSeleccionados.remove(metodo);
            }
          }
        });
      },
      selectedColor: AppConstants.primaryColor.withOpacity(0.2),
      checkmarkColor: AppConstants.primaryColor,
    );
  }

  bool _canExecute() {
    final cantidad = double.tryParse(_cantidadController.text) ?? 0;
    return cantidad > 0 && 
           cantidad <= widget.contrato.cantidadPendiente && 
           _metodosSeleccionados.isNotEmpty;
  }

  Future<void> _ejecutarFijacion() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final cantidad = double.parse(_cantidadController.text);
      
      if (_esSemiFijado) {
        // Crear contrato semi-fijado
        await widget.service.crearSemiFijado(
          contratoId: widget.contrato.id,
          porcentajeAnticipo: _porcentajeAnticipo,
        );
        
        Navigator.of(context).pop();
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              '✅ Contrato semi-fijado creado con ${_porcentajeAnticipo.toInt()}% anticipo',
            ),
            backgroundColor: Colors.purple.shade600,
            duration: const Duration(seconds: 3),
          ),
        );
      } else {
        // Fijación normal
        await widget.service.ejecutarFijacion(
          contratoId: widget.contrato.id,
          cantidad: cantidad,
          metodos: _metodosSeleccionados.toList(),
          observaciones: _observacionesController.text.isEmpty 
              ? null 
              : _observacionesController.text,
        );

        Navigator.of(context).pop();
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ Fijación ejecutada exitosamente'),
            backgroundColor: Colors.green,
            duration: const Duration(seconds: 3),
          ),
        );
      }
      
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('❌ Error: ${e.toString()}'),
          backgroundColor: Colors.red,
          duration: const Duration(seconds: 3),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _cantidadController.dispose();
    _observacionesController.dispose();
    super.dispose();
  }
}
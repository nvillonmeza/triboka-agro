import 'package:flutter/material.dart';
import 'package:flutter_staggered_animations/flutter_staggered_animations.dart';
import 'package:provider/provider.dart';
import '../widgets/cards/tendencia_card.dart';
import '../widgets/cards/exportadora_card.dart';
import '../widgets/cards/stock_card.dart';
import '../widgets/cards/proveedor_card.dart';
import '../services/notification_service.dart';
import '../utils/constants.dart';

class InicioPage extends StatefulWidget {
  const InicioPage({super.key});

  @override
  State<InicioPage> createState() => _InicioPageState();
}

class _InicioPageState extends State<InicioPage> {
  // Mock data para NY tendencias
  final List<Map<String, dynamic>> tendenciaData = [
    {'fecha': '15 Nov', 'precio': 6000.0},
    {'fecha': '16 Nov', 'precio': 6100.0},
    {'fecha': '17 Nov', 'precio': 6050.0},
    {'fecha': '18 Nov', 'precio': 6200.0},
    {'fecha': '19 Nov', 'precio': 6150.0},
    {'fecha': '20 Nov', 'precio': 6300.0},
    {'fecha': '21 Nov', 'precio': 6319.0},
  ];

  // Mock data para exportadoras
  final List<Map<String, dynamic>> exportadoras = [
    {
      'nombre': 'SUMAQAO S.A.C.',
      'contrato': 'Cacao fino de aroma',
      'volumen': 2500.0,
    },
    {
      'nombre': 'MACHU PICCHU TRADING',
      'contrato': 'Contrato NY Dic-25',
      'volumen': 1800.0,
    },
    {
      'nombre': 'AMAZONIAN CACAO CORP',
      'contrato': 'Cacao convencional',
      'volumen': 3200.0,
    },
  ];

  // Mock data para centros de acopio
  final List<Map<String, dynamic>> centros = [
    {
      'nombre': 'Centro Huánuco',
      'tipo': 'Centro de Acopio',
      'cantidad': 1250.0,
      'humedad': 7.2,
      'color': Colors.orange,
      'icono': Icons.home_work_outlined,
    },
    {
      'nombre': 'Centro Tocache',
      'tipo': 'Centro de Acopio',
      'cantidad': 890.0,
      'humedad': 6.8,
      'color': Colors.blue,
      'icono': Icons.home_work_outlined,
    },
  ];

  // Mock data para proveedores
  final List<Map<String, dynamic>> proveedores = [
    {
      'nombre': 'Carlos Mendoza',
      'comunidad': 'San José de Sisa',
      'cantidadTotal': 1500.0,
      'ultimaEntrega': '15 Nov',
      'calificacion': 4.8,
      'activo': true,
    },
    {
      'nombre': 'María Gonzales',
      'comunidad': 'Villa Mercedes',
      'cantidadTotal': 2100.0,
      'ultimaEntrega': '12 Nov',
      'calificacion': 4.9,
      'activo': true,
    },
    {
      'nombre': 'Jorge Vásquez',
      'comunidad': 'Nueva Esperanza',
      'cantidadTotal': 850.0,
      'ultimaEntrega': '8 Nov',
      'calificacion': 4.6,
      'activo': false,
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            children: [
              // Header con gradiente
              _buildHeader(context),
              
              // Contenido principal
              Padding(
                padding: const EdgeInsets.all(AppConstants.defaultPadding),
                child: AnimationLimiter(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: AnimationConfiguration.toStaggeredList(
                      duration: const Duration(milliseconds: 375),
                      childAnimationBuilder: (widget) => SlideAnimation(
                        verticalOffset: 50.0,
                        child: FadeInAnimation(
                          child: widget,
                        ),
                      ),
                      children: [
                        // Tendencia NY
                        TendenciaCard(
                          dataTendencia: tendenciaData,
                          precioActual: 6319.0,
                          contratoActivo: 'Dic-25',
                          cambio: '+2.4%',
                        ),
                        
                        const SizedBox(height: AppConstants.largePadding),
                        
                        // Exportadoras
                        _buildSectionWithTitle('Exportadoras', '${exportadoras.length} activas'),
                        ...exportadoras.map((exportadora) {
                          return ExportadoraCard(
                            nombre: exportadora['nombre'],
                            contrato: exportadora['contrato'],
                            volumen: exportadora['volumen'],
                          );
                        }).toList(),
                        
                        const SizedBox(height: AppConstants.largePadding),
                        
                        // Centros de Acopio
                        _buildSectionWithTitle('Centros de Acopio', '${centros.length} operativos'),
                        ...centros.map((centro) {
                          return StockCard(
                            nombre: centro['nombre'],
                            tipo: centro['tipo'],
                            cantidad: centro['cantidad'],
                            humedad: centro['humedad'],
                            color: centro['color'],
                            icono: centro['icono'],
                          );
                        }).toList(),
                        
                        const SizedBox(height: AppConstants.largePadding),
                        
                        // Proveedores
                        _buildSectionWithTitle('Proveedores', '${proveedores.where((p) => p['activo']).length} activos'),
                        ...proveedores.map((proveedor) {
                          return ProveedorCard(
                            nombre: proveedor['nombre'],
                            comunidad: proveedor['comunidad'],
                            cantidadTotal: proveedor['cantidadTotal'],
                            ultimaEntrega: proveedor['ultimaEntrega'],
                            calificacion: proveedor['calificacion'],
                            activo: proveedor['activo'],
                          );
                        }).toList(),
                        
                        const SizedBox(height: AppConstants.defaultPadding),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Container(
      width: double.infinity,
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppConstants.primaryColor,
            AppConstants.primaryColorDark,
          ],
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(AppConstants.largePadding),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Dashboard',
                        style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: AppConstants.smallPadding),
                      Text(
                        'Resumen general del mercado de cacao',
                        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          color: Colors.white.withOpacity(0.9),
                        ),
                      ),
                    ],
                  ),
                ),
                // Botón de notificaciones
                Consumer<NotificationService>(
                  builder: (context, notificationService, child) {
                    return IconButton(
                      onPressed: () => _simularNotificacionesMercado(notificationService),
                      icon: const Icon(
                        Icons.notifications_active,
                        color: Colors.white,
                        size: 28,
                      ),
                      tooltip: 'Simular notificaciones del mercado',
                    );
                  },
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionWithTitle(String titulo, String subtitulo) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppConstants.defaultPadding),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                titulo,
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: AppConstants.textPrimary,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                subtitulo,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppConstants.textSecondary,
                ),
              ),
            ],
          ),
          IconButton(
            onPressed: () {
              // TODO: Navegación a vista completa de la sección
            },
            icon: const Icon(
              Icons.arrow_forward_ios,
              size: 16,
              color: AppConstants.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  void _simularNotificacionesMercado(NotificationService notificationService) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('📈 Simulador de Mercado'),
        content: const Text(
          'Esto simulará las notificaciones típicas de un día de trading:\n\n'
          '• Apertura del mercado NY\n'
          '• Cambios de precio durante el día\n'
          '• Nuevas órdenes de exportadoras\n'
          '• Cierre del mercado\n\n'
          'Las notificaciones aparecerán en la consola de debug.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.of(context).pop();
              
              // Simular día de trading
              notificationService.notificarAperturaMercado(6319.0);
              
              Future.delayed(const Duration(seconds: 3), () {
                notificationService.notificarNuevaOrden('SUMAQAO S.A.C.', 1500.0, 6325.0);
              });
              
              Future.delayed(const Duration(seconds: 6), () {
                notificationService.notificarCambioPrecio(6319.0, 6390.0);
              });
              
              Future.delayed(const Duration(seconds: 9), () {
                notificationService.notificarNuevaOrden('MACHU PICCHU TRADING', 800.0, 6385.0);
              });
              
              Future.delayed(const Duration(seconds: 12), () {
                notificationService.notificarConfirmacionOrden('ORD-2024-003', 'confirmada');
              });
              
              Future.delayed(const Duration(seconds: 15), () {
                notificationService.notificarCierreMercado(6378.0, 0.93);
              });

              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('🔔 Simulación de mercado iniciada - Revisa la consola'),
                  backgroundColor: AppConstants.primaryColor,
                  duration: Duration(seconds: 3),
                ),
              );
            },
            child: const Text('Iniciar Simulación'),
          ),
        ],
      ),
    );
  }
}
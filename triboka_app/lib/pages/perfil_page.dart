import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../utils/constants.dart';
import '../services/theme_service.dart';
import '../services/notification_service.dart';
import '../services/auth_service.dart';

class PerfilPage extends StatefulWidget {
  const PerfilPage({super.key});

  @override
  State<PerfilPage> createState() => _PerfilPageState();
}

class _PerfilPageState extends State<PerfilPage> {
  // Mock data del usuario
  // State for UI toggles
  bool _sincronizacionIoT = false;
  String _unidadMedida = 'TM';



  @override
  Widget build(BuildContext context) {
    // Access current user from provider
    final authService = Provider.of<AuthService>(context);
    final user = authService.currentUser;
    
    // Fallbacks
    final userName = user?.name ?? 'Usuario';
    final userInitial = userName.isNotEmpty ? userName[0].toUpperCase() : 'U';
    final userEmail = user?.email ?? '-';
    final userRole = user?.role ?? 'Invitado';
    final userCompany = user?.company ?? 'Sin empresa asignada';
    
    final userPhone = user?.phone ?? 'No registrado';
    final userRuc = user?.taxId ?? 'No registrado';
    final userAddress = user?.address ?? 'No registrada';
    // Format date properly or use raw string
    final userDate = user?.createdAt.toIso8601String().split('T')[0] ?? '-';
    return Scaffold(
      backgroundColor: AppConstants.backgroundLight,
      appBar: AppBar(
        title: const Text('Perfil'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () {
              _showEditDialog();
            },
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppConstants.defaultPadding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Card de perfil principal
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(AppConstants.largePadding),
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
                  children: [
                    // Avatar y nombre
                    CircleAvatar(
                      radius: 40,
                      backgroundColor: AppConstants.primaryColor,
                      child: Text(
                        userInitial,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    const SizedBox(height: AppConstants.defaultPadding),
                    Text(
                      userName,
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: AppConstants.textPrimary,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 4),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: AppConstants.primaryColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        userRole.toUpperCase(),
                        style: const TextStyle(
                          color: AppConstants.primaryColor,
                          fontWeight: FontWeight.w600,
                          fontSize: 12,
                        ),
                      ),
                    ),
                    const SizedBox(height: AppConstants.smallPadding),
                    Text(
                      userCompany,
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: AppConstants.textSecondary,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: AppConstants.largePadding),
              
              // Información personal
              _buildSection(
                'Información personal',
                [
                  _buildInfoItem(Icons.email, 'Email', userEmail),
                  _buildInfoItem(Icons.phone, 'Teléfono', userPhone),
                  _buildInfoItem(Icons.business, 'RUC', userRuc),
                  _buildInfoItem(Icons.location_on, 'Dirección', userAddress),
                  _buildInfoItem(Icons.calendar_today, 'Registro', userDate),
                ],
              ),
              
              const SizedBox(height: AppConstants.largePadding),
              
              // Configuraciones de Notificaciones
              Consumer<NotificationService>(
                builder: (context, notificationService, child) {
                  return _buildSection(
                    'Notificaciones',
                    [
                      _buildSwitchItem(
                        Icons.notifications_active,
                        'Notificaciones generales',
                        'Activar/desactivar todas las notificaciones',
                        notificationService.notificacionesActivas,
                        (value) {
                          notificationService.setNotificacionesActivas(value);
                        },
                      ),
                      const Divider(),
                      // Chat
                      _buildSwitchItem(
                        Icons.chat_bubble_outline,
                        'Mensajes de chat',
                        'Notificaciones de nuevos mensajes entre partners',
                        notificationService.notificacionesChat,
                        (value) {
                          notificationService.setNotificacionesChat(value);
                        },
                      ),
                      // Mercado
                      _buildSwitchItem(
                        Icons.trending_up,
                        'Apertura del mercado',
                        'Notificar cuando abre la bolsa NY (8:00 AM EST)',
                        notificationService.notificacionesAperturaMercado,
                        (value) {
                          notificationService.setNotificacionesAperturaMercado(value);
                        },
                      ),
                      _buildSwitchItem(
                        Icons.trending_down,
                        'Cierre del mercado',
                        'Notificar cuando cierra la bolsa NY (17:00 PM EST)',
                        notificationService.notificacionesCierreMercado,
                        (value) {
                          notificationService.setNotificacionesCierreMercado(value);
                        },
                      ),
                      // Órdenes
                      _buildSwitchItem(
                        Icons.assignment,
                        'Órdenes fijadas',
                        'Alertas cuando se crean/modifican órdenes entre partes',
                        notificationService.notificacionesOrdenes,
                        (value) {
                          notificationService.setNotificacionesOrdenes(value);
                        },
                      ),
                      _buildSwitchItem(
                        Icons.check_circle_outline,
                        'Confirmación de órdenes',
                        'Notificar cuando una orden es confirmada',
                        notificationService.notificacionesConfirmacionOrdenes,
                        (value) {
                          notificationService.setNotificacionesConfirmacionOrdenes(value);
                        },
                      ),
                      // Precios
                      _buildSwitchItem(
                        Icons.price_change,
                        'Cambios de precio',
                        'Alertas por cambios significativos en precio NY (>2%)',
                        notificationService.notificacionesPrecios,
                        (value) {
                          notificationService.setNotificacionesPrecios(value);
                        },
                      ),
                      const Divider(),
                      _buildActionItem(
                        Icons.settings,
                        'Configuración avanzada',
                        () => _showNotificacionesAvanzadasDialog(),
                      ),
                      _buildActionItem(
                        Icons.notifications_active,
                        'Probar notificaciones',
                        () => _testearNotificaciones(),
                      ),
                    ],
                  );
                },
              ),
              
              const SizedBox(height: AppConstants.largePadding),
              
              // Configuraciones generales
              _buildSection(
                'Configuraciones',
                [
                  _buildSwitchItem(
                    Icons.sensors,
                    'Sincronización IoT',
                    'Conectar con balanzas y sensores',
                    _sincronizacionIoT,
                    (value) {
                      setState(() {
                        _sincronizacionIoT = value;
                      });
                    },
                  ),
                  _buildDropdownItem(),
                  _buildThemeSwitch(),
                ],
              ),
              
              const SizedBox(height: AppConstants.largePadding),
              
              // Opciones adicionales
              _buildSection(
                'Soporte y configuración',
                [
                  _buildActionItem(
                    Icons.help_outline,
                    'Reportar un problema',
                    () => _showSupportDialog(),
                  ),
                  _buildActionItem(
                    Icons.privacy_tip_outlined,
                    'Política de privacidad',
                    () => _showPrivacyDialog(),
                  ),
                  _buildActionItem(
                    Icons.info_outline,
                    'Acerca de TRIBOKA',
                    () => _showAboutDialog(),
                  ),
                ],
              ),
              
              const SizedBox(height: AppConstants.largePadding),
              
              // Botón de cerrar sesión
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () => _logout(context),
                  icon: const Icon(Icons.logout, color: Colors.red),
                  label: const Text(
                    'Cerrar sesión',
                    style: TextStyle(color: Colors.red),
                  ),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Colors.red),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                ),
              ),
              
              const SizedBox(height: AppConstants.defaultPadding),
              
              // Versión de la app
              Center(
                child: Text(
                  'Versión ${AppConstants.appVersion} - Flutter Multiplataforma',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppConstants.textSecondary,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSection(String title, List<Widget> children) {
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
            title,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
              color: AppConstants.textPrimary,
            ),
          ),
          const SizedBox(height: AppConstants.defaultPadding),
          ...children,
        ],
      ),
    );
  }

  Widget _buildInfoItem(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Icon(icon, size: 20, color: AppConstants.primaryColor),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppConstants.textSecondary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Text(
                  value,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppConstants.textPrimary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSwitchItem(
    IconData icon,
    String title,
    String subtitle,
    bool value,
    ValueChanged<bool> onChanged,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, size: 20, color: AppConstants.primaryColor),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w500,
                    color: AppConstants.textPrimary,
                  ),
                ),
                Text(
                  subtitle,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppConstants.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
            activeColor: AppConstants.primaryColor,
          ),
        ],
      ),
    );
  }

  Widget _buildDropdownItem() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          const Icon(Icons.straighten, size: 20, color: AppConstants.primaryColor),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Unidad de medida',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w500,
                    color: AppConstants.textPrimary,
                  ),
                ),
                Text(
                  'Cambiar entre TM, kg, QQ',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppConstants.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          DropdownButton<String>(
            value: _unidadMedida,
            items: ['TM', 'kg', 'QQ'].map((String value) {
              return DropdownMenuItem<String>(
                value: value,
                child: Text(value),
              );
            }).toList(),
            onChanged: (String? value) {
              if (value != null) {
                setState(() {
                  _unidadMedida = value;
                });
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _buildThemeSwitch() {
    return Consumer<ThemeService>(
      builder: (context, themeService, child) {
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: Row(
            children: [
              const Icon(Icons.dark_mode, size: 20, color: AppConstants.primaryColor),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Modo oscuro',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w500,
                        color: AppConstants.textPrimary,
                      ),
                    ),
                    Text(
                      'Activar/desactivar tema oscuro',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppConstants.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              Switch(
                value: themeService.isDarkMode,
                onChanged: (value) {
                  themeService.setThemeMode(
                    value ? ThemeMode.dark : ThemeMode.light,
                  );
                },
                activeColor: AppConstants.primaryColor,
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildActionItem(IconData icon, String title, VoidCallback onTap) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppConstants.smallPadding),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Row(
            children: [
              Icon(icon, size: 20, color: AppConstants.primaryColor),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  title,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w500,
                    color: AppConstants.textPrimary,
                  ),
                ),
              ),
              const Icon(
                Icons.chevron_right,
                color: AppConstants.textSecondary,
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showEditDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Editar perfil'),
        content: const Text('Función de edición próximamente disponible'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showSupportDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Soporte'),
        content: const Text(
          'Para reportar problemas o solicitar ayuda:\n\n'
          '📧 Email: soporte@triboka.com\n'
          '📱 WhatsApp: +593 99 999 9999\n'
          '🌐 Web: triboka.com/soporte',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showPrivacyDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Política de Privacidad'),
        content: const Text(
          'Tu privacidad es importante para nosotros. '
          'TRIBOKA protege tus datos siguiendo las mejores prácticas de seguridad.\n\n'
          'Para más información visita:\ntriboka.com/privacy',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showAboutDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('${AppConstants.appName} ${AppConstants.appVersion}'),
        content: Text(
          '${AppConstants.appDescription}\n\n'
          'Desarrollado para conectar productores, centros de acopio '
          'y exportadoras en el ecosistema del cacao.\n\n'
          '© 2024 TRIBOKA. Todos los derechos reservados.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _logout(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cerrar sesión'),
        content: const Text('¿Estás seguro de que quieres cerrar sesión?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () async {
              Navigator.of(context).pop(); // Close dialog
              
              final authService = Provider.of<AuthService>(context, listen: false);
              await authService.logout();
              
              // Depending on how main is setup, provider update might redirect to login automatically
              // or we force navigation
              if (context.mounted) {
                 // Clean navigation stack and go to login/authwrapper
                 // Using '/' assuming it maps to AuthWrapper or Login logic
                 Navigator.of(context).pushNamedAndRemoveUntil('/', (route) => false);
              }
            },
            child: const Text('Cerrar sesión'),
          ),
        ],
      ),
    );
  }

  void _showHorariosMercadoDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Horarios del Mercado NY'),
        content: SizedBox(
          width: 300,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'Configura los horarios para recibir notificaciones de apertura y cierre del mercado de Nueva York.',
                style: TextStyle(fontSize: 14),
              ),
              const SizedBox(height: 16),
              _buildTimeConfigItem(
                'Apertura del mercado',
                '08:00 AM EST',
                Icons.trending_up,
                () => _showTimePicker('apertura'),
              ),
              const SizedBox(height: 12),
              _buildTimeConfigItem(
                'Cierre del mercado',
                '17:00 PM EST',
                Icons.trending_down,
                () => _showTimePicker('cierre'),
              ),
              const SizedBox(height: 16),
              const Text(
                'Nota: Los horarios están en zona horaria EST (Nueva York)',
                style: TextStyle(fontSize: 12, color: Colors.grey),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.of(context).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Horarios configurados correctamente'),
                  backgroundColor: AppConstants.primaryColor,
                ),
              );
            },
            child: const Text('Guardar'),
          ),
        ],
      ),
    );
  }

  Widget _buildTimeConfigItem(String title, String time, IconData icon, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey.shade300),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            Icon(icon, color: AppConstants.primaryColor, size: 20),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                title,
                style: const TextStyle(fontWeight: FontWeight.w500),
              ),
            ),
            Text(
              time,
              style: TextStyle(
                color: AppConstants.primaryColor,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(width: 8),
            const Icon(Icons.access_time, color: Colors.grey, size: 16),
          ],
        ),
      ),
    );
  }

  void _showTimePicker(String tipo) {
    showTimePicker(
      context: context,
      initialTime: tipo == 'apertura' 
        ? const TimeOfDay(hour: 8, minute: 0)
        : const TimeOfDay(hour: 17, minute: 0),
    ).then((time) {
      if (time != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Horario de $tipo configurado: ${time.format(context)}'),
            backgroundColor: AppConstants.primaryColor,
          ),
        );
      }
    });
  }

  void _showNotificacionesAvanzadasDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Configuración Avanzada'),
        content: SizedBox(
          width: 300,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildAdvancedSetting(
                'Sonido personalizado',
                'Cambiar tono de notificaciones',
                Icons.music_note,
                () => _showSoundPicker(),
              ),
              _buildAdvancedSetting(
                'Horarios del mercado',
                'Configurar alertas de apertura/cierre',
                Icons.schedule,
                () => _showHorariosMercadoDialog(),
              ),
              _buildAdvancedSetting(
                'Umbral de precios',
                'Configurar % de cambio para alertas',
                Icons.percent,
                () => _showUmbralPreciosDialog(),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cerrar'),
          ),
        ],
      ),
    );
  }

  Widget _buildAdvancedSetting(String title, String subtitle, IconData icon, VoidCallback onTap) {
    return ListTile(
      leading: Icon(icon, color: AppConstants.primaryColor),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
      subtitle: Text(subtitle, style: const TextStyle(fontSize: 12)),
      trailing: const Icon(Icons.arrow_forward_ios, size: 16),
      onTap: onTap,
    );
  }

  void _showSoundPicker() {
    // TODO: Implementar selector de sonidos personalizados
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Selector de sonidos en desarrollo'),
        backgroundColor: AppConstants.primaryColor,
      ),
    );
  }

  void _showUmbralPreciosDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Umbral de Precios'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Recibir notificación cuando el precio del cacao cambie más de:'),
            const SizedBox(height: 16),
            DropdownButtonFormField<double>(
              value: 2.0,
              decoration: const InputDecoration(
                labelText: 'Porcentaje de cambio',
                suffixText: '%',
              ),
              items: [1.0, 2.0, 3.0, 5.0, 10.0].map((value) {
                return DropdownMenuItem<double>(
                  value: value,
                  child: Text('${value.toStringAsFixed(1)}%'),
                );
              }).toList(),
              onChanged: (value) {
                if (value != null) {
                  context.read<NotificationService>().setUmbralCambioPrecio(value);
                }
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.of(context).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Umbral de precios configurado'),
                  backgroundColor: AppConstants.primaryColor,
                ),
              );
            },
            child: const Text('Guardar'),
          ),
        ],
      ),
    );
  }

  void _testearNotificaciones() {
    final notificationService = context.read<NotificationService>();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('🧪 Probar Notificaciones'),
        content: const Text(
          'Esto enviará notificaciones de prueba para todos los tipos configurados. '
          'Verás las notificaciones en la consola de debug por ahora.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.of(context).pop();
              notificationService.testearNotificaciones();
              
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('🔔 Notificaciones de prueba enviadas. Revisa la consola.'),
                  backgroundColor: AppConstants.primaryColor,
                  duration: Duration(seconds: 3),
                ),
              );
            },
            child: const Text('Enviar Pruebas'),
          ),
        ],
      ),
    );
  }
}
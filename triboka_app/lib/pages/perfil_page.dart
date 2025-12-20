import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import '../utils/constants.dart';
import '../services/theme_service.dart';
import '../services/notification_service.dart';
import '../services/auth_service.dart';
import '../models/user.dart';

class PerfilPage extends StatefulWidget {
  const PerfilPage({super.key});

  @override
  State<PerfilPage> createState() => _PerfilPageState();
}

class _PerfilPageState extends State<PerfilPage> {
  bool _sincronizacionIoT = false;
  String _unidadMedida = 'TM';
  
  Map<String, String> _licenseInfo = {};

  @override
  void initState() {
    super.initState();
    _loadLicenseInfo();
  }

  Future<void> _loadLicenseInfo() async {
    final authService = context.read<AuthService>();
    final info = await authService.getLicenseInfo();
    if (mounted) {
      setState(() {
        _licenseInfo = info;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
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
    final userDate = user?.createdAt.toIso8601String().split('T')[0] ?? '-';
    
    final avatarUrl = user?.avatarUrl;

    return Scaffold(
      backgroundColor: AppConstants.backgroundLight,
      appBar: AppBar(
        title: const Text('Perfil'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () {
              if (user != null) _showEditDialog(user);
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
                    // Avatar
                    GestureDetector(
                      onTap: () {
                         if (user != null) _showEditDialog(user);
                      },
                      child: CircleAvatar(
                        radius: 50,
                        backgroundColor: AppConstants.primaryColor,
                        backgroundImage: avatarUrl != null 
                          ? (avatarUrl.startsWith('http') 
                              ? NetworkImage(avatarUrl) 
                              : FileImage(File(avatarUrl)) as ImageProvider)
                          : null,
                        child: avatarUrl == null 
                          ? Text(
                              userInitial,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 32,
                                fontWeight: FontWeight.bold,
                              ),
                            )
                          : null,
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
                    if (avatarUrl == null)
                       Padding(
                         padding: const EdgeInsets.only(top: 8.0),
                         child: Text('Toca para añadir foto', style: TextStyle(fontSize: 12, color: Colors.grey[600])),
                       ),
                  ],
                ),
              ),
              
              const SizedBox(height: AppConstants.largePadding),

              // NUEVO: Estado de Cuenta / Licencia
               _buildSection(
                'Estado de Cuenta',
                [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                        Text('Plan Actual', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                        Text(_licenseInfo['plan'] ?? 'Pro', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                      ]),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: Colors.green.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.green),
                        ),
                        child: Text(
                          (_licenseInfo['status'] ?? 'Activo').toUpperCase(),
                          style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  _buildInfoItem(Icons.access_time, 'Expira el', _licenseInfo['expiration'] ?? 'Consultando...'),
                  const SizedBox(height: 8),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton(
                      onPressed: () {},
                      child: const Text('Gestionar Suscripción (Web)'),
                    ),
                  ),
                ],
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
              
              // Configuraciones de Notificaciones (Mismo código)
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
                        (value) => notificationService.setNotificacionesActivas(value),
                      ),
                      const Divider(),
                      _buildSwitchItem(
                        Icons.price_change,
                        'Cambios de precio',
                        'Alertas por cambios significativos (>2%)',
                        notificationService.notificacionesPrecios,
                        (value) => notificationService.setNotificacionesPrecios(value),
                      ),
                      _buildActionItem(
                        Icons.settings,
                        'Configuración avanzada',
                        () => _showNotificacionesAvanzadasDialog(),
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
                    (value) => setState(() => _sincronizacionIoT = value),
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
                  label: const Text('Cerrar sesión', style: TextStyle(color: Colors.red)),
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

  // --- WIDGETS AUXILIARES ---

  Widget _buildSection(String title, List<Widget> children) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppConstants.defaultPadding),
      decoration: BoxDecoration(
        color: AppConstants.cardWhite,
        borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 8, offset: Offset(0, 2)),
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
                Text(label, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppConstants.textSecondary, fontWeight: FontWeight.w500)),
                Text(value, style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppConstants.textPrimary)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSwitchItem(IconData icon, String title, String subtitle, bool value, ValueChanged<bool> onChanged) {
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
                Text(title, style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w500, color: AppConstants.textPrimary)),
                Text(subtitle, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppConstants.textSecondary)),
              ],
            ),
          ),
          Switch(value: value, onChanged: onChanged, activeColor: AppConstants.primaryColor),
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
                Text('Unidad de medida', style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w500, color: AppConstants.textPrimary)),
                Text('Cambiar entre TM, kg, QQ', style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppConstants.textSecondary)),
              ],
            ),
          ),
          DropdownButton<String>(
            value: _unidadMedida,
            items: ['TM', 'kg', 'QQ'].map((String value) => DropdownMenuItem<String>(value: value, child: Text(value))).toList(),
            onChanged: (String? value) {
              if (value != null) setState(() => _unidadMedida = value);
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
                    Text('Modo oscuro', style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w500, color: AppConstants.textPrimary)),
                    Text('Activar/desactivar tema oscuro', style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppConstants.textSecondary)),
                  ],
                ),
              ),
              Switch(
                value: themeService.isDarkMode,
                onChanged: (value) => themeService.setThemeMode(value ? ThemeMode.dark : ThemeMode.light),
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
              Expanded(child: Text(title, style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w500, color: AppConstants.textPrimary))),
              const Icon(Icons.chevron_right, color: AppConstants.textSecondary),
            ],
          ),
        ),
      ),
    );
  }

  // --- DIÁLOGOS DE EDICIÓN ---

  void _showEditDialog(User currentUser) {
    final nameController = TextEditingController(text: currentUser.name);
    final phoneController = TextEditingController(text: currentUser.phone ?? '');
    final rucController = TextEditingController(text: currentUser.taxId ?? '');
    final addressController = TextEditingController(text: currentUser.address ?? '');
    final companyController = TextEditingController(text: currentUser.company ?? '');
    
    File? tempImage;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setStateDialog) {
          return AlertDialog(
            title: const Text('Editar perfil'),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  GestureDetector(
                    onTap: () async {
                      final ImagePicker picker = ImagePicker();
                      final XFile? image = await picker.pickImage(source: ImageSource.gallery);
                      if (image != null) {
                         setStateDialog(() {
                           tempImage = File(image.path);
                         });
                      }
                    },
                    child: CircleAvatar(
                      radius: 40,
                      backgroundColor: Colors.grey[200],
                      backgroundImage: tempImage != null 
                        ? FileImage(tempImage!) 
                        : (currentUser.avatarUrl != null ? NetworkImage(currentUser.avatarUrl!) as ImageProvider : null),
                      child: (tempImage == null && currentUser.avatarUrl == null)
                        ? const Icon(Icons.camera_alt, color: Colors.grey)
                        : null,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text('Toca para cambiar foto', style: TextStyle(fontSize: 10, color: Colors.grey)),
                  const SizedBox(height: 16),
                  TextField(controller: nameController, decoration: const InputDecoration(labelText: 'Nombre')),
                  TextField(controller: phoneController, decoration: const InputDecoration(labelText: 'Teléfono'), keyboardType: TextInputType.phone),
                  TextField(controller: rucController, decoration: const InputDecoration(labelText: 'RUC / Identificación')),
                  TextField(controller: addressController, decoration: const InputDecoration(labelText: 'Dirección')),
                  TextField(controller: companyController, decoration: const InputDecoration(labelText: 'Empresa', enabled: false)), // Empresa suele ser fija
                ],
              ),
            ),
            actions: [
              TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Cancelar')),
              FilledButton(
                onPressed: () async {
                  // Guardar cambios
                  final updatedUser = currentUser.copyWith(
                    name: nameController.text,
                    phone: phoneController.text,
                    taxId: rucController.text,
                    address: addressController.text,
                  );
                  
                  // Llamar al servicio
                  final authService = Provider.of<AuthService>(context, listen: false);
                  await authService.updateProfile(updatedUser, tempImage);
                  
                  if (context.mounted) Navigator.of(context).pop();
                },
                child: const Text('Guardar'),
              ),
            ],
          );
        }
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
        actions: [TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('OK'))],
      ),
    );
  }

  void _showPrivacyDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Política de Privacidad'),
        content: const Text('Tu privacidad es importante para nosotros. Visita triboka.com/privacy'),
        actions: [TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('OK'))],
      ),
    );
  }

  void _showAboutDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('${AppConstants.appName} ${AppConstants.appVersion}'),
        content: Text('© 2024 TRIBOKA. Todos los derechos reservados.'),
        actions: [TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('OK'))],
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
          TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Cancelar')),
          FilledButton(
            onPressed: () async {
              Navigator.of(context).pop();
              final authService = Provider.of<AuthService>(context, listen: false);
              await authService.logout();
              if (context.mounted) Navigator.of(context).pushNamedAndRemoveUntil('/', (route) => false);
            },
            child: const Text('Cerrar sesión'),
          ),
        ],
      ),
    );
  }

  void _showNotificacionesAvanzadasDialog() {
    // Placeholder para dialogo avanzado existente
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Configuración Avanzada'),
        content: const Text('Opciones avanzadas de notificaciones aquí.'),
        actions: [TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('OK'))],
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
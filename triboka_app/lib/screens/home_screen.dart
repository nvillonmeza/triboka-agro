import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'dart:io';
import '../services/platform_service.dart';
import '../widgets/platform_button.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String _platformInfo = '';
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadPlatformInfo();
  }

  Future<void> _loadPlatformInfo() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final info = await PlatformService.getPlatformInfo();
      setState(() {
        _platformInfo = info;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _platformInfo = 'Error al obtener información: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    // Usar diferentes estilos según la plataforma
    if (Platform.isIOS) {
      return CupertinoPageScaffold(
        navigationBar: const CupertinoNavigationBar(
          middle: Text('TRIBOKA'),
        ),
        child: SafeArea(
          child: _buildBody(),
        ),
      );
    } else {
      return Scaffold(
        appBar: AppBar(
          title: const Text('TRIBOKA'),
          centerTitle: true,
        ),
        body: SafeArea(
          child: _buildBody(),
        ),
      );
    }
  }

  Widget _buildBody() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header con logo/título
          Container(
            padding: const EdgeInsets.all(24.0),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primaryContainer,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              children: [
                Icon(
                  Platform.isIOS ? CupertinoIcons.device_phone_portrait : Icons.phone_android,
                  size: 64,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(height: 16),
                Text(
                  'Bienvenido a TRIBOKA',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                Text(
                  'Aplicación multiplataforma Flutter',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onPrimaryContainer,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 32),
          
          // Información de la plataforma
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Información de la Plataforma',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  if (_isLoading)
                    const Center(
                      child: CircularProgressIndicator(),
                    )
                  else
                    Text(
                      _platformInfo,
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 24),
          
          // Botones de acción
          PlatformButton(
            text: 'Actualizar Información',
            onPressed: _loadPlatformInfo,
            isLoading: _isLoading,
          ),
          
          const SizedBox(height: 16),
          
          PlatformButton(
            text: 'Configuración',
            onPressed: () {
              _showConfigDialog();
            },
            isPrimary: false,
          ),
          
          const Spacer(),
          
          // Footer con información de versión
          Text(
            'Versión 1.0.0 - Flutter ${Platform.isIOS ? 'iOS' : 'Android'}',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  void _showConfigDialog() {
    if (Platform.isIOS) {
      showCupertinoDialog(
        context: context,
        builder: (context) => CupertinoAlertDialog(
          title: const Text('Configuración'),
          content: const Text('Próximamente disponible'),
          actions: [
            CupertinoDialogAction(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    } else {
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Configuración'),
          content: const Text('Próximamente disponible'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    }
  }
}
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

class PlatformService {
  static final DeviceInfoPlugin _deviceInfo = DeviceInfoPlugin();
  static final Connectivity _connectivity = Connectivity();

  /// Obtiene información detallada de la plataforma
  static Future<String> getPlatformInfo() async {
    final StringBuffer info = StringBuffer();

    try {
      // Información básica de la plataforma
      info.writeln('Plataforma: ${Platform.operatingSystem}');
      info.writeln('Versión: ${Platform.operatingSystemVersion}');
      
      // Información del dispositivo específica por plataforma
      if (Platform.isAndroid) {
        final androidInfo = await _deviceInfo.androidInfo;
        info.writeln('Dispositivo: ${androidInfo.manufacturer} ${androidInfo.model}');
        info.writeln('Android API: ${androidInfo.version.sdkInt}');
        info.writeln('Versión Android: ${androidInfo.version.release}');
      } else if (Platform.isIOS) {
        final iosInfo = await _deviceInfo.iosInfo;
        info.writeln('Dispositivo: ${iosInfo.name}');
        info.writeln('Modelo: ${iosInfo.model}');
        info.writeln('iOS: ${iosInfo.systemVersion}');
      }

      // Información de la aplicación
      final packageInfo = await PackageInfo.fromPlatform();
      info.writeln('App: ${packageInfo.appName} v${packageInfo.version}');
      info.writeln('Build: ${packageInfo.buildNumber}');

      // Estado de conectividad
      final connectivityResult = await _connectivity.checkConnectivity();
      String connectivity = 'Sin conexión';
      switch (connectivityResult) {
        case ConnectivityResult.wifi:
          connectivity = 'WiFi';
          break;
        case ConnectivityResult.mobile:
          connectivity = 'Datos móviles';
          break;
        case ConnectivityResult.ethernet:
          connectivity = 'Ethernet';
          break;
        case ConnectivityResult.bluetooth:
          connectivity = 'Bluetooth';
          break;
        case ConnectivityResult.vpn:
          connectivity = 'VPN';
          break;
        case ConnectivityResult.other:
          connectivity = 'Otra conexión';
          break;
        case ConnectivityResult.none:
          connectivity = 'Sin conexión';
          break;
      }
      info.writeln('Conectividad: $connectivity');

    } catch (e) {
      info.writeln('Error al obtener información: $e');
    }

    return info.toString();
  }

  /// Verifica si es la primera vez que se ejecuta la app
  static Future<bool> isFirstRun() async {
    // Implementar con shared_preferences
    return false;
  }

  /// Obtiene el directorio de documentos de la aplicación
  static Future<String> getAppDocumentsDirectory() async {
    try {
      final directory = Directory.systemTemp; // Placeholder
      return directory.path;
    } catch (e) {
      return 'Error: $e';
    }
  }

  /// Detecta el tipo de dispositivo (tablet/phone)
  static bool isTablet() {
    // Lógica básica para detectar tablets
    // En una implementación real, usarías las dimensiones de pantalla
    return false;
  }

  /// Obtiene el tema del sistema (claro/oscuro)
  static Brightness getSystemBrightness() {
    // En una implementación real, detectarías el tema del sistema
    return Brightness.light;
  }
}
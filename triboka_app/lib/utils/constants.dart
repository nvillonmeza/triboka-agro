import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Constantes de la aplicación TRIBOKA - ERP de Cacao
class AppConstants {
  // Información de la aplicación
  static const String appName = 'TRIBOKA';
  static const String appVersion = '1.0.0';
  static const String appDescription = 'ERP de Cacao - Multiplataforma';
  
  // URLs y endpoints
  static const String baseUrl = 'https://api.triboka.com';
  static const String termsUrl = 'https://triboka.com/terms';
  static const String privacyUrl = 'https://triboka.com/privacy';
  
  // Configuraciones
  static const int requestTimeoutSeconds = 30;
  static const int maxRetries = 3;
  
  // Colores personalizados (según documentación de diseño)
  static const Color primaryColor = Color(0xFF059669); // Verde esmeralda
  static const Color primaryColorDark = Color(0xFF047857); // Verde esmeralda oscuro
  static const Color secondaryColor = Color(0xFF10B981); // Verde claro
  static const Color complementaryColor = Color(0xFFFBBF24); // Ámbar
  static const Color backgroundLight = Color(0xFFF8FAFC); // Fondo claro
  static const Color backgroundColor = Color(0xFFF8FAFC); // Alias para compatibilidad
  static const Color textPrimary = Color(0xFF1E293B); // Texto principal
  static const Color textSecondary = Color(0xFF64748B); // Texto secundario
  static const Color cardWhite = Colors.white; // Card blanca
  
  // Colores adicionales para funcionalidades
  static const Color errorColor = Color(0xFFBA1A1A);
  static const Color successColor = Color(0xFF059669); // Usando el verde primario
  static const Color warningColor = Color(0xFFFBBF24); // Usando el ámbar
  
  // Dimensiones
  static const double defaultPadding = 16.0;
  static const double smallPadding = 8.0;
  static const double largePadding = 24.0;
  static const double borderRadius = 16.0; // Aumentado según diseño
  static const double cardBorderRadius = 20.0; // Para cards principales
  
  // Animaciones
  static const Duration defaultAnimationDuration = Duration(milliseconds: 300);
  static const Duration shortAnimationDuration = Duration(milliseconds: 150);
  static const Duration longAnimationDuration = Duration(milliseconds: 500);
  
  // Calculadora - Datos específicos del cacao
  static const double spotPrecioNY = 6319.0; // USD/TM según documentación
  static const double divisorQQ = 22.0462; // División para convertir TM a QQ
}

/// Textos de la aplicación (para futura internacionalización)
class AppStrings {
  // Generales
  static const String ok = 'OK';
  static const String cancel = 'Cancelar';
  static const String confirm = 'Confirmar';
  static const String error = 'Error';
  static const String success = 'Éxito';
  static const String loading = 'Cargando...';
  
  // Pantalla principal
  static const String welcome = 'Bienvenido a TRIBOKA';
  static const String appDescription = 'Aplicación multiplataforma Flutter';
  static const String platformInfo = 'Información de la Plataforma';
  static const String updateInfo = 'Actualizar Información';
  static const String settings = 'Configuración';
  static const String comingSoon = 'Próximamente disponible';
  
  // Errores
  static const String networkError = 'Error de conexión a internet';
  static const String unknownError = 'Error desconocido';
  static const String timeoutError = 'Tiempo de espera agotado';
}

/// Temas personalizados para la aplicación TRIBOKA
class AppThemes {
  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    textTheme: GoogleFonts.poppinsTextTheme(),
    colorScheme: ColorScheme.fromSeed(
      seedColor: AppConstants.primaryColor,
      brightness: Brightness.light,
      primary: AppConstants.primaryColor,
      secondary: AppConstants.secondaryColor,
      tertiary: AppConstants.complementaryColor,
      surface: AppConstants.cardWhite,
      background: AppConstants.backgroundLight,
      onPrimary: Colors.white,
      onSecondary: Colors.white,
      onSurface: AppConstants.textPrimary,
      onBackground: AppConstants.textPrimary,
    ),
    scaffoldBackgroundColor: AppConstants.backgroundLight,
    appBarTheme: AppBarTheme(
      centerTitle: true,
      elevation: 0,
      scrolledUnderElevation: 1,
      backgroundColor: AppConstants.backgroundLight,
      foregroundColor: AppConstants.textPrimary,
      titleTextStyle: const TextStyle(
        fontFamily: 'Poppins',
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: AppConstants.textPrimary,
      ),
    ),
    cardTheme: CardThemeData(
      elevation: 2,
      color: AppConstants.cardWhite,
      shadowColor: Colors.black12,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: AppConstants.primaryColor,
        foregroundColor: Colors.white,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppConstants.borderRadius),
        ),
        padding: const EdgeInsets.symmetric(
          horizontal: AppConstants.largePadding,
          vertical: AppConstants.defaultPadding,
        ),
        textStyle: const TextStyle(
          fontFamily: 'Poppins',
          fontWeight: FontWeight.w600,
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: AppConstants.primaryColor,
        side: const BorderSide(color: AppConstants.primaryColor),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppConstants.borderRadius),
        ),
        padding: const EdgeInsets.symmetric(
          horizontal: AppConstants.largePadding,
          vertical: AppConstants.defaultPadding,
        ),
        textStyle: const TextStyle(
          fontFamily: 'Poppins',
          fontWeight: FontWeight.w600,
        ),
      ),
    ),
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: AppConstants.cardWhite,
      selectedItemColor: AppConstants.primaryColor,
      unselectedItemColor: AppConstants.textSecondary,
      type: BottomNavigationBarType.fixed,
      elevation: 8,
    ),
  );

  static ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    textTheme: GoogleFonts.poppinsTextTheme(ThemeData.dark().textTheme),
    colorScheme: ColorScheme.fromSeed(
      seedColor: AppConstants.primaryColor,
      brightness: Brightness.dark,
      primary: AppConstants.primaryColor,
      secondary: AppConstants.secondaryColor,
      tertiary: AppConstants.complementaryColor,
    ),
    appBarTheme: const AppBarTheme(
      centerTitle: true,
      elevation: 0,
      scrolledUnderElevation: 1,
      titleTextStyle: TextStyle(
        fontFamily: 'Poppins',
        fontSize: 18,
        fontWeight: FontWeight.w600,
      ),
    ),
    cardTheme: CardThemeData(
      elevation: 2,
      shadowColor: Colors.black54,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: AppConstants.primaryColor,
        foregroundColor: Colors.white,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppConstants.borderRadius),
        ),
        padding: const EdgeInsets.symmetric(
          horizontal: AppConstants.largePadding,
          vertical: AppConstants.defaultPadding,
        ),
        textStyle: const TextStyle(
          fontFamily: 'Poppins',
          fontWeight: FontWeight.w600,
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: AppConstants.primaryColor,
        side: const BorderSide(color: AppConstants.primaryColor),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppConstants.borderRadius),
        ),
        padding: const EdgeInsets.symmetric(
          horizontal: AppConstants.largePadding,
          vertical: AppConstants.defaultPadding,
        ),
        textStyle: const TextStyle(
          fontFamily: 'Poppins',
          fontWeight: FontWeight.w600,
        ),
      ),
    ),
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      selectedItemColor: AppConstants.primaryColor,
      type: BottomNavigationBarType.fixed,
      elevation: 8,
    ),
  );
}
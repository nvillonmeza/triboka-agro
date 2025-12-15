import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'utils/constants.dart';
import 'widgets/main_navigation.dart';
import 'services/theme_service.dart';
import 'services/notification_service.dart';
import 'services/fijacion_service.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();  
  runApp(const TribokaApp());
}

class TribokaApp extends StatelessWidget {
  const TribokaApp({super.key});

  @override
  Widget build(BuildContext context) {
    // Configurar la orientación y barras de estado
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
      DeviceOrientation.portraitDown,
    ]);

    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (context) => ThemeService()),
        ChangeNotifierProvider(create: (context) => NotificationService()),
        ChangeNotifierProvider(create: (context) => FijacionService()),
      ],
      child: Consumer<ThemeService>(
        builder: (context, themeService, child) {
          return MaterialApp(
            title: AppConstants.appName,
            theme: AppThemes.lightTheme,
            darkTheme: AppThemes.darkTheme,
            themeMode: themeService.themeMode,
            home: const MainNavigation(),
            debugShowCheckedModeBanner: false,
          );
        },
      ),
    );
  }
}



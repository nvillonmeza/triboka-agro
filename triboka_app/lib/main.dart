import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'utils/constants.dart';
import 'widgets/main_navigation.dart';
import 'pages/auth/login_page.dart';
import 'services/theme_service.dart';
import 'services/notification_service.dart';
import 'services/fijacion_service.dart';
import 'services/market_service.dart';
import 'services/chat_service.dart';
import 'services/contract_service.dart';
import 'services/auth_service.dart';
import 'services/analytics_service.dart';
import 'models/contract_model.dart';
import 'services/sync_service.dart';

import 'package:hive_flutter/hive_flutter.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Inicializar Hive
  await Hive.initFlutter();
  
  // Registrar Adapters
  Hive.registerAdapter(ExportContractAdapter());
  Hive.registerAdapter(FixationAdapter());
  Hive.registerAdapter(CompanyAdapter());
  
  // Abrir cajas
  await Hive.openBox('calculadora_history');
  await Hive.openBox<ExportContract>('contracts');
  await Hive.openBox<Fixation>('fixations');
  await Hive.openBox<Company>('companies');
  
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
        ChangeNotifierProvider(create: (_) => ThemeService()),
        ChangeNotifierProvider(create: (_) => NotificationService()),
        ChangeNotifierProvider(create: (_) => AuthService()..initService()),
        // MarketService moved up to be available for FijacionService
        ChangeNotifierProvider(create: (_) => MarketService()..initService()), 
        ChangeNotifierProvider(create: (_) => ChatService()..initService()),
        
        // FijacionService now depends on MarketService
        ChangeNotifierProxyProvider<MarketService, FijacionService>(
          create: (context) => FijacionService(context.read<MarketService>()),
          update: (_, market, previous) => previous ?? FijacionService(market),
        ),
        
        ChangeNotifierProvider(create: (_) => ContractService()..initService()..fetchContracts()),
        ChangeNotifierProvider(create: (_) => AnalyticsService()),
        ProxyProvider<AuthService, SyncService>(
          update: (_, auth, __) => SyncService(auth),
        ),
      ],
      child: Consumer<ThemeService>(
        builder: (context, themeService, child) {
          return MaterialApp(
            title: AppConstants.appName,
            theme: AppThemes.lightTheme,
            darkTheme: AppThemes.darkTheme,
            themeMode: themeService.themeMode,
            home: const AuthWrapper(), // Use AuthWrapper instead of MainNavigation
            debugShowCheckedModeBanner: false,
          );
        },
      ),
    );
  }
}

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    final authService = context.watch<AuthService>();
    
    // Simple check - in real app might need connection check
    if (authService.isLoggedIn) {
      return const MainNavigation();
    } else {
      return const LoginPage();
    }
  }
}



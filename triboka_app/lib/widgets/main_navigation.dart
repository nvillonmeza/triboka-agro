import 'package:flutter/material.dart';
import '../pages/inicio_page.dart';
import '../pages/calculadora_page.dart';
import '../pages/gestion_page.dart';
import '../pages/chat_page.dart';
import '../utils/constants.dart';
import '../pages/perfil_page.dart';
import '../utils/constants.dart';

class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _currentIndex = 0;

  final List<Widget> _pages = [
    const InicioPage(),
    const CalculadoraPage(),
    const GestionPage(),
    const ChatPage(),
    const PerfilPage(),
  ];

  final List<BottomNavigationBarItem> _bottomNavItems = [
    const BottomNavigationBarItem(
      icon: Icon(Icons.home_outlined),
      activeIcon: Icon(Icons.home),
      label: 'Inicio',
      tooltip: 'Dashboard principal',
    ),
    const BottomNavigationBarItem(
      icon: Icon(Icons.calculate_outlined),
      activeIcon: Icon(Icons.calculate),
      label: 'Calculadora',
      tooltip: 'Calculadora de precios',
    ),
    const BottomNavigationBarItem(
      icon: Icon(Icons.business_center_outlined),
      activeIcon: Icon(Icons.business_center),
      label: 'Gestión',
      tooltip: 'Gestión por rol',
    ),
    const BottomNavigationBarItem(
      icon: Icon(Icons.chat_bubble_outline),
      activeIcon: Icon(Icons.chat_bubble),
      label: 'Chat',
      tooltip: 'Comunicación con socios',
    ),
    const BottomNavigationBarItem(
      icon: Icon(Icons.person_outline),
      activeIcon: Icon(Icons.person),
      label: 'Perfil',
      tooltip: 'Perfil y configuración',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AnimatedSwitcher(
        duration: AppConstants.defaultAnimationDuration,
      body: _pages[_selectedIndex], // Removed AnimatedSwitcher
      bottomNavigationBar: NavigationBar( // Changed from BottomNavigationBar to NavigationBar
        selectedIndex: _selectedIndex,
        onDestinationSelected: (int index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Inicio',
          ),
          NavigationDestination(
            icon: Icon(Icons.analytics_outlined), // Changed icon for Gestion
            selectedIcon: Icon(Icons.analytics), // Changed icon for Gestion
            label: 'Gestión',
          ),
          NavigationDestination(
            icon: Icon(Icons.chat_bubble_outline),
            selectedIcon: Icon(Icons.chat_bubble),
            label: 'Chat',
          ),
          NavigationDestination(
            icon: Icon(Icons.calculate_outlined),
            selectedIcon: Icon(Icons.calculate),
            label: 'Calculadora',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: 'Perfil',
          ),
        ],
      ),
    );
  }
}

// Placeholder for Profile Page if not exists
class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});
  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Perfil de Usuario'));
  }
}
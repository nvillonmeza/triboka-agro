import 'package:flutter/material.dart';
import 'package:flutter_staggered_animations/flutter_staggered_animations.dart';
import 'package:provider/provider.dart';
import '../widgets/market_dashboard_widget.dart';
import '../widgets/publication_card.dart'; // Vitrina Widget
import '../services/auth_service.dart';
import '../utils/constants.dart';
import 'package:triboka_app/services/publication_service.dart';
import 'package:triboka_app/services/sync_manager.dart';
import 'package:triboka_app/services/chat_service.dart'; // Import ChatService
import 'package:triboka_app/pages/chat_page.dart'; // Import ChatDetailPage


class InicioPage extends StatefulWidget {
  const InicioPage({super.key});

  @override
  State<InicioPage> createState() => _InicioPageState();
}

class _InicioPageState extends State<InicioPage> {

  void _showActionSnackBar(String action) {
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(action)),
    );
  }

  Future<void> _handleRefresh() async {
    await SyncManager().triggerManualSync();
    setState(() {
      // Forzar reconstrucción del FutureBuilder
    });
    // Mostrar feedback visual
    if (mounted) {
       ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ Sincronización completada'),
          backgroundColor: Colors.green,
          duration: Duration(seconds: 2),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final authService = context.watch<AuthService>();
    final role = authService.currentUser?.role ?? 'centro'; 
    final userName = authService.currentUser?.name ?? 'Usuario (Centro)';

    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _handleRefresh,
          color: AppConstants.primaryColor,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(), // Asegura que funcione aunque haya poco contenido
            child: Column(
              children: [
                // Header con gradiente
                _buildHeader(context, userName, role),
                
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
                          // Tendencia NY - Real Data Widget
                          const MarketDashboardWidget(),
                          
                          const SizedBox(height: AppConstants.largePadding),
                          
                          // VITRINA COMERCIAL (Feed según Rol)
                          _buildVitrinaFeed(role),
                          
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
      ),
    );
  }

  Widget _buildVitrinaFeed(String role) {
    // Título de la sección
    String sectionTitle = 'Mercado Global'; 
    
    // Subtítulos dinámicos opcionales
    if (role == 'proveedor') sectionTitle = 'Mercado Global (Mejores Ofertas)';
    if (role == 'exportadora') sectionTitle = 'Mercado Global (Lotes Disponibles)';
    if (role == 'superuser') sectionTitle = 'Mercado Global (Vista de Superusuario)';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
           mainAxisAlignment: MainAxisAlignment.spaceBetween,
           children: [
             Text(sectionTitle, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppConstants.textPrimary)),
             if (PublicationService().isSyncing) // Future enhancement: reactive syncing state
                const SizedBox(
                  width: 16, height: 16, 
                  child: CircularProgressIndicator(strokeWidth: 2)
                ),
           ],
        ),
        const SizedBox(height: 16),
        
        // --- REAL DB DATA (Prioritized) ---
        FutureBuilder<List<Map<String, dynamic>>>(
          future: PublicationService().getFeedForRole(role),
          builder: (context, snapshot) {
            // Manejo de Carga
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: Padding(
                padding: EdgeInsets.all(32.0),
                child: CircularProgressIndicator.adaptive(),
              ));
            }

            // Manejo de Errores
            if (snapshot.hasError) {
              return _buildErrorState('Error al cargar publicaciones.\n${snapshot.error}');
            }

            // Datos Vacíos (Empty State)
            final dbList = snapshot.data ?? [];
            if (dbList.isEmpty) {
              return _buildEmptyState();
            }
            
            // Lista de Publicaciones
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: dbList.map((data) {
                  // Map DB data to Widget props
                  final type = data['type'] == 'buy_price' || data['type'] == 'demand_contract' 
                      ? PublicationType.demanda 
                      : PublicationType.oferta;
                      
                  String title = 'Publicación';
                  String subtitle = 'Detalles...';
                  String price = '\$0';
                  
                  // Safe parsing with fallbacks
                  try {
                    if (data['type'] == 'buy_price') {
                      title = 'Compra: ${data['variety'] ?? 'Cacao'}';
                      subtitle = 'Estado: ${data['state'] ?? 'N/A'}';
                      price = '\$${data['price'] ?? 0} / qq';
                    } else if (data['type'] == 'demand_contract') {
                      title = 'Cupo: ${data['contractType'] ?? 'General'}';
                      subtitle = '${data['grade'] ?? 'Std'}';
                      price = 'Ref: \$${data['priceRef'] ?? 0}';
                    } else {
                      // Lote / Oferta
                      title = 'Venta: ${data['variety'] ?? 'Cacao'}';
                      subtitle = '${data['volume'] ?? 0} kg';
                      price = '\$${data['price'] ?? 0}';
                    }
                  } catch (e) {
                     debugPrint('Error parsing publication item: $e');
                  }

                  return _buildPublication(
                    type, 
                    title, 
                    data['author_name'] ?? 'Usuario', 
                    data['role'] ?? 'unknown', 
                    subtitle, 
                    price, 
                    [], // Tags can be parsed from data if exists
                  );
                }).toList(),
            );
          },
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 40.0, horizontal: 20),
        child: Column(
          children: [
            Icon(Icons.inbox_outlined, size: 48, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              'No hay publicaciones recientes',
              style: TextStyle(fontSize: 16, color: Colors.grey[600], fontWeight: FontWeight.w500),
            ),
            const SizedBox(height: 8),
            Text(
              'Las ofertas y demandas del mercado aparecerán aquí.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 14, color: Colors.grey[500]),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState(String message) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            const Icon(Icons.error_outline, size: 40, color: Colors.redAccent),
            const SizedBox(height: 10),
            Text(
              message,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.redAccent),
            ),
            TextButton(
              onPressed: _handleRefresh,
              child: const Text('Reintentar'),
            )
          ],
        ),
      ),
    );
  }


  Widget _buildPublication(PublicationType type, String title, String author, String role, String subtitle, String price, List<String> tags) {
    return PublicationCard(
      type: type,
      title: title,
      author: author,
      role: role,
      subtitle: subtitle,
      price: price,
      tags: tags,
      onTap: () {
        // Start or Open Chat
        final chatService = context.read<ChatService>();
        final chat = chatService.startChat(author, title, role);
        
        // Navigate
        Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => ChatDetailPage(chat: chat)),
        );
      },
    );
  }
  
  Widget _buildHeader(BuildContext context, String userName, String role) {
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
                        'Hola, $userName 👋',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Mercado de $role',
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.9),
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.all(2),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white, width: 2),
                  ),
                  child: const CircleAvatar(
                    radius: 20,
                    backgroundColor: AppConstants.primaryColor,
                    child: Icon(Icons.person, color: Colors.white),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
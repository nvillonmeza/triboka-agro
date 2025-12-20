import 'package:flutter/material.dart';
import 'package:flutter_staggered_animations/flutter_staggered_animations.dart';
import 'package:provider/provider.dart';
import '../widgets/market_dashboard_widget.dart';
import '../widgets/publication_card.dart'; // Vitrina Widget
import '../services/auth_service.dart';
import '../utils/constants.dart';
import 'package:triboka_app/services/publication_service.dart';

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

  @override
  Widget build(BuildContext context) {
    final authService = context.watch<AuthService>();
    final role = authService.currentUser?.role ?? 'centro'; // Default to centro for testing
    final userName = authService.currentUser?.name ?? 'Usuario (Centro)';

    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
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
    );
  }

  Widget _buildVitrinaFeed(String role) {
    // Título de la sección
    String sectionTitle = 'Mercado Global'; // Updated per user request
    
    // Subtítulos dinámicos opcionales
    if (role == 'proveedor') sectionTitle = 'Mercado Global (Mejores Ofertas)';
    if (role == 'exportadora') sectionTitle = 'Mercado Global (Lotes Disponibles)';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(sectionTitle, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppConstants.textPrimary)),
        const SizedBox(height: 16),
        
        // --- REAL DB DATA (Prioritized) ---
        FutureBuilder<List<Map<String, dynamic>>>(
          future: PublicationService().getFeedForRole(role),
          builder: (context, snapshot) {
            if (!snapshot.hasData || snapshot.data!.isEmpty) return const SizedBox.shrink();
            
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                ...snapshot.data!.map((data) {
                  // Map DB data to Widget props
                  final type = data['type'] == 'buy_price' || data['type'] == 'demand_contract' 
                      ? PublicationType.demanda 
                      : PublicationType.oferta;
                      
                  String title = 'Publicación';
                  String subtitle = 'Detalles...';
                  String price = '\$0';
                  
                  if (data['type'] == 'buy_price') {
                    title = 'Compra: ${data['variety']}';
                    subtitle = 'Estado: ${data['state']}';
                    price = '\$${data['price']} / qq';
                  } else if (data['type'] == 'demand_contract') {
                    title = 'Cupo: ${data['contractType']}';
                    subtitle = '${data['grade']} (' + (data['requiresCert'] ? 'Certificado' : 'Std') + ')';
                    price = 'Ref: \$${data['priceRef']}';
                  } else {
                    // Lote / Oferta
                    title = 'Venta: ${data['variety']}';
                    subtitle = '${data['volume']} kg - ${data['state']}';
                    price = '\$${data['price']}';
                  }

                  return _buildPublication(
                    type, 
                    title, 
                    'Usuario Registrado', // In robust app, fetch user name
                    data['role'] ?? 'unknown', 
                    subtitle, 
                    price, 
                    ['Nuevo', 'Real DB'],
                  );
                }).toList(),
                const Divider(height: 32, thickness: 1, color: Colors.grey), // Separator between Real and Examples
              ],
            );
          },
        ),

        // --- STATIC EXAMPLES (Below) ---
        // Feed Logic - "Ceguera Competitiva"
        // Exportadora -> Ve: Centro, Proveedor
        if (role == 'exportadora') ...[
          _buildPublication(
            PublicationType.oferta, 'Lote Premium - 50 Tons', 'Centro de Acopio "El Triunfo"', 'centro', 
            'Listo para despacho', '\$240 / qq', ['Calidad A', 'Humedad 7%'],
          ),
          _buildPublication(
            PublicationType.oferta, 'Cacao Orgánico', 'Asoc. Productores San Juan', 'proveedor', 
            'Volumen: 5 Tons', '\$225 / qq', ['Orgánico', 'Certificado'],
          ),
        ],

        // Centro -> Ve: Exportadora, Proveedor
        if (role == 'centro') ...[
           _buildPublication(
            PublicationType.demanda, 'Busco Cacao CCN51', 'Exportadora "Global Cocoa"', 'exportadora', 
            'Contrato #EXP-2024', '\$250 / qq', ['CCN51', 'Seco'],
          ),
          _buildPublication(
            PublicationType.oferta, 'Cosecha Reciente - 1200 kg', 'Finca "La Bendición"', 'proveedor', 
            'Fermentado en cajón', '\$230 / qq', ['Nacional', 'Fermentado'],
          ),
        ],

        // Proveedor OR Default/Guest (Show Producer View as Fallback to ensure data is seen)
        if (role == 'proveedor' || role == 'user' || role == 'invitado') ...[
           _buildPublication(
            PublicationType.demanda, 'Compro Cacao Seco', 'Centro "El Buen Grano"', 'centro', 
            'Pago Inmediato', '\$220 / qq', ['Efectivo', 'Seco'],
          ),
          _buildPublication(
            PublicationType.demanda, 'Cupo Especial Certificado', 'Exp. "Natures Best"', 'exportadora', 
            'Certificación Orgánica', '\$260 / qq', ['Orgánico', 'FairTrade'],
          ),
           // Added extra example for richness
           _buildPublication(
            PublicationType.demanda, 'Busco Grado A', 'Centro "Acopio Norte"', 'centro', 
            'Pago Contra Entrega', '\$215 / qq', ['Seco', 'Limpio'],
          ),
        ],
      ],
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
      onTap: () => _showActionSnackBar('Abriendo detalle de ${type == PublicationType.oferta ? "Oferta" : "Demanda"}...'),
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
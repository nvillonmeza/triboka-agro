import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../utils/constants.dart';
import '../../services/analytics_service.dart';
import '../../widgets/dashboard_widgets.dart'; // Reusable widgets
import '../../widgets/publication_card.dart'; // Vitrina widget
import '../../widgets/simulation_banner.dart';
import '../forms/publish_lot_page.dart';
import '../forms/publish_price_page.dart';

class CentroDashboard extends StatefulWidget {
  const CentroDashboard({super.key}); // Updated with Action Buttons

  @override
  State<CentroDashboard> createState() => _CentroDashboardState();
}

class _CentroDashboardState extends State<CentroDashboard> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AnalyticsService>().fetchMetrics('centro');
    });
  }
  
  void _showActionSnackBar(String action) {
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(action)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final analytics = context.watch<AnalyticsService>();
    final metrics = analytics.metrics;

    if (analytics.isLoading && metrics == null) {
      return const Center(child: CircularProgressIndicator());
    }

    return Column(
      children: [
        // SimulationBanner(isVisible: analytics.isSimulated), // Hidden for Production Polish
        Expanded(
          child: SingleChildScrollView(
            physics: const ClampingScrollPhysics(),
            padding: const EdgeInsets.all(AppConstants.defaultPadding),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeader(),
                
                const SizedBox(height: AppConstants.largePadding),

                // --- RESUMEN OPERATIVO DIARIO ---
                _buildDailySummaryCard(metrics),
                const SizedBox(height: AppConstants.largePadding),

                // --- PUBLICAR (Oferta Comercial) ---
                const Text('Gestión Comercial', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
                const SizedBox(height: 12),
                
                // Botones de Acción
                Row(
                  children: [
                    Expanded(
                      child: _buildActionButton(
                        context,
                        'Vender Lote',
                        Icons.inventory_2_outlined,
                        Colors.green,
                        () => Navigator.push(context, MaterialPageRoute(builder: (_) => const PublishLotPage(role: 'centro'))),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildActionButton(
                        context,
                        'Comprar (Precio)',
                        Icons.monetization_on_outlined,
                        Colors.blue,
                        () => Navigator.push(context, MaterialPageRoute(builder: (_) => const PublishPricePage())),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                // Botón de Informe (Nuevo)
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () => _showActionSnackBar('Módulo de Informes: Conexión API / CSV (Próximamente)'),
                    icon: const Icon(Icons.assessment_outlined),
                    label: const Text('Registrar Informe Externo'),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.all(16),
                      side: const BorderSide(color: Colors.grey),
                    ),
                  ),
                ),
                
                const SizedBox(height: AppConstants.largePadding),

                const SizedBox(height: AppConstants.largePadding),
                
                const SizedBox(height: AppConstants.largePadding),
                
                // Alerts & Other Widgets
                if ((metrics?.capacityOccupied ?? 0) > 80)
                  _buildAlertCard(metrics!.capacityOccupied),

                const SizedBox(height: AppConstants.defaultPadding),

                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(color: Colors.grey.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, 4)),
                    ],
                  ),
                  child: const VolumeBarChart(weeklyData: []), // Pass empty list for now until API provides history
                ),
                
                const SizedBox(height: 80),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildHeader() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [const Color(0xFF0F766E), const Color(0xFF14B8A6)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF0F766E).withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Icon(Icons.storefront, color: Colors.white, size: 32),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Centro de Acopio', style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
                Container(
                  margin: const EdgeInsets.only(top: 4),
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text('Comercio & Operaciones', style: TextStyle(color: Colors.white, fontSize: 12)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildPublishSection() {
    return Row(
      children: [
        Expanded(
          child: _buildActionCard(
            label: 'Publicar\nLote a Venta',
            icon: Icons.upload,
            color: Colors.blue,
            onTap: () => _showActionSnackBar('Publicando Lote para Exportadores...'),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildActionCard(
            label: 'Publicar\nPrecio Compra',
            icon: Icons.price_check,
            color: Colors.green,
            onTap: () => _showActionSnackBar('Publicando Precio para Productores...'),
          ),
        ),
      ],
    );
  }
  
  Widget _buildActionCard({required String label, required IconData icon, required Color color, required VoidCallback onTap}) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.2)),
        ),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(shape: BoxShape.circle, color: color.withOpacity(0.1)),
              child: Icon(icon, color: color, size: 24),
            ),
            const SizedBox(height: 12),
            Text(label, textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
          ],
        ),
      ),
    );
  }

  Widget _buildDailySummaryCard(AnalyticsData? metrics) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white, // Keep it clean to contrast with Vitrina
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 15, offset: const Offset(0, 5)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Resumen Diario', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              Text('Stock: ${metrics?.stockKg.toStringAsFixed(0) ?? 0} kg', style: const TextStyle(color: Colors.teal, fontWeight: FontWeight.bold)),
            ],
          ),
          // ... Simplified summary for visual balance
        ],
      ),
    );
  }

  Widget _buildActionButton(BuildContext context, String label, IconData icon, Color color, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 100,
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(label, style: TextStyle(color: color, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }

  Widget _buildAlertCard(double capacity) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.red.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.red.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.warning_amber, color: Colors.red),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Alerta de Capacidad', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.red)),
                Text('Bodega al ${capacity.toStringAsFixed(0)}% de capacidad', style: const TextStyle(fontSize: 12)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../utils/constants.dart';
import '../../services/analytics_service.dart';
import '../../widgets/dashboard_widgets.dart'; // Reusable widgets
import '../../widgets/publication_card.dart'; // Vitrina widget
import '../forms/publish_lot_page.dart';
import '../../widgets/simulation_banner.dart';

class ProveedorDashboard extends StatefulWidget {
  const ProveedorDashboard({super.key});

  @override
  State<ProveedorDashboard> createState() => _ProveedorDashboardState();
}

class _ProveedorDashboardState extends State<ProveedorDashboard> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AnalyticsService>().fetchMetrics('proveedor');
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
        SimulationBanner(isVisible: analytics.isSimulated),
        Expanded(
          child: SingleChildScrollView(
            physics: const ClampingScrollPhysics(),
            padding: const EdgeInsets.all(AppConstants.defaultPadding),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeader(),
                
                const SizedBox(height: AppConstants.largePadding),
                
                // --- MIS LOTES (Gestión Interna) ---
                _buildLotesSection(),

                const SizedBox(height: AppConstants.largePadding),
                
                const SizedBox(height: AppConstants.largePadding),
                
                const SizedBox(height: AppConstants.largePadding),

                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(color: Colors.grey.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, 4)),
                    ],
                  ),
                  child: const QualityLineChart(),
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
          colors: [Colors.green.shade700, Colors.green.shade500],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.green.withOpacity(0.3),
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
            child: const Icon(Icons.agriculture, color: Colors.white, size: 32),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Productor', style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
                Container(
                  margin: const EdgeInsets.only(top: 4),
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text('Gestión & Ventas', style: TextStyle(color: Colors.white, fontSize: 12)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLotesSection() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.green.withOpacity(0.2)),
        boxShadow: [
          BoxShadow(color: Colors.green.withOpacity(0.05), blurRadius: 15, offset: const Offset(0, 5)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Mis Lotes', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              FilledButton.icon(
                onPressed: () => _showActionSnackBar('Publicando lote en Vitrina...'),
                icon: const Icon(Icons.store, size: 16),
                label: const Text('PUBLICAR'),
                style: FilledButton.styleFrom(
                  backgroundColor: Colors.green,
                  visualDensity: VisualDensity.compact,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Stepper remains the same
          Row(
            children: [
              _buildStepItem('Cosecha', true),
              _buildStepConnector(true),
              _buildStepItem('Fermento', true),
              _buildStepConnector(false),
              _buildStepItem('Secado', false),
              _buildStepConnector(false),
              _buildStepItem('Venta', false),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildStepItem(String label, bool isActive) {
    return Column(
      children: [
        CircleAvatar(
          radius: 14,
          backgroundColor: isActive ? Colors.green : Colors.grey.shade200,
          child: Icon(isActive ? Icons.check : Icons.circle, size: 12, color: isActive ? Colors.white : Colors.grey),
        ),
        const SizedBox(height: 4),
        Text(label, style: TextStyle(fontSize: 10, color: isActive ? Colors.green : Colors.grey, fontWeight: FontWeight.bold)),
      ],
    );
  }
  
  Widget _buildStepConnector(bool isActive) {
    return Expanded(
      child: Container(
        height: 2,
        color: isActive ? Colors.green : Colors.grey.shade200,
        margin: const EdgeInsets.symmetric(horizontal: 4, vertical: 14), 
        alignment: Alignment.center,
      ),
    );
  }
}

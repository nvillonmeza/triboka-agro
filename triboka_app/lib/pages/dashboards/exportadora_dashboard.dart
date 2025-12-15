import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../utils/constants.dart';
import '../../services/fijacion_service.dart';
import '../../services/contract_service.dart';
import '../../services/analytics_service.dart';
import '../../widgets/market_dashboard_widget.dart';

import '../../widgets/simulation_banner.dart';

class ExportadoraDashboard extends StatefulWidget {
  const ExportadoraDashboard({super.key});

  @override
  State<ExportadoraDashboard> createState() => _ExportadoraDashboardState();
}

class _ExportadoraDashboardState extends State<ExportadoraDashboard> {
  
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AnalyticsService>().fetchMetrics('exportadora');
    });
  }

  @override
  Widget build(BuildContext context) {
    // Consume services
    final contractService = context.watch<ContractService>();
    final fijacionService = context.watch<FijacionService>();
    final analytics = context.watch<AnalyticsService>();
    final metrics = analytics.metrics;
    
    int activeContracts = contractService.contracts.where((c) => c.status == 'active').length;
    // Combine isSimulated from Analytics or Contracts
    bool isSimulated = analytics.isSimulated || contractService.isSimulated;

    return Column(
      children: [
        SimulationBanner(isVisible: isSimulated),
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(AppConstants.defaultPadding),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeader(),
                const SizedBox(height: AppConstants.largePadding),
                
                // Market Dashboard Integration
                const MarketDashboardWidget(),
                const SizedBox(height: AppConstants.largePadding),

                const Text('KPIs Exportación', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
                const SizedBox(height: AppConstants.defaultPadding),
                
                _buildMetricsGrid(activeContracts, fijacionService),
                
                const SizedBox(height: AppConstants.largePadding),
                _buildDetailsCard(metrics),
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
      padding: const EdgeInsets.all(AppConstants.largePadding),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.blue.shade600, Colors.blue.shade400],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
      ),
      child: Row(
        children: [
          const Icon(Icons.local_shipping, color: Colors.white, size: 28),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Exportadora', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
              Text('Operaciones Internacionales', style: TextStyle(color: Colors.white.withOpacity(0.9))),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMetricsGrid(int activeContracts, FijacionService fijacionService) {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 3,
      crossAxisSpacing: 8,
      mainAxisSpacing: 8,
      childAspectRatio: 0.9,
      children: [
        _buildMetricCard('Pendientes', '$activeContracts', Icons.assignment_late, Colors.blue),
        _buildMetricCard('Fijaciones', '5', Icons.verified, Colors.green), // Mock count
        _buildMetricCard('Mercado', fijacionService.mercadoAbierto ? 'Abierto' : 'Cerrado', Icons.store, fijacionService.mercadoAbierto ? Colors.green : Colors.red),
      ],
    );
  }

  Widget _buildMetricCard(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 4),
          Text(label, style: TextStyle(fontSize: 11, color: color), textAlign: TextAlign.center),
          Text(value, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: color)),
        ],
      ),
    );
  }

  Widget _buildDetailsCard(AnalyticsData? metrics) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildDetailItem('Embarques esta semana', '${metrics?.pendingShipments ?? 3}'),
            const Divider(),
            _buildDetailItem('Volumen Comprometido', '120 MT'),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailItem(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey)), 
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold))
      ],
    );
  }
}

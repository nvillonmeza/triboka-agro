import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../utils/constants.dart';
import '../../services/analytics_service.dart';

import '../../widgets/simulation_banner.dart';

class CentroDashboard extends StatefulWidget {
  const CentroDashboard({super.key});

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
            padding: const EdgeInsets.all(AppConstants.defaultPadding),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeader(),
                const SizedBox(height: AppConstants.largePadding),
                const Text('Resumen del Centro', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
                const SizedBox(height: AppConstants.defaultPadding),
                _buildMetricsGrid(metrics),
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
          colors: [AppConstants.primaryColor, AppConstants.secondaryColor],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
      ),
      child: Row(
        children: [
          const Icon(Icons.home_work, color: Colors.white, size: 28),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Centro de Acopio', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
              Text('Administración y Logística', style: TextStyle(color: Colors.white.withOpacity(0.9))),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMetricsGrid(AnalyticsData? metrics) {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 3,
      crossAxisSpacing: 8,
      mainAxisSpacing: 8,
      childAspectRatio: 0.9,
      children: [
        _buildMetricCard('Ubicación', metrics?.location ?? 'Unknown', Icons.location_on, Colors.red),
        _buildMetricCard('Stock Total', '${metrics?.stockKg.toStringAsFixed(0) ?? 0} kg', Icons.inventory, Colors.green),
        _buildMetricCard('Socios', '${metrics?.partnerCount ?? 0}', Icons.people, Colors.blue),
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
            _buildDetailItem('Capacidad Ocupada', '${metrics?.capacityOccupied.toStringAsFixed(1) ?? 0}%'),
            const Divider(),
            _buildDetailItem('Envíos Pendientes', '${metrics?.pendingShipments ?? 0}'),
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

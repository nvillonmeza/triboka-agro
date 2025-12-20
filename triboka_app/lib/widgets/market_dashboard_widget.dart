import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../services/market_service.dart';
import '../services/contract_service.dart';
import '../utils/constants.dart';
import 'dart:math';

class MarketDashboardWidget extends StatefulWidget {
  const MarketDashboardWidget({super.key});

  @override
  State<MarketDashboardWidget> createState() => _MarketDashboardWidgetState();
}

class _MarketDashboardWidgetState extends State<MarketDashboardWidget> {
  @override
  void initState() {
    super.initState();
    // Fetch data initially
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<MarketService>().fetchData();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer2<MarketService, ContractService>(
      builder: (context, market, contracts, child) {
        if (market.isLoading && market.currentData == null) {
          return const SizedBox(
            height: 300,
            child: Center(child: CircularProgressIndicator()),
          );
        }

        final data = market.currentData;
        final isUp = (data?.changePercent ?? 0) >= 0;
        final color = isUp ? Colors.green : Colors.red;

        // Calculate Contract Averages
        double totalContractVol = 0;
        double totalContractVal = 0;
        double totalFixedVol = 0;
        double totalFixedVal = 0;

        for (var c in contracts.contracts) {
          if (c.status != 'draft') {
            // Using a mock avg price for contract if not detailed
            // In real app, calculate from batches
            double avgPrice = 3250.0; // Mock base
            totalContractVol += c.totalVolumeMt;
            totalContractVal += c.totalVolumeMt * avgPrice;

            if (c.fixations != null) {
               for (var f in c.fixations!) {
                 totalFixedVol += f.fixedQuantityMt;
                 totalFixedVal += f.fixedQuantityMt * f.spotPriceUsd; // Approx
               }
            }
          }
        }

        double avgContractPrice = totalContractVol > 0 ? totalContractVal / totalContractVol : 0;
        double avgFixedPrice = totalFixedVol > 0 ? totalFixedVal / totalFixedVol : 0;
        double differential = avgContractPrice - (data?.price ?? 0);

        return Column(
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Expanded(
                  child: Text(
                    'Bolsa de Valores (NY ICE)',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                if (market.isMarketOpen)
                  Padding(
                    padding: const EdgeInsets.only(left: 8.0),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.green.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.green),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (data?.isOffline == true)
                            Padding(
                              padding: const EdgeInsets.only(right: 4.0),
                              child: const Icon(Icons.wifi_off, size: 14, color: Colors.orange),
                            ),
                          Text(
                            market.isMarketOpen ? 'MERCADO ABIERTO' : 'CERRADO',
                            style: TextStyle(
                              color: market.isMarketOpen ? Colors.green : Colors.grey,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 16),

            // Spot Price Big Display
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [AppConstants.primaryColor, AppConstants.primaryColor.withOpacity(0.8)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(color: AppConstants.primaryColor.withOpacity(0.3), blurRadius: 10, offset: const Offset(0, 4)),
                ],
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    flex: 3,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('CACAO FUTURES (CC=F)', style: TextStyle(color: Colors.white70, fontSize: 12)),
                        const SizedBox(height: 4),
                        FittedBox(
                          fit: BoxFit.scaleDown,
                          child: Text(
                            '\$${data?.price.toStringAsFixed(2) ?? '---'}',
                            style: const TextStyle(color: Colors.white, fontSize: 32, fontWeight: FontWeight.bold),
                          ),
                        ),
                        FittedBox(
                          fit: BoxFit.scaleDown,
                          child: Row(
                            children: [
                              Icon(isUp ? Icons.arrow_upward : Icons.arrow_downward, color: Colors.white, size: 16),
                              const SizedBox(width: 4),
                              Text(
                                '${data?.change.abs().toStringAsFixed(2)} (${data?.changePercent.abs().toStringAsFixed(2)}%)',
                                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w500),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    flex: 2,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        _buildMiniStat('Rango Día', '${data?.dayLow.toStringAsFixed(0)} - ${data?.dayHigh.toStringAsFixed(0)}'),
                        const SizedBox(height: 8),
                        _buildMiniStat('Volumen', '15.2K'), // Mock volume if not in API
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 20),

            // 4 Key Stats Cards
            LayoutBuilder(
              builder: (context, constraints) {
                final width = constraints.maxWidth;
                final cardWidth = (width - 16) / 2; // 2 columns
                return Wrap(
                  spacing: 16,
                  runSpacing: 16,
                  children: [
                    _buildStatCard('Prom. Contratos', '\$${avgContractPrice.toStringAsFixed(0)}', Icons.description, Colors.blue, cardWidth),
                    _buildStatCard('Prom. Fijado', '\$${avgFixedPrice.toStringAsFixed(0)}', Icons.verified, Colors.orange, cardWidth),
                    _buildStatCard('Diferencial', '\$${differential.toStringAsFixed(0)}', Icons.compare_arrows, differential >= 0 ? Colors.green : Colors.red, cardWidth),
                    _buildStatCard('Volatilidad', '${((data?.changePercent ?? 0).abs() * 1.5).toStringAsFixed(2)}%', Icons.show_chart, Colors.purple, cardWidth),
                  ],
                );
              },
            ),

            const SizedBox(height: 24),
            
            // Chart
            const Text('Movimiento Intradía', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: LineChart(
                LineChartData(
                  gridData: const FlGridData(show: false),
                  titlesData: const FlTitlesData(
                     leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                     rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 40)),
                     topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                     bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  ),
                  borderData: FlBorderData(show: false),
                  lineBarsData: [
                    LineChartBarData(
                      spots: _generateSpots(market.intradayPoints),
                      isCurved: true,
                      color: isUp ? Colors.green : Colors.red,
                      barWidth: 3,
                      isStrokeCapRound: true,
                      dotData: const FlDotData(show: false),
                      belowBarData: BarAreaData(
                        show: true,
                        color: (isUp ? Colors.green : Colors.red).withOpacity(0.1),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 8),
             Center(
               child: TextButton.icon(
                 onPressed: () => market.fetchData(),
                 icon: const Icon(Icons.refresh, size: 16),
                 label: const Text('Actualizar Datos'),
               ),
             )
          ],
        );
      },
    );
  }

  Widget _buildMiniStat(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(label, style: TextStyle(color: Colors.white.withOpacity(0.7), fontSize: 10)),
        Text(value, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
      ],
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color, double width) {
    return Container(
      width: width,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 4, offset: const Offset(0, 2)),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 12),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 11),
                  overflow: TextOverflow.ellipsis,
                ),
                FittedBox(
                  alignment: Alignment.centerLeft,
                  fit: BoxFit.scaleDown,
                  child: Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  List<FlSpot> _generateSpots(List<double> points) {
    if (points.isEmpty) return [];
    return List.generate(points.length, (index) => FlSpot(index.toDouble(), points[index]));
  }
}

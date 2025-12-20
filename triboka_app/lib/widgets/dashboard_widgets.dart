import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../utils/constants.dart';

// --- QUICK ACTIONS ---

class QuickActionItem {
  final String label;
  final IconData icon;
  final VoidCallback onTap;
  final Color color;

  QuickActionItem({
    required this.label,
    required this.icon,
    required this.onTap,
    this.color = AppConstants.primaryColor,
  });
}

class QuickActionsGrid extends StatelessWidget {
  final List<QuickActionItem> actions;

  const QuickActionsGrid({super.key, required this.actions});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Acciones Rápidas',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 4,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 0.85,
          ),
          itemCount: actions.length,
          itemBuilder: (context, index) {
            final action = actions[index];
            return InkWell(
              onTap: action.onTap,
              borderRadius: BorderRadius.circular(12),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: action.color.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: action.color.withOpacity(0.2)),
                    ),
                    child: Icon(action.icon, color: action.color, size: 24),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    action.label,
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w500),
                  ),
                ],
              ),
            );
          },
        ),
      ],
    );
  }
}

// --- STATS WITH TREND ---

class PremiumStatCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;
  final String? trend; // "+12%" or "-5%"
  final bool isPositiveTrend;

  const PremiumStatCard({
    super.key,
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
    this.trend,
    this.isPositiveTrend = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12), // Reduced padding from 16
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.08),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: color, size: 18),
              ),
              if (trend != null)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: (isPositiveTrend ? Colors.green : Colors.red).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        isPositiveTrend ? Icons.arrow_upward : Icons.arrow_downward,
                        size: 10,
                        color: isPositiveTrend ? Colors.green : Colors.red,
                      ),
                      const SizedBox(width: 2),
                      Text(
                        trend!,
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          color: isPositiveTrend ? Colors.green : Colors.red,
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),
          const Spacer(),
          FittedBox( // Prevent overflow on large numbers
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerLeft,
            child: Text(
              value,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w800),
            ),
          ),
          const SizedBox(height: 2), // Reduced spacing
          Text(
            label,
            style: TextStyle(fontSize: 11, color: Colors.grey.shade600), // Slightly smaller font
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}

// --- CHARTS ---

// --- CHARTS ---
// Updated for Production: Accepts data or shows Empty State

class QualityLineChart extends StatelessWidget {
  final List<FlSpot>? spots;
  final String title;

  const QualityLineChart({super.key, this.spots, this.title = 'Calidad (Últimos 6 meses)'});

  @override
  Widget build(BuildContext context) {
    if (spots == null || spots!.isEmpty) {
      return _buildEmptyChart(title);
    }

    // Calculate Average
    double sum = spots!.fold(0, (p, c) => p + c.y);
    double avg = sum / spots!.length;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.green.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text('Promedio: ${avg.toStringAsFixed(0)}%', style: const TextStyle(fontSize: 11, color: Colors.green, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
        const SizedBox(height: 16),
        AspectRatio(
          aspectRatio: 1.70,
          child: LineChart(
            LineChartData(
              gridData: const FlGridData(show: false),
              titlesData: FlTitlesData(
                show: true,
                rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                bottomTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 30,
                    interval: 1,
                    getTitlesWidget: (value, meta) {
                       return Text(value.toInt().toString(), style: const TextStyle(fontSize: 10));
                    },
                  ),
                ),
                leftTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    interval: 20,
                    getTitlesWidget: (value, meta) {
                      if (value == 0) return const SizedBox.shrink();
                      return Text('${value.toInt()}%', style: const TextStyle(fontSize: 10));
                    },
                    reservedSize: 30,
                  ),
                ),
              ),
              borderData: FlBorderData(show: false),
              minX: 0,
              maxX: spots!.length.toDouble() - 1,
              minY: 0,
              maxY: 100,
              lineBarsData: [
                LineChartBarData(
                  spots: spots!,
                  isCurved: true,
                  color: AppConstants.primaryColor,
                  barWidth: 3,
                  isStrokeCapRound: true,
                  dotData: const FlDotData(show: false),
                  belowBarData: BarAreaData(
                    show: true,
                    color: AppConstants.primaryColor.withOpacity(0.1),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyChart(String title) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 24),
        Center(
          child: Column(
            children: [
              Icon(Icons.show_chart, color: Colors.grey[300], size: 48),
              const SizedBox(height: 8),
              Text('No hay datos históricos aún', style: TextStyle(color: Colors.grey[500], fontSize: 12)),
            ],
          ),
        ),
        const SizedBox(height: 24),
      ],
    );
  }
}

class VolumeBarChart extends StatelessWidget {
  final List<double>? weeklyData; // 7 days

  const VolumeBarChart({super.key, this.weeklyData});

  @override
  Widget build(BuildContext context) {
    if (weeklyData == null || weeklyData!.isEmpty) {
       return _buildEmptyChart();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Acopio Semanal (TM)', style: TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 16),
        AspectRatio(
          aspectRatio: 1.7,
          child: BarChart(
            BarChartData(
              alignment: BarChartAlignment.spaceAround,
              maxY: 20,
              barTouchData: BarTouchData(
                enabled: false,
                touchTooltipData: BarTouchTooltipData(
                  tooltipBgColor: Colors.transparent,
                  tooltipPadding: EdgeInsets.zero,
                  tooltipMargin: 8,
                  getTooltipItem: (
                    BarChartGroupData group,
                    int groupIndex,
                    BarChartRodData rod,
                    int rodIndex,
                  ) {
                    return BarTooltipItem(
                      rod.toY.round().toString(),
                      const TextStyle(
                        color: AppConstants.primaryColor,
                        fontWeight: FontWeight.bold,
                      ),
                    );
                  },
                ),
              ),
              titlesData: FlTitlesData(
                show: true,
                bottomTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    getTitlesWidget: (value, meta) {
                      const style = TextStyle(
                        color: Colors.grey,
                        fontWeight: FontWeight.bold,
                        fontSize: 10,
                      );
                      String text;
                      switch (value.toInt()) {
                        case 0: text = 'Lun'; break;
                        case 1: text = 'Mar'; break;
                        case 2: text = 'Mié'; break;
                        case 3: text = 'Jue'; break;
                        case 4: text = 'Vie'; break;
                        case 5: text = 'Sáb'; break;
                        case 6: text = 'Dom'; break;
                        default: text = '';
                      }
                      return SideTitleWidget(axisSide: meta.axisSide, space: 4, child: Text(text, style: style));
                    },
                  ),
                ),
                leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
              ),
              gridData: const FlGridData(show: false),
              borderData: FlBorderData(show: false),
              barGroups: List.generate(weeklyData!.length, (index) {
                return _makeBarGroup(index, weeklyData![index], 20, Colors.blue);
              }),
            ),
          ),
        ),
      ],
    );
  }
  
  Widget _buildEmptyChart() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Acopio Semanal (TM)', style: TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 24),
        Center(
          child: Column(
            children: [
               Icon(Icons.bar_chart, color: Colors.grey[300], size: 48),
               const SizedBox(height: 8),
               Text('No hay registros de acopio reciente', style: TextStyle(color: Colors.grey[500], fontSize: 12)),
            ],
          ),
        ),
        const SizedBox(height: 24),
      ],
    );
  }

  BarChartGroupData _makeBarGroup(int x, double y, double maxY, Color color) {
    return BarChartGroupData(
      x: x,
      barRods: [
        BarChartRodData(
          toY: y,
          color: color,
          width: 14,
          borderRadius: const BorderRadius.only(topLeft: Radius.circular(4), topRight: Radius.circular(4)),
          backDrawRodData: BackgroundBarChartRodData(
            show: true,
            toY: 20, // Max scale
            color: Colors.grey.withOpacity(0.1),
          ),
        ),
      ],
      showingTooltipIndicators: [0],
    );
  }
}

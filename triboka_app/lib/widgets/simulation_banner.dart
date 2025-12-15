import 'package:flutter/material.dart';

class SimulationBanner extends StatelessWidget {
  final bool isVisible;
  
  const SimulationBanner({super.key, required this.isVisible});

  @override
  Widget build(BuildContext context) {
    if (!isVisible) return const SizedBox.shrink();

    return Container(
      width: double.infinity,
      color: Colors.orange.shade100,
      padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: const [
          Icon(Icons.warning_amber_rounded, size: 16, color: Colors.orange),
          SizedBox(width: 8),
          Text(
            'MODO DEMO: DATOS SIMULADOS',
            style: TextStyle(
              color: Colors.deepOrange,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}

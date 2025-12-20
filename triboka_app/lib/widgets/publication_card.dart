import 'package:flutter/material.dart';
import '../utils/constants.dart';

enum PublicationType { oferta, demanda }

class PublicationCard extends StatelessWidget {
  final PublicationType type;
  final String title;
  final String author;
  final String subtitle; // e.g., "Disponible: 1250 kg" or "Busco: 500 TM"
  final String price;    // e.g., "$220 / qq"
  final List<String> tags; // e.g., ["Cacao Seco", "Grado A", "Humedad 7%"]
  final VoidCallback onTap;
  final String role; // 'exportadora', 'centro', 'productor' needed for coloring/icon

  const PublicationCard({
    super.key,
    required this.type,
    required this.title,
    required this.author,
    required this.subtitle,
    required this.price,
    required this.tags,
    required this.onTap,
    required this.role,
  });

  Color _getRoleColor() {
    switch (role) {
      case 'exportadora': return Colors.blue;
      case 'centro': return const Color(0xFF0F766E); // Teal
      case 'proveedor': return Colors.green;
      default: return Colors.grey;
    }
  }

  IconData _getRoleIcon() {
    switch (role) {
      case 'exportadora': return Icons.public;
      case 'centro': return Icons.storefront;
      case 'proveedor': return Icons.agriculture;
      default: return Icons.person;
    }
  }

  @override
  Widget build(BuildContext context) {
    final roleColor = _getRoleColor();
    final isDemand = type == PublicationType.demanda;

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: Colors.grey.withOpacity(0.2)),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header: Role Badge & Type
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: roleColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: [
                        Icon(_getRoleIcon(), size: 12, color: roleColor),
                        const SizedBox(width: 4),
                        Text(
                          author.toUpperCase(),
                          style: TextStyle(fontSize: 10, color: roleColor, fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: (isDemand ? Colors.orange : Colors.green).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      isDemand ? 'DEMANDA' : 'OFERTA',
                      style: TextStyle(
                        fontSize: 10, 
                        fontWeight: FontWeight.bold, 
                        color: isDemand ? Colors.orange : Colors.green
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              
              // Main Content
              Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppConstants.textPrimary)),
              const SizedBox(height: 4),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(subtitle, style: TextStyle(fontSize: 14, color: Colors.grey.shade600)),
                  Text(price, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppConstants.primaryColor)),
                ],
              ),
              
              const SizedBox(height: 12),
              
              // Tags
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: tags.map((tag) => Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(tag, style: TextStyle(fontSize: 10, color: Colors.grey.shade700)),
                )).toList(),
              ),

              const SizedBox(height: 16),
              
              // Action Button
              SizedBox(
                width: double.infinity,
                child: FilledButton(
                  onPressed: onTap,
                  style: FilledButton.styleFrom(
                    backgroundColor: isDemand ? Colors.orange.shade50 : Colors.green.shade50,
                    foregroundColor: isDemand ? Colors.orange.shade700 : Colors.green.shade700,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: Text(isDemand ? 'VENDERLE A $author' : 'COMPRAR ESTE LOTE'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

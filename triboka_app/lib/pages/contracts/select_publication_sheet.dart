import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:triboka_app/services/publication_service.dart';
import '../../utils/constants.dart';
import '../../services/contract_service.dart';

class SelectPublicationSheet extends StatefulWidget {
  final String userRole;
  const SelectPublicationSheet({super.key, required this.userRole});

  @override
  State<SelectPublicationSheet> createState() => _SelectPublicationSheetState();
}

class _SelectPublicationSheetState extends State<SelectPublicationSheet> {
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.7,
      padding: const EdgeInsets.all(16),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.only(topLeft: Radius.circular(20), topRight: Radius.circular(20)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Seleccionar Publicación Base', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              IconButton(onPressed: () => Navigator.pop(context), icon: const Icon(Icons.close)),
            ],
          ),
          const Divider(),
          if (_isLoading)
             const Expanded(child: Center(child: CircularProgressIndicator()))
          else
            Expanded(
              child: FutureBuilder<List<Map<String, dynamic>>>(
                future: PublicationService().getFeedForRole(widget.userRole),
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
                  final pubs = snapshot.data ?? [];
                  
                  if (pubs.isEmpty) {
                    return Center(child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.inbox, size: 48, color: Colors.grey),
                        const SizedBox(height: 16),
                        const Text('No hay publicaciones activas.'),
                        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cerrar')),
                      ],
                    ));
                  }

                  return ListView.builder(
                    itemCount: pubs.length,
                    itemBuilder: (context, index) {
                      final p = pubs[index];
                      return _buildPublicationItem(p);
                    },
                  );
                },
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildPublicationItem(Map<String, dynamic> pub) {
    final title = pub['variety'] ?? 'Publicación';
    final vol = pub['volume'] != null ? '${pub['volume']} kg' : 'N/A';
    final price = pub['price'] != null ? '\$${pub['price']}' : 'N/A';
    final author = pub['author_name'] ?? 'Desconocido';

    return Card(
      elevation: 0,
      color: Colors.grey[50],
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide(color: Colors.grey[300]!)),
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(backgroundColor: AppConstants.primaryColor.withOpacity(0.1), child: const Icon(Icons.description, color: AppConstants.primaryColor)),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text('De: $author • Vol: $vol • $price'),
        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
        onTap: () => _confirmCreation(pub),
      ),
    );
  }

  void _confirmCreation(Map<String, dynamic> pub) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Crear Contrato'),
        content: Text('¿Generar contrato basado en "${pub['variety']}"?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
          FilledButton(
            onPressed: () async {
              Navigator.pop(ctx); // Close Alert
              await _createContract(pub);
            },
            child: const Text('Crear'),
          ),
        ],
      ),
    );
  }

  Future<void> _createContract(Map<String, dynamic> pub) async {
    setState(() => _isLoading = true);
    
    // Map Publication -> Contract
    // This is a simplification. Real mapping should be robust.
    final contractData = {
      'contract_code': 'CTR-${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}',
      'product_type': pub['variety'] ?? 'Cacao',
      'product_grade': 'Standard', // Default
      'total_volume_mt': (double.tryParse(pub['volume']?.toString() ?? '0') ?? 0) / 1000,
      'differential_usd': 0.0, // Default
      'start_date': DateTime.now().toIso8601String(),
      'end_date': DateTime.now().add(const Duration(days: 30)).toIso8601String(),
    };

    final service = context.read<ContractService>();
    final newContract = await service.createContract(contractData);
    
    setState(() => _isLoading = false);
    
    if (newContract != null) {
      if (mounted) {
         Navigator.pop(context); // Close Sheet
         ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('✅ Contrato Creado'), backgroundColor: Colors.green));
      }
    } else {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Error al crear contrato'), backgroundColor: Colors.red));
    }
  }
}

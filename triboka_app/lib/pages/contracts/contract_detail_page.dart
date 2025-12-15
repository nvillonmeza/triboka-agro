import 'package:flutter/material.dart';
import '../../utils/constants.dart';
import '../../models/contract_model.dart';
import '../../services/pdf_service.dart';
import '../../services/fijacion_service.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'create_fixation_dialog.dart';

class ContractDetailPage extends StatelessWidget {
  final ExportContract contract;

  const ContractDetailPage({super.key, required this.contract});

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('dd MMM yyyy');

    return Scaffold(
      backgroundColor: AppConstants.backgroundLight,
      appBar: AppBar(
        title: Text(contract.contractCode),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.edit_outlined),
            onPressed: () {
              // TODO: Implementar edición
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Edición próximamente')),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.picture_as_pdf_outlined),
            tooltip: 'Exportar PDF',
            onPressed: () async {
              try {
                await PdfService().generateAndOpenContract(contract);
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Error al generar PDF: $e'), backgroundColor: Colors.red),
                  );
                }
              }
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppConstants.defaultPadding),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Card
            Container(
              padding: const EdgeInsets.all(AppConstants.defaultPadding),
              decoration: BoxDecoration(
                color: AppConstants.cardWhite,
                borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
                boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 4)],
              ),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Estado',
                        style: TextStyle(color: AppConstants.textSecondary),
                      ),
                      Chip(
                        label: Text(
                          contract.status.toUpperCase(),
                          style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                        ),
                        backgroundColor: contract.status == 'active' 
                          ? Colors.green 
                          : contract.status == 'draft' ? Colors.orange : Colors.blue,
                        padding: EdgeInsets.zero,
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        side: BorderSide.none,
                      ),
                    ],
                  ),
                  const Divider(),
                  _buildDetailRow('Comprador', contract.buyerCompany?.name ?? '-'),
                  _buildDetailRow('Exportador', contract.exporterCompany?.name ?? '-'),
                  _buildDetailRow('Entrega', contract.deliveryDate != null 
                    ? dateFormat.format(contract.deliveryDate!) 
                    : '-'),
                ],
              ),
            ),

            const SizedBox(height: AppConstants.defaultPadding),
            const Text('Detalles Comerciales', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 8),

            // Commercial Details
            Container(
              padding: const EdgeInsets.all(AppConstants.defaultPadding),
              decoration: BoxDecoration(
                color: AppConstants.cardWhite,
                borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
              ),
              child: Column(
                children: [
                  _buildDetailRow('Producto', contract.productType),
                  _buildDetailRow('Calidad', contract.productGrade),
                  const Divider(),
                  _buildDetailRow('Volumen Total', '${contract.totalVolumeMt} TM'),
                  _buildDetailRow('Volumen Fijado', '${contract.fixedVolumeMt} TM'),
                  _buildDetailRow('Pendiente', '${contract.totalVolumeMt - contract.fixedVolumeMt} TM'),
                  const Divider(),
                  _buildDetailRow('Diferencial', '${contract.differentialUsd >= 0 ? '+' : ''}\$${contract.differentialUsd} USD/TM'),
                ],
              ),
            ),

            const SizedBox(height: AppConstants.defaultPadding),
            const Text('Progreso de Fijación', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 8),

            // Progress Bar
            Container(
              padding: const EdgeInsets.all(AppConstants.defaultPadding),
              decoration: BoxDecoration(
                color: AppConstants.cardWhite,
                borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
              ),
              child: Column(
                children: [
                  LinearProgressIndicator(
                    value: contract.totalVolumeMt > 0 
                      ? contract.fixedVolumeMt / contract.totalVolumeMt 
                      : 0,
                    minHeight: 10,
                    borderRadius: BorderRadius.circular(5),
                    color: AppConstants.primaryColor,
                    backgroundColor: Colors.grey.shade200,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${((contract.totalVolumeMt > 0 ? contract.fixedVolumeMt / contract.totalVolumeMt : 0) * 100).toStringAsFixed(1)}% Completado',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),

            const SizedBox(height: AppConstants.largePadding),
            
            // Fixations List Section
            if (contract.fixations != null && contract.fixations!.isNotEmpty) ...[
              const Text('Historial de Fijaciones', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 8),
              ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: contract.fixations!.length,
                itemBuilder: (context, index) {
                  final fixation = contract.fixations![index];
                  return Card(
                    elevation: 1,
                    margin: const EdgeInsets.only(bottom: 8),
                    child: ListTile(
                      leading: const CircleAvatar(
                        backgroundColor: AppConstants.secondaryColor,
                        child: Icon(Icons.price_check, color: Colors.white, size: 20),
                      ),
                      title: Text('${fixation.fixedQuantityMt} MT @ \$${fixation.spotPriceUsd}'),
                      subtitle: Text(dateFormat.format(fixation.fixationDate ?? DateTime.now())),
                      trailing: Text(
                        '\$${fixation.totalValueUsd.toStringAsFixed(0)}',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: AppConstants.largePadding),
            ],
            
            // Actions
            if (contract.status == 'draft')
              SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  onPressed: () {
                    // TODO: Implement activate logic
                  },
                  icon: const Icon(Icons.check_circle_outline),
                  label: const Text('ACTIVAR CONTRATO'),
                  style: FilledButton.styleFrom(
                    backgroundColor: AppConstants.secondaryColor,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),

            if (contract.status == 'active' && contract.fixedVolumeMt < contract.totalVolumeMt)
               SizedBox(
                width: double.infinity,
                child: Consumer<FijacionService>(
                  builder: (context, fijacionService, _) {
                    return FilledButton.icon(
                      onPressed: () async {
                         await showDialog(
                          context: context,
                          builder: (context) => CreateFixationDialog(contract: contract),
                        );
                      },
                      icon: const Icon(Icons.trending_up),
                      label: Text(fijacionService.mercadoAbierto ? 'FIJAR PRECIO AHORA' : 'MERCADO CERRADO'),
                      style: FilledButton.styleFrom(
                        backgroundColor: fijacionService.mercadoAbierto ? AppConstants.primaryColor : Colors.grey,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                    );
                  }
                ),
              ),
              
            const SizedBox(height: 20),
            Center(
              child: Text(
                'ID: #${contract.id}',
                style: const TextStyle(color: Colors.grey, fontSize: 10),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: AppConstants.textSecondary)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}

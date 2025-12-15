import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/contract_model.dart';
import '../../services/fijacion_service.dart';
import '../../services/contract_service.dart';
import '../../utils/constants.dart';

class CreateFixationDialog extends StatefulWidget {
  final ExportContract contract;

  const CreateFixationDialog({super.key, required this.contract});

  @override
  State<CreateFixationDialog> createState() => _CreateFixationDialogState();
}

class _CreateFixationDialogState extends State<CreateFixationDialog> {
  final _amountController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    // Pre-fill with remaining amount or a sane default
    double remaining = widget.contract.totalVolumeMt - widget.contract.fixedVolumeMt;
    _amountController.text = remaining.toStringAsFixed(2);
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<FijacionService>(
      builder: (context, fijacionService, child) {
        final precioSpot = fijacionService.precioNYActual;
        final diferencial = widget.contract.differentialUsd;
        final precioFinal = precioSpot + diferencial;
        
        return AlertDialog(
          title: Row(
            children: [
              const Icon(Icons.show_chart, color: AppConstants.primaryColor),
              const SizedBox(width: 8),
              const Text('Fijar Precio'),
            ],
          ),
          content: SingleChildScrollView(
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Live Market Monitor
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.black87,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      children: [
                        const Text('BOLSA NY (ICE)', 
                          style: TextStyle(color: Colors.grey, fontSize: 10, letterSpacing: 1.5)),
                        const SizedBox(height: 4),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text(
                              '\$${precioSpot.toStringAsFixed(2)}',
                              style: const TextStyle(
                                color: Colors.greenAccent, 
                                fontSize: 32, 
                                fontWeight: FontWeight.bold,
                                fontFamily: 'Courier'
                              ),
                            ),
                            const Padding(
                              padding: EdgeInsets.only(bottom: 6, left: 4),
                              child: Text('USD/MT', style: TextStyle(color: Colors.grey, fontSize: 12)),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          fijacionService.estadoMercadoTexto,
                          style: TextStyle(
                            color: fijacionService.mercadoAbierto ? Colors.green : Colors.red,
                            fontSize: 10,
                            fontWeight: FontWeight.bold
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  const SizedBox(height: 20),
                  
                  // Calculation Details
                  _buildDetailRow('Diferencial (Contrato)', '+\$${diferencial.toStringAsFixed(2)}'),
                  const Divider(),
                  _buildDetailRow('PRECIO FINAL', '\$${precioFinal.toStringAsFixed(2)}', isBold: true),
                  
                  const SizedBox(height: 20),

                  // Amount Input
                  TextFormField(
                    controller: _amountController,
                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                    decoration: const InputDecoration(
                      labelText: 'Cantidad a Fijar (MT)',
                      border: OutlineInputBorder(),
                      suffixText: 'MT',
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) return 'Requerido';
                      final amount = double.tryParse(value);
                      if (amount == null || amount <= 0) return 'Inválido';
                      if (amount > (widget.contract.totalVolumeMt - widget.contract.fixedVolumeMt)) {
                        return 'Excede volumen pendiente';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Pendiente: ${(widget.contract.totalVolumeMt - widget.contract.fixedVolumeMt).toStringAsFixed(2)} MT',
                    style: const TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: _isSubmitting ? null : () => Navigator.pop(context),
              child: const Text('CANCELAR'),
            ),
            FilledButton(
              onPressed: _isSubmitting || !fijacionService.mercadoAbierto 
                ? null 
                : () => _submitFixation(context, fijacionService),
              style: FilledButton.styleFrom(backgroundColor: AppConstants.primaryColor),
              child: _isSubmitting 
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                : const Text('CONFIRMAR FIJACIÓN'),
            ),
          ],
        );
      },
    );
  }

  Widget _buildDetailRow(String label, String value, {bool isBold = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(
            fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
            color: isBold ? Colors.black : Colors.grey[700]
          )),
          Text(value, style: TextStyle(
            fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
            fontSize: isBold ? 16 : 14,
             color: isBold ? AppConstants.primaryColor : Colors.black
          )),
        ],
      ),
    );
  }

  Future<void> _submitFixation(BuildContext context, FijacionService fijacionService) async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSubmitting = true);

    try {
      final contractService = Provider.of<ContractService>(context, listen: false);
      final amount = double.parse(_amountController.text);

      await fijacionService.realizarFijacion(
        contract: widget.contract,
        cantidadMt: amount,
        contractService: contractService,
      );

      if (context.mounted) {
        Navigator.pop(context, true); // Return true to indicate success
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Precio fijado exitosamente'), backgroundColor: Colors.green),
        );
      }
    } catch (e) {
      if (context.mounted) {
        setState(() => _isSubmitting = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }
}

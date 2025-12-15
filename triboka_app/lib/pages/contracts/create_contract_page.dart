import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../utils/constants.dart';
import '../../services/contract_service.dart';

class CreateContractPage extends StatefulWidget {
  const CreateContractPage({super.key});

  @override
  State<CreateContractPage> createState() => _CreateContractPageState();
}

class _CreateContractPageState extends State<CreateContractPage> {
  final _formKey = GlobalKey<FormState>();
  
  // Controllers
  final _codeController = TextEditingController(); // Opcional, auto-generado si vacío
  final _volumeController = TextEditingController();
  final _differentialController = TextEditingController();
  String _productType = 'Cacao';
  String _productGrade = 'Grado 1';
  
  // Fechas
  DateTime _startDate = DateTime.now();
  DateTime _endDate = DateTime.now().add(const Duration(days: 90));
  DateTime _deliveryDate = DateTime.now().add(const Duration(days: 90));

  Future<void> _selectDate(BuildContext context, String type) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: type == 'start' ? _startDate : type == 'end' ? _endDate : _deliveryDate,
      firstDate: DateTime.now().subtract(const Duration(days: 365)),
      lastDate: DateTime.now().add(const Duration(days: 365 * 5)),
    );
    if (picked != null) {
      setState(() {
        if (type == 'start') _startDate = picked;
        if (type == 'end') _endDate = picked;
        if (type == 'delivery') _deliveryDate = picked;
      });
    }
  }

  Future<void> _submit() async {
    if (_formKey.currentState!.validate()) {
      final contractData = {
        'contract_code': _codeController.text.isNotEmpty ? _codeController.text : null,
        'product_type': _productType,
        'product_grade': _productGrade,
        'total_volume_mt': double.parse(_volumeController.text),
        'differential_usd': double.parse(_differentialController.text),
        'start_date': _startDate.toIso8601String(),
        'end_date': _endDate.toIso8601String(),
        'delivery_date': _deliveryDate.toIso8601String(),
        // Hardcoded for dev
        'buyer_company_id': 10,
        'exporter_company_id': 1,
      };

      final service = Provider.of<ContractService>(context, listen: false);
      final newContract = await service.createContract(contractData);

      if (mounted) {
        if (newContract != null) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Contrato creado exitosamente'), backgroundColor: Colors.green),
          );
          Navigator.pop(context);
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error: ${service.error}'), backgroundColor: Colors.red),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppConstants.backgroundLight,
      appBar: AppBar(title: const Text('Nuevo Contrato')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppConstants.defaultPadding),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Información General', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 16),
              
              TextFormField(
                controller: _codeController,
                decoration: const InputDecoration(
                  labelText: 'Código de Contrato (Opcional)',
                  helperText: 'Dejar vacío para autogenerar',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.qr_code),
                ),
              ),
              const SizedBox(height: 16),
              
              DropdownButtonFormField<String>(
                value: _productType,
                decoration: const InputDecoration(
                  labelText: 'Tipo de Producto',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.category_outlined),
                ),
                items: ['Cacao', 'Café', 'Maíz', 'Soja']
                    .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                    .toList(),
                onChanged: (v) => setState(() => _productType = v!),
              ),
              const SizedBox(height: 16),
              
              DropdownButtonFormField<String>(
                value: _productGrade,
                decoration: const InputDecoration(
                  labelText: 'Grado / Calidad',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.grade_outlined),
                ),
                items: ['Grado 1', 'Grado 2', 'Premium', 'Standard', 'Industrial']
                    .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                    .toList(),
                onChanged: (v) => setState(() => _productGrade = v!),
              ),

              const SizedBox(height: 24),
              const Text('Términos Comerciales', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 16),

              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _volumeController,
                      decoration: const InputDecoration(
                        labelText: 'Volumen (TM)',
                        border: OutlineInputBorder(),
                        suffixText: 'TM',
                      ),
                      keyboardType: TextInputType.number,
                      validator: (v) => v!.isEmpty ? 'Requerido' : null,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: TextFormField(
                      controller: _differentialController,
                      decoration: const InputDecoration(
                        labelText: 'Diferencial',
                        border: OutlineInputBorder(),
                        prefixText: '\$',
                        suffixText: 'USD',
                      ),
                      keyboardType: TextInputType.numberWithOptions(signed: true, decimal: true),
                      validator: (v) => v!.isEmpty ? 'Requerido' : null,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),
              const Text('Vigencia y Entrega', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 16),

              _buildDateSelector('Fecha Inicio', _startDate, 'start'),
              const SizedBox(height: 12),
              _buildDateSelector('Fecha Fin', _endDate, 'end'),
              const SizedBox(height: 12),
              _buildDateSelector('Fecha Entrega', _deliveryDate, 'delivery'),

              const SizedBox(height: 32),
              
              Consumer<ContractService>(
                builder: (context, service, _) {
                  return SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: FilledButton(
                      onPressed: service.isLoading ? null : _submit,
                      child: service.isLoading 
                        ? const CircularProgressIndicator(color: Colors.white)
                        : const Text('CREAR BORRADOR'),
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDateSelector(String label, DateTime date, String type) {
    return InkWell(
      onTap: () => _selectDate(context, type),
      child: InputDecorator(
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
          suffixIcon: const Icon(Icons.calendar_today),
        ),
        child: Text(DateFormat('dd MMM yyyy').format(date)),
      ),
    );
  }
}

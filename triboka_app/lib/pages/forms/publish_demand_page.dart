import 'package:flutter/material.dart';
import '../../utils/constants.dart';
import '../../services/publication_service.dart';

class PublishDemandPage extends StatefulWidget {
  const PublishDemandPage({super.key});

  @override
  State<PublishDemandPage> createState() => _PublishDemandPageState();
}

class _PublishDemandPageState extends State<PublishDemandPage> {
  final _formKey = GlobalKey<FormState>();
  final _volumeController = TextEditingController();
  final _priceController = TextEditingController();
  
  // State
  String _contractType = 'Spot';
  String _gradeRequired = 'Grado 1';
  bool _requiresCertification = false;

  Future<void> _submitForm() async {
    if (_formKey.currentState!.validate()) {
      // 1. Generate ID
      final String demandId = 'CUPO-${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}';
      
      // 2. Structure Data
      final Map<String, dynamic> demandData = {
        'id': demandId,
        'role': 'exportadora', // Required for visibility logic
        'type': 'demand_contract',
        'contractType': _contractType,
        'grade': _gradeRequired,
        'volume': double.tryParse(_volumeController.text) ?? 0.0,
        'priceRef': double.tryParse(_priceController.text) ?? 0.0,
        'requiresCert': _requiresCertification,
        'createdAt': DateTime.now().toIso8601String(),
      };

      // 3. Real Save
      try {
        await PublicationService().createPublication(demandData);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Cupo #$demandId guardado y activo 🌍')),
          );
          Navigator.pop(context);
        }
      } catch (e) {
        debugPrint(e.toString());
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Publicar Cupo / Contrato'),
        backgroundColor: Colors.white,
        foregroundColor: AppConstants.textPrimary,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppConstants.defaultPadding),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
               _buildSectionTitle('Detalles del Contrato'),
              const SizedBox(height: 20),
              
              DropdownButtonFormField<String>(
                value: _contractType,
                decoration: _inputDecoration('Tipo de Contrato'),
                items: ['Spot', 'Futuro', 'Fijación']
                    .map((v) => DropdownMenuItem(value: v, child: Text(v)))
                    .toList(),
                onChanged: (val) => setState(() => _contractType = val!),
              ),
              const SizedBox(height: 16),
              
              DropdownButtonFormField<String>(
                value: _gradeRequired,
                decoration: _inputDecoration('Calidad Requerida'),
                items: ['Grado 1', 'Grado 2', 'Pasilla', 'Orgánico Certificado']
                    .map((v) => DropdownMenuItem(value: v, child: Text(v)))
                    .toList(),
                onChanged: (val) => setState(() => _gradeRequired = val!),
              ),
              const SizedBox(height: 16),
              
              TextFormField(
                controller: _volumeController,
                keyboardType: TextInputType.number,
                decoration: _inputDecoration('Volumen Requerido (Tons)'),
                validator: (v) => v!.isEmpty ? 'Requerido' : null,
              ),
              const SizedBox(height: 16),

              TextFormField(
                controller: _priceController,
                keyboardType: TextInputType.number,
                decoration: _inputDecoration('Precio Referencial (NY +/- Diff)'),
                validator: (v) => v!.isEmpty ? 'Requerido' : null,
              ),

              const SizedBox(height: 24),
              _buildSectionTitle('Requisitos Adicionales'),
              
              SwitchListTile(
                title: const Text('Requiere Certificación (Traza)'),
                value: _requiresCertification,
                activeColor: Colors.orange,
                onChanged: (val) => setState(() => _requiresCertification = val),
              ),
              
              const SizedBox(height: 32),
              
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _submitForm,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.orange.shade800, // Demand color
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('PUBLICAR CUPO', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  InputDecoration _inputDecoration(String label) {
    return InputDecoration(
      labelText: label,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.bold,
        color: AppConstants.textPrimary,
      ),
    );
  }
}

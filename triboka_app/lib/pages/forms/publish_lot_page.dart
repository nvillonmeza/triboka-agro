import 'package:flutter/material.dart';
import '../../utils/constants.dart';
import '../../services/publication_service.dart';

class PublishLotPage extends StatefulWidget {
  final String role; // 'proveedor' or 'centro'
  const PublishLotPage({super.key, required this.role});

  @override
  State<PublishLotPage> createState() => _PublishLotPageState();
}

class _PublishLotPageState extends State<PublishLotPage> {
  final _formKey = GlobalKey<FormState>();
  
  // Controllers
  final _volumeController = TextEditingController();
  final _priceController = TextEditingController();
  final _descriptionController = TextEditingController();
  
  // State variables
  String _selectedVariety = 'CCN51';
  String _selectedState = 'Seco';
  bool _isCertified = false;
  String? _selectedCertification;

  @override
  void dispose() {
    _volumeController.dispose();
    _priceController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _submitForm() async {
    if (_formKey.currentState!.validate()) {
      // 1. Generate Unique Identifier (Mock ID)
      final String lotId = 'LOTE-${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}';
      
      // 2. Structure the Data Object
      final Map<String, dynamic> lotData = {
        'id': lotId,
        'role': widget.role,
        'variety': _selectedVariety,
        'state': _selectedState,
        'volume': double.tryParse(_volumeController.text) ?? 0.0,
        'price': double.tryParse(_priceController.text) ?? 0.0,
        'certification': _isCertified ? _selectedCertification : null,
        'description': _descriptionController.text,
        'createdAt': DateTime.now().toIso8601String(),
        'status': 'published', // Estado inicial
      };

      // 3. Current: Real DB Interaction
      try {
        await PublicationService().createPublication(lotData);
        
        // 4. Feedback
        if (mounted) {
           ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Lote #$lotId guardado en Base de Datos Local 💾'),
              backgroundColor: Colors.green,
            ),
          );
          Navigator.pop(context);
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error al guardar: $e'), backgroundColor: Colors.red),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isCentro = widget.role == 'centro';
    
    return Scaffold(
      appBar: AppBar(
        title: Text(isCentro ? 'Publicar Lote a Venta' : 'Registrar Lote de Cosecha'),
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
              _buildSectionTitle('Detalles del Producto'),
              const SizedBox(height: 16),
              
              // Variedad
              DropdownButtonFormField<String>(
                value: _selectedVariety,
                decoration: _inputDecoration('Variedad de Cacao'),
                items: ['CCN51', 'Nacional', 'Fino de Aroma', 'Trinitario']
                    .map((v) => DropdownMenuItem(value: v, child: Text(v)))
                    .toList(),
                onChanged: (val) => setState(() => _selectedVariety = val!),
              ),
              const SizedBox(height: 16),

              // Estado
              DropdownButtonFormField<String>(
                value: _selectedState,
                decoration: _inputDecoration('Estado del Grano'),
                items: ['Seco', 'En Baba', 'Fermentado', 'Semi-seco']
                    .map((v) => DropdownMenuItem(value: v, child: Text(v)))
                    .toList(),
                onChanged: (val) => setState(() => _selectedState = val!),
              ),
              const SizedBox(height: 16),
              
              // Volumen y Precio Row
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _volumeController,
                      keyboardType: TextInputType.number,
                      decoration: _inputDecoration('Volumen (kg/qq)'),
                      validator: (v) => v!.isEmpty ? 'Requerido' : null,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: TextFormField(
                      controller: _priceController,
                      keyboardType: TextInputType.number,
                      decoration: _inputDecoration('Precio Esperado (\$)'),
                      validator: (v) => v!.isEmpty ? 'Requerido' : null,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              _buildSectionTitle('Calidad y Certificaciones'),
              const SizedBox(height: 16),
              
              SwitchListTile(
                title: const Text('¿Tiene Certificación?'),
                value: _isCertified,
                activeColor: AppConstants.primaryColor,
                onChanged: (val) => setState(() => _isCertified = val),
              ),
              
              if (_isCertified)
                Padding(
                  padding: const EdgeInsets.only(top: 16),
                  child: DropdownButtonFormField<String>(
                    value: _selectedCertification,
                    decoration: _inputDecoration('Tipo de Certificación'),
                    items: ['Orgánica', 'FairTrade', 'Rainforest Alliance', 'UTZ']
                        .map((v) => DropdownMenuItem(value: v, child: Text(v)))
                        .toList(),
                    onChanged: (val) => setState(() => _selectedCertification = val),
                  ),
                ),

              const SizedBox(height: 24),
              
              _buildSectionTitle('Información Adicional'),
              const SizedBox(height: 16),
              
              TextFormField(
                controller: _descriptionController,
                maxLines: 3,
                decoration: _inputDecoration('Descripción / Observaciones / Ubicación exacta'),
              ),
              
              const SizedBox(height: 32),
              
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _submitForm,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppConstants.primaryColor,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('PUBLICAR AHORA', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
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
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
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

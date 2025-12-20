import 'package:flutter/material.dart';
import '../../utils/constants.dart';
import '../../services/publication_service.dart';

class PublishPricePage extends StatefulWidget {
  const PublishPricePage({super.key});

  @override
  State<PublishPricePage> createState() => _PublishPricePageState();
}

class _PublishPricePageState extends State<PublishPricePage> {
  final _formKey = GlobalKey<FormState>();
  final _priceController = TextEditingController();
  String _selectedVariety = 'CCN51';
  String _selectedState = 'En Baba';

  Future<void> _submitForm() async {
    if (_formKey.currentState!.validate()) {
      // 1. Generate ID
      final String offerId = 'OFERTA-${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}';
      
      // 2. Structure Data
      final Map<String, dynamic> priceData = {
        'id': offerId,
        'role': 'centro', // Required for visibility logic
        'type': 'buy_price',
        'variety': _selectedVariety,
        'state': _selectedState,
        'price': double.tryParse(_priceController.text) ?? 0.0,
        'publishedAt': DateTime.now().toIso8601String(),
      };

      // 3. Real Save
      try {
        await PublicationService().createPublication(priceData);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Oferta #$offerId guardada en DB 💾')),
          );
          Navigator.pop(context);
        }
      } catch (e) {
        debugPrint('Error saving: $e');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Publicar Precio de Compra'),
        backgroundColor: Colors.white,
        foregroundColor: AppConstants.textPrimary,
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(AppConstants.defaultPadding),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
               _buildSectionTitle('Configuración de Oferta'),
              const SizedBox(height: 20),
              
              DropdownButtonFormField<String>(
                value: _selectedVariety,
                decoration: _inputDecoration('Variedad'),
                items: ['CCN51', 'Nacional', 'Ramilla']
                    .map((v) => DropdownMenuItem(value: v, child: Text(v)))
                    .toList(),
                onChanged: (val) => setState(() => _selectedVariety = val!),
              ),
              const SizedBox(height: 16),
              
              DropdownButtonFormField<String>(
                value: _selectedState,
                decoration: _inputDecoration('Estado Requerido'),
                items: ['En Baba', 'Seco', 'Semiseco']
                    .map((v) => DropdownMenuItem(value: v, child: Text(v)))
                    .toList(),
                onChanged: (val) => setState(() => _selectedState = val!),
              ),
              const SizedBox(height: 16),
              
              TextFormField(
                controller: _priceController,
                keyboardType: TextInputType.number,
                decoration: _inputDecoration('Precio de Compra (por Quintal/Kilo)'),
                validator: (v) => v!.isEmpty ? 'Requerido' : null,
              ),

              const Spacer(),
              
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _submitForm,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green, // Green for buying offer
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('PUBLICAR PRECIO', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                ),
              ),
              const SizedBox(height: 20),
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

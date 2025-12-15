import 'package:flutter/material.dart';
import '../utils/constants.dart';

class CalculadoraPage extends StatefulWidget {
  const CalculadoraPage({super.key});

  @override
  State<CalculadoraPage> createState() => _CalculadoraPageState();
}

class _CalculadoraPageState extends State<CalculadoraPage> {
  final List<Map<String, dynamic>> _diferenciales = [
    {'nombre': 'Exportadora', 'valor': 200.0},
  ];
  
  final List<Map<String, dynamic>> _historial = [];

  void _agregarDiferencial() {
    setState(() {
      _diferenciales.add({
        'nombre': 'Dif-${_diferenciales.length + 1}',
        'valor': 0.0,
      });
    });
  }

  void _eliminarDiferencial(int index) {
    if (_diferenciales.length > 1) {
      setState(() {
        _diferenciales.removeAt(index);
      });
    }
  }

  Map<String, double> _calcular(double diferencial) {
    final tmNeto = AppConstants.spotPrecioNY - diferencial;
    final qq = tmNeto / AppConstants.divisorQQ;
    return {'tmNeto': tmNeto, 'qq': qq};
  }

  void _guardarHistorial() {
    final fecha = DateTime.now();
    final resultados = _diferenciales.map((d) {
      final calc = _calcular(d['valor']);
      return {
        'nombre': d['nombre'],
        'valor': d['valor'],
        'tmNeto': calc['tmNeto']!.toStringAsFixed(2),
        'qq': calc['qq']!.toStringAsFixed(2),
      };
    }).toList();

    setState(() {
      _historial.insert(0, {
        'fecha': fecha,
        'resultados': resultados,
      });
      
      // Mantener solo los últimos 5 cálculos
      if (_historial.length > 5) {
        _historial.removeLast();
      }
    });

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Cálculo guardado en el historial'),
        backgroundColor: AppConstants.primaryColor,
      ),
    );
  }

  void _borrarHistorial() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Borrar historial'),
        content: const Text('¿Deseas borrar todo el historial de cálculos?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () {
              setState(() {
                _historial.clear();
              });
              Navigator.of(context).pop();
            },
            child: const Text('Borrar'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppConstants.backgroundLight,
      appBar: AppBar(
        title: const Text('Calculadora de precios'),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppConstants.defaultPadding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Calculadora de precios según diferenciales',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: AppConstants.textPrimary,
                ),
              ),
              
              const SizedBox(height: AppConstants.defaultPadding),
              
              // Card principal de calculadora
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(AppConstants.defaultPadding),
                decoration: BoxDecoration(
                  color: AppConstants.cardWhite,
                  borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
                  boxShadow: const [
                    BoxShadow(
                      color: Colors.black12,
                      blurRadius: 8,
                      offset: Offset(0, 2),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    RichText(
                      text: TextSpan(
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: AppConstants.textSecondary,
                        ),
                        children: [
                          const TextSpan(text: 'Spot actual: '),
                          TextSpan(
                            text: '\$${AppConstants.spotPrecioNY.toStringAsFixed(0)} / TM',
                            style: const TextStyle(
                              fontWeight: FontWeight.w600,
                              color: AppConstants.primaryColor,
                            ),
                          ),
                        ],
                      ),
                    ),
                    
                    const SizedBox(height: AppConstants.defaultPadding),
                    
                    // Lista de diferenciales
                    ..._diferenciales.asMap().entries.map((entry) {
                      final index = entry.key;
                      final diferencial = entry.value;
                      final calculo = _calcular(diferencial['valor']);
                      
                      return Container(
                        margin: const EdgeInsets.only(bottom: AppConstants.defaultPadding),
                        padding: const EdgeInsets.all(AppConstants.defaultPadding),
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey.shade300),
                          borderRadius: BorderRadius.circular(AppConstants.borderRadius),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: TextFormField(
                                    initialValue: diferencial['nombre'],
                                    decoration: const InputDecoration(
                                      labelText: 'Nombre',
                                      border: OutlineInputBorder(),
                                      contentPadding: EdgeInsets.symmetric(
                                        horizontal: 12,
                                        vertical: 8,
                                      ),
                                    ),
                                    onChanged: (value) {
                                      setState(() {
                                        _diferenciales[index]['nombre'] = value;
                                      });
                                    },
                                  ),
                                ),
                                const SizedBox(width: 8),
                                if (_diferenciales.length > 1)
                                  IconButton(
                                    icon: const Icon(
                                      Icons.delete_outline,
                                      color: Colors.red,
                                    ),
                                    onPressed: () => _eliminarDiferencial(index),
                                  ),
                              ],
                            ),
                            const SizedBox(height: AppConstants.smallPadding),
                            TextFormField(
                              initialValue: diferencial['valor'].toString(),
                              decoration: const InputDecoration(
                                labelText: 'Diferencial (USD/TM)',
                                border: OutlineInputBorder(),
                                contentPadding: EdgeInsets.symmetric(
                                  horizontal: 12,
                                  vertical: 8,
                                ),
                              ),
                              keyboardType: TextInputType.number,
                              onChanged: (value) {
                                setState(() {
                                  _diferenciales[index]['valor'] = double.tryParse(value) ?? 0.0;
                                });
                              },
                            ),
                            const SizedBox(height: AppConstants.defaultPadding),
                            Row(
                              children: [
                                Expanded(
                                  child: _buildResultCard(
                                    'Precio Neto (TM)',
                                    '\$${calculo['tmNeto']!.toStringAsFixed(2)}',
                                    '',
                                  ),
                                ),
                                const SizedBox(width: AppConstants.smallPadding),
                                Expanded(
                                  child: _buildResultCard(
                                    'Precio por QQ',
                                    '\$${calculo['qq']!.toStringAsFixed(2)}',
                                    'División ${AppConstants.divisorQQ}',
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      );
                    }),
                    
                    // Botón agregar diferencial
                    SizedBox(
                      width: double.infinity,
                      child: OutlinedButton.icon(
                        onPressed: _agregarDiferencial,
                        icon: const Icon(Icons.add_circle_outline),
                        label: const Text('Añadir diferencial'),
                      ),
                    ),
                    
                    const SizedBox(height: AppConstants.defaultPadding),
                    
                    // Botones de acción
                    Row(
                      children: [
                        Expanded(
                          child: FilledButton(
                            onPressed: _guardarHistorial,
                            child: const Text('Guardar cálculo'),
                          ),
                        ),
                        const SizedBox(width: AppConstants.smallPadding),
                        OutlinedButton.icon(
                          onPressed: _historial.isNotEmpty ? _borrarHistorial : null,
                          icon: const Icon(Icons.delete_outline, size: 16),
                          label: const Text('Borrar'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              
              // Historial
              if (_historial.isNotEmpty) ...[
                const SizedBox(height: AppConstants.largePadding),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(AppConstants.defaultPadding),
                  decoration: BoxDecoration(
                    color: AppConstants.cardWhite,
                    borderRadius: BorderRadius.circular(AppConstants.cardBorderRadius),
                    boxShadow: const [
                      BoxShadow(
                        color: Colors.black12,
                        blurRadius: 8,
                        offset: Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(
                            Icons.history,
                            color: AppConstants.primaryColor,
                            size: 20,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Historial reciente',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const Spacer(),
                          Text(
                            '(${_historial.length}) cálculos',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: AppConstants.textSecondary,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: AppConstants.defaultPadding),
                      ..._historial.map((h) => Container(
                        margin: const EdgeInsets.only(bottom: AppConstants.smallPadding),
                        padding: const EdgeInsets.all(AppConstants.smallPadding),
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey.shade200),
                          borderRadius: BorderRadius.circular(AppConstants.smallPadding),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '${h['fecha'].day}/${h['fecha'].month}/${h['fecha'].year} - ${h['fecha'].hour}:${h['fecha'].minute.toString().padLeft(2, '0')}',
                              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: AppConstants.textSecondary,
                              ),
                            ),
                            const SizedBox(height: 4),
                            ...h['resultados'].map<Widget>((r) => Text(
                              '${r['nombre']}: \$${r['tmNeto']} TM / \$${r['qq']} QQ',
                              style: Theme.of(context).textTheme.bodySmall,
                            )),
                          ],
                        ),
                      )),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildResultCard(String title, String value, String subtitle) {
    return Container(
      padding: const EdgeInsets.all(AppConstants.smallPadding),
      decoration: BoxDecoration(
        color: AppConstants.backgroundLight,
        borderRadius: BorderRadius.circular(AppConstants.smallPadding),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 11,
              color: AppConstants.textSecondary,
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: AppConstants.textPrimary,
            ),
          ),
          if (subtitle.isNotEmpty)
            Text(
              subtitle,
              style: const TextStyle(
                fontSize: 10,
                color: AppConstants.textSecondary,
              ),
            ),
        ],
      ),
    );
  }
}
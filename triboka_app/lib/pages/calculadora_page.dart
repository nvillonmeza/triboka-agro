import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart';
import '../utils/constants.dart';

class CalculadoraPage extends StatefulWidget {
  const CalculadoraPage({super.key});

  @override
  State<CalculadoraPage> createState() => _CalculadoraPageState();
}

class _CalculadoraPageState extends State<CalculadoraPage> {
  // Caja de Hive
  late Box _historyBox;

  // Lista de diferenciales actuales (Estado UI)
  List<Map<String, dynamic>> _diferenciales = [
    {'nombre': 'Exportadora', 'valor': 200.0},
  ];

  @override
  void initState() {
    super.initState();
    _historyBox = Hive.box('calculadora_history');
  }

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

  Future<void> _guardarHistorial() async {
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

    // Guardar en Hive
    await _historyBox.add({
      'fecha': fecha.toIso8601String(),
      'resultados': resultados,
      'origen_diferenciales': _diferenciales, // Guardar configuración original para restaurar
    });

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Cálculo guardado exitosamente'),
          backgroundColor: AppConstants.primaryColor,
        ),
      );
    }
  }

  void _borrarHistorialCompleto() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Borrar historial'),
        content: const Text('¿Deseas borrar TODO el historial de cálculos?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () {
              _historyBox.clear();
              Navigator.of(context).pop();
            },
            style: FilledButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Borrar Todo'),
          ),
        ],
      ),
    );
  }

  void _borrarItemHistorial(int index) {
    _historyBox.deleteAt(index);
  }

  void _restaurarCalculo(Map<dynamic, dynamic> item) {
    try {
      final configOriginal = List<Map<String, dynamic>>.from(
        (item['origen_diferenciales'] as List).map((e) => Map<String, dynamic>.from(e))
      );
      
      setState(() {
        _diferenciales = configOriginal;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Configuración restaurada'),
          backgroundColor: AppConstants.secondaryColor,
          duration: Duration(seconds: 2),
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('No se pudo restaurar esta configuración antigua'),
          backgroundColor: Colors.grey,
        ),
      );
    }
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
                                    key: ValueKey('name_${index}_${diferencial.hashCode}'), // Key para forzar rebuild al restaurar
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
                                      _diferenciales[index]['nombre'] = value;
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
                              key: ValueKey('val_${index}_${diferencial.hashCode}'),
                              initialValue: diferencial['valor'].toString(),
                              decoration: const InputDecoration(
                                labelText: 'Diferencial (USD/TM)',
                                border: OutlineInputBorder(),
                                contentPadding: EdgeInsets.symmetric(
                                  horizontal: 12,
                                  vertical: 8,
                                ),
                              ),
                              keyboardType: TextInputType.numberWithOptions(decimal: true, signed: true),
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
                    
                    // Botón Guardar
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton.icon(
                        onPressed: _guardarHistorial,
                        icon: const Icon(Icons.save),
                        label: const Text('Guardar cálculo'),
                      ),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: AppConstants.largePadding),

              // Historial con Hive (ValueListenableBuilder)
              ValueListenableBuilder(
                valueListenable: _historyBox.listenable(),
                builder: (context, Box box, _) {
                  if (box.isEmpty) {
                    return const SizedBox.shrink();
                  }

                  // Obtener historial y revertir para mostrar reciente primero
                  final historial = box.values.toList().reversed.toList();
                  // Necesitamos los índices originales para borrar correctamente
                  final keys = box.keys.toList().reversed.toList();

                  return Container(
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
                              'Historial Local',
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const Spacer(),
                            TextButton.icon(
                              onPressed: _borrarHistorialCompleto,
                              icon: const Icon(Icons.delete_sweep, size: 16, color: Colors.red),
                              label: const Text('Borrar Todo', style: TextStyle(color: Colors.red)),
                            ),
                          ],
                        ),
                        const SizedBox(height: AppConstants.defaultPadding),
                        
                        ...historial.asMap().entries.map((entry) {
                          final index = entry.key;
                          final item = entry.value;
                          final originalKey = keys[index]; // Key real en la caja
                          final fecha = DateTime.parse(item['fecha']);
                          final resultados = item['resultados'] as List;

                          return Dismissible(
                            key: Key('hist_$originalKey'),
                            direction: DismissDirection.endToStart,
                            background: Container(
                              color: Colors.red,
                              alignment: Alignment.centerRight,
                              padding: const EdgeInsets.only(right: 16),
                              child: const Icon(Icons.delete, color: Colors.white),
                            ),
                            onDismissed: (direction) {
                              _historyBox.delete(originalKey);
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Eliminado del historial')),
                              );
                            },
                            child: Container(
                              margin: const EdgeInsets.only(bottom: AppConstants.smallPadding),
                              padding: const EdgeInsets.all(AppConstants.smallPadding),
                              decoration: BoxDecoration(
                                border: Border.all(color: Colors.grey.shade200),
                                borderRadius: BorderRadius.circular(AppConstants.smallPadding),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text(
                                        '${fecha.day}/${fecha.month} - ${fecha.hour}:${fecha.minute.toString().padLeft(2, '0')}',
                                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                          color: AppConstants.textSecondary,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      if (item['origen_diferenciales'] != null)
                                        TextButton(
                                          onPressed: () => _restaurarCalculo(item),
                                          style: TextButton.styleFrom(
                                            padding: EdgeInsets.zero,
                                            minimumSize: const Size(60, 24),
                                            tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                          ),
                                          child: const Text('Restaurar', style: TextStyle(fontSize: 12)),
                                        ),
                                    ],
                                  ),
                                  const Divider(height: 8),
                                  ...resultados.map<Widget>((r) => Padding(
                                    padding: const EdgeInsets.symmetric(vertical: 2),
                                    child: Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text('${r['nombre']}: \$${r['tmNeto']} TM', style: const TextStyle(fontSize: 12)),
                                        Text('\$${r['qq']} QQ', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                                      ],
                                    ),
                                  )),
                                ],
                              ),
                            ),
                          );
                        }),
                      ],
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
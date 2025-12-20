import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:hive_flutter/hive_flutter.dart';
import '../utils/constants.dart';
import '../services/market_service.dart';

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

  // Ahora acepta el spot actual como parámetro para ser reactivo
  Map<String, double> _calcular(double diferencial, double currentSpot) {
    final tmNeto = currentSpot - diferencial;
    final qq = tmNeto / AppConstants.divisorQQ;
    return {'tmNeto': tmNeto, 'qq': qq};
  }

  Future<void> _guardarHistorial(double currentSpot) async {
    final fecha = DateTime.now();
    final resultados = _diferenciales.map((d) {
      final calc = _calcular(d['valor'], currentSpot);
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
      'spot_referencia': currentSpot,
      'resultados': resultados,
      'origen_diferenciales': _diferenciales,
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
    // Escuchamos el MarketService para obtener el precio real
    final marketService = Provider.of<MarketService>(context);
    final currentDataPrice = marketService.currentData?.price ?? 0.0;
    
    final currentSpot = (currentDataPrice > 0) 
        ? currentDataPrice 
        : AppConstants.spotPrecioNY; // Fallback

    return Scaffold(
      backgroundColor: AppConstants.backgroundLight,
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: const Text('Calculadora de Precios', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        centerTitle: true,
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: const BackButton(color: Colors.white),
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            stops: [0.0, 0.3],
            colors: [
              AppConstants.primaryColor,
              AppConstants.backgroundLight,
            ],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(AppConstants.defaultPadding),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Header Card con Precio Spot Real
                Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(24),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 20,
                        offset: const Offset(0, 10),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      const Text(
                        'PRECIO SPOT (NY ICE)',
                        style: TextStyle(
                          color: AppConstants.textSecondary,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1.2,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '\$${currentSpot.toStringAsFixed(0)}',
                        style: const TextStyle(
                          color: AppConstants.primaryColor,
                          fontSize: 48,
                          fontWeight: FontWeight.w800,
                          height: 1,
                        ),
                      ),
                      const Text(
                        'USD / TM',
                        style: TextStyle(
                          color: AppConstants.textSecondary,
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      if (marketService.currentData?.isOffline == true)
                         Padding(
                           padding: const EdgeInsets.only(top: 8.0),
                           child: Row(
                             mainAxisSize: MainAxisSize.min,
                             children: const [
                               Icon(Icons.wifi_off, size: 12, color: Colors.orange),
                               SizedBox(width: 4),
                               Text('Offline', style: TextStyle(fontSize: 10, color: Colors.orange)),
                             ],
                           ),
                         ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 32),
                
                Row(
                  children: [
                    const Icon(Icons.calculate_outlined, color: AppConstants.primaryColor),
                    const SizedBox(width: 8),
                    Text(
                      'Diferenciales & Resultados',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 16),
                
                // Lista de diferenciales
                ..._diferenciales.asMap().entries.map((entry) {
                  final index = entry.key;
                  final diferencial = entry.value;
                  final calculo = _calcular(diferencial['valor'], currentSpot);
                  
                  return Container(
                    margin: const EdgeInsets.only(bottom: 20),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.grey.withOpacity(0.05),
                          blurRadius: 10,
                          offset: const Offset(0, 4),
                        ),
                      ],
                      border: Border.all(color: Colors.grey.withOpacity(0.1)),
                    ),
                    child: Column(
                      children: [
                        // Header del diferencial
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                          decoration: BoxDecoration(
                            color: Colors.grey.withOpacity(0.05),
                            borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
                          ),
                          child: Row(
                            children: [
                              Expanded(
                                child: TextFormField(
                                  key: ValueKey('name_${index}_${diferencial.hashCode}'),
                                  initialValue: diferencial['nombre'],
                                  style: const TextStyle(fontWeight: FontWeight.bold),
                                  decoration: const InputDecoration.collapsed(
                                    hintText: 'Nombre del diferencial',
                                  ),
                                  onChanged: (value) => _diferenciales[index]['nombre'] = value,
                                ),
                              ),
                              if (_diferenciales.length > 1)
                                IconButton(
                                  icon: const Icon(Icons.close, color: Colors.red, size: 20),
                                  onPressed: () => _eliminarDiferencial(index),
                                  padding: EdgeInsets.zero,
                                  constraints: const BoxConstraints(),
                                ),
                            ],
                          ),
                        ),
                        
                        Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Input de Valor
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                decoration: BoxDecoration(
                                  color: AppConstants.backgroundLight,
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(color: Colors.grey.withOpacity(0.2)),
                                ),
                                child: Row(
                                  children: [
                                    const Text('Diferencial:', style: TextStyle(color: Colors.grey)),
                                    const SizedBox(width: 12),
                                    Expanded(
                                      child: TextFormField(
                                        key: ValueKey('val_${index}_${diferencial.hashCode}'),
                                        initialValue: diferencial['valor'].toString(),
                                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                                        keyboardType: const TextInputType.numberWithOptions(decimal: true, signed: true),
                                        decoration: const InputDecoration.collapsed(hintText: '0.0'),
                                        onChanged: (value) {
                                          setState(() {
                                            _diferenciales[index]['valor'] = double.tryParse(value) ?? 0.0;
                                          });
                                        },
                                      ),
                                    ),
                                    const Text('USD/TM', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey)),
                                  ],
                                ),
                              ),
                              
                              const SizedBox(height: 20),
                              
                              // Resultados
                              Row(
                                children: [
                                  Expanded(
                                    child: _buildPremiumResultCard(
                                      'PRECIO NETO',
                                      '\$${calculo['tmNeto']!.toStringAsFixed(2)}',
                                      'Por Tonelada',
                                      AppConstants.primaryColor,
                                      Icons.check_circle_outline,
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: _buildPremiumResultCard(
                                      'PRECIO QQ',
                                      '\$${calculo['qq']!.toStringAsFixed(2)}',
                                      'Por Quintal',
                                      AppConstants.secondaryColor,
                                      Icons.scale_outlined,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  );
                }),
                
                // Botones de acción
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton(
                        onPressed: _agregarDiferencial,
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                          side: const BorderSide(color: AppConstants.primaryColor),
                        ),
                        child: const Text('AÑADIR OTRO'),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: FilledButton(
                        onPressed: () => _guardarHistorial(currentSpot),
                        style: FilledButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                        ),
                        child: const Text('GUARDAR CÁLCULO'),
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 40),
                
                // Historial Section
                ValueListenableBuilder(
                  valueListenable: _historyBox.listenable(),
                  builder: (context, Box box, _) {
                    if (box.isEmpty) return const SizedBox.shrink();

                    final historial = box.values.toList().reversed.toList();
                    final keys = box.keys.toList().reversed.toList();

                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text(
                              'Historial Reciente',
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                            ),
                            TextButton(
                              onPressed: _borrarHistorialCompleto,
                              child: const Text('Borrar Todo', style: TextStyle(color: Colors.red)),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        ...historial.asMap().entries.map((entry) {
                           final index = entry.key;
                           final item = entry.value;
                           final originalKey = keys[index];
                           final fecha = DateTime.parse(item['fecha']);
                           final resultados = item['resultados'] as List;
                           final spotRef = item['spot_referencia'] ?? 0.0;

                           return Dismissible(
                             key: Key('hist_$originalKey'),
                             direction: DismissDirection.endToStart,
                             background: Container(
                               alignment: Alignment.centerRight,
                               padding: const EdgeInsets.only(right: 20),
                               decoration: BoxDecoration(
                                 color: Colors.red.shade100,
                                 borderRadius: BorderRadius.circular(16),
                               ),
                               child: const Icon(Icons.delete, color: Colors.red),
                             ),
                             onDismissed: (_) => _historyBox.delete(originalKey),
                             child: Container(
                               margin: const EdgeInsets.only(bottom: 12),
                               padding: const EdgeInsets.all(16),
                               decoration: BoxDecoration(
                                 color: Colors.white,
                                 borderRadius: BorderRadius.circular(16),
                                 border: Border.all(color: Colors.grey.shade100),
                               ),
                               child: Column(
                                 children: [
                                   Row(
                                     mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                     children: [
                                       Column(
                                         crossAxisAlignment: CrossAxisAlignment.start,
                                         children: [
                                           Text(
                                             '${fecha.day}/${fecha.month} • ${fecha.hour}:${fecha.minute.toString().padLeft(2, '0')}',
                                             style: TextStyle(color: Colors.grey.shade500, fontSize: 12, fontWeight: FontWeight.bold),
                                           ),
                                           Text(
                                             'Spot: \$${spotRef.toStringAsFixed(0)}',
                                              style: const TextStyle(fontSize: 12, color: AppConstants.primaryColor, fontWeight: FontWeight.bold),
                                           ),
                                         ],
                                       ),
                                       IconButton(
                                         icon: const Icon(Icons.restore, color: AppConstants.primaryColor),
                                         onPressed: () => _restaurarCalculo(item),
                                       ),
                                     ],
                                   ),
                                   const Divider(),
                                   ...resultados.map<Widget>((r) => Padding(
                                     padding: const EdgeInsets.symmetric(vertical: 4),
                                     child: Row(
                                       mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                       children: [
                                         Text(r['nombre'], style: const TextStyle(fontSize: 13)),
                                         Text('\$${r['tmNeto']} TM  |  \$${r['qq']} QQ', 
                                           style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                                       ],
                                     ),
                                   )),
                                 ],
                               ),
                             ),
                           );
                        }),
                        const SizedBox(height: 80), // Espacio final
                      ],
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPremiumResultCard(String title, String value, String subtitle, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.08),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: color),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  title,
                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: color),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          FittedBox(
            fit: BoxFit.scaleDown,
            child: Text(
              value,
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: color),
            ),
          ),
          Text(
            subtitle,
            style: TextStyle(fontSize: 10, color: color.withOpacity(0.8), fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }
}
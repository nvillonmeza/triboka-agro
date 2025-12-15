import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../utils/constants.dart';
import '../../services/contract_service.dart';
import '../../models/contract_model.dart';
import 'contract_detail_page.dart';
import 'create_contract_page.dart';

class ContractsPage extends StatefulWidget {
  const ContractsPage({super.key});

  @override
  State<ContractsPage> createState() => _ContractsPageState();
}

class _ContractsPageState extends State<ContractsPage> {
  String _selectedFilter = 'all'; // all, active, draft, completed

  @override
  void initState() {
    super.initState();
    // Refrescar al entrar a la página
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<ContractService>(context, listen: false).fetchContracts();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppConstants.backgroundLight,
      appBar: AppBar(
        title: const Text('Contratos Digitales'),
        centerTitle: true,
      ),
      body: Column(
        children: [
          // Filtros
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.all(AppConstants.defaultPadding),
            child: Row(
              children: [
                _buildFilterChip('Todos', 'all'),
                const SizedBox(width: 8),
                _buildFilterChip('Activos', 'active'),
                const SizedBox(width: 8),
                _buildFilterChip('Borradores', 'draft'),
                const SizedBox(width: 8),
                _buildFilterChip('Completados', 'completed'),
              ],
            ),
          ),
          
          // Lista
          Expanded(
            child: Consumer<ContractService>(
              builder: (context, service, child) {
                if (service.isLoading) {
                  return const Center(child: CircularProgressIndicator());
                }

                if (service.error != null) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.error_outline, size: 48, color: Colors.grey),
                        const SizedBox(height: 16),
                        Text(service.error!),
                        TextButton(
                          onPressed: () => service.fetchContracts(),
                          child: const Text('Reintentar'),
                        ),
                      ],
                    ),
                  );
                }

                var filteredList = service.contracts;
                if (_selectedFilter != 'all') {
                  filteredList = filteredList.where((c) => c.status == _selectedFilter).toList();
                }

                if (filteredList.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.description_outlined, size: 64, color: Colors.grey),
                        const SizedBox(height: 16),
                        Text(
                          'No hay contratos ${_selectedFilter != "all" ? _selectedFilter : ""}',
                          style: const TextStyle(color: Colors.grey),
                        ),
                      ],
                    ),
                  );
                }

                return RefreshIndicator(
                  onRefresh: () => service.fetchContracts(),
                  child: ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: AppConstants.defaultPadding),
                    itemCount: filteredList.length,
                    itemBuilder: (context, index) {
                      final contract = filteredList[index];
                      return _buildContractCard(contract);
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const CreateContractPage()),
          );
        },
        backgroundColor: AppConstants.primaryColor,
        icon: const Icon(Icons.add, color: Colors.white),
        label: const Text('Nuevo Contrato', style: TextStyle(color: Colors.white)),
      ),
    );
  }

  Widget _buildFilterChip(String label, String value) {
    final isSelected = _selectedFilter == value;
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (bool selected) {
        setState(() {
          _selectedFilter = value;
        });
      },
      backgroundColor: Colors.white,
      selectedColor: AppConstants.secondaryColor.withOpacity(0.2),
      checkmarkColor: AppConstants.primaryColor,
      labelStyle: TextStyle(
        color: isSelected ? AppConstants.primaryColor : AppConstants.textSecondary,
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
      ),
    );
  }

  Widget _buildContractCard(ExportContract contract) {
    Color statusColor;
    String statusText;

    switch (contract.status) {
      case 'active':
        statusColor = Colors.green;
        statusText = 'ACTIVO';
        break;
      case 'draft':
        statusColor = Colors.orange;
        statusText = 'BORRADOR';
        break;
      case 'completed':
        statusColor = Colors.blue;
        statusText = 'COMPLETADO';
        break;
      default:
        statusColor = Colors.grey;
        statusText = contract.status.toUpperCase();
    }

    return Card(
      margin: const EdgeInsets.only(bottom: AppConstants.defaultPadding),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => ContractDetailPage(contract: contract)),
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    contract.contractCode,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: statusColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: statusColor.withOpacity(0.5)),
                    ),
                    child: Text(
                      statusText,
                      style: TextStyle(
                        color: statusColor,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  const Icon(Icons.business_outlined, size: 16, color: Colors.grey),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      contract.buyerCompany?.name ?? 'Comprador Desconocido',
                      style: const TextStyle(fontWeight: FontWeight.w500),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _infoBadge(Icons.inventory_2_outlined, '${contract.totalVolumeMt} TM'),
                  _infoBadge(Icons.shopping_bag_outlined, contract.productType),
                  _infoBadge(Icons.attach_money, '\$${contract.differentialUsd} Dif'),
                ],
              ),
              const SizedBox(height: 12),
              LinearProgressIndicator(
                value: contract.totalVolumeMt > 0 
                  ? contract.fixedVolumeMt / contract.totalVolumeMt 
                  : 0,
                backgroundColor: Colors.grey.shade200,
                color: AppConstants.primaryColor,
                borderRadius: BorderRadius.circular(4),
              ),
              const SizedBox(height: 4),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Fijado: ${contract.fixedVolumeMt} TM',
                    style: const TextStyle(fontSize: 10, color: Colors.grey),
                  ),
                  Text(
                    '${((contract.totalVolumeMt > 0 ? contract.fixedVolumeMt / contract.totalVolumeMt : 0) * 100).toStringAsFixed(1)}%',
                    style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _infoBadge(IconData icon, String text) {
    return Row(
      children: [
        Icon(icon, size: 14, color: AppConstants.textSecondary),
        const SizedBox(width: 4),
        Text(
          text,
          style: const TextStyle(
            fontSize: 12,
            color: AppConstants.textSecondary,
          ),
        ),
      ],
    );
  }
}

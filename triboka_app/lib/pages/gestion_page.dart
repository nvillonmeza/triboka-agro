import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../utils/constants.dart';
import '../services/fijacion_service.dart';
import '../services/contract_service.dart';
import '../services/auth_service.dart';
import '../models/contract_model.dart';
import 'contracts/contract_detail_page.dart';
import 'contracts/create_fixation_dialog.dart';
import '../widgets/market_dashboard_widget.dart';
import 'dashboards/proveedor_dashboard.dart';
import 'dashboards/centro_dashboard.dart';
import 'dashboards/exportadora_dashboard.dart';
import 'package:intl/intl.dart';
import 'auth/login_page.dart';

class GestionPage extends StatefulWidget {
  const GestionPage({super.key});

  @override
  State<GestionPage> createState() => _GestionPageState();
}

class _GestionPageState extends State<GestionPage> with TickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authService = context.watch<AuthService>();
    final user = authService.currentUser;
    final role = authService.currentUser?.role ?? 'centro';

    return Scaffold(
      backgroundColor: AppConstants.backgroundLight,
      appBar: AppBar(
        title: const Text('Gestión Comercial'),
        centerTitle: true,
        actions: [
          // User Avatar / Logout
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: PopupMenuButton<String>(
              child: CircleAvatar(
                backgroundColor: Colors.white,
                backgroundImage: user?.avatarUrl != null ? NetworkImage(user!.avatarUrl!) : null,
                child: user?.avatarUrl == null ? Text(user?.name[0] ?? 'U', style: TextStyle(color: AppConstants.primaryColor)) : null,
              ),
              onSelected: (value) {
                if (value == 'logout') {
                  authService.logout();
                   // Navigation handles itself via main wrapper
                }
              },
              itemBuilder: (context) => [
                 PopupMenuItem(
                  enabled: false,
                  child: Text(user?.name ?? 'Usuario', style: const TextStyle(fontWeight: FontWeight.bold)),
                ),
                const PopupMenuItem(
                  value: 'logout',
                  child: Row(children: [Icon(Icons.logout, color: Colors.grey), SizedBox(width: 8), Text('Cerrar Sesión')]),
                ),
              ],
            ),
          )
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.business), text: 'General'),
            Tab(icon: Icon(Icons.assignment), text: 'Contratos'),
            Tab(icon: Icon(Icons.trending_up), text: 'Fijaciones'),
          ],
        ),
      ),
      body: Consumer2<FijacionService, ContractService>(
        builder: (context, fijacionService, contractService, child) {
          return TabBarView(
            controller: _tabController,
            children: [
              _buildGeneralTab(role),
              _buildContratosTab(contractService, fijacionService),
              _buildFijacionesTab(contractService, fijacionService),
            ],
          );
        },
      ),
    );
  }

  Widget _buildGeneralTab(String role) {
    switch (role) {
      case 'proveedor':
        return const ProveedorDashboard();
      case 'exportadora':
        return const ExportadoraDashboard();
      case 'centro':
      default:
        return const CentroDashboard();
    }
  }

  // --- CONTRATOS TAB ---

  Widget _buildContratosTab(ContractService contractService, FijacionService fijacionService) {
    if (contractService.contracts.isEmpty) {
      return const Center(child: Text('No hay contratos activos'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: contractService.contracts.length,
      itemBuilder: (context, index) {
        return _buildContractCard(contractService.contracts[index], fijacionService);
      },
    );
  }

  Widget _buildContractCard(ExportContract contract, FijacionService fijacionService) {
    final progress = contract.totalVolumeMt > 0 ? contract.fixedVolumeMt / contract.totalVolumeMt : 0.0;
    
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
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
                   Text(contract.contractCode, style: const TextStyle(fontWeight: FontWeight.bold)),
                   Chip(
                     label: Text(contract.status.toUpperCase(), style: const TextStyle(fontSize: 10, color: Colors.white)),
                     backgroundColor: contract.status == 'active' ? Colors.green : Colors.grey,
                     visualDensity: VisualDensity.compact,
                   )
                ],
              ),
              const SizedBox(height: 8),
              _buildDetailItem('Producto', contract.productType),
              _buildDetailItem('Volumen', '${contract.totalVolumeMt} MT'),
              _buildDetailItem('Fijado', '${contract.fixedVolumeMt} MT'),
              const SizedBox(height: 12),
              LinearProgressIndicator(value: progress, backgroundColor: Colors.grey[200], color: AppConstants.primaryColor),
              const SizedBox(height: 12),
              if (contract.status == 'active' && contract.fixedVolumeMt < contract.totalVolumeMt)
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () {
                        showDialog(
                          context: context,
                          builder: (context) => CreateFixationDialog(contract: contract),
                        );
                    },
                    icon: const Icon(Icons.trending_up),
                    label: const Text('FIJAR PRECIO'),
                  ),
                )
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.grey[600], fontSize: 13)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 13)),
        ],
      ),
    );
  }

  // --- FIJACIONES TAB ---

  Widget _buildFijacionesTab(ContractService contractService, FijacionService fijacionService) {
    List<Fixation> allFixations = [];
    for (var c in contractService.contracts) {
      if (c.fixations != null) {
        allFixations.addAll(c.fixations!);
      }
    }
    
    // Ordenar por fecha reciente
    allFixations.sort((a, b) => (b.fixationDate ?? DateTime.now()).compareTo(a.fixationDate ?? DateTime.now()));

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          const MarketDashboardWidget(),
          const SizedBox(height: 20),
          if (allFixations.isEmpty)
             const Center(child: Padding(
               padding: EdgeInsets.all(32.0),
               child: Text('No hay fijaciones registradas aún.'),
             ))
          else
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: allFixations.length,
              itemBuilder: (context, index) {
                final fix = allFixations[index];
                return _buildFixationCard(fix);
              },
            ),
        ],
      ),
    );
  }

  Widget _buildFixationCard(Fixation fixation) {
    final dateStr = fixation.fixationDate != null 
        ? DateFormat('dd MMM HH:mm').format(fixation.fixationDate!) 
        : '-';
        
    return Card(
      child: ListTile(
        leading: const CircleAvatar(backgroundColor: Colors.green, child: Icon(Icons.attach_money, color: Colors.white)),
        title: Text('${fixation.fixedQuantityMt} MT @ \$${fixation.spotPriceUsd}'),
        subtitle: Text(dateStr),
        trailing: Text('\$${fixation.totalValueUsd.toStringAsFixed(0)}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
      ),
    );
  }
}
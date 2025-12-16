import 'package:hive/hive.dart';

part 'contract_model.g.dart';

@HiveType(typeId: 0)
class ExportContract extends HiveObject {
  @HiveField(0)
  final int id;
  @HiveField(1)
  final String contractCode;
  @HiveField(2)
  final int buyerCompanyId;
  @HiveField(3)
  final int exporterCompanyId;
  @HiveField(4)
  final String productType;
  @HiveField(5)
  final String productGrade;
  @HiveField(6)
  final double totalVolumeMt;
  @HiveField(7)
  final double fixedVolumeMt;
  @HiveField(8)
  final double differentialUsd;
  @HiveField(9)
  final DateTime? startDate;
  @HiveField(10)
  final DateTime? endDate;
  @HiveField(11)
  final DateTime? deliveryDate;
  @HiveField(12)
  final String status;
  @HiveField(13)
  final String? blockchainContractId;
  @HiveField(14)
  final int createdByUserId;
  @HiveField(15)
  final DateTime? createdAt;
  @HiveField(16)
  final DateTime? updatedAt;
  
  // Sync Metadata
  @HiveField(17)
  String syncStatus; // 'synced', 'created', 'updated', 'deleted'
  @HiveField(18)
  int? lastUpdatedLocal;

  // Relaciones (no persistidas directamente en Hive por ahora, o requieren ids)
  // Ignoramos para Hive por simplicidad inicial, o deberíamos relacionar por ID
  final Company? buyerCompany;
  final Company? exporterCompany;
  final List<Fixation>? fixations;

  ExportContract({
    required this.id,
    required this.contractCode,
    required this.buyerCompanyId,
    required this.exporterCompanyId,
    required this.productType,
    required this.productGrade,
    required this.totalVolumeMt,
    this.fixedVolumeMt = 0.0,
    required this.differentialUsd,
    this.startDate,
    this.endDate,
    this.deliveryDate,
    required this.status,
    this.blockchainContractId,
    required this.createdByUserId,
    this.createdAt,
    this.updatedAt,
    this.syncStatus = 'synced',
    this.lastUpdatedLocal,
    this.buyerCompany,
    this.exporterCompany,
    this.fixations,
  });

  factory ExportContract.fromJson(Map<String, dynamic> json) {
    return ExportContract(
      id: json['id'],
      contractCode: json['contract_code'] ?? '',
      buyerCompanyId: json['buyer_company_id'],
      exporterCompanyId: json['exporter_company_id'],
      productType: json['product_type'] ?? '',
      productGrade: json['product_grade'] ?? '',
      totalVolumeMt: (json['total_volume_mt'] as num?)?.toDouble() ?? 0.0,
      fixedVolumeMt: (json['fixed_volume_mt'] as num?)?.toDouble() ?? 0.0,
      differentialUsd: (json['differential_usd'] as num?)?.toDouble() ?? 0.0,
      startDate: json['start_date'] != null ? DateTime.parse(json['start_date']) : null,
      endDate: json['end_date'] != null ? DateTime.parse(json['end_date']) : null,
      deliveryDate: json['delivery_date'] != null ? DateTime.parse(json['delivery_date']) : null,
      status: json['status'] ?? 'draft',
      blockchainContractId: json['blockchain_contract_id'],
      createdByUserId: json['created_by_user_id'],
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
      buyerCompany: json['buyer_company'] != null ? Company.fromJson(json['buyer_company']) : null,
      exporterCompany: json['exporter_company'] != null ? Company.fromJson(json['exporter_company']) : null,
      fixations: json['fixations'] != null 
          ? (json['fixations'] as List).map((i) => Fixation.fromJson(i)).toList()
          : null,
      syncStatus: 'synced', // From server implies synced
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'contract_code': contractCode,
      'buyer_company_id': buyerCompanyId,
      'exporter_company_id': exporterCompanyId,
      'product_type': productType,
      'product_grade': productGrade,
      'total_volume_mt': totalVolumeMt,
      'differential_usd': differentialUsd,
      'start_date': startDate?.toIso8601String(),
      'end_date': endDate?.toIso8601String(),
      'delivery_date': deliveryDate?.toIso8601String(),
      'status': status,
    };
  }
}

@HiveType(typeId: 1)
class Fixation extends HiveObject {
  @HiveField(0)
  final int id;
  @HiveField(1)
  final int exportContractId;
  @HiveField(2)
  final double fixedQuantityMt;
  @HiveField(3)
  final double spotPriceUsd;
  @HiveField(4)
  final double totalValueUsd;
  @HiveField(5)
  final DateTime? fixationDate;
  @HiveField(6)
  final String? notes;
  @HiveField(7)
  final String? blockchainFixationId;
  
  @HiveField(8)
  String syncStatus;

  Fixation({
    required this.id,
    required this.exportContractId,
    required this.fixedQuantityMt,
    required this.spotPriceUsd,
    required this.totalValueUsd,
    this.fixationDate,
    this.notes,
    this.blockchainFixationId,
    this.syncStatus = 'synced',
  });

  factory Fixation.fromJson(Map<String, dynamic> json) {
    return Fixation(
      id: json['id'],
      exportContractId: json['export_contract_id'],
      fixedQuantityMt: (json['fixed_quantity_mt'] as num?)?.toDouble() ?? 0.0,
      spotPriceUsd: (json['spot_price_usd'] as num?)?.toDouble() ?? 0.0,
      totalValueUsd: (json['total_value_usd'] as num?)?.toDouble() ?? 0.0,
      fixationDate: json['fixation_date'] != null ? DateTime.parse(json['fixation_date']) : null,
      notes: json['notes'],
      blockchainFixationId: json['blockchain_fixation_id'],
      syncStatus: 'synced',
    );
  }
}

@HiveType(typeId: 2)
class Company extends HiveObject {
  @HiveField(0)
  final int id;
  @HiveField(1)
  final String name;
  @HiveField(2)
  final String? companyType;
  @HiveField(3)
  final String? country;

  Company({
    required this.id,
    required this.name,
    this.companyType,
    this.country,
  });

  factory Company.fromJson(Map<String, dynamic> json) {
    return Company(
      id: json['id'],
      name: json['name'] ?? 'Unknown',
      companyType: json['company_type'],
      country: json['country'],
    );
  }
}

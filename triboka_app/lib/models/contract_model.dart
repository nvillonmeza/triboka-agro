class ExportContract {
  final int id;
  final String contractCode;
  final int buyerCompanyId;
  final int exporterCompanyId;
  final String productType;
  final String productGrade;
  final double totalVolumeMt;
  final double fixedVolumeMt;
  final double differentialUsd;
  final DateTime? startDate;
  final DateTime? endDate;
  final DateTime? deliveryDate;
  final String status;
  final String? blockchainContractId;
  final int createdByUserId;
  final DateTime? createdAt;
  final DateTime? updatedAt;
  
  // Relaciones (pueden ser nulas si no se cargan)
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

class Fixation {
  final int id;
  final int exportContractId;
  final double fixedQuantityMt;
  final double spotPriceUsd;
  final double totalValueUsd;
  final DateTime? fixationDate;
  final String? notes;
  final String? blockchainFixationId;

  Fixation({
    required this.id,
    required this.exportContractId,
    required this.fixedQuantityMt,
    required this.spotPriceUsd,
    required this.totalValueUsd,
    this.fixationDate,
    this.notes,
    this.blockchainFixationId,
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
    );
  }
}

class Company {
  final int id;
  final String name;
  final String? companyType;
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

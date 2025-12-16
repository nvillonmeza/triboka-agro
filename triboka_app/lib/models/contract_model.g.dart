// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'contract_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class ExportContractAdapter extends TypeAdapter<ExportContract> {
  @override
  final int typeId = 0;

  @override
  ExportContract read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return ExportContract(
      id: fields[0] as int,
      contractCode: fields[1] as String,
      buyerCompanyId: fields[2] as int,
      exporterCompanyId: fields[3] as int,
      productType: fields[4] as String,
      productGrade: fields[5] as String,
      totalVolumeMt: fields[6] as double,
      fixedVolumeMt: fields[7] as double,
      differentialUsd: fields[8] as double,
      startDate: fields[9] as DateTime?,
      endDate: fields[10] as DateTime?,
      deliveryDate: fields[11] as DateTime?,
      status: fields[12] as String,
      blockchainContractId: fields[13] as String?,
      createdByUserId: fields[14] as int,
      createdAt: fields[15] as DateTime?,
      updatedAt: fields[16] as DateTime?,
      syncStatus: fields[17] as String,
      lastUpdatedLocal: fields[18] as int?,
    );
  }

  @override
  void write(BinaryWriter writer, ExportContract obj) {
    writer
      ..writeByte(19)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.contractCode)
      ..writeByte(2)
      ..write(obj.buyerCompanyId)
      ..writeByte(3)
      ..write(obj.exporterCompanyId)
      ..writeByte(4)
      ..write(obj.productType)
      ..writeByte(5)
      ..write(obj.productGrade)
      ..writeByte(6)
      ..write(obj.totalVolumeMt)
      ..writeByte(7)
      ..write(obj.fixedVolumeMt)
      ..writeByte(8)
      ..write(obj.differentialUsd)
      ..writeByte(9)
      ..write(obj.startDate)
      ..writeByte(10)
      ..write(obj.endDate)
      ..writeByte(11)
      ..write(obj.deliveryDate)
      ..writeByte(12)
      ..write(obj.status)
      ..writeByte(13)
      ..write(obj.blockchainContractId)
      ..writeByte(14)
      ..write(obj.createdByUserId)
      ..writeByte(15)
      ..write(obj.createdAt)
      ..writeByte(16)
      ..write(obj.updatedAt)
      ..writeByte(17)
      ..write(obj.syncStatus)
      ..writeByte(18)
      ..write(obj.lastUpdatedLocal);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ExportContractAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class FixationAdapter extends TypeAdapter<Fixation> {
  @override
  final int typeId = 1;

  @override
  Fixation read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return Fixation(
      id: fields[0] as int,
      exportContractId: fields[1] as int,
      fixedQuantityMt: fields[2] as double,
      spotPriceUsd: fields[3] as double,
      totalValueUsd: fields[4] as double,
      fixationDate: fields[5] as DateTime?,
      notes: fields[6] as String?,
      blockchainFixationId: fields[7] as String?,
      syncStatus: fields[8] as String,
    );
  }

  @override
  void write(BinaryWriter writer, Fixation obj) {
    writer
      ..writeByte(9)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.exportContractId)
      ..writeByte(2)
      ..write(obj.fixedQuantityMt)
      ..writeByte(3)
      ..write(obj.spotPriceUsd)
      ..writeByte(4)
      ..write(obj.totalValueUsd)
      ..writeByte(5)
      ..write(obj.fixationDate)
      ..writeByte(6)
      ..write(obj.notes)
      ..writeByte(7)
      ..write(obj.blockchainFixationId)
      ..writeByte(8)
      ..write(obj.syncStatus);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FixationAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class CompanyAdapter extends TypeAdapter<Company> {
  @override
  final int typeId = 2;

  @override
  Company read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return Company(
      id: fields[0] as int,
      name: fields[1] as String,
      companyType: fields[2] as String?,
      country: fields[3] as String?,
    );
  }

  @override
  void write(BinaryWriter writer, Company obj) {
    writer
      ..writeByte(4)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.name)
      ..writeByte(2)
      ..write(obj.companyType)
      ..writeByte(3)
      ..write(obj.country);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is CompanyAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

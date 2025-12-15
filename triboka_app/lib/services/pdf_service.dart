import 'dart:typed_data';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';
import '../models/contract_model.dart';
import 'package:intl/intl.dart';

class PdfService {
  /// Genera y abre el PDF del contrato
  Future<void> generateAndOpenContract(ExportContract contract) async {
    final pdf = await _generateContractPdf(contract);
    await Printing.layoutPdf(
      onLayout: (PdfPageFormat format) async => pdf.save(),
      name: 'Contrato-${contract.contractCode}.pdf',
    );
  }

  /// Construye el documento PDF
  Future<pw.Document> _generateContractPdf(ExportContract contract) async {
    final pdf = pw.Document();
    final dateFormat = DateFormat('dd MMM yyyy');

    pdf.addPage(
      pw.MultiPage(
        pageFormat: PdfPageFormat.a4,
        margin: const pw.EdgeInsets.all(32),
        build: (pw.Context context) {
          return [
            _buildHeader(contract),
            pw.SizedBox(height: 20),
            _buildContractDetails(contract, dateFormat),
            pw.SizedBox(height: 20),
            _buildTermsAndConditions(),
            pw.SizedBox(height: 40),
            _buildSignatures(contract),
          ];
        },
        footer: (pw.Context context) {
          return pw.Container(
            alignment: pw.Alignment.centerRight,
            margin: const pw.EdgeInsets.only(top: 10),
            child: pw.Text(
              'Página ${context.pageNumber} de ${context.pagesCount}',
              style: const pw.TextStyle(color: PdfColors.grey),
            ),
          );
        },
      ),
    );

    return pdf;
  }

  pw.Widget _buildHeader(ExportContract contract) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Header(
          level: 0,
          child: pw.Row(
            mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
            children: [
              pw.Text('CONTRATO DE COMPRAVENTA', style: pw.TextStyle(fontSize: 24, fontWeight: pw.FontWeight.bold)),
              pw.Text(contract.contractCode, style: pw.TextStyle(fontSize: 18, color: PdfColors.grey700)),
            ],
          ),
        ),
        pw.Divider(),
      ],
    );
  }

  pw.Widget _buildContractDetails(ExportContract contract, DateFormat dateFormat) {
    return pw.Container(
      decoration: pw.BoxDecoration(
        border: pw.Border.all(color: PdfColors.grey300),
        borderRadius: const pw.BorderRadius.all(pw.Radius.circular(8)),
      ),
      padding: const pw.EdgeInsets.all(16),
      child: pw.Column(
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: [
          pw.Text('PARTES', style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 14)),
          pw.SizedBox(height: 8),
          pw.Row(
            children: [
              pw.Expanded(child: _buildInfoRow('VENDEDOR', contract.exporterCompany?.name ?? 'Triboka Agro')),
              pw.SizedBox(width: 16),
              pw.Expanded(child: _buildInfoRow('COMPRADOR', contract.buyerCompany?.name ?? 'Cliente')),
            ],
          ),
          pw.Divider(height: 20),
          pw.Text('DETALLES DEL PRODUCTO', style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 14)),
          pw.SizedBox(height: 8),
          pw.Row(
            children: [
              pw.Expanded(child: _buildInfoRow('PRODUCTO', contract.productType)),
              pw.SizedBox(width: 16),
              pw.Expanded(child: _buildInfoRow('CALIDAD/GRADO', contract.productGrade)),
            ],
          ),
          pw.SizedBox(height: 8),
          pw.Row(
            children: [
              pw.Expanded(child: _buildInfoRow('VOLUMEN TOTAL', '${contract.totalVolumeMt} MT')),
              pw.SizedBox(width: 16),
              pw.Expanded(child: _buildInfoRow('DIFERENCIAL', '\$${contract.differentialUsd} USD/MT')),
            ],
          ),
          pw.Divider(height: 20),
          pw.Text('PERIODO Y ENTREGA', style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 14)),
          pw.SizedBox(height: 8),
          pw.Row(
            children: [
              pw.Expanded(child: _buildInfoRow('FECHA CONTRATO', dateFormat.format(contract.startDate ?? DateTime.now()))),
              pw.SizedBox(width: 16),
              pw.Expanded(child: _buildInfoRow('FECHA ENTREGA', contract.deliveryDate != null ? dateFormat.format(contract.deliveryDate!) : 'A coordinar')),
            ],
          ),
        ],
      ),
    );
  }

  pw.Widget _buildInfoRow(String label, String value) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text(label, style: pw.TextStyle(fontSize: 10, color: PdfColors.grey600)),
        pw.Text(value, style: pw.TextStyle(fontSize: 12, fontWeight: pw.FontWeight.bold)),
      ],
    );
  }

  pw.Widget _buildTermsAndConditions() {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text('TÉRMINOS Y CONDICIONES', style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 14)),
        pw.SizedBox(height: 8),
        pw.Paragraph(
          text: '1. CALIDAD: El producto entregado cumplirá estrictamente con las especificaciones de calidad acordadas. Cualquier desviación deberá ser notificada antes del embarque.',
          style: const pw.TextStyle(fontSize: 10, lineSpacing: 2),
        ),
        pw.Paragraph(
          text: '2. PESO: El peso final será determinado en el lugar de destino por un supervisor independiente acordado por ambas partes.',
          style: const pw.TextStyle(fontSize: 10, lineSpacing: 2),
        ),
        pw.Paragraph(
          text: '3. PAGO: Las condiciones de pago serán las establecidas en la factura proforma adjunta a este contrato.',
          style: const pw.TextStyle(fontSize: 10, lineSpacing: 2),
        ),
        pw.Paragraph(
          text: '4. ARBITRAJE: Cualquier disputa derivada de este contrato se resolverá mediante arbitraje de conformidad con las reglas de la FCC.',
          style: const pw.TextStyle(fontSize: 10, lineSpacing: 2),
        ),
      ],
    );
  }

  pw.Widget _buildSignatures(ExportContract contract) {
    return pw.Row(
      mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
      children: [
        _buildSignatureBox('VENDEDOR', contract.exporterCompany?.name),
        _buildSignatureBox('COMPRADOR', contract.buyerCompany?.name),
      ],
    );
  }

  pw.Widget _buildSignatureBox(String role, String? name) {
    return pw.Column(
      children: [
        pw.Container(
          width: 200,
          height: 1,
          color: PdfColors.black,
        ),
        pw.SizedBox(height: 5),
        pw.Text(role, style: pw.TextStyle(fontWeight: pw.FontWeight.bold)),
        if (name != null) pw.Text(name, style: const pw.TextStyle(fontSize: 10)),
      ],
    );
  }
}

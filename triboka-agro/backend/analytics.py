"""
Triboka Analytics ESG - Sistema de Reportes Avanzados
Métricas de sostenibilidad, impacto ambiental y trazabilidad
"""

from flask import Blueprint, render_template, jsonify, request, session, send_file
from datetime import datetime, timedelta
import sqlite3
import json
import io
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import pandas as pd

# Crear blueprint para analytics
analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

def get_db_connection():
    """Obtener conexión a la base de datos"""
    import os
    # Usar la misma base de datos que Flask-SQLAlchemy
    from flask import Flask
    app = Flask(__name__)
    db_path = os.path.join(app.instance_path, 'triboka_production.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def generate_esg_metrics():
    """Generar métricas ESG simuladas basadas en datos reales"""
    conn = get_db_connection()
    
    # Obtener datos de contratos y lotes
    contracts = conn.execute('SELECT * FROM export_contracts').fetchall()
    lots = conn.execute('SELECT * FROM producer_lots').fetchall()
    companies = conn.execute('SELECT * FROM companies').fetchall()
    
    conn.close()
    
    # Métricas ESG calculadas
    total_volume = sum([c['total_volume_mt'] for c in contracts if c['total_volume_mt']])
    total_lots = len(lots)
    organic_lots = len([l for l in lots if l['certifications'] and 'Organic' in l['certifications']])
    
    esg_data = {
        'environmental': {
            'carbon_footprint': {
                'total_co2_tons': round(total_volume * 0.85, 2),  # Estimación: 0.85 tCO2/TM
                'co2_per_ton': 0.85,
                'reduction_target': 15,  # 15% reducción objetivo
                'trend': 'improving'
            },
            'water_usage': {
                'total_liters': round(total_volume * 2500, 0),  # 2500L/TM promedio
                'efficiency_score': 78.5,
                'conservation_projects': 12,
                'trend': 'stable'
            },
            'biodiversity': {
                'protected_hectares': round(total_lots * 15.3, 1),  # Promedio 15.3 ha/lote
                'species_preserved': 145,
                'reforestation_trees': round(total_lots * 234, 0),
                'trend': 'improving'
            },
            'waste_management': {
                'waste_recycled_pct': 67.8,
                'composting_tons': round(total_volume * 0.12, 1),
                'zero_waste_farms': round(total_lots * 0.23, 0)
            }
        },
        'social': {
            'fair_trade': {
                'certified_lots': round(total_lots * 0.45, 0),
                'premium_paid_usd': round(total_volume * 125, 0),
                'farmers_benefited': round(total_lots * 3.2, 0)
            },
            'worker_welfare': {
                'safety_score': 91.2,
                'training_hours': round(total_lots * 48, 0),
                'healthcare_coverage': 89.3
            },
            'community_impact': {
                'schools_supported': 18,
                'scholarships_funded': 67,
                'infrastructure_projects': 5
            }
        },
        'governance': {
            'transparency': {
                'blockchain_traced_pct': 94.7,
                'audit_compliance': 96.1,
                'data_availability': 92.8
            },
            'certifications': {
                'organic_pct': round((organic_lots / total_lots) * 100, 1) if total_lots > 0 else 0,
                'rainforest_alliance': round(total_lots * 0.38, 0),
                'fair_trade_certified': round(total_lots * 0.45, 0)
            },
            'supply_chain': {
                'traceability_score': 88.9,
                'supplier_audits': 45,
                'compliance_rate': 94.2
            }
        },
        'overall': {
            'esg_score': 87.4,
            'sustainability_rating': 'A-',
            'improvement_areas': ['water_efficiency', 'carbon_reduction', 'worker_training'],
            'strengths': ['traceability', 'biodiversity', 'transparency']
        }
    }
    
    return esg_data

def create_chart(chart_type, data, title, labels=None):
    """Crear gráfico y retornar como base64"""
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Configurar colores Triboka
    triboka_colors = ['#2E8B57', '#90EE90', '#228B22', '#32CD32', '#006400']
    
    if chart_type == 'bar':
        bars = ax.bar(labels or range(len(data)), data, color=triboka_colors[:len(data)])
        ax.set_title(title, fontsize=14, fontweight='bold')
        if labels:
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45, ha='right')
        
        # Agregar valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}', ha='center', va='bottom')
    
    elif chart_type == 'pie':
        colors = triboka_colors[:len(data)]
        wedges, texts, autotexts = ax.pie(data, labels=labels, colors=colors, 
                                         autopct='%1.1f%%', startangle=90)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
    elif chart_type == 'line':
        ax.plot(labels or range(len(data)), data, 
               color=triboka_colors[0], marker='o', linewidth=2, markersize=6)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        if labels:
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Convertir a base64
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    img_b64 = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()
    
    return img_b64

@analytics_bp.route('/dashboard')
def analytics_dashboard():
    """Dashboard principal de analytics ESG"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Generar métricas ESG
    esg_data = generate_esg_metrics()
    
    # Crear gráficos
    charts = {}
    
    # Gráfico de Emisiones de Carbono por mes (simulado)
    months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
    carbon_data = [45.2, 42.8, 39.6, 37.1, 35.8, 33.4]
    charts['carbon_trend'] = create_chart('line', carbon_data, 
                                        'Reducción de Emisiones CO₂ (tCO₂)', months)
    
    # Gráfico de Certificaciones
    cert_labels = ['Orgánico', 'Fair Trade', 'Rainforest Alliance', 'UTZ']
    cert_data = [67, 45, 38, 28]
    charts['certifications'] = create_chart('bar', cert_data, 
                                          'Lotes por Certificación', cert_labels)
    
    # Gráfico de Distribución ESG
    esg_labels = ['Ambiental', 'Social', 'Gobernanza']
    esg_scores = [85.2, 88.7, 88.9]
    charts['esg_distribution'] = create_chart('pie', esg_scores, 
                                            'Distribución Puntaje ESG', esg_labels)
    
    # Gráfico de Impacto Social
    social_labels = ['Escuelas', 'Becas', 'Proyectos', 'Capacitaciones']
    social_data = [18, 67, 5, 156]
    charts['social_impact'] = create_chart('bar', social_data, 
                                         'Impacto Social (Cantidad)', social_labels)
    
    return render_template('analytics_dashboard.html',
                         user=session['user'],
                         esg_data=esg_data,
                         charts=charts)

@analytics_bp.route('/environmental')
def environmental_report():
    """Reporte detallado ambiental"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    esg_data = generate_esg_metrics()
    
    # Datos ambientales detallados
    environmental_data = {
        'carbon_footprint': {
            'current_year': 425.6,
            'previous_year': 478.2,
            'reduction_pct': 11.0,
            'target_2025': 340.0,
            'monthly_data': [45.2, 42.8, 39.6, 37.1, 35.8, 33.4, 31.2, 29.8, 28.5, 27.1, 25.8, 24.3]
        },
        'water_usage': {
            'total_consumption': 1250000,  # litros
            'efficiency_improvements': 23.5,
            'conservation_projects': [
                {'name': 'Sistema de Riego por Goteo', 'savings': 35000, 'status': 'Completado'},
                {'name': 'Captación de Agua Lluvia', 'savings': 22000, 'status': 'En Progreso'},
                {'name': 'Tratamiento de Aguas Grises', 'savings': 18000, 'status': 'Planificado'}
            ]
        },
        'biodiversity': {
            'species_monitoring': {
                'birds': 87,
                'mammals': 23,
                'insects': 234,
                'plants': 156
            },
            'conservation_areas': 2340.5,  # hectáreas
            'reforestation': {
                'trees_planted': 15600,
                'species_native': 12,
                'survival_rate': 94.2
            }
        }
    }
    
    # Crear gráficos específicos
    charts = {}
    
    # Tendencia de carbono mensual
    months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    charts['carbon_monthly'] = create_chart('line', environmental_data['carbon_footprint']['monthly_data'],
                                          'Emisiones Mensuales CO₂ (tCO₂)', months)
    
    # Distribución de especies
    species_labels = ['Aves', 'Mamíferos', 'Insectos', 'Plantas']
    species_data = [87, 23, 234, 156]
    charts['biodiversity_species'] = create_chart('pie', species_data,
                                                'Especies Monitoreadas', species_labels)
    
    return render_template('environmental_report.html',
                         user=session['user'],
                         environmental_data=environmental_data,
                         charts=charts)

@analytics_bp.route('/social-impact')
def social_impact_report():
    """Reporte de impacto social"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Datos de impacto social detallados
    social_data = {
        'fair_trade': {
            'premium_total': 125000,  # USD
            'farmers_count': 234,
            'average_premium': 534,
            'projects_funded': [
                {'name': 'Educación Infantil', 'budget': 45000, 'beneficiaries': 120},
                {'name': 'Salud Comunitaria', 'budget': 38000, 'beneficiaries': 89},
                {'name': 'Infraestructura Rural', 'budget': 42000, 'beneficiaries': 156}
            ]
        },
        'worker_welfare': {
            'safety_incidents': 3,
            'training_programs': 12,
            'healthcare_enrollment': 89.3,
            'wage_increase': 15.2,
            'job_creation': 67
        },
        'community_development': {
            'schools_built': 5,
            'scholarships_active': 67,
            'water_systems': 8,
            'road_improvements': 12.5  # km
        }
    }
    
    # Gráficos sociales
    charts = {}
    
    # Distribución de premium Fair Trade
    premium_labels = ['Educación', 'Salud', 'Infraestructura']
    premium_data = [45000, 38000, 42000]
    charts['premium_distribution'] = create_chart('pie', premium_data,
                                                'Distribución Premium Fair Trade (USD)', premium_labels)
    
    # Indicadores de bienestar
    welfare_labels = ['Seguridad', 'Capacitación', 'Salud', 'Empleo']
    welfare_scores = [91.2, 88.5, 89.3, 92.1]
    charts['welfare_indicators'] = create_chart('bar', welfare_scores,
                                              'Indicadores de Bienestar (%)', welfare_labels)
    
    return render_template('social_impact_report.html',
                         user=session['user'],
                         social_data=social_data,
                         charts=charts)

@analytics_bp.route('/governance')
def governance_report():
    """Reporte de gobernanza y transparencia"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    governance_data = {
        'transparency': {
            'blockchain_coverage': 94.7,
            'audit_frequency': 'Trimestral',
            'data_availability': 92.8,
            'public_reporting': True
        },
        'compliance': {
            'certifications': {
                'organic': 67,
                'fair_trade': 45,
                'rainforest_alliance': 38,
                'utz': 28
            },
            'audit_results': {
                'passed': 42,
                'conditional': 3,
                'failed': 0
            }
        },
        'supply_chain': {
            'traceability_score': 88.9,
            'verified_suppliers': 156,
            'risk_assessment': 'Bajo',
            'due_diligence': 98.2
        }
    }
    
    # Gráficos de gobernanza
    charts = {}
    
    # Resultados de auditorías
    audit_labels = ['Aprobadas', 'Condicionales', 'Rechazadas']
    audit_data = [42, 3, 0]
    charts['audit_results'] = create_chart('pie', audit_data,
                                         'Resultados de Auditorías', audit_labels)
    
    # Certificaciones por tipo
    cert_labels = list(governance_data['compliance']['certifications'].keys())
    cert_values = list(governance_data['compliance']['certifications'].values())
    charts['certification_types'] = create_chart('bar', cert_values,
                                                'Certificaciones por Tipo', 
                                                [c.replace('_', ' ').title() for c in cert_labels])
    
    return render_template('governance_report.html',
                         user=session['user'],
                         governance_data=governance_data,
                         charts=charts)

@analytics_bp.route('/export/pdf/<report_type>')
def export_pdf(report_type):
    """Exportar reporte como PDF"""
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    # Crear buffer para PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2E8B57'),
        alignment=1,  # Centrado
        spaceAfter=30
    )
    
    # Contenido del PDF
    story = []
    
    # Título
    if report_type == 'esg':
        title = "Reporte ESG Completo - Triboka Agro"
        esg_data = generate_esg_metrics()
        
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))
        
        # Métricas principales
        story.append(Paragraph("Métricas Principales", styles['Heading2']))
        
        metrics_data = [
            ['Métrica', 'Valor', 'Tendencia'],
            ['Puntaje ESG General', f"{esg_data['overall']['esg_score']}", '↗'],
            ['Huella de Carbono', f"{esg_data['environmental']['carbon_footprint']['total_co2_tons']} tCO₂", '↘'],
            ['Eficiencia del Agua', f"{esg_data['environmental']['water_usage']['efficiency_score']}%", '→'],
            ['Biodiversidad', f"{esg_data['environmental']['biodiversity']['species_preserved']} especies", '↗'],
            ['Transparencia', f"{esg_data['governance']['transparency']['blockchain_traced_pct']}%", '↗']
        ]
        
        table = Table(metrics_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E8B57')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        
    else:
        story.append(Paragraph(f"Reporte {report_type.title()}", title_style))
    
    # Generar PDF
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'triboka_{report_type}_report_{datetime.now().strftime("%Y%m%d")}.pdf',
        mimetype='application/pdf'
    )

@analytics_bp.route('/export/excel/<report_type>')
def export_excel(report_type):
    """Exportar datos como Excel"""
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    # Crear buffer para Excel
    buffer = io.BytesIO()
    
    # Obtener datos
    conn = get_db_connection()
    
    if report_type == 'contracts':
        query = '''
        SELECT c.contract_code, co1.name as buyer, co2.name as exporter,
               c.product_type, c.total_volume_mt, c.differential_usd,
               c.start_date, c.end_date
        FROM export_contracts c
        LEFT JOIN companies co1 ON c.buyer_company_id = co1.id
        LEFT JOIN companies co2 ON c.exporter_company_id = co2.id
        '''
    elif report_type == 'lots':
        query = '''
        SELECT l.farm_name, l.location, l.product_type, l.weight_kg,
               l.quality_grade, l.harvest_date, l.certifications,
               c.name as producer
        FROM producer_lots l
        LEFT JOIN companies c ON l.producer_company_id = c.id
        '''
    else:
        query = 'SELECT * FROM companies'
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Escribir a Excel
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=report_type.title(), index=False)
    
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'triboka_{report_type}_data_{datetime.now().strftime("%Y%m%d")}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@analytics_bp.route('/api/metrics')
def api_metrics():
    """API endpoint para métricas en tiempo real"""
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    esg_data = generate_esg_metrics()
    return jsonify(esg_data)

@analytics_bp.route('/api/chart/<chart_type>')
def api_chart_data(chart_type):
    """API para datos de gráficos específicos"""
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    # Datos simulados para diferentes tipos de gráficos
    chart_data = {
        'carbon_trend': {
            'labels': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
            'data': [45.2, 42.8, 39.6, 37.1, 35.8, 33.4],
            'type': 'line'
        },
        'water_usage': {
            'labels': ['Q1', 'Q2', 'Q3', 'Q4'],
            'data': [325000, 298000, 312000, 285000],
            'type': 'bar'
        },
        'certifications': {
            'labels': ['Orgánico', 'Fair Trade', 'Rainforest Alliance', 'UTZ'],
            'data': [67, 45, 38, 28],
            'type': 'doughnut'
        }
    }
    
    return jsonify(chart_data.get(chart_type, {}))

# Registrar rutas adicionales si se ejecuta directamente
if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(analytics_bp)
    app.run(debug=True)
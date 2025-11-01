"""
Sistema de Exportación de Reportes en PDF
Genera reportes profesionales con gráficos y métricas
Autor: Sistema UX Mejorado
"""

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import io
from typing import Dict, List, Optional
import logging

# Para generar PDFs más avanzados
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
import plotly.graph_objects as go
import plotly.express as px

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generador de reportes PDF profesionales"""
    
    def __init__(self, title: str = "Reporte de Predicción de Churn", 
                 company_name: str = "FinTech Analytics"):
        """
        Inicializa el generador de reportes
        
        Args:
            title: Título del reporte
            company_name: Nombre de la empresa
        """
        self.title = title
        self.company_name = company_name
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Configura estilos personalizados"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            spaceAfter=12
        ))
    
    def generate_executive_report(self, 
                                  metrics: Dict,
                                  high_risk_customers: pd.DataFrame,
                                  trends_data: pd.DataFrame,
                                  output_path: str):
        """
        Genera reporte ejecutivo completo
        
        Args:
            metrics: Diccionario con métricas clave
            high_risk_customers: DataFrame con clientes de alto riesgo
            trends_data: DataFrame con datos de tendencias
            output_path: Ruta donde guardar el PDF
        """
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Portada
        story.extend(self._create_cover_page())
        story.append(PageBreak())
        
        # Resumen ejecutivo
        story.extend(self._create_executive_summary(metrics))
        story.append(PageBreak())
        
        # Métricas clave
        story.extend(self._create_metrics_section(metrics))
        story.append(Spacer(1, 0.3*inch))
        
        # Clientes de alto riesgo
        story.extend(self._create_high_risk_section(high_risk_customers))
        story.append(PageBreak())
        
        # Tendencias y gráficos
        if trends_data is not None and not trends_data.empty:
            story.extend(self._create_trends_section(trends_data))
            story.append(PageBreak())
        
        # Recomendaciones
        story.extend(self._create_recommendations_section(metrics))
        
        # Generar PDF
        doc.build(story)
        logger.info(f"✓ Reporte ejecutivo generado: {output_path}")
        
        return output_path
    
    def _create_cover_page(self) -> List:
        """Crea página de portada"""
        elements = []
        
        # Espacio superior
        elements.append(Spacer(1, 2*inch))
        
        # Título
        title = Paragraph(self.title, self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.5*inch))
        
        # Empresa
        company = Paragraph(
            f"<b>{self.company_name}</b>",
            ParagraphStyle(
                'company',
                parent=self.styles['Normal'],
                fontSize=18,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#7f8c8d')
            )
        )
        elements.append(company)
        elements.append(Spacer(1, 0.3*inch))
        
        # Fecha
        date = Paragraph(
            datetime.now().strftime("%d de %B de %Y"),
            ParagraphStyle(
                'date',
                parent=self.styles['Normal'],
                fontSize=12,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#95a5a6')
            )
        )
        elements.append(date)
        
        return elements
    
    def _create_executive_summary(self, metrics: Dict) -> List:
        """Crea sección de resumen ejecutivo"""
        elements = []
        
        # Título de sección
        elements.append(Paragraph("📊 Resumen Ejecutivo", self.styles['CustomHeading']))
        
        # Texto del resumen
        churn_rate = metrics.get('churn_rate', 0) * 100
        high_risk = metrics.get('high_risk_count', 0)
        critical = metrics.get('critical_risk_count', 0)
        
        summary_text = f"""
        <para>
        <b>Situación Actual:</b><br/>
        La tasa de churn actual es de <b>{churn_rate:.1f}%</b>, con un total de 
        <b>{high_risk}</b> clientes en riesgo alto, de los cuales <b>{critical}</b> 
        requieren atención inmediata (riesgo crítico).
        <br/><br/>
        <b>Impacto Proyectado:</b><br/>
        Sin intervención, se estima una pérdida potencial de 
        <b>${metrics.get('revenue_at_risk', 0):,.0f}</b> en los próximos 90 días.
        <br/><br/>
        <b>Acción Requerida:</b><br/>
        Se recomienda implementar estrategias de retención enfocadas en los 
        segmentos de mayor riesgo identificados en este reporte.
        </para>
        """
        
        elements.append(Paragraph(summary_text, self.styles['CustomBody']))
        
        return elements
    
    def _create_metrics_section(self, metrics: Dict) -> List:
        """Crea sección de métricas clave"""
        elements = []
        
        elements.append(Paragraph("📈 Métricas Clave", self.styles['CustomHeading']))
        
        # Crear tabla de métricas
        data = [
            ['Métrica', 'Valor', 'Estado'],
            ['Tasa de Churn', f"{metrics.get('churn_rate', 0)*100:.1f}%", 
             '🔴 Crítico' if metrics.get('churn_rate', 0) > 0.2 else '🟡 Atención'],
            ['Clientes Totales', f"{metrics.get('total_customers', 0):,}", '✅ OK'],
            ['Clientes en Riesgo Alto', f"{metrics.get('high_risk_count', 0):,}", 
             '⚠️ Requiere Acción'],
            ['Clientes en Riesgo Crítico', f"{metrics.get('critical_risk_count', 0):,}", 
             '🔴 Urgente'],
            ['Revenue en Riesgo', f"${metrics.get('revenue_at_risk', 0):,.0f}", 
             '💰 Alto Impacto'],
            ['Tasa de Retención Objetivo', f"{metrics.get('target_retention', 85):.0f}%", 
             '🎯 Meta'],
        ]
        
        table = Table(data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _create_high_risk_section(self, df: pd.DataFrame) -> List:
        """Crea sección de clientes de alto riesgo"""
        elements = []
        
        elements.append(Paragraph("⚠️ Top 10 Clientes de Alto Riesgo", 
                                 self.styles['CustomHeading']))
        
        if df.empty:
            elements.append(Paragraph("No hay clientes de alto riesgo identificados.", 
                                    self.styles['CustomBody']))
            return elements
        
        # Tomar top 10
        top_customers = df.head(10)
        
        # Crear tabla
        table_data = [['#', 'Cliente ID', 'Probabilidad', 'Factores Principales']]
        
        for idx, row in enumerate(top_customers.itertuples(), 1):
            customer_id = getattr(row, 'Customer_ID', f'CUST_{idx:05d}')
            prob = getattr(row, 'Churn_Probability', getattr(row, 'Risk_Score', 0))
            
            # Factores principales (simplificado)
            factors = []
            if getattr(row, 'Complain', 0) == 1:
                factors.append('Quejas')
            if getattr(row, 'IsActiveMember', 1) == 0:
                factors.append('Inactivo')
            if getattr(row, 'NumOfProducts', 0) >= 3:
                factors.append('3+ Productos')
            
            factors_text = ', '.join(factors[:3]) if factors else 'N/A'
            
            table_data.append([
                str(idx),
                customer_id,
                f"{prob:.1%}" if prob <= 1 else f"{prob:.0f}",
                factors_text
            ])
        
        table = Table(table_data, colWidths=[0.5*inch, 1.5*inch, 1*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _create_trends_section(self, df: pd.DataFrame) -> List:
        """Crea sección de tendencias con gráficos"""
        elements = []
        
        elements.append(Paragraph("📊 Análisis de Tendencias", self.styles['CustomHeading']))
        
        # Crear gráfico temporal si hay datos
        try:
            # Gráfico simple con matplotlib
            fig, ax = plt.subplots(figsize=(7, 4))
            
            if 'date' in df.columns or 'Date' in df.columns:
                date_col = 'date' if 'date' in df.columns else 'Date'
                df_grouped = df.groupby(date_col).size()
                df_grouped.plot(ax=ax, marker='o', color='#3498db')
                ax.set_title('Tendencia de Clientes en Riesgo')
                ax.set_xlabel('Fecha')
                ax.set_ylabel('Cantidad')
                ax.grid(True, alpha=0.3)
            else:
                # Gráfico de distribución por riesgo
                if 'Risk_Level' in df.columns:
                    risk_counts = df['Risk_Level'].value_counts()
                    risk_counts.plot(kind='bar', ax=ax, color=['#27ae60', '#f39c12', '#e74c3c'])
                    ax.set_title('Distribución por Nivel de Riesgo')
                    ax.set_ylabel('Cantidad de Clientes')
                    ax.set_xlabel('Nivel de Riesgo')
                    plt.xticks(rotation=45)
            
            # Guardar gráfico en memoria
            img_buffer = io.BytesIO()
            plt.tight_layout()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            # Agregar imagen al PDF
            img = Image(img_buffer, width=6*inch, height=3.5*inch)
            elements.append(img)
            
        except Exception as e:
            logger.warning(f"No se pudo crear gráfico de tendencias: {e}")
            elements.append(Paragraph("Gráficos no disponibles con los datos actuales.", 
                                    self.styles['CustomBody']))
        
        return elements
    
    def _create_recommendations_section(self, metrics: Dict) -> List:
        """Crea sección de recomendaciones"""
        elements = []
        
        elements.append(Paragraph("💡 Recomendaciones Estratégicas", 
                                 self.styles['CustomHeading']))
        
        recommendations = [
            "<b>1. Acción Inmediata (0-7 días):</b><br/>"
            "   • Contactar a clientes en riesgo CRÍTICO vía llamada telefónica<br/>"
            "   • Ofrecer incentivos personalizados (descuentos, upgrades)<br/>"
            "   • Asignar account manager dedicado<br/><br/>",
            
            "<b>2. Corto Plazo (1-4 semanas):</b><br/>"
            "   • Implementar campaña de reactivación para clientes inactivos<br/>"
            "   • Mejorar programa de onboarding para nuevos clientes<br/>"
            "   • Lanzar encuestas de satisfacción<br/><br/>",
            
            "<b>3. Mediano Plazo (1-3 meses):</b><br/>"
            "   • Desarrollar programa de lealtad mejorado<br/>"
            "   • Optimizar productos basado en feedback<br/>"
            "   • A/B testing de estrategias de retención<br/><br/>",
            
            "<b>4. Largo Plazo (3-12 meses):</b><br/>"
            "   • Invertir en mejora de experiencia de usuario<br/>"
            "   • Implementar sistema de early warning automatizado<br/>"
            "   • Desarrollar modelo predictivo más avanzado<br/>"
        ]
        
        for rec in recommendations:
            elements.append(Paragraph(rec, self.styles['CustomBody']))
        
        return elements
    
    def generate_customer_report(self,
                                customer_data: Dict,
                                prediction: Dict,
                                output_path: str):
        """
        Genera reporte individual de cliente
        
        Args:
            customer_data: Datos del cliente
            prediction: Predicción y explicación
            output_path: Ruta de salida
        """
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Título
        story.append(Paragraph(
            "Reporte de Riesgo de Churn - Cliente Individual",
            self.styles['CustomTitle']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # Información del cliente
        story.append(Paragraph("👤 Información del Cliente", self.styles['CustomHeading']))
        
        customer_info = [
            ['Campo', 'Valor'],
            ['Customer ID', customer_data.get('customer_id', 'N/A')],
            ['Edad', str(customer_data.get('Age', 'N/A'))],
            ['País', customer_data.get('Geography', 'N/A')],
            ['Balance', f"${customer_data.get('Balance', 0):,.2f}"],
            ['Productos', str(customer_data.get('NumOfProducts', 'N/A'))],
            ['Score de Crédito', str(customer_data.get('CreditScore', 'N/A'))],
        ]
        
        table = Table(customer_info, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Predicción
        story.append(Paragraph("🎯 Predicción de Churn", self.styles['CustomHeading']))
        
        prob = prediction.get('churn_probability', 0)
        risk_level = prediction.get('risk_level', 'BAJO')
        
        # Color según riesgo
        risk_color = {
            'CRÍTICO': '#e74c3c',
            'ALTO': '#f39c12',
            'MEDIO': '#f1c40f',
            'BAJO': '#27ae60'
        }.get(risk_level, '#95a5a6')
        
        pred_text = f"""
        <para>
        <b>Probabilidad de Churn:</b> <font color="{risk_color}"><b>{prob*100:.1f}%</b></font><br/>
        <b>Nivel de Riesgo:</b> <font color="{risk_color}"><b>{risk_level}</b></font><br/>
        <b>Confianza del Modelo:</b> {prediction.get('confidence', 'Alta')}
        </para>
        """
        
        story.append(Paragraph(pred_text, self.styles['CustomBody']))
        story.append(Spacer(1, 0.3*inch))
        
        # Factores de riesgo
        if 'factors' in prediction:
            story.append(Paragraph("⚠️ Factores de Riesgo", self.styles['CustomHeading']))
            
            factors_data = [['Factor', 'Valor', 'Impacto']]
            for factor in prediction['factors'][:5]:
                factors_data.append([
                    factor.get('factor', ''),
                    str(factor.get('feature_value', '')),
                    factor.get('impact', '')
                ])
            
            table = Table(factors_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.3*inch))
        
        # Recomendaciones
        if 'recommendations' in prediction:
            story.append(Paragraph("💡 Acciones Recomendadas", self.styles['CustomHeading']))
            
            for i, rec in enumerate(prediction['recommendations'], 1):
                story.append(Paragraph(f"{i}. {rec}", self.styles['CustomBody']))
        
        # Generar PDF
        doc.build(story)
        logger.info(f"✓ Reporte de cliente generado: {output_path}")
        
        return output_path


# ============= FUNCIONES DE USO RÁPIDO =============

def export_executive_summary(metrics: Dict, customers_df: pd.DataFrame, 
                            output_path: str = "executive_report.pdf"):
    """
    Función rápida para exportar resumen ejecutivo
    
    Args:
        metrics: Diccionario con métricas
        customers_df: DataFrame con datos de clientes
        output_path: Ruta de salida
    """
    generator = PDFReportGenerator()
    
    # Filtrar alto riesgo
    high_risk = customers_df[
        customers_df.get('Risk_Level', 'BAJO').isin(['ALTO', 'CRÍTICO'])
    ] if 'Risk_Level' in customers_df.columns else customers_df.head(10)
    
    return generator.generate_executive_report(
        metrics=metrics,
        high_risk_customers=high_risk,
        trends_data=customers_df,
        output_path=output_path
    )


if __name__ == "__main__":
    print("="*70)
    print("SISTEMA DE EXPORTACIÓN DE REPORTES PDF")
    print("="*70)
    
    # Datos de ejemplo
    metrics = {
        'churn_rate': 0.204,
        'total_customers': 10000,
        'high_risk_count': 1200,
        'critical_risk_count': 350,
        'revenue_at_risk': 450000,
        'target_retention': 85
    }
    
    # DataFrame de ejemplo
    customers_data = pd.DataFrame({
        'Customer_ID': [f'CUST_{i:05d}' for i in range(1, 11)],
        'Churn_Probability': np.random.uniform(0.7, 0.95, 10),
        'Risk_Level': ['CRÍTICO'] * 5 + ['ALTO'] * 5,
        'Complain': [1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        'IsActiveMember': [0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        'NumOfProducts': [3, 4, 2, 3, 2, 4, 3, 2, 3, 4]
    })
    
    print("\n1. Generando reporte ejecutivo...")
    generator = PDFReportGenerator()
    
    try:
        output = generator.generate_executive_report(
            metrics=metrics,
            high_risk_customers=customers_data,
            trends_data=customers_data,
            output_path='reporte_ejecutivo_demo.pdf'
        )
        
        print(f"✓ Reporte generado: {output}")
        
        # Reporte individual
        print("\n2. Generando reporte de cliente individual...")
        
        customer_data = {
            'customer_id': 'CUST_00001',
            'Age': 45,
            'Geography': 'Germany',
            'Balance': 125000,
            'NumOfProducts': 3,
            'CreditScore': 650
        }
        
        prediction = {
            'churn_probability': 0.85,
            'risk_level': 'CRÍTICO',
            'confidence': 'Alta',
            'factors': [
                {'factor': 'Tiene quejas registradas', 'feature_value': 1, 'impact': 'CRÍTICO'},
                {'factor': '3+ productos', 'feature_value': 3, 'impact': 'ALTO'},
                {'factor': 'Días sin transacción', 'feature_value': 45, 'impact': 'ALTO'}
            ],
            'recommendations': [
                '📞 Contacto directo en próximas 24 horas',
                '🎁 Aplicar incentivo de alto valor',
                '👨‍💼 Asignar account manager dedicado'
            ]
        }
        
        output2 = generator.generate_customer_report(
            customer_data=customer_data,
            prediction=prediction,
            output_path='reporte_cliente_demo.pdf'
        )
        
        print(f"✓ Reporte de cliente generado: {output2}")
        
        print("\n" + "="*70)
        print("✅ SISTEMA DE PDF FUNCIONANDO CORRECTAMENTE")
        print("="*70)
        print(f"\nArchivos generados:")
        print(f"  - reporte_ejecutivo_demo.pdf")
        print(f"  - reporte_cliente_demo.pdf")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nAsegúrate de tener instalado:")
        print("  pip install reportlab matplotlib seaborn")

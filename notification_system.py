"""
Sistema de Notificaciones y Alertas de Churn
Envía notificaciones al equipo de CRM sobre clientes en riesgo
"""

import pandas as pd
import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import os
from typing import List, Dict
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationSystem:
    """Sistema completo de notificaciones para alertas de churn"""
    
    def __init__(self):
        self.email_config = self._load_email_config()
        self.webhook_url = os.getenv('WEBHOOK_URL', None)
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL', None)
        
    def _load_email_config(self):
        """Carga configuración de email desde variables de entorno"""
        return {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', 587)),
            'sender_email': os.getenv('SENDER_EMAIL', ''),
            'sender_password': os.getenv('SENDER_PASSWORD', ''),
            'default_recipients': os.getenv('CRM_TEAM_EMAILS', '').split(',')
        }
    
    def identify_high_risk_customers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identifica clientes de alto riesgo
        
        Args:
            df: DataFrame con datos de clientes
            
        Returns:
            DataFrame filtrado con clientes de alto riesgo
        """
        # Agregar Customer_ID si no existe
        if 'Customer_ID' not in df.columns:
            df['Customer_ID'] = ['CUST_' + str(i).zfill(5) for i in range(len(df))]
        
        # Calcular score de riesgo
        df['Risk_Score'] = 0
        df.loc[df['Complain'] == 1, 'Risk_Score'] += 40
        df.loc[df['IsActiveMember'] == 0, 'Risk_Score'] += 25
        df.loc[df['NumOfProducts'] >= 3, 'Risk_Score'] += 30
        df.loc[df['Days_Since_Last_Transaction'] > 25, 'Risk_Score'] += 20
        df.loc[df['Monthly_Logins'] < 5, 'Risk_Score'] += 15
        df.loc[df['Satisfaction Score'] <= 2, 'Risk_Score'] += 25
        
        # Clasificar nivel de riesgo
        df['Risk_Level'] = 'BAJO'
        df.loc[df['Risk_Score'] >= 40, 'Risk_Level'] = 'MEDIO'
        df.loc[df['Risk_Score'] >= 70, 'Risk_Level'] = 'ALTO'
        df.loc[df['Risk_Score'] >= 100, 'Risk_Level'] = 'CRÍTICO'
        
        # Filtrar alto riesgo (ALTO y CRÍTICO)
        high_risk = df[df['Risk_Level'].isin(['ALTO', 'CRÍTICO'])].copy()
        
        # Ordenar por score descendente
        high_risk = high_risk.sort_values('Risk_Score', ascending=False)
        
        return high_risk
    
    def create_customer_alert(self, customer: pd.Series) -> Dict:
        """
        Crea alerta estructurada para un cliente
        
        Args:
            customer: Serie con datos del cliente
            
        Returns:
            Diccionario con alerta estructurada
        """
        # Identificar factores de riesgo
        risk_factors = []
        
        if customer.get('Complain', 0) == 1:
            risk_factors.append('⚠️ Tiene quejas registradas')
        
        if customer.get('IsActiveMember', 1) == 0:
            risk_factors.append('💤 Miembro inactivo')
        
        if customer.get('NumOfProducts', 0) >= 3:
            risk_factors.append('📦 3+ productos (sobrecarga)')
        
        if customer.get('Days_Since_Last_Transaction', 0) > 25:
            risk_factors.append(f"⏱️ {customer.get('Days_Since_Last_Transaction', 0)} días sin transacción")
        
        if customer.get('Monthly_Logins', 10) < 5:
            risk_factors.append(f"📱 Solo {customer.get('Monthly_Logins', 0)} logins/mes")
        
        if customer.get('Satisfaction Score', 5) <= 2:
            risk_factors.append(f"😟 Baja satisfacción ({customer.get('Satisfaction Score', 0)}/5)")
        
        # Acciones recomendadas según nivel de riesgo
        if customer.get('Risk_Level', 'BAJO') == 'CRÍTICO':
            actions = [
                '🚨 URGENTE: Contacto inmediato (24h)',
                '👨‍💼 Asignar account manager dedicado',
                '💰 Aplicar incentivo de alto valor',
                '🔍 Investigar causa raíz'
            ]
        else:
            actions = [
                '📞 Contacto proactivo (48-72h)',
                '📧 Campaña de reactivación',
                '💬 Encuesta de satisfacción',
                '🎯 Ofertas personalizadas'
            ]
        
        return {
            'customer_id': customer.get('Customer_ID', 'N/A'),
            'risk_level': customer.get('Risk_Level', 'BAJO'),
            'risk_score': int(customer.get('Risk_Score', 0)),
            'geography': customer.get('Geography', 'N/A'),
            'age': int(customer.get('Age', 0)),
            'gender': customer.get('Gender', 'N/A'),
            'products': int(customer.get('NumOfProducts', 0)),
            'monthly_logins': int(customer.get('Monthly_Logins', 0)),
            'days_inactive': int(customer.get('Days_Since_Last_Transaction', 0)),
            'satisfaction': int(customer.get('Satisfaction Score', 0)),
            'has_complained': bool(customer.get('Complain', 0)),
            'is_active': bool(customer.get('IsActiveMember', 1)),
            'risk_factors': risk_factors,
            'recommended_actions': actions,
            'alert_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def send_email_alert(self, alerts: List[Dict], recipients: List[str] = None):
        """
        Envía email con alertas de clientes en riesgo
        
        Args:
            alerts: Lista de alertas de clientes
            recipients: Lista de emails destinatarios
        """
        if not recipients:
            recipients = self.email_config['default_recipients']
        
        if not recipients or not recipients[0]:
            logger.warning("No hay destinatarios configurados")
            return False
        
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'🚨 Alerta de Churn - {len(alerts)} Clientes en Riesgo'
            msg['From'] = self.email_config['sender_email']
            msg['To'] = ', '.join(recipients)
            
            # Crear HTML del email
            html = self._create_email_html(alerts)
            
            # Adjuntar HTML
            html_part = MIMEText(html, 'html')
            msg.attach(html_part)
            
            # Crear CSV adjunto
            csv_data = self._create_csv_from_alerts(alerts)
            csv_attachment = MIMEApplication(csv_data)
            csv_attachment.add_header('Content-Disposition', 'attachment', 
                                    filename=f'alertas_churn_{datetime.now().strftime("%Y%m%d")}.csv')
            msg.attach(csv_attachment)
            
            # Enviar email
            with smtplib.SMTP(self.email_config['smtp_server'], 
                            self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['sender_email'], 
                           self.email_config['sender_password'])
                server.send_message(msg)
            
            logger.info(f"✅ Email enviado a {len(recipients)} destinatarios")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al enviar email: {e}")
            return False
    
    def _create_email_html(self, alerts: List[Dict]) -> str:
        """Crea HTML formateado para el email"""
        
        # Contar por nivel de riesgo
        critical = sum(1 for a in alerts if a['risk_level'] == 'CRÍTICO')
        high = sum(1 for a in alerts if a['risk_level'] == 'ALTO')
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .metric {{ text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
                .metric-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
                .metric-label {{ color: #666; font-size: 0.9em; }}
                .alert {{ border-left: 4px solid; padding: 15px; margin: 15px 0; background: #f8f9fa; border-radius: 5px; }}
                .critical {{ border-left-color: #ff4b4b; background: #fff5f5; }}
                .high {{ border-left-color: #ffa500; background: #fff9f0; }}
                .customer-info {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 10px 0; }}
                .info-item {{ color: #555; font-size: 0.9em; }}
                .actions {{ background: #e3f2fd; padding: 10px; border-radius: 5px; margin-top: 10px; }}
                .action-item {{ color: #1976d2; margin: 5px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 0.85em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Alerta de Churn - Acción Requerida</h1>
                    <p>Sistema de Predicción de Churn FinTech</p>
                </div>
                
                <div class="summary">
                    <div class="metric">
                        <div class="metric-value" style="color: #ff4b4b;">{critical}</div>
                        <div class="metric-label">Clientes CRÍTICOS</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" style="color: #ffa500;">{high}</div>
                        <div class="metric-label">Clientes ALTO Riesgo</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{len(alerts)}</div>
                        <div class="metric-label">Total Alertas</div>
                    </div>
                </div>
                
                <h2>👥 Clientes que Requieren Atención Inmediata</h2>
        """
        
        # Top 10 clientes
        for alert in alerts[:10]:
            risk_class = 'critical' if alert['risk_level'] == 'CRÍTICO' else 'high'
            
            html += f"""
                <div class="alert {risk_class}">
                    <h3>🆔 {alert['customer_id']} - Riesgo {alert['risk_level']} ({alert['risk_score']}%)</h3>
                    
                    <div class="customer-info">
                        <div class="info-item">📍 <strong>Ubicación:</strong> {alert['geography']}</div>
                        <div class="info-item">👤 <strong>Edad:</strong> {alert['age']} años</div>
                        <div class="info-item">💳 <strong>Productos:</strong> {alert['products']}</div>
                        <div class="info-item">📱 <strong>Logins/mes:</strong> {alert['monthly_logins']}</div>
                        <div class="info-item">⏱️ <strong>Días inactivo:</strong> {alert['days_inactive']}</div>
                        <div class="info-item">😊 <strong>Satisfacción:</strong> {alert['satisfaction']}/5</div>
                    </div>
                    
                    <p><strong>⚠️ Factores de Riesgo:</strong></p>
                    <ul>
                        {''.join([f'<li>{factor}</li>' for factor in alert['risk_factors']])}
                    </ul>
                    
                    <div class="actions">
                        <p><strong>🎯 Acciones Recomendadas:</strong></p>
                        {''.join([f'<div class="action-item">{action}</div>' for action in alert['recommended_actions']])}
                    </div>
                </div>
            """
        
        if len(alerts) > 10:
            html += f"""
                <div class="alert" style="border-left-color: #2196F3; background: #e3f2fd;">
                    <p><strong>ℹ️ Hay {len(alerts) - 10} clientes adicionales en riesgo.</strong></p>
                    <p>Consulta el archivo CSV adjunto para la lista completa.</p>
                </div>
            """
        
        html += f"""
                <div class="footer">
                    <p>📅 Alerta generada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>📊 Sistema de Predicción de Churn | FinTech Analytics</p>
                    <p>💡 Para más detalles, accede al dashboard: <a href="http://localhost:8501">Dashboard</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_csv_from_alerts(self, alerts: List[Dict]) -> bytes:
        """Crea CSV con todas las alertas"""
        df = pd.DataFrame(alerts)
        
        # Seleccionar columnas relevantes
        columns = ['customer_id', 'risk_level', 'risk_score', 'geography', 'age', 
                  'products', 'monthly_logins', 'days_inactive', 'satisfaction',
                  'has_complained', 'is_active', 'alert_date']
        
        df_export = df[columns].copy()
        df_export.columns = ['ID_Cliente', 'Nivel_Riesgo', 'Score_Riesgo', 'País', 'Edad',
                            'Productos', 'Logins_Mes', 'Días_Inactivo', 'Satisfacción',
                            'Tiene_Quejas', 'Activo', 'Fecha_Alerta']
        
        return df_export.to_csv(index=False).encode('utf-8')
    
    def send_slack_notification(self, alerts: List[Dict]):
        """
        Envía notificación a Slack
        
        Args:
            alerts: Lista de alertas
        """
        if not self.slack_webhook:
            logger.warning("Slack webhook no configurado")
            return False
        
        try:
            critical = sum(1 for a in alerts if a['risk_level'] == 'CRÍTICO')
            high = sum(1 for a in alerts if a['risk_level'] == 'ALTO')
            
            # Crear mensaje estructurado
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 Alerta de Churn - Acción Requerida"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*🔴 Críticos:*\n{critical}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*🟠 Alto Riesgo:*\n{high}"
                        }
                    ]
                },
                {
                    "type": "divider"
                }
            ]
            
            # Top 5 clientes
            for alert in alerts[:5]:
                emoji = "🔴" if alert['risk_level'] == 'CRÍTICO' else "🟠"
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{emoji} *{alert['customer_id']}* - {alert['risk_level']}\n"
                               f"📍 {alert['geography']} | 👤 {alert['age']} años | 📱 {alert['monthly_logins']} logins/mes"
                    }
                })
            
            if len(alerts) > 5:
                blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"_Y {len(alerts) - 5} clientes más en riesgo_"
                        }
                    ]
                })
            
            # Enviar a Slack
            response = requests.post(
                self.slack_webhook,
                json={"blocks": blocks},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info("✅ Notificación enviada a Slack")
                return True
            else:
                logger.error(f"❌ Error al enviar a Slack: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error en Slack notification: {e}")
            return False
    
    def send_webhook(self, alerts: List[Dict]):
        """
        Envía webhook a sistema CRM externo
        
        Args:
            alerts: Lista de alertas
        """
        if not self.webhook_url:
            logger.warning("Webhook URL no configurada")
            return False
        
        try:
            payload = {
                'event': 'churn_alert',
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_alerts': len(alerts),
                    'critical': sum(1 for a in alerts if a['risk_level'] == 'CRÍTICO'),
                    'high': sum(1 for a in alerts if a['risk_level'] == 'ALTO')
                },
                'customers': alerts
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Webhook enviado exitosamente")
                return True
            else:
                logger.error(f"❌ Error en webhook: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error al enviar webhook: {e}")
            return False
    
    def generate_daily_report(self, df: pd.DataFrame, output_dir='reports'):
        """
        Genera reporte diario de clientes en riesgo
        
        Args:
            df: DataFrame con datos de clientes
            output_dir: Directorio para guardar reportes
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Identificar clientes en riesgo
        high_risk = self.identify_high_risk_customers(df)
        
        if len(high_risk) == 0:
            logger.info("✅ No hay clientes en riesgo alto")
            return None
        
        # Crear alertas
        alerts = [self.create_customer_alert(row) for _, row in high_risk.iterrows()]
        
        # Guardar CSV
        filename = f"reporte_churn_{datetime.now().strftime('%Y%m%d')}.csv"
        filepath = os.path.join(output_dir, filename)
        
        df_report = pd.DataFrame(alerts)
        df_report.to_csv(filepath, index=False)
        
        logger.info(f"✅ Reporte guardado: {filepath}")
        
        return filepath, alerts

# Función principal para ejecutar desde línea de comandos
def run_daily_alerts():
    """Ejecuta proceso diario de alertas"""
    print("="*60)
    print("SISTEMA DE ALERTAS DE CHURN - Ejecución Diaria")
    print("="*60)
    
    # Cargar datos
    try:
        df = pd.read_csv('cleaned_data.csv')
        print(f"✓ Datos cargados: {len(df)} clientes")
    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")
        return
    
    # Inicializar sistema de notificaciones
    notif_system = NotificationSystem()
    
    # Identificar clientes en riesgo
    high_risk = notif_system.identify_high_risk_customers(df)
    print(f"✓ Clientes en riesgo: {len(high_risk)}")
    
    if len(high_risk) == 0:
        print("✅ No hay clientes en riesgo alto")
        return
    
    # Crear alertas
    alerts = [notif_system.create_customer_alert(row) for _, row in high_risk.iterrows()]
    
    # Generar reporte
    filepath, _ = notif_system.generate_daily_report(df)
    print(f"✓ Reporte generado: {filepath}")
    
    # Enviar notificaciones
    print("\nEnviando notificaciones...")
    
    # Email
    if notif_system.email_config['sender_email']:
        notif_system.send_email_alert(alerts[:20])  # Top 20
        print("✓ Email enviado")
    
    # Slack
    if notif_system.slack_webhook:
        notif_system.send_slack_notification(alerts[:10])  # Top 10
        print("✓ Notificación Slack enviada")
    
    # Webhook
    if notif_system.webhook_url:
        notif_system.send_webhook(alerts)
        print("✓ Webhook enviado")
    
    print("\n" + "="*60)
    print("✅ PROCESO COMPLETADO")
    print("="*60)

if __name__ == "__main__":
    run_daily_alerts()
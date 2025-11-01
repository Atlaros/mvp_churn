"""
Sistema de Internacionalización (i18n)
Soporte multi-idioma para el dashboard
Idiomas: Español, Inglés, Portugués
Autor: Sistema UX Mejorado
"""

import json
import os
from typing import Dict, Optional
import streamlit as st
from pathlib import Path


class I18n:
    """Gestor de internacionalización"""
    
    def __init__(self, default_language: str = 'es'):
        """
        Inicializa el sistema i18n
        
        Args:
            default_language: Idioma por defecto ('es', 'en', 'pt')
        """
        self.default_language = default_language
        self.current_language = default_language
        self.translations = {}
        self._load_translations()
    
    def _load_translations(self):
        """Carga traducciones desde archivos o define inline"""
        self.translations = {
            'es': self._get_spanish_translations(),
            'en': self._get_english_translations(),
            'pt': self._get_portuguese_translations()
        }
    
    def _get_spanish_translations(self) -> Dict:
        """Traducciones en español"""
        return {
            # Navegación
            'nav': {
                'title': 'Sistema de Predicción de Churn',
                'dashboard': '📊 Dashboard Ejecutivo',
                'analysis': '👥 Análisis de Clientes',
                'prediction': '🤖 Predicción Individual',
                'segments': '📈 Análisis de Segmentos',
                'alerts': '⚡ Alertas Tempranas',
                'recommendations': '💡 Recomendaciones',
                'reports': '📄 Reportes',
                'settings': '⚙️ Configuración'
            },
            
            # Dashboard
            'dashboard': {
                'title': 'Panel de Control Ejecutivo',
                'subtitle': 'Métricas clave de retención de clientes',
                'churn_rate': 'Tasa de Churn',
                'total_customers': 'Clientes Totales',
                'high_risk': 'Alto Riesgo',
                'critical_risk': 'Riesgo Crítico',
                'revenue_at_risk': 'Revenue en Riesgo',
                'retention_rate': 'Tasa de Retención',
                'avg_lifetime_value': 'LTV Promedio',
                'churn_trend': 'Tendencia de Churn',
                'risk_distribution': 'Distribución por Riesgo',
                'geographic_analysis': 'Análisis Geográfico',
                'last_update': 'Última actualización'
            },
            
            # Filtros
            'filters': {
                'title': 'Filtros Avanzados',
                'quick_filters': 'Filtros Rápidos',
                'age': 'Edad',
                'geography': 'País',
                'gender': 'Género',
                'credit_score': 'Score de Crédito',
                'balance': 'Balance',
                'products': 'Número de Productos',
                'active_members': 'Solo Miembros Activos',
                'with_complaints': 'Con Quejas',
                'transactions': 'Transacciones Mensuales',
                'days_inactive': 'Días Inactivo',
                'risk_level': 'Nivel de Riesgo',
                'clear': 'Limpiar Filtros',
                'apply': 'Aplicar',
                'showing': 'Mostrando',
                'of': 'de',
                'records': 'registros'
            },
            
            # Predicción
            'prediction': {
                'title': 'Predicción Individual de Churn',
                'subtitle': 'Predice el riesgo de abandono de un cliente específico',
                'customer_info': 'Información del Cliente',
                'customer_id': 'ID de Cliente',
                'predict_button': 'PREDECIR RIESGO DE CHURN',
                'results': 'Resultados de la Predicción',
                'probability': 'Probabilidad de Churn',
                'risk_level': 'Nivel de Riesgo',
                'confidence': 'Confianza',
                'risk_factors': 'Factores de Riesgo',
                'recommendations': 'Acciones Recomendadas',
                'low': 'BAJO',
                'medium': 'MEDIO',
                'high': 'ALTO',
                'critical': 'CRÍTICO'
            },
            
            # Alertas
            'alerts': {
                'title': 'Sistema de Alertas Tempranas',
                'subtitle': 'Clientes que requieren atención inmediata',
                'priority': 'Prioridad',
                'all': 'Todas',
                'critical': 'Crítica',
                'high': 'Alta',
                'medium': 'Media',
                'customer': 'Cliente',
                'risk': 'Riesgo',
                'factors': 'Factores',
                'action': 'Acción',
                'export': 'Exportar Lista',
                'no_alerts': 'No hay alertas en este momento',
                'total_alerts': 'Total de Alertas'
            },
            
            # Segmentos
            'segments': {
                'title': 'Análisis de Segmentos',
                'subtitle': 'Identifica grupos de clientes con características similares',
                'predefined': 'Segmentos Predefinidos',
                'custom': 'Segmento Personalizado',
                'create_segment': 'Crear Segmento',
                'segment_name': 'Nombre del Segmento',
                'criteria': 'Criterios',
                'size': 'Tamaño',
                'avg_churn': 'Churn Promedio',
                'characteristics': 'Características Principales'
            },
            
            # Reportes
            'reports': {
                'title': 'Generación de Reportes',
                'subtitle': 'Exporta reportes profesionales en PDF',
                'executive_summary': 'Resumen Ejecutivo',
                'customer_list': 'Lista de Clientes',
                'trend_analysis': 'Análisis de Tendencias',
                'custom_report': 'Reporte Personalizado',
                'generate': 'Generar Reporte',
                'download': 'Descargar PDF',
                'report_type': 'Tipo de Reporte',
                'date_range': 'Rango de Fechas',
                'include_charts': 'Incluir Gráficos',
                'include_recommendations': 'Incluir Recomendaciones'
            },
            
            # Mensajes
            'messages': {
                'loading': 'Cargando datos...',
                'processing': 'Procesando...',
                'success': 'Operación exitosa',
                'error': 'Ha ocurrido un error',
                'no_data': 'No hay datos disponibles',
                'model_not_found': 'Modelo no encontrado. Entrena los modelos primero.',
                'invalid_input': 'Entrada inválida',
                'export_success': 'Reporte exportado exitosamente',
                'filter_applied': 'Filtros aplicados',
                'prediction_complete': 'Predicción completada'
            },
            
            # Recomendaciones
            'recommendations': {
                'title': 'Estrategias de Retención',
                'subtitle': 'Acciones recomendadas para reducir el churn',
                'immediate': 'Acción Inmediata (0-7 días)',
                'short_term': 'Corto Plazo (1-4 semanas)',
                'medium_term': 'Mediano Plazo (1-3 meses)',
                'long_term': 'Largo Plazo (3-12 meses)',
                'impact': 'Impacto Esperado',
                'cost': 'Costo Estimado',
                'roi': 'ROI Proyectado'
            },
            
            # Común
            'common': {
                'yes': 'Sí',
                'no': 'No',
                'all': 'Todos',
                'none': 'Ninguno',
                'select': 'Seleccionar',
                'search': 'Buscar',
                'export': 'Exportar',
                'import': 'Importar',
                'save': 'Guardar',
                'cancel': 'Cancelar',
                'delete': 'Eliminar',
                'edit': 'Editar',
                'view': 'Ver',
                'close': 'Cerrar',
                'refresh': 'Actualizar',
                'help': 'Ayuda',
                'about': 'Acerca de',
                'settings': 'Configuración',
                'language': 'Idioma',
                'confirm': 'Confirmar',
                'back': 'Volver',
                'next': 'Siguiente',
                'previous': 'Anterior',
                'finish': 'Finalizar',
                'continue': 'Continuar',
                'retry': 'Reintentar',
                'download': 'Descargar',
                'upload': 'Cargar',
                'loading': 'Cargando...',
                'processing': 'Procesando...',
                'please_wait': 'Por favor espere...',
                'actions': 'Acciones'
            },
            
            # Validaciones
            'validation': {
                'required_field': 'Este campo es obligatorio',
                'invalid_email': 'Correo electrónico inválido',
                'invalid_number': 'Número inválido',
                'invalid_date': 'Fecha inválida',
                'invalid_range': 'Valor fuera de rango',
                'min_value': 'Valor mínimo: {min}',
                'max_value': 'Valor máximo: {max}',
                'min_length': 'Longitud mínima: {min} caracteres',
                'max_length': 'Longitud máxima: {max} caracteres',
                'must_be_positive': 'Debe ser un número positivo',
                'must_be_integer': 'Debe ser un número entero',
                'invalid_format': 'Formato inválido',
                'passwords_not_match': 'Las contraseñas no coinciden',
                'weak_password': 'Contraseña débil. Use al menos 8 caracteres',
                'file_too_large': 'Archivo demasiado grande. Máximo: {max}MB',
                'invalid_file_type': 'Tipo de archivo no permitido',
                'no_data_selected': 'No hay datos seleccionados',
                'select_at_least_one': 'Seleccione al menos un elemento'
            },
            
            # Confirmaciones
            'confirmations': {
                'delete_title': '¿Eliminar elemento?',
                'delete_message': '¿Está seguro que desea eliminar este elemento? Esta acción no se puede deshacer.',
                'delete_multiple': '¿Eliminar {count} elementos?',
                'delete_multiple_message': 'Esta acción eliminará {count} elementos permanentemente.',
                'save_changes': '¿Guardar cambios?',
                'save_changes_message': 'Tiene cambios sin guardar. ¿Desea guardarlos?',
                'discard_changes': '¿Descartar cambios?',
                'discard_changes_message': 'Los cambios no guardados se perderán.',
                'export_data': '¿Exportar datos?',
                'export_data_message': 'Se exportarán {count} registros a {format}.',
                'clear_filters': '¿Limpiar todos los filtros?',
                'clear_filters_message': 'Se restaurarán los valores por defecto.',
                'reset_settings': '¿Restaurar configuración?',
                'reset_settings_message': 'Se perderán todas las configuraciones personalizadas.',
                'send_notification': '¿Enviar notificación?',
                'send_notification_message': 'Se enviará una notificación a {count} usuarios.',
                'execute_action': '¿Ejecutar acción?',
                'execute_action_message': 'Esta acción afectará a {count} clientes.'
            },
            
            # Tooltips y ayuda contextual
            'tooltips': {
                'churn_rate': 'Porcentaje de clientes que abandonaron el servicio en el período',
                'credit_score': 'Puntuación crediticia del cliente (300-850)',
                'balance': 'Saldo actual de la cuenta del cliente',
                'tenure': 'Número de meses que el cliente ha estado con nosotros',
                'products_number': 'Cantidad de productos contratados por el cliente',
                'active_member': 'Cliente que ha realizado transacciones recientemente',
                'estimated_salary': 'Salario estimado basado en perfil del cliente',
                'complaint': 'Cliente ha registrado quejas o reclamos',
                'satisfaction_score': 'Nivel de satisfacción del cliente (1-5)',
                'point_earned': 'Puntos acumulados en programa de fidelización',
                'risk_score': 'Probabilidad calculada de abandono (0-100%)',
                'ltv': 'Valor de vida del cliente (Lifetime Value)',
                'revenue_at_risk': 'Ingresos potenciales que podrían perderse',
                'retention_rate': 'Porcentaje de clientes retenidos en el período',
                'filter_age': 'Filtre clientes por rango de edad',
                'filter_geography': 'Filtre por ubicación geográfica',
                'filter_gender': 'Filtre por género del cliente',
                'export_format': 'Seleccione el formato de exportación (CSV, Excel, PDF)',
                'refresh_data': 'Actualice los datos más recientes',
                'prediction_confidence': 'Nivel de confianza del modelo predictivo',
                'risk_factors': 'Factores que contribuyen al riesgo de churn'
            },
            
            # Mensajes de éxito específicos
            'success': {
                'data_loaded': '✅ Datos cargados exitosamente',
                'data_exported': '✅ Datos exportados correctamente',
                'data_imported': '✅ Datos importados correctamente',
                'model_trained': '✅ Modelo entrenado exitosamente',
                'prediction_completed': '✅ Predicción completada',
                'report_generated': '✅ Reporte generado exitosamente',
                'settings_saved': '✅ Configuración guardada',
                'filters_applied': '✅ Filtros aplicados',
                'email_sent': '✅ Correo enviado correctamente',
                'notification_sent': '✅ Notificación enviada',
                'customer_updated': '✅ Cliente actualizado',
                'segment_created': '✅ Segmento creado exitosamente',
                'alert_configured': '✅ Alerta configurada',
                'changes_saved': '✅ Cambios guardados correctamente',
                'action_completed': '✅ Acción completada exitosamente',
                'file_uploaded': '✅ Archivo cargado correctamente'
            },
            
            # Mensajes de error específicos
            'errors': {
                'generic': '❌ Ha ocurrido un error inesperado',
                'no_data': '⚠️ No hay datos disponibles',
                'data_load_failed': '❌ Error al cargar los datos',
                'model_not_found': '⚠️ Modelo no encontrado. Por favor, entrene el modelo primero',
                'prediction_failed': '❌ Error en la predicción',
                'invalid_input': '⚠️ Entrada inválida. Verifique los datos',
                'export_failed': '❌ Error al exportar datos',
                'import_failed': '❌ Error al importar datos',
                'file_not_found': '❌ Archivo no encontrado',
                'permission_denied': '🔒 Acceso denegado',
                'network_error': '🌐 Error de conexión',
                'timeout': '⏱️ Tiempo de espera agotado',
                'server_error': '🔧 Error del servidor',
                'invalid_credentials': '🔑 Credenciales inválidas',
                'session_expired': '⏰ Sesión expirada. Por favor, inicie sesión nuevamente',
                'insufficient_data': '⚠️ Datos insuficientes para realizar la operación',
                'duplicate_entry': '⚠️ Entrada duplicada',
                'database_error': '💾 Error de base de datos',
                'email_failed': '📧 Error al enviar correo',
                'notification_failed': '🔔 Error al enviar notificación'
            },
            
            # Mensajes de advertencia
            'warnings': {
                'unsaved_changes': '⚠️ Tiene cambios sin guardar',
                'low_confidence': '⚠️ Predicción con baja confianza',
                'outdated_data': '⚠️ Los datos podrían estar desactualizados',
                'high_risk_detected': '🚨 Alto riesgo de churn detectado',
                'critical_alert': '🚨 Alerta crítica: Requiere atención inmediata',
                'missing_data': '⚠️ Algunos campos están vacíos',
                'approaching_limit': '⚠️ Acercándose al límite',
                'deprecated_feature': '⚠️ Esta función quedará obsoleta pronto',
                'slow_performance': '⚠️ Rendimiento lento detectado',
                'large_dataset': '⚠️ Conjunto de datos grande. Puede tardar unos minutos'
            },
            
            # Mensajes informativos
            'info': {
                'loading_data': 'ℹ️ Cargando datos...',
                'processing_request': 'ℹ️ Procesando solicitud...',
                'calculating': 'ℹ️ Calculando...',
                'training_model': 'ℹ️ Entrenando modelo...',
                'generating_report': 'ℹ️ Generando reporte...',
                'sending_email': 'ℹ️ Enviando correo...',
                'optimizing': 'ℹ️ Optimizando resultados...',
                'analyzing': 'ℹ️ Analizando datos...',
                'no_results': 'ℹ️ No se encontraron resultados',
                'empty_state': 'ℹ️ No hay elementos para mostrar',
                'first_time': '👋 ¡Bienvenido! Parece que es su primera vez aquí',
                'tip': '💡 Consejo: {tip}',
                'beta_feature': '🧪 Esta es una función en versión beta',
                'new_feature': '✨ Nueva función disponible'
            },
            
            # Tutorial/Onboarding
            'onboarding': {
                'welcome_title': '¡Bienvenido al Sistema de Predicción de Churn!',
                'welcome_message': 'Le guiaremos a través de las principales funcionalidades',
                'step1_title': 'Dashboard Ejecutivo',
                'step1_desc': 'Visualice métricas clave y tendencias de churn en tiempo real',
                'step2_title': 'Análisis de Clientes',
                'step2_desc': 'Explore el comportamiento de sus clientes con filtros avanzados',
                'step3_title': 'Predicción Individual',
                'step3_desc': 'Prediga el riesgo de abandono para clientes específicos',
                'step4_title': 'Alertas Tempranas',
                'step4_desc': 'Reciba notificaciones de clientes en riesgo crítico',
                'step5_title': 'Recomendaciones',
                'step5_desc': 'Estrategias personalizadas para retener clientes',
                'skip_tour': 'Omitir tutorial',
                'next_step': 'Siguiente',
                'previous_step': 'Anterior',
                'finish_tour': 'Finalizar',
                'get_started': 'Comenzar'
            },
            
            # Estados de carga
            'loading_states': {
                'initializing': 'Inicializando aplicación...',
                'loading_models': 'Cargando modelos predictivos...',
                'loading_data': 'Cargando datos de clientes...',
                'applying_filters': 'Aplicando filtros...',
                'generating_charts': 'Generando gráficos...',
                'calculating_metrics': 'Calculando métricas...',
                'preparing_export': 'Preparando exportación...',
                'uploading': 'Cargando archivo...',
                'saving': 'Guardando cambios...',
                'please_wait': 'Por favor espere, esto puede tomar unos momentos...'
            },
            
            # Acciones de usuario
            'actions': {
                'click_to_view': 'Clic para ver detalles',
                'click_to_edit': 'Clic para editar',
                'click_to_delete': 'Clic para eliminar',
                'drag_to_reorder': 'Arrastre para reordenar',
                'double_click': 'Doble clic para abrir',
                'right_click': 'Clic derecho para opciones',
                'hover_for_details': 'Pase el cursor para más detalles',
                'select_to_compare': 'Seleccione para comparar',
                'scroll_for_more': 'Desplace para ver más'
            },
            
            # Feedback del sistema
            'system_feedback': {
                'calculating_progress': 'Progreso: {percent}%',
                'items_processed': '{current} de {total} procesados',
                'estimated_time': 'Tiempo estimado: {time}',
                'completed': 'Completado',
                'queued': 'En cola',
                'in_progress': 'En progreso',
                'paused': 'Pausado',
                'cancelled': 'Cancelado',
                'failed': 'Fallido',
                'ready': 'Listo',
                'waiting': 'Esperando'
            }
        }
    
    def _get_english_translations(self) -> Dict:
        """Traducciones en inglés"""
        return {
            'nav': {
                'title': 'Churn Prediction System',
                'dashboard': '📊 Executive Dashboard',
                'analysis': '👥 Customer Analysis',
                'prediction': '🤖 Individual Prediction',
                'segments': '📈 Segment Analysis',
                'alerts': '⚡ Early Alerts',
                'recommendations': '💡 Recommendations',
                'reports': '📄 Reports',
                'settings': '⚙️ Settings'
            },
            
            'dashboard': {
                'title': 'Executive Dashboard',
                'subtitle': 'Key customer retention metrics',
                'churn_rate': 'Churn Rate',
                'total_customers': 'Total Customers',
                'high_risk': 'High Risk',
                'critical_risk': 'Critical Risk',
                'revenue_at_risk': 'Revenue at Risk',
                'retention_rate': 'Retention Rate',
                'avg_lifetime_value': 'Avg Lifetime Value',
                'churn_trend': 'Churn Trend',
                'risk_distribution': 'Risk Distribution',
                'geographic_analysis': 'Geographic Analysis',
                'last_update': 'Last updated'
            },
            
            'filters': {
                'title': 'Advanced Filters',
                'quick_filters': 'Quick Filters',
                'age': 'Age',
                'geography': 'Country',
                'gender': 'Gender',
                'credit_score': 'Credit Score',
                'balance': 'Balance',
                'products': 'Number of Products',
                'active_members': 'Active Members Only',
                'with_complaints': 'With Complaints',
                'transactions': 'Monthly Transactions',
                'days_inactive': 'Days Inactive',
                'risk_level': 'Risk Level',
                'clear': 'Clear Filters',
                'apply': 'Apply',
                'showing': 'Showing',
                'of': 'of',
                'records': 'records'
            },
            
            'prediction': {
                'title': 'Individual Churn Prediction',
                'subtitle': 'Predict the abandonment risk of a specific customer',
                'customer_info': 'Customer Information',
                'customer_id': 'Customer ID',
                'predict_button': 'PREDICT CHURN RISK',
                'results': 'Prediction Results',
                'probability': 'Churn Probability',
                'risk_level': 'Risk Level',
                'confidence': 'Confidence',
                'risk_factors': 'Risk Factors',
                'recommendations': 'Recommended Actions',
                'low': 'LOW',
                'medium': 'MEDIUM',
                'high': 'HIGH',
                'critical': 'CRITICAL'
            },
            
            'alerts': {
                'title': 'Early Warning System',
                'subtitle': 'Customers requiring immediate attention',
                'priority': 'Priority',
                'all': 'All',
                'critical': 'Critical',
                'high': 'High',
                'medium': 'Medium',
                'customer': 'Customer',
                'risk': 'Risk',
                'factors': 'Factors',
                'action': 'Action',
                'export': 'Export List',
                'no_alerts': 'No alerts at this time',
                'total_alerts': 'Total Alerts'
            },
            
            'segments': {
                'title': 'Segment Analysis',
                'subtitle': 'Identify groups of customers with similar characteristics',
                'predefined': 'Predefined Segments',
                'custom': 'Custom Segment',
                'create_segment': 'Create Segment',
                'segment_name': 'Segment Name',
                'criteria': 'Criteria',
                'size': 'Size',
                'avg_churn': 'Average Churn',
                'characteristics': 'Main Characteristics'
            },
            
            'reports': {
                'title': 'Report Generation',
                'subtitle': 'Export professional PDF reports',
                'executive_summary': 'Executive Summary',
                'customer_list': 'Customer List',
                'trend_analysis': 'Trend Analysis',
                'custom_report': 'Custom Report',
                'generate': 'Generate Report',
                'download': 'Download PDF',
                'report_type': 'Report Type',
                'date_range': 'Date Range',
                'include_charts': 'Include Charts',
                'include_recommendations': 'Include Recommendations'
            },
            
            'messages': {
                'loading': 'Loading data...',
                'processing': 'Processing...',
                'success': 'Operation successful',
                'error': 'An error occurred',
                'no_data': 'No data available',
                'model_not_found': 'Model not found. Train models first.',
                'invalid_input': 'Invalid input',
                'export_success': 'Report exported successfully',
                'filter_applied': 'Filters applied',
                'prediction_complete': 'Prediction completed'
            },
            
            'recommendations': {
                'title': 'Retention Strategies',
                'subtitle': 'Recommended actions to reduce churn',
                'immediate': 'Immediate Action (0-7 days)',
                'short_term': 'Short Term (1-4 weeks)',
                'medium_term': 'Medium Term (1-3 months)',
                'long_term': 'Long Term (3-12 months)',
                'impact': 'Expected Impact',
                'cost': 'Estimated Cost',
                'roi': 'Projected ROI'
            },
            
            'common': {
                'yes': 'Yes',
                'no': 'No',
                'all': 'All',
                'none': 'None',
                'select': 'Select',
                'search': 'Search',
                'export': 'Export',
                'import': 'Import',
                'save': 'Save',
                'cancel': 'Cancel',
                'delete': 'Delete',
                'edit': 'Edit',
                'view': 'View',
                'close': 'Close',
                'refresh': 'Refresh',
                'help': 'Help',
                'about': 'About',
                'settings': 'Settings',
                'language': 'Language',
                'confirm': 'Confirm',
                'back': 'Back',
                'next': 'Next',
                'previous': 'Previous',
                'finish': 'Finish',
                'continue': 'Continue',
                'retry': 'Retry',
                'download': 'Download',
                'upload': 'Upload',
                'loading': 'Loading...',
                'processing': 'Processing...',
                'please_wait': 'Please wait...',
                'actions': 'Actions'
            },
            
            'validation': {
                'required_field': 'This field is required',
                'invalid_email': 'Invalid email address',
                'invalid_number': 'Invalid number',
                'invalid_date': 'Invalid date',
                'invalid_range': 'Value out of range',
                'min_value': 'Minimum value: {min}',
                'max_value': 'Maximum value: {max}',
                'min_length': 'Minimum length: {min} characters',
                'max_length': 'Maximum length: {max} characters',
                'must_be_positive': 'Must be a positive number',
                'must_be_integer': 'Must be an integer',
                'invalid_format': 'Invalid format',
                'passwords_not_match': 'Passwords do not match',
                'weak_password': 'Weak password. Use at least 8 characters',
                'file_too_large': 'File too large. Maximum: {max}MB',
                'invalid_file_type': 'File type not allowed',
                'no_data_selected': 'No data selected',
                'select_at_least_one': 'Select at least one item'
            },
            
            'confirmations': {
                'delete_title': 'Delete item?',
                'delete_message': 'Are you sure you want to delete this item? This action cannot be undone.',
                'delete_multiple': 'Delete {count} items?',
                'delete_multiple_message': 'This action will permanently delete {count} items.',
                'save_changes': 'Save changes?',
                'save_changes_message': 'You have unsaved changes. Do you want to save them?',
                'discard_changes': 'Discard changes?',
                'discard_changes_message': 'Unsaved changes will be lost.',
                'export_data': 'Export data?',
                'export_data_message': '{count} records will be exported to {format}.',
                'clear_filters': 'Clear all filters?',
                'clear_filters_message': 'Default values will be restored.',
                'reset_settings': 'Reset settings?',
                'reset_settings_message': 'All custom settings will be lost.',
                'send_notification': 'Send notification?',
                'send_notification_message': 'A notification will be sent to {count} users.',
                'execute_action': 'Execute action?',
                'execute_action_message': 'This action will affect {count} customers.'
            },
            
            'tooltips': {
                'churn_rate': 'Percentage of customers who left the service in the period',
                'credit_score': 'Customer credit score (300-850)',
                'balance': 'Current account balance',
                'tenure': 'Number of months the customer has been with us',
                'products_number': 'Number of products contracted by the customer',
                'active_member': 'Customer who has made recent transactions',
                'estimated_salary': 'Estimated salary based on customer profile',
                'complaint': 'Customer has registered complaints',
                'satisfaction_score': 'Customer satisfaction level (1-5)',
                'point_earned': 'Points accumulated in loyalty program',
                'risk_score': 'Calculated probability of churn (0-100%)',
                'ltv': 'Customer Lifetime Value',
                'revenue_at_risk': 'Potential revenue that could be lost',
                'retention_rate': 'Percentage of customers retained in the period',
                'filter_age': 'Filter customers by age range',
                'filter_geography': 'Filter by geographic location',
                'filter_gender': 'Filter by customer gender',
                'export_format': 'Select export format (CSV, Excel, PDF)',
                'refresh_data': 'Refresh with latest data',
                'prediction_confidence': 'Predictive model confidence level',
                'risk_factors': 'Factors contributing to churn risk'
            },
            
            'success': {
                'data_loaded': '✅ Data loaded successfully',
                'data_exported': '✅ Data exported successfully',
                'data_imported': '✅ Data imported successfully',
                'model_trained': '✅ Model trained successfully',
                'prediction_completed': '✅ Prediction completed',
                'report_generated': '✅ Report generated successfully',
                'settings_saved': '✅ Settings saved',
                'filters_applied': '✅ Filters applied',
                'email_sent': '✅ Email sent successfully',
                'notification_sent': '✅ Notification sent',
                'customer_updated': '✅ Customer updated',
                'segment_created': '✅ Segment created successfully',
                'alert_configured': '✅ Alert configured',
                'changes_saved': '✅ Changes saved successfully',
                'action_completed': '✅ Action completed successfully',
                'file_uploaded': '✅ File uploaded successfully'
            },
            
            'errors': {
                'generic': '❌ An unexpected error occurred',
                'no_data': '⚠️ No data available',
                'data_load_failed': '❌ Failed to load data',
                'model_not_found': '⚠️ Model not found. Please train the model first',
                'prediction_failed': '❌ Prediction failed',
                'invalid_input': '⚠️ Invalid input. Please verify the data',
                'export_failed': '❌ Failed to export data',
                'import_failed': '❌ Failed to import data',
                'file_not_found': '❌ File not found',
                'permission_denied': '🔒 Access denied',
                'network_error': '🌐 Connection error',
                'timeout': '⏱️ Request timeout',
                'server_error': '🔧 Server error',
                'invalid_credentials': '🔑 Invalid credentials',
                'session_expired': '⏰ Session expired. Please log in again',
                'insufficient_data': '⚠️ Insufficient data to perform operation',
                'duplicate_entry': '⚠️ Duplicate entry',
                'database_error': '💾 Database error',
                'email_failed': '📧 Failed to send email',
                'notification_failed': '🔔 Failed to send notification'
            },
            
            'warnings': {
                'unsaved_changes': '⚠️ You have unsaved changes',
                'low_confidence': '⚠️ Prediction with low confidence',
                'outdated_data': '⚠️ Data might be outdated',
                'high_risk_detected': '🚨 High churn risk detected',
                'critical_alert': '🚨 Critical alert: Requires immediate attention',
                'missing_data': '⚠️ Some fields are empty',
                'approaching_limit': '⚠️ Approaching limit',
                'deprecated_feature': '⚠️ This feature will be deprecated soon',
                'slow_performance': '⚠️ Slow performance detected',
                'large_dataset': '⚠️ Large dataset. May take a few minutes'
            },
            
            'info': {
                'loading_data': 'ℹ️ Loading data...',
                'processing_request': 'ℹ️ Processing request...',
                'calculating': 'ℹ️ Calculating...',
                'training_model': 'ℹ️ Training model...',
                'generating_report': 'ℹ️ Generating report...',
                'sending_email': 'ℹ️ Sending email...',
                'optimizing': 'ℹ️ Optimizing results...',
                'analyzing': 'ℹ️ Analyzing data...',
                'no_results': 'ℹ️ No results found',
                'empty_state': 'ℹ️ No items to display',
                'first_time': '👋 Welcome! Looks like it\'s your first time here',
                'tip': '💡 Tip: {tip}',
                'beta_feature': '🧪 This is a beta feature',
                'new_feature': '✨ New feature available'
            },
            
            'onboarding': {
                'welcome_title': 'Welcome to the Churn Prediction System!',
                'welcome_message': 'We will guide you through the main features',
                'step1_title': 'Executive Dashboard',
                'step1_desc': 'View key metrics and churn trends in real-time',
                'step2_title': 'Customer Analysis',
                'step2_desc': 'Explore customer behavior with advanced filters',
                'step3_title': 'Individual Prediction',
                'step3_desc': 'Predict abandonment risk for specific customers',
                'step4_title': 'Early Alerts',
                'step4_desc': 'Receive notifications of customers at critical risk',
                'step5_title': 'Recommendations',
                'step5_desc': 'Personalized strategies to retain customers',
                'skip_tour': 'Skip tour',
                'next_step': 'Next',
                'previous_step': 'Previous',
                'finish_tour': 'Finish',
                'get_started': 'Get started'
            },
            
            'loading_states': {
                'initializing': 'Initializing application...',
                'loading_models': 'Loading predictive models...',
                'loading_data': 'Loading customer data...',
                'applying_filters': 'Applying filters...',
                'generating_charts': 'Generating charts...',
                'calculating_metrics': 'Calculating metrics...',
                'preparing_export': 'Preparing export...',
                'uploading': 'Uploading file...',
                'saving': 'Saving changes...',
                'please_wait': 'Please wait, this may take a few moments...'
            },
            
            'actions': {
                'click_to_view': 'Click to view details',
                'click_to_edit': 'Click to edit',
                'click_to_delete': 'Click to delete',
                'drag_to_reorder': 'Drag to reorder',
                'double_click': 'Double-click to open',
                'right_click': 'Right-click for options',
                'hover_for_details': 'Hover for more details',
                'select_to_compare': 'Select to compare',
                'scroll_for_more': 'Scroll for more'
            },
            
            'system_feedback': {
                'calculating_progress': 'Progress: {percent}%',
                'items_processed': '{current} of {total} processed',
                'estimated_time': 'Estimated time: {time}',
                'completed': 'Completed',
                'queued': 'Queued',
                'in_progress': 'In progress',
                'paused': 'Paused',
                'cancelled': 'Cancelled',
                'failed': 'Failed',
                'ready': 'Ready',
                'waiting': 'Waiting'
            }
        }
    
    def _get_portuguese_translations(self) -> Dict:
        """Traducciones en portugués"""
        return {
            'nav': {
                'title': 'Sistema de Previsão de Churn',
                'dashboard': '📊 Dashboard Executivo',
                'analysis': '👥 Análise de Clientes',
                'prediction': '🤖 Previsão Individual',
                'segments': '📈 Análise de Segmentos',
                'alerts': '⚡ Alertas Antecipados',
                'recommendations': '💡 Recomendações',
                'reports': '📄 Relatórios',
                'settings': '⚙️ Configurações'
            },
            
            'dashboard': {
                'title': 'Painel de Controle Executivo',
                'subtitle': 'Métricas-chave de retenção de clientes',
                'churn_rate': 'Taxa de Churn',
                'total_customers': 'Total de Clientes',
                'high_risk': 'Alto Risco',
                'critical_risk': 'Risco Crítico',
                'revenue_at_risk': 'Receita em Risco',
                'retention_rate': 'Taxa de Retenção',
                'avg_lifetime_value': 'LTV Médio',
                'churn_trend': 'Tendência de Churn',
                'risk_distribution': 'Distribuição por Risco',
                'geographic_analysis': 'Análise Geográfica',
                'last_update': 'Última atualização'
            },
            
            'filters': {
                'title': 'Filtros Avançados',
                'quick_filters': 'Filtros Rápidos',
                'age': 'Idade',
                'geography': 'País',
                'gender': 'Gênero',
                'credit_score': 'Score de Crédito',
                'balance': 'Saldo',
                'products': 'Número de Produtos',
                'active_members': 'Apenas Membros Ativos',
                'with_complaints': 'Com Reclamações',
                'transactions': 'Transações Mensais',
                'days_inactive': 'Dias Inativo',
                'risk_level': 'Nível de Risco',
                'clear': 'Limpar Filtros',
                'apply': 'Aplicar',
                'showing': 'Mostrando',
                'of': 'de',
                'records': 'registros'
            },
            
            'prediction': {
                'title': 'Previsão Individual de Churn',
                'subtitle': 'Prevê o risco de abandono de um cliente específico',
                'customer_info': 'Informações do Cliente',
                'customer_id': 'ID do Cliente',
                'predict_button': 'PREVER RISCO DE CHURN',
                'results': 'Resultados da Previsão',
                'probability': 'Probabilidade de Churn',
                'risk_level': 'Nível de Risco',
                'confidence': 'Confiança',
                'risk_factors': 'Fatores de Risco',
                'recommendations': 'Ações Recomendadas',
                'low': 'BAIXO',
                'medium': 'MÉDIO',
                'high': 'ALTO',
                'critical': 'CRÍTICO'
            },
            
            'alerts': {
                'title': 'Sistema de Alertas Antecipados',
                'subtitle': 'Clientes que requerem atenção imediata',
                'priority': 'Prioridade',
                'all': 'Todos',
                'critical': 'Crítica',
                'high': 'Alta',
                'medium': 'Média',
                'customer': 'Cliente',
                'risk': 'Risco',
                'factors': 'Fatores',
                'action': 'Ação',
                'export': 'Exportar Lista',
                'no_alerts': 'Não há alertas no momento',
                'total_alerts': 'Total de Alertas'
            },
            
            'segments': {
                'title': 'Análise de Segmentos',
                'subtitle': 'Identifica grupos de clientes com características similares',
                'predefined': 'Segmentos Predefinidos',
                'custom': 'Segmento Personalizado',
                'create_segment': 'Criar Segmento',
                'segment_name': 'Nome do Segmento',
                'criteria': 'Critérios',
                'size': 'Tamanho',
                'avg_churn': 'Churn Médio',
                'characteristics': 'Características Principais'
            },
            
            'reports': {
                'title': 'Geração de Relatórios',
                'subtitle': 'Exporte relatórios profissionais em PDF',
                'executive_summary': 'Resumo Executivo',
                'customer_list': 'Lista de Clientes',
                'trend_analysis': 'Análise de Tendências',
                'custom_report': 'Relatório Personalizado',
                'generate': 'Gerar Relatório',
                'download': 'Baixar PDF',
                'report_type': 'Tipo de Relatório',
                'date_range': 'Intervalo de Datas',
                'include_charts': 'Incluir Gráficos',
                'include_recommendations': 'Incluir Recomendações'
            },
            
            'messages': {
                'loading': 'Carregando dados...',
                'processing': 'Processando...',
                'success': 'Operação bem-sucedida',
                'error': 'Ocorreu um erro',
                'no_data': 'Não há dados disponíveis',
                'model_not_found': 'Modelo não encontrado. Treine os modelos primeiro.',
                'invalid_input': 'Entrada inválida',
                'export_success': 'Relatório exportado com sucesso',
                'filter_applied': 'Filtros aplicados',
                'prediction_complete': 'Previsão concluída'
            },
            
            'recommendations': {
                'title': 'Estratégias de Retenção',
                'subtitle': 'Ações recomendadas para reduzir o churn',
                'immediate': 'Ação Imediata (0-7 dias)',
                'short_term': 'Curto Prazo (1-4 semanas)',
                'medium_term': 'Médio Prazo (1-3 meses)',
                'long_term': 'Longo Prazo (3-12 meses)',
                'impact': 'Impacto Esperado',
                'cost': 'Custo Estimado',
                'roi': 'ROI Projetado'
            },
            
            'common': {
                'yes': 'Sim',
                'no': 'Não',
                'all': 'Todos',
                'none': 'Nenhum',
                'select': 'Selecionar',
                'search': 'Buscar',
                'export': 'Exportar',
                'import': 'Importar',
                'save': 'Salvar',
                'cancel': 'Cancelar',
                'delete': 'Excluir',
                'edit': 'Editar',
                'view': 'Ver',
                'close': 'Fechar',
                'refresh': 'Atualizar',
                'help': 'Ajuda',
                'about': 'Sobre',
                'settings': 'Configurações',
                'language': 'Idioma',
                'confirm': 'Confirmar',
                'back': 'Voltar',
                'next': 'Próximo',
                'previous': 'Anterior',
                'finish': 'Finalizar',
                'continue': 'Continuar',
                'retry': 'Tentar novamente',
                'download': 'Baixar',
                'upload': 'Carregar',
                'loading': 'Carregando...',
                'processing': 'Processando...',
                'please_wait': 'Por favor aguarde...',
                'actions': 'Ações'
            },
            
            'validation': {
                'required_field': 'Este campo é obrigatório',
                'invalid_email': 'E-mail inválido',
                'invalid_number': 'Número inválido',
                'invalid_date': 'Data inválida',
                'invalid_range': 'Valor fora do intervalo',
                'min_value': 'Valor mínimo: {min}',
                'max_value': 'Valor máximo: {max}',
                'min_length': 'Comprimento mínimo: {min} caracteres',
                'max_length': 'Comprimento máximo: {max} caracteres',
                'must_be_positive': 'Deve ser um número positivo',
                'must_be_integer': 'Deve ser um número inteiro',
                'invalid_format': 'Formato inválido',
                'passwords_not_match': 'As senhas não coincidem',
                'weak_password': 'Senha fraca. Use pelo menos 8 caracteres',
                'file_too_large': 'Arquivo muito grande. Máximo: {max}MB',
                'invalid_file_type': 'Tipo de arquivo não permitido',
                'no_data_selected': 'Nenhum dado selecionado',
                'select_at_least_one': 'Selecione pelo menos um item'
            },
            
            'confirmations': {
                'delete_title': 'Excluir item?',
                'delete_message': 'Tem certeza de que deseja excluir este item? Esta ação não pode ser desfeita.',
                'delete_multiple': 'Excluir {count} itens?',
                'delete_multiple_message': 'Esta ação excluirá {count} itens permanentemente.',
                'save_changes': 'Salvar alterações?',
                'save_changes_message': 'Você tem alterações não salvas. Deseja salvá-las?',
                'discard_changes': 'Descartar alterações?',
                'discard_changes_message': 'As alterações não salvas serão perdidas.',
                'export_data': 'Exportar dados?',
                'export_data_message': '{count} registros serão exportados para {format}.',
                'clear_filters': 'Limpar todos os filtros?',
                'clear_filters_message': 'Os valores padrão serão restaurados.',
                'reset_settings': 'Restaurar configurações?',
                'reset_settings_message': 'Todas as configurações personalizadas serão perdidas.',
                'send_notification': 'Enviar notificação?',
                'send_notification_message': 'Uma notificação será enviada para {count} usuários.',
                'execute_action': 'Executar ação?',
                'execute_action_message': 'Esta ação afetará {count} clientes.'
            },
            
            'tooltips': {
                'churn_rate': 'Porcentagem de clientes que abandonaram o serviço no período',
                'credit_score': 'Pontuação de crédito do cliente (300-850)',
                'balance': 'Saldo atual da conta do cliente',
                'tenure': 'Número de meses que o cliente está conosco',
                'products_number': 'Quantidade de produtos contratados pelo cliente',
                'active_member': 'Cliente que realizou transações recentemente',
                'estimated_salary': 'Salário estimado baseado no perfil do cliente',
                'complaint': 'Cliente registrou reclamações',
                'satisfaction_score': 'Nível de satisfação do cliente (1-5)',
                'point_earned': 'Pontos acumulados no programa de fidelidade',
                'risk_score': 'Probabilidade calculada de abandono (0-100%)',
                'ltv': 'Valor de vida do cliente (Lifetime Value)',
                'revenue_at_risk': 'Receita potencial que pode ser perdida',
                'retention_rate': 'Porcentagem de clientes retidos no período',
                'filter_age': 'Filtre clientes por faixa etária',
                'filter_geography': 'Filtre por localização geográfica',
                'filter_gender': 'Filtre por gênero do cliente',
                'export_format': 'Selecione o formato de exportação (CSV, Excel, PDF)',
                'refresh_data': 'Atualize com os dados mais recentes',
                'prediction_confidence': 'Nível de confiança do modelo preditivo',
                'risk_factors': 'Fatores que contribuem para o risco de churn'
            },
            
            'success': {
                'data_loaded': '✅ Dados carregados com sucesso',
                'data_exported': '✅ Dados exportados com sucesso',
                'data_imported': '✅ Dados importados com sucesso',
                'model_trained': '✅ Modelo treinado com sucesso',
                'prediction_completed': '✅ Previsão concluída',
                'report_generated': '✅ Relatório gerado com sucesso',
                'settings_saved': '✅ Configurações salvas',
                'filters_applied': '✅ Filtros aplicados',
                'email_sent': '✅ E-mail enviado com sucesso',
                'notification_sent': '✅ Notificação enviada',
                'customer_updated': '✅ Cliente atualizado',
                'segment_created': '✅ Segmento criado com sucesso',
                'alert_configured': '✅ Alerta configurado',
                'changes_saved': '✅ Alterações salvas com sucesso',
                'action_completed': '✅ Ação concluída com sucesso',
                'file_uploaded': '✅ Arquivo carregado com sucesso'
            },
            
            'errors': {
                'generic': '❌ Ocorreu um erro inesperado',
                'no_data': '⚠️ Não há dados disponíveis',
                'data_load_failed': '❌ Falha ao carregar dados',
                'model_not_found': '⚠️ Modelo não encontrado. Por favor, treine o modelo primeiro',
                'prediction_failed': '❌ Falha na previsão',
                'invalid_input': '⚠️ Entrada inválida. Verifique os dados',
                'export_failed': '❌ Falha ao exportar dados',
                'import_failed': '❌ Falha ao importar dados',
                'file_not_found': '❌ Arquivo não encontrado',
                'permission_denied': '🔒 Acesso negado',
                'network_error': '🌐 Erro de conexão',
                'timeout': '⏱️ Tempo de espera esgotado',
                'server_error': '🔧 Erro do servidor',
                'invalid_credentials': '🔑 Credenciais inválidas',
                'session_expired': '⏰ Sessão expirada. Por favor, faça login novamente',
                'insufficient_data': '⚠️ Dados insuficientes para realizar a operação',
                'duplicate_entry': '⚠️ Entrada duplicada',
                'database_error': '💾 Erro de banco de dados',
                'email_failed': '📧 Falha ao enviar e-mail',
                'notification_failed': '🔔 Falha ao enviar notificação'
            },
            
            'warnings': {
                'unsaved_changes': '⚠️ Você tem alterações não salvas',
                'low_confidence': '⚠️ Previsão com baixa confiança',
                'outdated_data': '⚠️ Os dados podem estar desatualizados',
                'high_risk_detected': '🚨 Alto risco de churn detectado',
                'critical_alert': '🚨 Alerta crítico: Requer atenção imediata',
                'missing_data': '⚠️ Alguns campos estão vazios',
                'approaching_limit': '⚠️ Aproximando-se do limite',
                'deprecated_feature': '⚠️ Este recurso será descontinuado em breve',
                'slow_performance': '⚠️ Desempenho lento detectado',
                'large_dataset': '⚠️ Conjunto de dados grande. Pode levar alguns minutos'
            },
            
            'info': {
                'loading_data': 'ℹ️ Carregando dados...',
                'processing_request': 'ℹ️ Processando solicitação...',
                'calculating': 'ℹ️ Calculando...',
                'training_model': 'ℹ️ Treinando modelo...',
                'generating_report': 'ℹ️ Gerando relatório...',
                'sending_email': 'ℹ️ Enviando e-mail...',
                'optimizing': 'ℹ️ Otimizando resultados...',
                'analyzing': 'ℹ️ Analisando dados...',
                'no_results': 'ℹ️ Nenhum resultado encontrado',
                'empty_state': 'ℹ️ Nenhum item para exibir',
                'first_time': '👋 Bem-vindo! Parece que é sua primeira vez aqui',
                'tip': '💡 Dica: {tip}',
                'beta_feature': '🧪 Este é um recurso em versão beta',
                'new_feature': '✨ Novo recurso disponível'
            },
            
            'onboarding': {
                'welcome_title': 'Bem-vindo ao Sistema de Previsão de Churn!',
                'welcome_message': 'Vamos guiá-lo pelas principais funcionalidades',
                'step1_title': 'Dashboard Executivo',
                'step1_desc': 'Visualize métricas-chave e tendências de churn em tempo real',
                'step2_title': 'Análise de Clientes',
                'step2_desc': 'Explore o comportamento dos clientes com filtros avançados',
                'step3_title': 'Previsão Individual',
                'step3_desc': 'Preveja o risco de abandono para clientes específicos',
                'step4_title': 'Alertas Antecipados',
                'step4_desc': 'Receba notificações de clientes em risco crítico',
                'step5_title': 'Recomendações',
                'step5_desc': 'Estratégias personalizadas para reter clientes',
                'skip_tour': 'Pular tour',
                'next_step': 'Próximo',
                'previous_step': 'Anterior',
                'finish_tour': 'Finalizar',
                'get_started': 'Começar'
            },
            
            'loading_states': {
                'initializing': 'Inicializando aplicação...',
                'loading_models': 'Carregando modelos preditivos...',
                'loading_data': 'Carregando dados de clientes...',
                'applying_filters': 'Aplicando filtros...',
                'generating_charts': 'Gerando gráficos...',
                'calculating_metrics': 'Calculando métricas...',
                'preparing_export': 'Preparando exportação...',
                'uploading': 'Carregando arquivo...',
                'saving': 'Salvando alterações...',
                'please_wait': 'Por favor aguarde, isso pode levar alguns momentos...'
            },
            
            'actions': {
                'click_to_view': 'Clique para ver detalhes',
                'click_to_edit': 'Clique para editar',
                'click_to_delete': 'Clique para excluir',
                'drag_to_reorder': 'Arraste para reordenar',
                'double_click': 'Clique duplo para abrir',
                'right_click': 'Clique com botão direito para opções',
                'hover_for_details': 'Passe o cursor para mais detalhes',
                'select_to_compare': 'Selecione para comparar',
                'scroll_for_more': 'Role para ver mais'
            },
            
            'system_feedback': {
                'calculating_progress': 'Progresso: {percent}%',
                'items_processed': '{current} de {total} processados',
                'estimated_time': 'Tempo estimado: {time}',
                'completed': 'Concluído',
                'queued': 'Na fila',
                'in_progress': 'Em progresso',
                'paused': 'Pausado',
                'cancelled': 'Cancelado',
                'failed': 'Falhou',
                'ready': 'Pronto',
                'waiting': 'Aguardando'
            }
        }
    
    def set_language(self, language: str):
        """
        Cambia el idioma actual
        
        Args:
            language: Código de idioma ('es', 'en', 'pt')
        """
        if language in self.translations:
            self.current_language = language
        else:
            raise ValueError(f"Idioma no soportado: {language}")
    
    def t(self, key: str, default: str = None) -> str:
        """
        Obtiene traducción
        
        Args:
            key: Clave en formato 'section.key' (ej: 'dashboard.title')
            default: Valor por defecto si no se encuentra
            
        Returns:
            Texto traducido
        """
        parts = key.split('.')
        translation = self.translations.get(self.current_language, {})
        
        for part in parts:
            if isinstance(translation, dict):
                translation = translation.get(part)
            else:
                return default or key
        
        return translation or default or key
    
    def get_available_languages(self) -> Dict[str, str]:
        """Retorna idiomas disponibles"""
        return {
            'es': '🇪🇸 Español',
            'en': '🇬🇧 English',
            'pt': '🇧🇷 Português'
        }


# ============= INTEGRACIÓN CON STREAMLIT =============

def init_i18n_streamlit() -> I18n:
    """
    Inicializa i18n en Streamlit con selector de idioma
    
    Returns:
        Instancia de I18n configurada
    """
    # Inicializar en session state si no existe
    if 'i18n' not in st.session_state:
        st.session_state.i18n = I18n()
    
    if 'language' not in st.session_state:
        st.session_state.language = 'es'
    
    # Selector de idioma en sidebar
    with st.sidebar:
        st.markdown("---")
        
        languages = st.session_state.i18n.get_available_languages()
        
        selected = st.selectbox(
            "🌐 " + st.session_state.i18n.t('common.language', 'Idioma'),
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=list(languages.keys()).index(st.session_state.language)
        )
        
        if selected != st.session_state.language:
            st.session_state.language = selected
            st.session_state.i18n.set_language(selected)
            st.rerun()
    
    return st.session_state.i18n


# Alias para facilitar uso
_ = lambda key, default=None: st.session_state.i18n.t(key, default) if 'i18n' in st.session_state else default or key


# ============= EJEMPLO DE USO =============

if __name__ == "__main__":
    print("="*70)
    print("SISTEMA DE INTERNACIONALIZACIÓN (i18n)")
    print("="*70)
    
    # Crear instancia
    i18n = I18n(default_language='es')
    
    print(f"\n📚 Idiomas disponibles:")
    for code, name in i18n.get_available_languages().items():
        print(f"  {code}: {name}")
    
    # Probar traducciones en cada idioma
    for lang in ['es', 'en', 'pt']:
        i18n.set_language(lang)
        print(f"\n{i18n.get_available_languages()[lang]}:")
        print(f"  Dashboard: {i18n.t('nav.dashboard')}")
        print(f"  Churn Rate: {i18n.t('dashboard.churn_rate')}")
        print(f"  High Risk: {i18n.t('dashboard.high_risk')}")
        print(f"  Predict Button: {i18n.t('prediction.predict_button')}")
        print(f"  Loading: {i18n.t('messages.loading')}")
    
    print("\n" + "="*70)
    print("✅ SISTEMA I18N FUNCIONANDO CORRECTAMENTE")
    print("="*70)
    print("\nPara usar en Streamlit, importa:")
    print("  from i18n import init_i18n_streamlit")
    print("  i18n = init_i18n_streamlit()")
    print("  title = i18n.t('dashboard.title')")

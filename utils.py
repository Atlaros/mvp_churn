"""
Utilidades y funciones auxiliares para el Sistema de Predicción de Churn
Autor: Equipo Data Science
Fecha: Octubre 2025
"""

import pandas as pd
import numpy as np
import pickle
import json
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============= FUNCIONES DE CARGA DE DATOS =============

def load_dataset(filepath='cleaned_data.csv', sample_size=None):
    """
    Carga el dataset con opción de muestreo
    
    Args:
        filepath: Ruta al archivo CSV
        sample_size: Número de filas a cargar (None = todas)
    
    Returns:
        DataFrame de pandas
    """
    try:
        logger.info(f"Cargando datos desde {filepath}")
        df = pd.read_csv(filepath)
        
        if sample_size and sample_size < len(df):
            df = df.sample(n=sample_size, random_state=42)
            logger.info(f"Muestra de {sample_size} filas cargada")
        else:
            logger.info(f"Dataset completo cargado: {len(df)} filas")
        
        return df
    except Exception as e:
        logger.error(f"Error al cargar dataset: {e}")
        return None

def validate_data(df, required_columns):
    """
    Valida que el DataFrame tenga las columnas requeridas
    
    Args:
        df: DataFrame a validar
        required_columns: Lista de columnas requeridas
    
    Returns:
        Tuple (is_valid, missing_columns)
    """
    missing = [col for col in required_columns if col not in df.columns]
    
    if missing:
        logger.warning(f"Columnas faltantes: {missing}")
        return False, missing
    
    logger.info("Validación de datos exitosa")
    return True, []

# ============= FUNCIONES DE FEATURE ENGINEERING =============

def create_risk_score(df):
    """
    Calcula un score de riesgo basado en factores clave
    
    Args:
        df: DataFrame con datos de clientes
    
    Returns:
        DataFrame con columna 'Risk_Score' agregada
    """
    from column_schema import COLUMN_NAMES
    
    df_copy = df.copy()
    df_copy['Risk_Score'] = 0
    
    # Factores de riesgo
    if 'Complain' in df_copy.columns:
        df_copy.loc[df_copy['Complain'] == 1, 'Risk_Score'] += 40
    
    if 'IsActiveMember' in df_copy.columns:
        df_copy.loc[df_copy['IsActiveMember'] == 0, 'Risk_Score'] += 25
    
    if 'NumOfProducts' in df_copy.columns:
        df_copy.loc[df_copy['NumOfProducts'] >= 3, 'Risk_Score'] += 30
    
    if 'Days_Since_Last_Transaction' in df_copy.columns:
        df_copy.loc[df_copy['Days_Since_Last_Transaction'] > 25, 'Risk_Score'] += 20
    
    if 'Monthly_Logins' in df_copy.columns:
        df_copy.loc[df_copy['Monthly_Logins'] < 5, 'Risk_Score'] += 15
    
    satisfaction_col = COLUMN_NAMES['SATISFACTION_SCORE']
    if satisfaction_col in df_copy.columns:
        df_copy.loc[df_copy[satisfaction_col] <= 2, 'Risk_Score'] += 25
    
    logger.info("Risk Score calculado")
    return df_copy

def create_engagement_features(df):
    """
    Crea features de engagement
    
    Args:
        df: DataFrame con datos de clientes
    
    Returns:
        DataFrame con nuevas features
    """
    df_copy = df.copy()
    
    # Ratio logins/transacciones
    if 'Monthly_Logins' in df_copy.columns and 'Monthly_Transactions' in df_copy.columns:
        df_copy['Login_Transaction_Ratio'] = df_copy['Monthly_Logins'] / (df_copy['Monthly_Transactions'] + 1)
    
    # Balance por producto
    if 'Balance' in df_copy.columns and 'NumOfProducts' in df_copy.columns:
        df_copy['Balance_Per_Product'] = df_copy['Balance'] / (df_copy['NumOfProducts'] + 1)
    
    # Edad relativa de la cuenta
    if 'Tenure' in df_copy.columns and 'Age' in df_copy.columns:
        df_copy['Tenure_Age_Ratio'] = df_copy['Tenure'] / df_copy['Age']
    
    logger.info("Features de engagement creadas")
    return df_copy

# ============= FUNCIONES DE ANÁLISIS =============

def calculate_churn_metrics(df, target_col='Exited'):
    """
    Calcula métricas agregadas de churn
    
    Args:
        df: DataFrame con datos
        target_col: Nombre de la columna target
    
    Returns:
        Dictionary con métricas
    """
    metrics = {
        'total_customers': len(df),
        'churned_customers': df[target_col].sum(),
        'churn_rate': (df[target_col].sum() / len(df)) * 100,
        'retention_rate': ((len(df) - df[target_col].sum()) / len(df)) * 100
    }
    
    if 'IsActiveMember' in df.columns:
        active = df[df['IsActiveMember'] == 1]
        inactive = df[df['IsActiveMember'] == 0]
        
        metrics['active_members'] = len(active)
        metrics['inactive_members'] = len(inactive)
        metrics['active_churn_rate'] = (active[target_col].sum() / len(active)) * 100 if len(active) > 0 else 0
        metrics['inactive_churn_rate'] = (inactive[target_col].sum() / len(inactive)) * 100 if len(inactive) > 0 else 0
    
    return metrics

def segment_customers(df):
    """
    Segmenta clientes en grupos de riesgo
    
    Args:
        df: DataFrame con datos
    
    Returns:
        DataFrame con columna 'Segment' agregada
    """
    df_copy = df.copy()
    
    # Calcular risk score si no existe
    if 'Risk_Score' not in df_copy.columns:
        df_copy = create_risk_score(df_copy)
    
    # Segmentación
    conditions = [
        (df_copy['Risk_Score'] >= 70),
        (df_copy['Risk_Score'] >= 40) & (df_copy['Risk_Score'] < 70),
        (df_copy['Risk_Score'] < 40)
    ]
    
    choices = ['High Risk', 'Medium Risk', 'Low Risk']
    df_copy['Segment'] = np.select(conditions, choices, default='Unknown')
    
    logger.info("Clientes segmentados")
    return df_copy

def get_segment_summary(df):
    """
    Genera resumen por segmento
    
    Args:
        df: DataFrame con columna 'Segment'
    
    Returns:
        DataFrame con estadísticas por segmento
    """
    if 'Segment' not in df.columns:
        df = segment_customers(df)
    
    summary = df.groupby('Segment').agg({
        'Exited': ['count', 'sum', 'mean'],
        'Age': 'mean',
        'Balance': 'mean',
        'Monthly_Logins': 'mean',
        'Monthly_Transactions': 'mean'
    }).round(2)
    
    summary.columns = ['Total', 'Churned', 'Churn_Rate', 'Avg_Age', 'Avg_Balance', 'Avg_Logins', 'Avg_Transactions']
    summary['Churn_Rate'] = (summary['Churn_Rate'] * 100).round(1)
    
    return summary.reset_index()

# ============= FUNCIONES DE EXPORTACIÓN =============

from column_schema import COLUMN_NAMES

def export_high_risk_customers(df, output_file='high_risk_customers.csv'):
    """
    Exporta lista de clientes de alto riesgo
    
    Args:
        df: DataFrame con datos
        output_file: Nombre del archivo de salida
    
    Returns:
        Path al archivo exportado
    """
    # Segmentar si no está hecho
    if 'Segment' not in df.columns:
        df = segment_customers(df)
    
    # Filtrar alto riesgo
    high_risk = df[df['Segment'] == 'High Risk'].copy()
    
    # Seleccionar columnas relevantes usando nombres estandarizados
    columns = [
        'Geography', 'Gender', 'Age', 'NumOfProducts', 
        'IsActiveMember', 'Monthly_Logins', 'Days_Since_Last_Transaction',
        'Complain', COLUMN_NAMES['SATISFACTION_SCORE'], 'Risk_Score', 'Exited'
    ]
    
    available_columns = [col for col in columns if col in high_risk.columns]
    export_df = high_risk[available_columns]
    
    # Exportar
    export_df.to_csv(output_file, index=False)
    logger.info(f"Exportados {len(export_df)} clientes de alto riesgo a {output_file}")
    
    return output_file

def create_action_plan(df, output_file='action_plan.json'):
    """
    Crea plan de acción basado en análisis
    
    Args:
        df: DataFrame con datos
        output_file: Nombre del archivo JSON de salida
    
    Returns:
        Dictionary con plan de acción
    """
    metrics = calculate_churn_metrics(df)
    
    # Identificar problemas críticos
    problems = []
    
    if 'Complain' in df.columns:
        complaints = df[df['Complain'] == 1]
        if len(complaints) > 0:
            problems.append({
                'issue': 'Clientes con quejas',
                'count': int(len(complaints)),
                'churn_rate': float((complaints['Exited'].sum() / len(complaints)) * 100),
                'priority': 'CRÍTICA',
                'action': 'Protocolo de respuesta en 24h'
            })
    
    if 'Days_Since_Last_Transaction' in df.columns:
        inactive = df[df['Days_Since_Last_Transaction'] > 25]
        if len(inactive) > 0:
            problems.append({
                'issue': 'Inactividad prolongada',
                'count': int(len(inactive)),
                'churn_rate': float((inactive['Exited'].sum() / len(inactive)) * 100),
                'priority': 'ALTA',
                'action': 'Campaña de reactivación'
            })
    
    if 'NumOfProducts' in df.columns:
        multi_product = df[df['NumOfProducts'] >= 3]
        if len(multi_product) > 0:
            problems.append({
                'issue': 'Clientes con 3+ productos',
                'count': int(len(multi_product)),
                'churn_rate': float((multi_product['Exited'].sum() / len(multi_product)) * 100),
                'priority': 'ALTA',
                'action': 'Auditoría y simplificación'
            })
    
    # Plan de acción
    action_plan = {
        'generated_at': datetime.now().isoformat(),
        'metrics': {k: float(v) if isinstance(v, (int, float, np.number)) else v 
                   for k, v in metrics.items()},
        'problems_identified': problems,
        'quick_wins': [
            {
                'action': 'Protocolo de quejas',
                'estimated_retention': '100-150 clientes/año',
                'effort': 'Bajo',
                'impact': 'Alto'
            },
            {
                'action': 'Reactivación de inactivos',
                'estimated_retention': '200-300 clientes/año',
                'effort': 'Medio',
                'impact': 'Alto'
            },
            {
                'action': 'Simplificación multi-producto',
                'estimated_retention': '250-270 clientes/año',
                'effort': 'Alto',
                'impact': 'Crítico'
            }
        ]
    }
    
    # Guardar
    with open(output_file, 'w') as f:
        json.dump(action_plan, f, indent=2)
    
    logger.info(f"Plan de acción guardado en {output_file}")
    return action_plan

# ============= FUNCIONES DE UTILIDAD =============

def format_number(num, decimals=2, percentage=False):
    """
    Formatea números para display
    
    Args:
        num: Número a formatear
        decimals: Decimales a mostrar
        percentage: Si es porcentaje
    
    Returns:
        String formateado
    """
    if percentage:
        return f"{num:.{decimals}f}%"
    
    if num >= 1000000:
        return f"{num/1000000:.{decimals}f}M"
    elif num >= 1000:
        return f"{num/1000:.{decimals}f}K"
    else:
        return f"{num:.{decimals}f}"

def get_date_range(days_back=30):
    """
    Genera rango de fechas para análisis temporal
    
    Args:
        days_back: Días hacia atrás desde hoy
    
    Returns:
        Tuple (start_date, end_date)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    return start_date, end_date

def calculate_retention_value(num_customers, avg_value_per_customer=1000):
    """
    Calcula valor de retención
    
    Args:
        num_customers: Número de clientes retenidos
        avg_value_per_customer: Valor promedio por cliente/año
    
    Returns:
        Valor total
    """
    return num_customers * avg_value_per_customer

# ============= FUNCIÓN PRINCIPAL DE ANÁLISIS =============

def run_complete_analysis(filepath='cleaned_data.csv', export_results=True):
    """
    Ejecuta análisis completo del dataset
    
    Args:
        filepath: Ruta al dataset
        export_results: Si exportar resultados
    
    Returns:
        Dictionary con todos los resultados
    """
    logger.info("="*60)
    logger.info("INICIANDO ANÁLISIS COMPLETO")
    logger.info("="*60)
    
    # Cargar datos
    df = load_dataset(filepath)
    if df is None:
        return None
    
    # Calcular métricas
    logger.info("\n1. Calculando métricas generales...")
    metrics = calculate_churn_metrics(df)
    
    for key, value in metrics.items():
        if isinstance(value, float):
            logger.info(f"   {key}: {value:.2f}")
        else:
            logger.info(f"   {key}: {value}")
    
    # Segmentar clientes
    logger.info("\n2. Segmentando clientes...")
    df = segment_customers(df)
    segment_summary = get_segment_summary(df)
    logger.info(f"\n{segment_summary.to_string()}")
    
    # Exportar resultados
    if export_results:
        logger.info("\n3. Exportando resultados...")
        high_risk_file = export_high_risk_customers(df)
        action_plan = create_action_plan(df)
        
        logger.info(f"   ✓ Clientes de alto riesgo: {high_risk_file}")
        logger.info(f"   ✓ Plan de acción: action_plan.json")
    
    logger.info("\n" + "="*60)
    logger.info("ANÁLISIS COMPLETADO")
    logger.info("="*60)
    
    results = {
        'metrics': metrics,
        'segment_summary': segment_summary.to_dict(),
        'dataframe': df,
        'high_risk_count': len(df[df['Segment'] == 'High Risk'])
    }
    
    return results

# ============= FUNCIONES DE PREDICCIÓN =============

def predict_single_customer(customer_data, model_path='models/random_forest_model.pkl'):
    """
    Predice churn para un cliente individual
    
    Args:
        customer_data: Dictionary con datos del cliente
        model_path: Ruta al modelo entrenado
    
    Returns:
        Dictionary con predicción y probabilidad
    """
    try:
        # Cargar modelo
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        # Convertir a DataFrame
        df = pd.DataFrame([customer_data])
        
        # Cargar encoders y scaler si existen
        encoders_path = 'models/label_encoders.pkl'
        scaler_path = 'models/scaler.pkl'
        
        if os.path.exists(encoders_path):
            with open(encoders_path, 'rb') as f:
                encoders = pickle.load(f)
            
            for col, encoder in encoders.items():
                if col in df.columns:
                    df[col] = encoder.transform(df[col].astype(str))
        
        # Predecir
        probability = model.predict_proba(df)[0][1]
        prediction = int(probability >= 0.5)
        
        # Determinar nivel de riesgo
        if probability >= 0.7:
            risk_level = "CRÍTICO"
        elif probability >= 0.4:
            risk_level = "ALTO"
        else:
            risk_level = "BAJO"
        
        result = {
            'probability': float(probability),
            'prediction': prediction,
            'risk_level': risk_level,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Predicción exitosa - Prob: {probability:.2%} - Riesgo: {risk_level}")
        return result
        
    except Exception as e:
        logger.error(f"Error en predicción: {e}")
        return None

def batch_predict(df, model_path='models/random_forest_model.pkl'):
    """
    Predice churn para múltiples clientes
    
    Args:
        df: DataFrame con datos de clientes
        model_path: Ruta al modelo
    
    Returns:
        DataFrame con predicciones agregadas
    """
    try:
        # Cargar modelo
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        df_copy = df.copy()
        
        # Cargar encoders si existen
        encoders_path = 'models/label_encoders.pkl'
        if os.path.exists(encoders_path):
            with open(encoders_path, 'rb') as f:
                encoders = pickle.load(f)
            
            for col, encoder in encoders.items():
                if col in df_copy.columns:
                    df_copy[col] = encoder.transform(df_copy[col].astype(str))
        
        # Predecir
        probabilities = model.predict_proba(df_copy)[:, 1]
        predictions = (probabilities >= 0.5).astype(int)
        
        # Agregar resultados
        df['Churn_Probability'] = probabilities
        df['Churn_Prediction'] = predictions
        df['Risk_Level'] = ['CRÍTICO' if p >= 0.7 else 'ALTO' if p >= 0.4 else 'BAJO' 
                           for p in probabilities]
        
        logger.info(f"Predicción batch completada para {len(df)} clientes")
        return df
        
    except Exception as e:
        logger.error(f"Error en predicción batch: {e}")
        return None

# ============= FUNCIONES DE VISUALIZACIÓN =============

def generate_summary_report(df):
    """
    Genera reporte de resumen en texto
    
    Args:
        df: DataFrame con datos
    
    Returns:
        String con reporte
    """
    metrics = calculate_churn_metrics(df)
    
    report = f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║          REPORTE DE ANÁLISIS DE CHURN                     ║
    ╚═══════════════════════════════════════════════════════════╝
    
    MÉTRICAS GENERALES:
    ├─ Total de Clientes: {metrics['total_customers']:,}
    ├─ Clientes en Churn: {metrics['churned_customers']:,}
    ├─ Tasa de Churn: {metrics['churn_rate']:.2f}%
    └─ Tasa de Retención: {metrics['retention_rate']:.2f}%
    
    DISTRIBUCIÓN POR ACTIVIDAD:
    ├─ Miembros Activos: {metrics.get('active_members', 'N/A')}
    ├─ Miembros Inactivos: {metrics.get('inactive_members', 'N/A')}
    ├─ Churn Rate (Activos): {metrics.get('active_churn_rate', 0):.2f}%
    └─ Churn Rate (Inactivos): {metrics.get('inactive_churn_rate', 0):.2f}%
    
    ANÁLISIS POR SEGMENTO:
    """
    
    if 'Segment' in df.columns or True:
        df_segmented = segment_customers(df)
        segment_summary = get_segment_summary(df_segmented)
        
        for _, row in segment_summary.iterrows():
            report += f"""
    {row['Segment']}:
    ├─ Clientes: {int(row['Total']):,}
    ├─ Churn Rate: {row['Churn_Rate']:.1f}%
    └─ Edad Promedio: {row['Avg_Age']:.1f} años
    """
    
    report += f"""
    
    GENERADO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    return report

# ============= MAIN PARA TESTING =============

if __name__ == "__main__":
    import os
    
    print("\n" + "="*60)
    print("TESTING DE UTILIDADES")
    print("="*60)
    
    # Test 1: Cargar datos
    print("\n[TEST 1] Cargando datos...")
    df = load_dataset('cleaned_data.csv', sample_size=1000)
    
    if df is not None:
        print(f"✓ Datos cargados: {df.shape}")
        
        # Test 2: Calcular métricas
        print("\n[TEST 2] Calculando métricas...")
        metrics = calculate_churn_metrics(df)
        print(f"✓ Tasa de churn: {metrics['churn_rate']:.2f}%")
        
        # Test 3: Segmentar clientes
        print("\n[TEST 3] Segmentando clientes...")
        df = segment_customers(df)
        summary = get_segment_summary(df)
        print(f"✓ Segmentación completada")
        print(summary)
        
        # Test 4: Crear risk score
        print("\n[TEST 4] Calculando Risk Score...")
        df = create_risk_score(df)
        print(f"✓ Risk Score agregado")
        print(f"   Promedio: {df['Risk_Score'].mean():.2f}")
        print(f"   Máximo: {df['Risk_Score'].max():.0f}")
        
        # Test 5: Generar reporte
        print("\n[TEST 5] Generando reporte...")
        report = generate_summary_report(df)
        print(report)
        
        # Test 6: Exportar resultados
        print("\n[TEST 6] Exportando resultados...")
        high_risk_file = export_high_risk_customers(df)
        print(f"✓ Exportado: {high_risk_file}")
        
        action_plan = create_action_plan(df)
        print(f"✓ Plan de acción creado")
        print(f"   Problemas identificados: {len(action_plan['problems_identified'])}")
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS PASARON")
        print("="*60)
    else:
        print("❌ Error al cargar datos")
        print("\nAsegúrate de que 'cleaned_data.csv' está en el directorio actual")
    
    print("\n💡 Funciones disponibles:")
    print("   - load_dataset()")
    print("   - calculate_churn_metrics()")
    print("   - segment_customers()")
    print("   - create_risk_score()")
    print("   - export_high_risk_customers()")
    print("   - create_action_plan()")
    print("   - predict_single_customer()")
    print("   - batch_predict()")
    print("   - generate_summary_report()")
    print("\n   Importa este módulo: from utils import *")
    print()
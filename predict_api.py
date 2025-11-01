"""
API REST para Predicción de Churn
Expone endpoints para predicciones individuales y batch
Uso: python predict_api.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import pandas as pd
import pickle
import numpy as np
from datetime import datetime
import logging
from column_schema import COLUMN_NAMES, API_COLUMN_NAMES, standardize_columns
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="Churn Prediction API",
    description="API para predicción de abandono de clientes FinTech",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos globales
MODELS = {}
SCALER = None
LABEL_ENCODERS = {}

# Cargar modelos al iniciar
@app.on_event("startup")
async def load_models():
    """Carga los modelos entrenados"""
    global MODELS, SCALER, LABEL_ENCODERS
    
    try:
        # Random Forest
        with open('models/random_forest_model.pkl', 'rb') as f:
            MODELS['random_forest'] = pickle.load(f)
        logger.info("✓ Random Forest cargado")
        
        # XGBoost
        with open('models/xgboost_model.pkl', 'rb') as f:
            MODELS['xgboost'] = pickle.load(f)
        logger.info("✓ XGBoost cargado")
        
        # Scaler
        with open('models/scaler.pkl', 'rb') as f:
            SCALER = pickle.load(f)
        logger.info("✓ Scaler cargado")
        
        # Label Encoders
        with open('models/label_encoders.pkl', 'rb') as f:
            LABEL_ENCODERS = pickle.load(f)
        logger.info("✓ Label Encoders cargados")
        
        logger.info("🚀 Todos los modelos cargados exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error al cargar modelos: {e}")
        raise

# Modelos Pydantic para validación
class CustomerData(BaseModel):
    """Esquema de datos del cliente"""
    
    # Usar nombres estandarizados de columnas
    CreditScore: int = Field(..., ge=300, le=850, description="Score de crédito")
    Geography: str = Field(..., description="País (France, Spain, Germany)")
    Gender: str = Field(..., description="Género (Male, Female)")
    Age: int = Field(..., ge=18, le=100, description="Edad")
    Balance: float = Field(..., ge=0, description="Balance de cuenta")
    NumOfProducts: int = Field(..., ge=1, le=4, description="Número de productos")
    HasCrCard: int = Field(..., ge=0, le=1, description="Tiene tarjeta de crédito (0/1)")
    IsActiveMember: int = Field(..., ge=0, le=1, description="Miembro activo (0/1)")
    EstimatedSalary: float = Field(..., ge=0, description="Salario estimado")
    Complain: int = Field(..., ge=0, le=1, description="Tiene quejas (0/1)")
    SatisfactionScore: int = Field(..., ge=1, le=5, description="Score de satisfacción", alias=COLUMN_NAMES['SATISFACTION_SCORE'])
    CardType: str = Field(..., description="Tipo de tarjeta (DIAMOND, GOLD, SILVER, PLATINUM)", alias=COLUMN_NAMES['CARD_TYPE'])
    PointEarned: int = Field(..., ge=0, description="Puntos ganados", alias=COLUMN_NAMES['POINT_EARNED'])
    MonthlyTransactions: int = Field(..., ge=0, description="Transacciones mensuales", alias=COLUMN_NAMES['MONTHLY_TRANSACTIONS'])
    Days_Since_Last_Transaction: int = Field(..., ge=0, description="Días desde última transacción")
    Monthly_Logins: int = Field(..., ge=0, description="Logins mensuales")
    Avg_Session_Duration: float = Field(..., ge=0, description="Duración promedio de sesión")
    Support_Interactions: int = Field(..., ge=0, description="Interacciones con soporte")
    Session_Abandonment_Rate: float = Field(..., ge=0, le=1, description="Tasa de abandono de sesión")
    Local_Competition_Index: float = Field(..., ge=0, description="Índice de competencia local")
    
    class Config:
        schema_extra = {
            "example": {
                "CreditScore": 650,
                "Geography": "France",
                "Gender": "Female",
                "Age": 35,
                "Balance": 75000.0,
                "NumOfProducts": 2,
                "HasCrCard": 1,
                "IsActiveMember": 1,
                "EstimatedSalary": 50000.0,
                "Complain": 0,
                "Satisfaction_Score": 3,
                "Card_Type": "GOLD",
                "Point_Earned": 500,
                "Monthly_Transactions": 60,
                "Days_Since_Last_Transaction": 10,
                "Monthly_Logins": 8,
                "Avg_Session_Duration": 12.5,
                "Support_Interactions": 2,
                "Session_Abandonment_Rate": 0.15,
                "Local_Competition_Index": 0.5
            }
        }

class PredictionResponse(BaseModel):
    """Respuesta de predicción"""
    customer_id: Optional[str] = None
    churn_probability: float
    churn_prediction: int
    risk_level: str
    confidence: str
    factors: List[Dict[str, Any]]
    recommendations: List[str]
    timestamp: str

class BatchPredictionRequest(BaseModel):
    """Solicitud de predicción batch"""
    customers: List[CustomerData]
    model_name: Optional[str] = "random_forest"

# Funciones auxiliares
def preprocess_customer_data(customer: CustomerData) -> pd.DataFrame:
    """Preprocesa los datos del cliente"""
    # Convertir a diccionario usando aliases (si los hay)
    data = customer.dict(by_alias=True)

    # Crear DataFrame y estandarizar nombres
    df = pd.DataFrame([data])
    df = standardize_columns(df)

    # Si no hay encoders o scaler cargados (p. ej. import directo sin startup event), intentar cargarlos
    try:
        if not LABEL_ENCODERS and os.path.exists('models/label_encoders.pkl'):
            with open('models/label_encoders.pkl', 'rb') as f:
                loaded = pickle.load(f)
                LABEL_ENCODERS.update(loaded if isinstance(loaded, dict) else {})
        if SCALER is None and os.path.exists('models/scaler.pkl'):
            with open('models/scaler.pkl', 'rb') as f:
                globals()['SCALER'] = pickle.load(f)
    except Exception:
        # ignore loading errors; fallback to in-memory values
        pass

    # Codificar variables categóricas si los encoders están cargados
    if LABEL_ENCODERS:
        for col, encoder in LABEL_ENCODERS.items():
            if col in df.columns:
                df[col] = encoder.transform(df[col].astype(str))

    # Intentar reordenar según features guardadas y escalar si hay scaler
    try:
        features_path = 'models/features_list.txt'
        if SCALER is not None and os.path.exists(features_path):
            with open(features_path, 'r') as fh:
                features = [l.strip() for l in fh if l.strip()]
            # Seleccionar solo features disponibles
            selected = [f for f in features if f in df.columns]
            if selected:
                X = df[selected].copy()
                X_scaled = SCALER.transform(X)
                return pd.DataFrame(X_scaled, columns=selected)
    except Exception:
        # Si algo falla en este paso, devolvemos el df sin escalar (fallback seguro)
        pass

    return df

def get_risk_level(probability: float) -> tuple:
    """Determina el nivel de riesgo"""
    if probability >= 0.7:
        return "CRÍTICO", "Alta"
    elif probability >= 0.4:
        return "ALTO", "Media"
    else:
        return "BAJO", "Alta"

def identify_risk_factors(customer: CustomerData, probability: float) -> List[Dict]:
    """Identifica factores de riesgo"""
    factors = []
    
    if customer.Complain == 1:
        factors.append({
            "factor": "Cliente tiene quejas registradas",
            "impact": "CRÍTICO",
            "score": 40
        })
    
    if customer.IsActiveMember == 0:
        factors.append({
            "factor": "Miembro inactivo",
            "impact": "MUY ALTO",
            "score": 25
        })
    
    if customer.NumOfProducts >= 3:
        factors.append({
            "factor": "3+ productos (sobrecarga)",
            "impact": "MUY ALTO",
            "score": 30
        })
    
    if customer.Days_Since_Last_Transaction > 25:
        factors.append({
            "factor": "Más de 25 días sin transacción",
            "impact": "ALTO",
            "score": 20
        })
    
    if customer.Monthly_Logins < 5:
        factors.append({
            "factor": "Bajo engagement (< 5 logins/mes)",
            "impact": "ALTO",
            "score": 15
        })
    
    if customer.Satisfaction_Score <= 2:
        factors.append({
            "factor": "Baja satisfacción",
            "impact": "MUY ALTO",
            "score": 25
        })
    
    if customer.Geography == "Germany":
        factors.append({
            "factor": "Ubicación en mercado de alto riesgo",
            "impact": "MEDIO",
            "score": 15
        })
    
    if customer.Age > 50:
        factors.append({
            "factor": "Edad > 50 años",
            "impact": "MEDIO",
            "score": 15
        })
    
    # Ordenar por score descendente
    factors.sort(key=lambda x: x['score'], reverse=True)
    
    return factors

def generate_recommendations(risk_level: str, factors: List[Dict]) -> List[str]:
    """Genera recomendaciones basadas en el riesgo"""
    recommendations = []
    
    if risk_level == "CRÍTICO":
        recommendations = [
            "📞 Contacto directo del equipo de retención en próximas 24 horas",
            "🎁 Aplicar incentivo de alto valor (descuento, cashback)",
            "👨‍💼 Asignar account manager dedicado",
            "🔍 Investigar causa raíz del descontento",
            "📊 Revisión completa de productos contratados"
        ]
    elif risk_level == "ALTO":
        recommendations = [
            "📧 Campaña de reactivación personalizada",
            "💬 Encuesta de satisfacción",
            "🎯 Ofertas dirigidas basadas en comportamiento",
            "📱 Re-onboarding de funcionalidades clave",
            "🔔 Activar notificaciones push personalizadas"
        ]
    else:
        recommendations = [
            "👍 Continuar con comunicación regular",
            "🎁 Considerar programa de lealtad",
            "📚 Educación sobre nuevas funcionalidades",
            "🌟 Incentivar referidos",
            "📊 Monitoreo mensual de métricas"
        ]
    
    return recommendations

# Endpoints
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Churn Prediction API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "predict_batch": "/predict/batch",
            "models": "/models"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint para Docker healthcheck"""
    models_loaded = len(MODELS) > 0
    scaler_loaded = SCALER is not None
    encoders_loaded = len(LABEL_ENCODERS) > 0
    
    status = "healthy" if (models_loaded and scaler_loaded and encoders_loaded) else "unhealthy"
    
    return {
        "status": status,
        "models_loaded": list(MODELS.keys()),
        "scaler_loaded": scaler_loaded,
        "encoders_loaded": encoders_loaded,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/models")
async def list_models():
    """Lista los modelos disponibles"""
    return {
        "available_models": list(MODELS.keys()),
        "default_model": "random_forest"
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_churn(
    customer: CustomerData,
    model_name: str = "random_forest",
    customer_id: Optional[str] = None
):
    """
    Predice la probabilidad de churn para un cliente individual
    
    Args:
        customer: Datos del cliente
        model_name: Nombre del modelo a usar (random_forest, xgboost)
        customer_id: ID del cliente (opcional)
    
    Returns:
        Predicción de churn con probabilidad y recomendaciones
    """
    try:
        # Validar modelo
        if model_name not in MODELS:
            raise HTTPException(
                status_code=400,
                detail=f"Modelo '{model_name}' no disponible. Usa: {list(MODELS.keys())}"
            )
        
        # Preprocesar datos
        df = preprocess_customer_data(customer)
        
        # Realizar predicción
        model = MODELS[model_name]
        probability = model.predict_proba(df)[0][1]
        prediction = int(probability >= 0.5)
        
        # Determinar nivel de riesgo
        risk_level, confidence = get_risk_level(probability)
        
        # Identificar factores de riesgo
        factors = identify_risk_factors(customer, probability)
        
        # Generar recomendaciones
        recommendations = generate_recommendations(risk_level, factors)
        
        # Construir respuesta
        response = PredictionResponse(
            customer_id=customer_id or f"CUST_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            churn_probability=round(float(probability), 4),
            churn_prediction=prediction,
            risk_level=risk_level,
            confidence=confidence,
            factors=factors[:5],  # Top 5 factores
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Predicción exitosa: {customer_id} - Prob: {probability:.4f}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error en predicción: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/batch")
async def predict_batch(request: BatchPredictionRequest):
    """
    Predice churn para múltiples clientes
    
    Args:
        request: Lista de clientes y modelo a usar
    
    Returns:
        Lista de predicciones
    """
    try:
        predictions = []
        
        for idx, customer in enumerate(request.customers):
            pred = await predict_churn(
                customer=customer,
                model_name=request.model_name,
                customer_id=f"BATCH_{idx+1}"
            )
            predictions.append(pred)
        
        return {
            "total_customers": len(predictions),
            "predictions": predictions,
            "summary": {
                "high_risk": sum(1 for p in predictions if p.risk_level == "CRÍTICO"),
                "medium_risk": sum(1 for p in predictions if p.risk_level == "ALTO"),
                "low_risk": sum(1 for p in predictions if p.risk_level == "BAJO"),
                "avg_probability": np.mean([p.churn_probability for p in predictions])
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error en predicción batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/csv")
async def predict_from_csv(file_path: str, model_name: str = "random_forest"):
    """
    Predice churn desde un archivo CSV
    
    Args:
        file_path: Ruta al archivo CSV
        model_name: Modelo a usar
    
    Returns:
        Resultados guardados en CSV
    """
    try:
        # Leer CSV
        df = pd.read_csv(file_path)
        
        # Validar columnas requeridas
        required_cols = list(CustomerData.__fields__.keys())
        missing_cols = [col for col in required_cols if col not in df.columns and col.replace('_', ' ') not in df.columns]
        
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Columnas faltantes: {missing_cols}"
            )
        
        # Realizar predicciones
        model = MODELS[model_name]
        
        # Preprocesar
        df_processed = df.copy()
        for col, encoder in LABEL_ENCODERS.items():
            if col in df_processed.columns:
                df_processed[col] = encoder.transform(df_processed[col].astype(str))
        
        # Predecir
        probabilities = model.predict_proba(df_processed)[:, 1]
        predictions = (probabilities >= 0.5).astype(int)
        
        # Agregar resultados
        df['Churn_Probability'] = probabilities
        df['Churn_Prediction'] = predictions
        df['Risk_Level'] = ['CRÍTICO' if p >= 0.7 else 'ALTO' if p >= 0.4 else 'BAJO' for p in probabilities]
        
        # Guardar resultados
        output_path = file_path.replace('.csv', '_predictions.csv')
        df.to_csv(output_path, index=False)
        
        return {
            "status": "success",
            "input_file": file_path,
            "output_file": output_path,
            "total_customers": len(df),
            "summary": {
                "high_risk": sum(df['Risk_Level'] == 'CRÍTICO'),
                "medium_risk": sum(df['Risk_Level'] == 'ALTO'),
                "low_risk": sum(df['Risk_Level'] == 'BAJO')
            }
        }
        
    except Exception as e:
        logger.error(f"Error en predicción CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Ejecutar con: uvicorn predict_api:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
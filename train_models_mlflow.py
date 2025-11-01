"""
Script de Entrenamiento con MLflow para Versionado de Modelos
Versión mejorada de train_models.py con tracking completo
Autor: Sistema de ML Mejorado
"""

import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime
import json

# Machine Learning
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (classification_report, confusion_matrix, 
                             roc_auc_score, roc_curve, precision_score,
                             recall_score, f1_score, accuracy_score)
import xgboost as xgb
from tensorflow import keras
from tensorflow.keras import layers
from imblearn.over_sampling import SMOTE

# MLflow para versionado
import mlflow
import mlflow.sklearn
import mlflow.xgboost
import mlflow.keras

# Configuración
np.random.seed(42)
MODELS_DIR = 'models'
DATA_PATH = 'cleaned_data.csv'
MLFLOW_TRACKING_URI = 'file:./mlruns'  # Puede ser remoto
EXPERIMENT_NAME = 'churn_prediction'

# Configurar MLflow
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

print("="*70)
print("ENTRENAMIENTO DE MODELOS CON MLFLOW - PREDICCIÓN DE CHURN")
print("="*70)
print(f"📊 MLflow URI: {MLFLOW_TRACKING_URI}")
print(f"🧪 Experimento: {EXPERIMENT_NAME}")

# Crear directorio de modelos
os.makedirs(MODELS_DIR, exist_ok=True)

# 1. CARGA Y PREPARACIÓN DE DATOS
print("\n[1/7] Cargando datos...")
df = pd.read_csv(DATA_PATH)
print(f"✓ Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas")

# 2. FEATURE ENGINEERING
print("\n[2/7] Ingeniería de características...")

features_to_use = [
    'CreditScore', 'Geography', 'Gender', 'Age', 'Balance', 'NumOfProducts',
    'HasCrCard', 'IsActiveMember', 'EstimatedSalary', 'Complain',
    'Satisfaction Score', 'Card_Type', 'Point Earned', 'Monthly_Transactions',
    'Days_Since_Last_Transaction', 'Monthly_Logins', 'Avg_Session_Duration',
    'Support_Interactions', 'Session_Abandonment_Rate', 'Local_Competition_Index'
]

available_features = [f for f in features_to_use if f in df.columns]
print(f"✓ Features disponibles: {len(available_features)}/{len(features_to_use)}")

X = df[available_features].copy()
y = df['Exited'].copy()

# Encoding de variables categóricas
categorical_cols = X.select_dtypes(include=['object']).columns
print(f"✓ Codificando {len(categorical_cols)} variables categóricas...")

label_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col].astype(str))
    label_encoders[col] = le

# Guardar encoders
with open(f'{MODELS_DIR}/label_encoders.pkl', 'wb') as f:
    pickle.dump(label_encoders, f)

# 3. SPLIT DE DATOS
print("\n[3/7] Dividiendo datos...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"✓ Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")
print(f"✓ Distribución Train - Churn: {y_train.sum()/len(y_train)*100:.1f}%")
print(f"✓ Distribución Test - Churn: {y_test.sum()/len(y_test)*100:.1f}%")

# Aplicar SMOTE
print("\n   Aplicando SMOTE...")
smote = SMOTE(random_state=42)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
print(f"✓ Datos balanceados: {X_train_balanced.shape[0]} muestras")

# Escalado
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_balanced)
X_test_scaled = scaler.transform(X_test)

# Guardar scaler
with open(f'{MODELS_DIR}/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

# 4. ENTRENAMIENTO DE MODELOS CON MLFLOW
print("\n[4/7] Entrenando modelos con MLflow tracking...")

models_performance = {}

# ============= MODELO 1: RANDOM FOREST =============
print("\n   → Random Forest Classifier...")

with mlflow.start_run(run_name="Random_Forest"):
    # Log de parámetros
    rf_params = {
        'n_estimators': 200,
        'max_depth': 15,
        'min_samples_split': 10,
        'min_samples_leaf': 4,
        'max_features': 'sqrt',
        'random_state': 42,
        'class_weight': 'balanced'
    }
    
    mlflow.log_params(rf_params)
    mlflow.log_param('model_type', 'RandomForest')
    mlflow.log_param('smote_applied', True)
    mlflow.log_param('n_features', len(available_features))
    
    # Entrenar
    rf_model = RandomForestClassifier(**rf_params, n_jobs=-1)
    rf_model.fit(X_train_balanced, y_train_balanced)
    
    # Predicciones
    rf_pred = rf_model.predict(X_test)
    rf_pred_proba = rf_model.predict_proba(X_test)[:, 1]
    
    # Métricas
    rf_metrics = {
        'auc': roc_auc_score(y_test, rf_pred_proba),
        'accuracy': accuracy_score(y_test, rf_pred),
        'precision': precision_score(y_test, rf_pred),
        'recall': recall_score(y_test, rf_pred),
        'f1_score': f1_score(y_test, rf_pred)
    }
    
    # Log de métricas
    mlflow.log_metrics(rf_metrics)
    
    # Log del modelo
    mlflow.sklearn.log_model(rf_model, "model")
    
    # Guardar también localmente
    with open(f'{MODELS_DIR}/random_forest_model.pkl', 'wb') as f:
        pickle.dump(rf_model, f)
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': available_features,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    feature_importance.to_csv(f'{MODELS_DIR}/feature_importance_rf.csv', index=False)
    mlflow.log_artifact(f'{MODELS_DIR}/feature_importance_rf.csv')
    
    print(f"   ✓ Random Forest - AUC: {rf_metrics['auc']:.4f}")
    
    models_performance['Random Forest'] = rf_metrics

# ============= MODELO 2: XGBOOST =============
print("\n   → XGBoost Classifier...")

with mlflow.start_run(run_name="XGBoost"):
    # Parámetros
    scale_pos_weight = (y_train_balanced == 0).sum() / (y_train_balanced == 1).sum()
    
    xgb_params = {
        'n_estimators': 200,
        'max_depth': 6,
        'learning_rate': 0.1,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'scale_pos_weight': scale_pos_weight,
        'random_state': 42,
        'use_label_encoder': False,
        'eval_metric': 'logloss'
    }
    
    mlflow.log_params(xgb_params)
    mlflow.log_param('model_type', 'XGBoost')
    mlflow.log_param('smote_applied', True)
    
    # Entrenar
    xgb_model = xgb.XGBClassifier(**xgb_params)
    xgb_model.fit(X_train_balanced, y_train_balanced)
    
    # Predicciones
    xgb_pred = xgb_model.predict(X_test)
    xgb_pred_proba = xgb_model.predict_proba(X_test)[:, 1]
    
    # Métricas
    xgb_metrics = {
        'auc': roc_auc_score(y_test, xgb_pred_proba),
        'accuracy': accuracy_score(y_test, xgb_pred),
        'precision': precision_score(y_test, xgb_pred),
        'recall': recall_score(y_test, xgb_pred),
        'f1_score': f1_score(y_test, xgb_pred)
    }
    
    mlflow.log_metrics(xgb_metrics)
    mlflow.xgboost.log_model(xgb_model, "model")
    
    # Guardar localmente
    with open(f'{MODELS_DIR}/xgboost_model.pkl', 'wb') as f:
        pickle.dump(xgb_model, f)
    
    print(f"   ✓ XGBoost - AUC: {xgb_metrics['auc']:.4f}")
    
    models_performance['XGBoost'] = xgb_metrics

# ============= MODELO 3: RED NEURONAL =============
print("\n   → Red Neuronal (Deep Learning)...")

with mlflow.start_run(run_name="Neural_Network"):
    # Parámetros
    nn_params = {
        'layers': '128-64-32-1',
        'activation': 'relu',
        'dropout': 0.3,
        'optimizer': 'adam',
        'learning_rate': 0.001,
        'batch_size': 32,
        'epochs': 50
    }
    
    mlflow.log_params(nn_params)
    mlflow.log_param('model_type', 'NeuralNetwork')
    
    # Arquitectura
    nn_model = keras.Sequential([
        layers.Input(shape=(X_train_scaled.shape[1],)),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.BatchNormalization(),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.3),
        layers.BatchNormalization(),
        layers.Dense(32, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(1, activation='sigmoid')
    ])
    
    nn_model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy', keras.metrics.AUC(name='auc')]
    )
    
    # Early stopping
    early_stopping = keras.callbacks.EarlyStopping(
        monitor='val_auc',
        patience=10,
        restore_best_weights=True,
        mode='max'
    )
    
    # Entrenar
    history = nn_model.fit(
        X_train_scaled, y_train_balanced,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        callbacks=[early_stopping],
        verbose=0
    )
    
    # Predicciones
    nn_pred_proba = nn_model.predict(X_test_scaled, verbose=0).flatten()
    nn_pred = (nn_pred_proba > 0.5).astype(int)
    
    # Métricas
    nn_metrics = {
        'auc': roc_auc_score(y_test, nn_pred_proba),
        'accuracy': accuracy_score(y_test, nn_pred),
        'precision': precision_score(y_test, nn_pred),
        'recall': recall_score(y_test, nn_pred),
        'f1_score': f1_score(y_test, nn_pred),
        'epochs_trained': len(history.history['loss'])
    }
    
    mlflow.log_metrics(nn_metrics)
    mlflow.keras.log_model(nn_model, "model")
    
    # Guardar localmente
    nn_model.save(f'{MODELS_DIR}/neural_network_model.h5')
    
    print(f"   ✓ Neural Network - AUC: {nn_metrics['auc']:.4f}")
    
    models_performance['Neural Network'] = nn_metrics

# 5. EVALUACIÓN COMPARATIVA
print("\n[5/7] Evaluación comparativa...")
print("\n" + "="*70)
print("RESULTADOS FINALES")
print("="*70)

for model_name, metrics in models_performance.items():
    print(f"\n{model_name}:")
    print(f"   AUC-ROC:   {metrics['auc']:.4f}")
    print(f"   Accuracy:  {metrics['accuracy']:.4f}")
    print(f"   Precision: {metrics['precision']:.4f}")
    print(f"   Recall:    {metrics['recall']:.4f}")
    print(f"   F1-Score:  {metrics['f1_score']:.4f}")

# Mejor modelo
best_model_name = max(models_performance.items(), key=lambda x: x[1]['auc'])[0]
print("\n" + "="*70)
print(f"🏆 MEJOR MODELO: {best_model_name}")
print(f"   AUC: {models_performance[best_model_name]['auc']:.4f}")
print("="*70)

# 6. GUARDAR METADATA
print("\n[6/7] Guardando metadata...")

metadata = {
    'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'data_shape': df.shape,
    'features_used': available_features,
    'train_samples': len(X_train),
    'test_samples': len(X_test),
    'models': {
        name.lower().replace(' ', '_'): {
            'auc': float(metrics['auc']),
            'accuracy': float(metrics['accuracy']),
            'precision': float(metrics['precision']),
            'recall': float(metrics['recall']),
            'f1_score': float(metrics['f1_score'])
        }
        for name, metrics in models_performance.items()
    },
    'best_model': best_model_name,
    'smote_applied': True,
    'mlflow_experiment': EXPERIMENT_NAME,
    'mlflow_tracking_uri': MLFLOW_TRACKING_URI
}

with open(f'{MODELS_DIR}/training_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=4)

# Guardar lista de features
with open(f'{MODELS_DIR}/features_list.txt', 'w') as f:
    for feature in available_features:
        f.write(f"{feature}\n")

print("✓ Metadata guardada")

# 7. LOG FINAL EN MLFLOW
print("\n[7/7] Registrando experimento completo...")

with mlflow.start_run(run_name="Comparison_Summary"):
    mlflow.log_params({
        'best_model': best_model_name,
        'n_models_trained': len(models_performance),
        'n_features': len(available_features),
        'smote_applied': True
    })
    
    # Log best model metrics
    mlflow.log_metrics({
        f'best_{k}': v 
        for k, v in models_performance[best_model_name].items()
    })
    
    # Log metadata
    mlflow.log_artifact(f'{MODELS_DIR}/training_metadata.json')
    mlflow.log_artifact(f'{MODELS_DIR}/features_list.txt')

print("\n" + "="*70)
print("✅ ENTRENAMIENTO COMPLETADO CON MLFLOW")
print("="*70)
print(f"\n📁 Modelos guardados en: '{MODELS_DIR}/'")
print(f"📊 Tracking MLflow en: {MLFLOW_TRACKING_URI}")
print(f"\n🚀 Para ver resultados en UI:")
print(f"   mlflow ui")
print(f"   Accede a: http://localhost:5000")
print("\n💡 Para cargar un modelo:")
print(f"   model = mlflow.sklearn.load_model('runs:/<RUN_ID>/model')")
print("\n🎯 Los modelos están listos para producción!\n")

"""
Script de Entrenamiento de Modelos de Churn
Entrena Random Forest, XGBoost y Red Neuronal
"""

import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime

# Machine Learning
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import xgboost as xgb
HAS_TF = True
try:
    from tensorflow import keras
    from tensorflow.keras import layers
except Exception:
    HAS_TF = False
    keras = None
    layers = None
from imblearn.over_sampling import SMOTE

# Configuración
np.random.seed(42)
MODELS_DIR = 'models'
DATA_PATH = 'cleaned_data.csv'

# Crear directorio de modelos si no existe
os.makedirs(MODELS_DIR, exist_ok=True)

print("="*60)
print("SISTEMA DE ENTRENAMIENTO DE MODELOS - PREDICCIÓN DE CHURN")
print("="*60)

# 1. CARGA Y PREPARACIÓN DE DATOS
print("\n[1/6] Cargando datos...")
df = pd.read_csv(DATA_PATH)
print(f"✓ Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas")

# 2. FEATURE ENGINEERING
print("\n[2/6] Ingeniería de características...")

# Variables a usar (según análisis EDA)
from column_schema import COLUMN_NAMES

# Usar nombres estandarizados de columnas
features_to_use = [
    'CreditScore', 'Geography', 'Gender', 'Age', 'Balance', 'NumOfProducts',
    'HasCrCard', 'IsActiveMember', 'EstimatedSalary', 'Complain',
    COLUMN_NAMES['SATISFACTION_SCORE'], COLUMN_NAMES['CARD_TYPE'], 
    COLUMN_NAMES['POINT_EARNED'], COLUMN_NAMES['MONTHLY_TRANSACTIONS'],
    'Days_Since_Last_Transaction', 'Monthly_Logins', 'Avg_Session_Duration',
    'Support_Interactions', 'Session_Abandonment_Rate', 'Local_Competition_Index'
]

# Verificar que todas las columnas existen
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
print("✓ Label encoders guardados")

# 3. SPLIT DE DATOS
print("\n[3/6] Dividiendo datos...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"✓ Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")
print(f"✓ Distribución Train - Churn: {y_train.sum()/len(y_train)*100:.1f}%")
print(f"✓ Distribución Test - Churn: {y_test.sum()/len(y_test)*100:.1f}%")

# Aplicar SMOTE para balancear clases
print("\n   Aplicando SMOTE para balanceo de clases...")
smote = SMOTE(random_state=42)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
print(f"✓ Datos balanceados: {X_train_balanced.shape[0]} muestras")
print(f"✓ Nueva distribución - Churn: {y_train_balanced.sum()/len(y_train_balanced)*100:.1f}%")

# Escalado de características
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_balanced)
X_test_scaled = scaler.transform(X_test)

# Guardar scaler
with open(f'{MODELS_DIR}/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print("✓ Scaler guardado")

# 4. ENTRENAMIENTO DE MODELOS
print("\n[4/6] Entrenando modelos...")

# ============= MODELO 1: RANDOM FOREST =============
print("\n   → Random Forest Classifier...")
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=4,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)

rf_model.fit(X_train_balanced, y_train_balanced)
rf_pred = rf_model.predict(X_test)
rf_pred_proba = rf_model.predict_proba(X_test)[:, 1]
rf_auc = roc_auc_score(y_test, rf_pred_proba)

print(f"   ✓ Random Forest entrenado - AUC: {rf_auc:.4f}")

# Guardar modelo
with open(f'{MODELS_DIR}/random_forest_model.pkl', 'wb') as f:
    pickle.dump(rf_model, f)

# Feature importance
feature_importance = pd.DataFrame({
    'feature': available_features,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

feature_importance.to_csv(f'{MODELS_DIR}/feature_importance_rf.csv', index=False)
print("   ✓ Feature importance guardado")

# ============= MODELO 2: XGBOOST =============
print("\n   → XGBoost Classifier...")

# Calcular scale_pos_weight para desbalanceo
scale_pos_weight = (y_train_balanced == 0).sum() / (y_train_balanced == 1).sum()

xgb_model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)

xgb_model.fit(X_train_balanced, y_train_balanced)
xgb_pred = xgb_model.predict(X_test)
xgb_pred_proba = xgb_model.predict_proba(X_test)[:, 1]
xgb_auc = roc_auc_score(y_test, xgb_pred_proba)

print(f"   ✓ XGBoost entrenado - AUC: {xgb_auc:.4f}")

# Guardar modelo
with open(f'{MODELS_DIR}/xgboost_model.pkl', 'wb') as f:
    pickle.dump(xgb_model, f)

# ============= MODELO 3: RED NEURONAL =============
print("\n   → Red Neuronal (Deep Learning)...")
if HAS_TF:
    # Arquitectura de la red
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

    # Entrenar con early stopping
    early_stopping = keras.callbacks.EarlyStopping(
        monitor='val_auc',
        patience=10,
        restore_best_weights=True,
        mode='max'
    )

    history = nn_model.fit(
        X_train_scaled, y_train_balanced,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        callbacks=[early_stopping],
        verbose=0
    )

    nn_pred_proba = nn_model.predict(X_test_scaled, verbose=0).flatten()
    nn_pred = (nn_pred_proba > 0.5).astype(int)
    nn_auc = roc_auc_score(y_test, nn_pred_proba)

    print(f"   ✓ Red Neuronal entrenada - AUC: {nn_auc:.4f}")

    # Guardar modelo
    nn_model.save(f'{MODELS_DIR}/neural_network_model.h5')
else:
    print("   ⚠️ TensorFlow no disponible — se omitirá el entrenamiento de la red neuronal.")
    nn_auc = None

# 5. EVALUACIÓN COMPARATIVA
print("\n[5/6] Evaluación comparativa de modelos...")

models_performance = {
    'Random Forest': {
        'AUC': rf_auc,
        'predictions': rf_pred,
        'probabilities': rf_pred_proba
    },
    'XGBoost': {
        'AUC': xgb_auc,
        'predictions': xgb_pred,
        'probabilities': xgb_pred_proba
    },
    'Neural Network': {
        'AUC': nn_auc,
        'predictions': nn_pred,
        'probabilities': nn_pred_proba
    }
}

print("\n" + "="*60)
print("RESULTADOS FINALES")
print("="*60)

for model_name, metrics in models_performance.items():
    print(f"\n{model_name}:")
    print(f"   AUC-ROC: {metrics['AUC']:.4f}")
    print(f"\n   Classification Report:")
    print(classification_report(y_test, metrics['predictions'], 
                                target_names=['Retenido', 'Churn'],
                                digits=4))

# Determinar mejor modelo
best_model_name = max(models_performance.items(), key=lambda x: x[1]['AUC'])[0]
print("\n" + "="*60)
print(f"🏆 MEJOR MODELO: {best_model_name}")
print(f"   AUC: {models_performance[best_model_name]['AUC']:.4f}")
print("="*60)

# 6. GUARDAR METADATA
print("\n[6/6] Guardando metadata...")

metadata = {
    'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'data_shape': df.shape,
    'features_used': available_features,
    'train_samples': len(X_train),
    'test_samples': len(X_test),
    'models': {
        'random_forest': {
            'auc': float(rf_auc),
            'file': 'random_forest_model.pkl'
        },
        'xgboost': {
            'auc': float(xgb_auc),
            'file': 'xgboost_model.pkl'
        },
        'neural_network': {
            'auc': float(nn_auc),
            'file': 'neural_network_model.h5'
        }
    },
    'best_model': best_model_name,
    'smote_applied': True,
    'class_distribution_train': {
        'original': float(y_train.sum()/len(y_train)),
        'balanced': float(y_train_balanced.sum()/len(y_train_balanced))
    }
}

import json
with open(f'{MODELS_DIR}/training_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=4)

print("✓ Metadata guardada")

# Guardar lista de características
with open(f'{MODELS_DIR}/features_list.txt', 'w') as f:
    for feature in available_features:
        f.write(f"{feature}\n")

print("\n" + "="*60)
print("✅ ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
print("="*60)
print(f"\nArchivos generados en '{MODELS_DIR}/':")
print("   - random_forest_model.pkl")
print("   - xgboost_model.pkl")
print("   - neural_network_model.h5")
print("   - label_encoders.pkl")
print("   - scaler.pkl")
print("   - feature_importance_rf.csv")
print("   - training_metadata.json")
print("   - features_list.txt")

print("\n🚀 Los modelos están listos para ser usados en producción!")
print("\nPara usar en Streamlit, ejecuta: streamlit run app.py\n")
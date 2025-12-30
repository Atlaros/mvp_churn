# 📊 FinTech Churn Prediction Platform

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn)
![Status](https://img.shields.io/badge/Status-MVP%20Completed-success?style=for-the-badge)

> **Una solución End-to-End para la retención de clientes: desde el análisis de datos hasta la predicción en tiempo real y la toma de decisiones operativa.**

## 📖 Descripción del Proyecto

Este proyecto es una aplicación web analítica diseñada para combatir la fuga de clientes (Churn) en el sector financiero. A diferencia de los modelos estáticos, esta plataforma ofrece una **interfaz operativa completa** que permite a los managers y equipos de marketing no solo visualizar el estado de la cartera, sino también evaluar el riesgo de clientes individuales en tiempo real.

El sistema integra un **motor de inferencia híbrido** que combina modelos de Machine Learning (Redes Neuronales, XGBoost, Random Forest) con reglas de negocio expertas, asegurando predicciones robustas incluso en escenarios de datos incompletos.

### 🌟 Características Principales (Features)

El código (`app.py`) despliega una suite completa de herramientas:

* **📊 Dashboard Ejecutivo en Tiempo Real:** Visualización interactiva de KPIs (Tasa de Churn, Retención, MRR) con gráficos avanzados de Plotly.
* **🤖 Motor de Inferencia "Ensemble":** Sistema de votación ponderada que combina:
    * 🧠 **Red Neuronal (TensorFlow):** 40% peso.
    * ⚡ **XGBoost:** 35% peso.
    * 🌲 **Random Forest:** 25% peso.
    * 🛡️ **Fallback System:** Sistema de puntuación manual (Scoring) basado en reglas si los modelos no están disponibles.
* **🎨 UI/UX Avanzada:** Diseño personalizado con CSS3 (Glassmorphism, Dark Mode, Animaciones) para una experiencia de usuario premium.
* **⚡ Sistema de Alertas Tempranas:** Detección automática de perfiles críticos (ej. clientes con quejas + inactividad >25 días) y sugerencia de acciones.
* **📈 Análisis de Segmentos:** Desglose profundo por geografía, edad y productos para identificar nichos de riesgo.
* **📋 Generación de Reportes:** Exportación automática de diagnósticos individuales en formato CSV para el equipo de ventas.

## 🛠️ Tecnologías Utilizadas

* **Frontend & Framework:** Streamlit (Python).
* **Data Processing:** Pandas, NumPy.
* **Visualización:** Plotly Express & Graph Objects (Gráficos interactivos).
* **Machine Learning:** Scikit-Learn, XGBoost, TensorFlow/Keras.
* **Persistencia:** Pickle (Serialización de modelos).
* **Diseño:** CSS3 Inyectado (Custom Styling).

## 📂 Estructura del Proyecto

```text
├── app.py                   # Aplicación principal (Streamlit)
├── requirements.txt         # Dependencias del proyecto
├── cleaned_data.csv         # Dataset procesado para el dashboard
├── notification_system.py   # Módulo de notificaciones (Simulado)
├── models/                  # Artefactos de ML entrenados
│   ├── random_forest_model.pkl
│   ├── xgboost_model.pkl
│   ├── neural_network_model.h5
│   ├── scaler.pkl           # Escalador para normalización
│   └── label_encoders.pkl   # Codificadores de categorías
├── assets/                  # Recursos estáticos
│   └── logo-no-churn.png
└── README.md                # Documentación


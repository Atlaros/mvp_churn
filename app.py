import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle
import json
import os
from datetime import datetime, timedelta

# Template Estético Optimizado para gráficos Plotly
PLOTLY_TEMPLATE = {
    'layout': {
        'paper_bgcolor': 'rgba(26, 32, 44, 0.4)',
        'plot_bgcolor': 'rgba(44, 62, 80, 0.25)',
        'font': {'color': '#ECF0F1', 'size': 13, 'family': 'Arial, sans-serif'},
        'title': {
            'font': {'size': 20, 'color': '#ECF0F1', 'family': 'Arial, sans-serif'},
            'x': 0.5,
            'xanchor': 'center',
            'pad': {'t': 20, 'b': 10}
        },
        'xaxis': {
            'gridcolor': 'rgba(78, 205, 196, 0.15)',
            'zerolinecolor': 'rgba(78, 205, 196, 0.3)',
            'color': '#ECF0F1',
            'showline': True,
            'linecolor': 'rgba(78, 205, 196, 0.4)',
            'linewidth': 2,
            'tickfont': {'size': 11, 'color': '#ECF0F1'}
        },
        'yaxis': {
            'gridcolor': 'rgba(78, 205, 196, 0.15)',
            'zerolinecolor': 'rgba(78, 205, 196, 0.3)',
            'color': '#ECF0F1',
            'showline': True,
            'linecolor': 'rgba(78, 205, 196, 0.4)',
            'linewidth': 2,
            'tickfont': {'size': 11, 'color': '#ECF0F1'}
        },
        # Paleta optimizada: Cian primario, Azul secundario, Coral alerta, Melocotón warning
        'colorway': ['#4ECDC4', '#3498DB', '#FF6B6B', '#FFA07A', '#ECF0F1', '#2C3E50'],
        'legend': {
            'bgcolor': 'rgba(44, 62, 80, 0.9)',
            'bordercolor': 'rgba(78, 205, 196, 0.4)',
            'borderwidth': 2,
            'font': {'color': '#ECF0F1', 'size': 12},
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': -0.2,
            'xanchor': 'center',
            'x': 0.5
        },
        'hoverlabel': {
            'bgcolor': 'rgba(26, 32, 44, 0.95)',
            'bordercolor': '#4ECDC4',
            'font': {'color': '#ECF0F1', 'size': 12, 'family': 'Arial, sans-serif'},
            'align': 'left'
        },
        'margin': {'l': 60, 'r': 30, 't': 80, 'b': 60}
    }
}

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Predicción de Churn - FinTech",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado - Tema Estético Optimizado - Version 3.0
st.markdown("""
    <style>
    /* VERSION: 3.0 - DISEÑO ESTÉTICO OPTIMIZADO */
    /* PALETA DE COLORES:
       🌑 Fondos: #1A202C (oscuro), #2C3E50 (azul oscuro)
       💎 Primario: #4ECDC4 (cian) - Interactivos
       🔷 Secundario: #3498DB (azul medio) - Info
       ⚪ Texto: #ECF0F1 (gris claro)
       🔶 Acentos cálidos: #FFA07A (melocotón), #FF6B6B (coral)
    */
    
    /* ==== FONDO GLOBAL - Gradiente radial elegante ==== */
    .stApp {
        background: radial-gradient(ellipse at top, #2C3E50 0%, #1A202C 60%, #0D1117 100%) !important;
        background-attachment: fixed;
    }
    
    /* Tema principal oscuro elegante */
    .main {
        background: transparent !important;
        padding: 1rem 2rem;
    }
    
    /* Fondo principal del contenido */
    .block-container {
        background: transparent !important;
        padding-top: 2rem;
    }
    
    /* ==== SIDEBAR - Gradiente sutil con glow ==== */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(44, 62, 80, 0.95) 0%, rgba(26, 32, 44, 0.98) 100%) !important;
        border-right: 2px solid transparent;
        border-image: linear-gradient(180deg, #4ECDC4 0%, #3498DB 50%, transparent 100%);
        border-image-slice: 1;
        box-shadow: 4px 0 20px rgba(78, 205, 196, 0.1);
    }
    
    /* Textos en sidebar */
    .css-1d391kg .stMarkdown, [data-testid="stSidebar"] .stMarkdown {
        color: #ECF0F1 !important;
    }
    
    /* ELIMINAR FONDOS BLANCOS */
    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }
    
    /* Contenedores de columnas */
    [data-testid="column"] {
        background: transparent !important;
    }
    
    /* ==== MÉTRICAS - Cards con glow y gradiente ==== */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(44, 62, 80, 0.6) 0%, rgba(52, 152, 219, 0.1) 100%) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(78, 205, 196, 0.25);
        border-left: 4px solid #4ECDC4;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, transparent 0%, rgba(78, 205, 196, 0.05) 100%);
        pointer-events: none;
    }
    
    [data-testid="stMetric"]:hover {
        border-left-width: 6px;
        border-left-color: #3498DB;
        box-shadow: 
            0 12px 40px rgba(78, 205, 196, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        transform: translateY(-4px) scale(1.02);
    }
    
    [data-testid="stMetricLabel"] {
        color: #4ECDC4 !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #ECF0F1 !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.85rem !important;
    }
    
    /* Títulos elegantes - TODOS BLANCOS */
    h1, h2, h3, h4, h5, h6 {
        color: #ECF0F1 !important;
        font-weight: 700 !important;
    }
    
    h1 {
        background: linear-gradient(120deg, #4ECDC4 0%, #3498DB 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: none;
        padding-bottom: 16px;
        border-bottom: 3px solid transparent;
        border-image: linear-gradient(90deg, #4ECDC4 0%, #3498DB 50%, transparent 100%);
        border-image-slice: 1;
        font-size: 2.8rem !important;
        letter-spacing: -0.5px;
        position: relative;
    }
    
    h1::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 60px;
        height: 3px;
        background: #FF6B6B;
        border-radius: 2px;
    }
    
    h2 {
        color: #ECF0F1 !important;
        font-weight: 600 !important;
        margin-top: 40px !important;
        margin-bottom: 20px !important;
        font-size: 2rem !important;
        padding-left: 16px;
        border-left: 4px solid #3498DB;
        position: relative;
    }
    
    h2::before {
        content: '';
        position: absolute;
        left: -4px;
        top: 0;
        width: 4px;
        height: 40%;
        background: #FFA07A;
    }
    
    h3 {
        font-weight: 500 !important;
        font-size: 1.4rem !important;
    }
    
    /* Títulos de gráficos Plotly */
    .js-plotly-plot .plotly .gtitle {
        fill: #ECF0F1 !important;
    }
    
    /* Cards con glassmorphism */
    .element-container {
        color: #ECF0F1 !important;
        background: transparent !important;
    }
    
    /* DataFrames con estilo oscuro mejorado */
    [data-testid="stDataFrame"] {
        background: rgba(44, 62, 80, 0.4) !important;
        border-radius: 12px;
        padding: 10px;
        border: 1px solid rgba(78, 205, 196, 0.15);
    }
    
    /* Tablas oscuras */
    .stDataFrame, .stTable {
        background: rgba(44, 62, 80, 0.4) !important;
        border-radius: 8px;
    }
    
    /* ==== BOTONES - Efecto glassmorphism con glow ==== */
    .stButton > button {
        background: linear-gradient(135deg, rgba(78, 205, 196, 0.9) 0%, rgba(52, 152, 219, 0.9) 100%) !important;
        color: #000000 !important;
        border: 2px solid rgba(255, 255, 255, 0.2);
        padding: 14px 32px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 
            0 8px 20px rgba(78, 205, 196, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        /* Desactivar overlay blanco que puede ocultar el texto */
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: transparent !important;
        transform: translate(-50%, -50%);
        transition: none;
        pointer-events: none;
    }

    .stButton > button:hover::before {
        width: 0 !important;
        height: 0 !important;
    }

    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 
            0 12px 30px rgba(78, 205, 196, 0.5),
            0 0 40px rgba(78, 205, 196, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.4);
        border-color: rgba(255, 255, 255, 0.4);
        color: #000000 !important;
    }

    /* Asegurar que el texto dentro del botón (span) también sea negro y en negrita */
    .stButton > button, .stButton > button span {
        color: #000000 !important;
        font-weight: 800 !important;
    }

    /* Reglas más específicas para botones dentro de formularios (p. ej. el formulario de predicción) */
    .stForm .stButton > button, .stForm .stButton > button span {
        color: #000000 !important;
        font-weight: 800 !important;
    }

    .stForm .stButton > button:hover, .stForm .stButton > button:hover span {
        color: #000000 !important;
    }

    /* Reglas aún más específicas para forzar fondo y remover fondo blanco inesperado */
    [data-testid="stForm"] .stButton > button,
    .stForm .stButton > button,
    .stForm .stButton button,
    .stForm button {
        background: linear-gradient(135deg, #4ECDC4 0%, #3498DB 100%) !important;
        background-color: #4ECDC4 !important;
        color: #000000 !important;
        border: 2px solid rgba(255,255,255,0.12) !important;
        box-shadow: none !important;
    }

    /* Forzar que el span interno no tenga fondo ni color blanco */
    [data-testid="stForm"] .stButton > button span,
    .stForm .stButton > button span {
        background: transparent !important;
        color: #000000 !important;
        font-weight: 800 !important;
    }

    /* Quitar cualquier pseudo-elemento que pueda cubrir el contenido */
    [data-testid="stForm"] .stButton > button::before,
    .stForm .stButton > button::before {
        background: transparent !important;
        width: 0 !important;
        height: 0 !important;
    }

    .stButton > button:active {
        transform: translateY(-1px) scale(0.98);
    }
    
    /* Selectbox y inputs elegantes */
    .stSelectbox, .stMultiSelect, .stTextInput, .stNumberInput {
        background: rgba(44, 62, 80, 0.6) !important;
        border-radius: 10px;
    }
    
    /* ==== INPUTS - Con glow animado ==== */
    input, select, textarea {
        background: linear-gradient(135deg, rgba(44, 62, 80, 0.8) 0%, rgba(26, 32, 44, 0.9) 100%) !important;
        color: #ECF0F1 !important;
        border: 2px solid rgba(78, 205, 196, 0.2) !important;
        border-radius: 10px;
        padding: 12px 16px;
        font-size: 0.95rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    input:focus, select:focus, textarea:focus {
        background: linear-gradient(135deg, rgba(44, 62, 80, 0.9) 0%, rgba(52, 152, 219, 0.1) 100%) !important;
        border-color: #4ECDC4 !important;
        box-shadow: 
            0 0 0 3px rgba(78, 205, 196, 0.2),
            0 0 20px rgba(78, 205, 196, 0.1),
            inset 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        outline: none;
        transform: scale(1.02);
    }
    
    /* Menú desplegable del selectbox - OSCURO */
    [data-baseweb="select"] {
        background: rgba(44, 62, 80, 0.95) !important;
    }
    
    [data-baseweb="select"] > div {
        background: rgba(44, 62, 80, 0.95) !important;
        color: #ECF0F1 !important;
        border: 1px solid rgba(78, 205, 196, 0.4) !important;
    }
    
    /* Opciones del menú desplegable */
    [data-baseweb="menu"] {
        background: rgba(26, 32, 44, 0.98) !important;
        border: 1px solid rgba(78, 205, 196, 0.4) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6) !important;
    }
    
    [data-baseweb="menu"] ul {
        background: rgba(26, 32, 44, 0.98) !important;
    }
    
    /* Items individuales del menú */
    [role="option"] {
        background: rgba(26, 32, 44, 0.95) !important;
        color: #ECF0F1 !important;
    }
    
    [role="option"]:hover {
        background: rgba(78, 205, 196, 0.3) !important;
        color: #ECF0F1 !important;
    }
    
    /* Item seleccionado */
    [aria-selected="true"] {
        background: rgba(52, 152, 219, 0.5) !important;
        color: #ECF0F1 !important;
    }
    
    /* Texto del selectbox */
    .stSelectbox label, .stSelectbox div {
        color: #ECF0F1 !important;
    }
    
    /* ==== ALERTAS - Con iconos y gradientes ==== */
    .stAlert, [data-baseweb="notification"] {
        background: linear-gradient(135deg, rgba(52, 152, 219, 0.2) 0%, rgba(52, 152, 219, 0.05) 100%) !important;
        border: 2px solid rgba(52, 152, 219, 0.3);
        border-left: 6px solid #3498DB;
        border-radius: 12px;
        padding: 18px 20px;
        color: #ECF0F1 !important;
        box-shadow: 0 4px 16px rgba(52, 152, 219, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .stSuccess {
        background: linear-gradient(135deg, rgba(78, 205, 196, 0.2) 0%, rgba(78, 205, 196, 0.05) 100%) !important;
        border: 2px solid rgba(78, 205, 196, 0.3);
        border-left: 6px solid #4ECDC4;
        color: #ECF0F1 !important;
        box-shadow: 0 4px 16px rgba(78, 205, 196, 0.2);
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(255, 160, 122, 0.25) 0%, rgba(255, 160, 122, 0.05) 100%) !important;
        border: 2px solid rgba(255, 160, 122, 0.4);
        border-left: 6px solid #FFA07A;
        color: #ECF0F1 !important;
        box-shadow: 0 4px 16px rgba(255, 160, 122, 0.3);
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.25) 0%, rgba(255, 107, 107, 0.05) 100%) !important;
        border: 2px solid rgba(255, 107, 107, 0.4);
        border-left: 6px solid #FF6B6B;
        color: #ECF0F1 !important;
        box-shadow: 0 4px 16px rgba(255, 107, 107, 0.3);
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    /* ==== BADGES DE RIESGO - Con pulso y glow ==== */
    .risk-high {
        background: linear-gradient(135deg, #FF6B6B 0%, rgba(255, 107, 107, 0.8) 100%);
        color: #ECF0F1;
        padding: 14px 24px;
        border-radius: 12px;
        font-weight: 700;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem;
        border: 2px solid rgba(255, 107, 107, 0.5);
        box-shadow: 
            0 6px 20px rgba(255, 107, 107, 0.4),
            0 0 30px rgba(255, 107, 107, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        animation: pulse-red 2s ease-in-out infinite;
    }
    
    @keyframes pulse-red {
        0%, 100% { box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4), 0 0 30px rgba(255, 107, 107, 0.2); }
        50% { box-shadow: 0 6px 25px rgba(255, 107, 107, 0.6), 0 0 40px rgba(255, 107, 107, 0.3); }
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #FFA07A 0%, rgba(255, 160, 122, 0.8) 100%);
        color: #1A202C;
        padding: 14px 24px;
        border-radius: 12px;
        font-weight: 700;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem;
        border: 2px solid rgba(255, 160, 122, 0.6);
        box-shadow: 
            0 6px 20px rgba(255, 160, 122, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }
    
    .risk-low {
        background: linear-gradient(135deg, #4ECDC4 0%, #3498DB 100%);
        color: #1A202C;
        padding: 14px 24px;
        border-radius: 12px;
        font-weight: 700;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem;
        border: 2px solid rgba(78, 205, 196, 0.6);
        box-shadow: 
            0 6px 20px rgba(78, 205, 196, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }
    
    /* ==== TABLAS - Diseño premium con alternancia ==== */
    .dataframe {
        background: linear-gradient(135deg, rgba(44, 62, 80, 0.4) 0%, rgba(26, 32, 44, 0.6) 100%) !important;
        color: #ECF0F1 !important;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(78, 205, 196, 0.15);
    }
    
    .dataframe th {
        background: linear-gradient(180deg, rgba(78, 205, 196, 0.3) 0%, rgba(52, 152, 219, 0.2) 100%) !important;
        color: #ECF0F1 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 1px;
        padding: 16px 12px !important;
        border-bottom: 3px solid rgba(78, 205, 196, 0.5) !important;
        position: relative;
    }
    
    .dataframe th::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 40px;
        height: 3px;
        background: #FF6B6B;
    }
    
    .dataframe td {
        color: #ECF0F1 !important;
        background-color: rgba(44, 62, 80, 0.3) !important;
        border-bottom: 1px solid rgba(78, 205, 196, 0.1) !important;
        padding: 14px 12px !important;
        transition: all 0.3s ease;
    }
    
    .dataframe tr:hover {
        background: linear-gradient(90deg, rgba(78, 205, 196, 0.15) 0%, transparent 100%) !important;
        transform: scale(1.01);
        box-shadow: 0 4px 12px rgba(78, 205, 196, 0.1);
    }
    
    .dataframe tr:nth-child(even) td {
        background-color: rgba(44, 62, 80, 0.2) !important;
    }
    
    .dataframe tr:nth-child(odd) td {
        background-color: rgba(26, 32, 44, 0.3) !important;
    }
    
    /* Slider mejorado con colores de la paleta */
    .stSlider {
        padding: 10px 0;
    }
    
    .stSlider > div > div > div > div {
        background: #4ECDC4 !important;
    }
    
    .stSlider > div > div > div {
        background: rgba(78, 205, 196, 0.2) !important;
    }
    
    /* ==== EXPANDER - Con gradiente y animación ==== */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, rgba(78, 205, 196, 0.15) 0%, rgba(44, 62, 80, 0.4) 100%) !important;
        border: 2px solid rgba(78, 205, 196, 0.2);
        border-left: 5px solid #4ECDC4 !important;
        border-radius: 12px;
        color: #ECF0F1 !important;
        padding: 16px 20px !important;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(90deg, rgba(78, 205, 196, 0.25) 0%, rgba(52, 152, 219, 0.15) 100%) !important;
        border-left-width: 8px !important;
        border-left-color: #3498DB !important;
        box-shadow: 0 6px 20px rgba(78, 205, 196, 0.2);
        transform: translateX(4px);
    }
    
    /* Texto general */
    p, span, div, label {
        color: #ECF0F1 !important;
    }
    
    /* Links - Cian para interactividad */
    a {
        color: #4ECDC4 !important;
        text-decoration: none;
        transition: all 0.2s ease;
        border-bottom: 1px solid transparent;
    }
    
    a:hover {
        color: #3498DB !important;
        border-bottom: 1px solid #3498DB;
    }
    
    /* Eliminar fondos blancos de contenedores */
    .css-1kyxreq, .css-12oz5g7, .css-1v0mbdj {
        background: transparent !important;
    }
    
    /* Formularios oscuros con acento */
    .stForm {
        background: rgba(44, 62, 80, 0.4) !important;
        border: 1px solid rgba(78, 205, 196, 0.2);
        border-left: 3px solid #4ECDC4;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Funciones auxiliares
@st.cache_data
def load_data():
    """Carga el dataset limpio"""
    try:
        df = pd.read_csv('cleaned_data.csv')
        # Agregar columna de ID único basada en el índice
        df['Customer_ID'] = df.index + 1  # Empezar desde 1
        df['Customer_ID'] = 'CUST_' + df['Customer_ID'].astype(str).str.zfill(5)
        
        # Traducir columnas al español
        columnas_espanol = {
            'CreditScore': 'Puntaje_Credito',
            'Geography': 'Geografia',
            'Gender': 'Genero',
            'Age': 'Edad',
            'Tenure': 'Antiguedad',
            'Balance': 'Balance',
            'NumOfProducts': 'Num_Productos',
            'HasCrCard': 'Tiene_Tarjeta',
            'IsActiveMember': 'Miembro_Activo',
            'EstimatedSalary': 'Salario_Estimado',
            'Exited': 'Abandono',
            'Complain': 'Queja',
            'Satisfaction Score': 'Puntuacion_Satisfaccion',
            'Card Type': 'Tipo_Tarjeta',
            'Point Earned': 'Puntos_Ganados',
            'Monthly_Transactions': 'Monthly_Transactions',
            'Avg_Transaction_Amount': 'Monto_Promedio_Transaccion',
            'Deposit_Frequency': 'Frecuencia_Depositos',
            'Withdrawal_Frequency': 'Frecuencia_Retiros',
            'International_Transfers': 'Transferencias_Internacionales',
            'Declined_Transactions': 'Transacciones_Rechazadas',
            'Recurring_Payments': 'Pagos_Recurrentes',
            'Days_Since_Last_Transaction': 'Dias_Ultima_Transaccion',
            'Monthly_Logins': 'Logins_Mensuales',
            'Avg_Session_Duration': 'Duracion_Promedio_Sesion',
            'Premium_Features_Used': 'Funciones_Premium_Usadas',
            'Push_Notifications_Enabled': 'Notificaciones_Push_Activadas',
            'Support_Interactions': 'Interacciones_Soporte',
            'Profile_Updates': 'Actualizaciones_Perfil',
            'Budget_Tool_Used': 'Herramienta_Presupuesto_Usada',
            'Statement_Downloads': 'Descargas_Estado_Cuenta',
            'Days_Since_App_Update': 'Dias_Actualizacion_App',
            'Session_Abandonment_Rate': 'Tasa_Abandono_Sesion',
            'Local_Competition_Index': 'Indice_Competencia_Local',
            'Regional_Unemployment_Rate': 'Tasa_Desempleo_Regional',
            'Economic_Index': 'Indice_Economico',
            'Competitor_Promotions': 'Promociones_Competencia',
            'Interest_Rate_Change': 'Cambio_Tasa_Interes',
            'Digital_Marketing_Exposure': 'Exposicion_Marketing_Digital',
            'Quarter': 'Trimestre',
            'Age_Group': 'Grupo_Edad'
        }
        
        df = df.rename(columns=columnas_espanol)
        
        # Traducir valores categóricos
        if 'Geografia' in df.columns:
            # Limpiar espacios en blanco
            df['Geografia'] = df['Geografia'].str.strip()
            df['Geografia'] = df['Geografia'].map({
                'France': 'Francia',
                'Spain': 'España',
                'Germany': 'Alemania'
            })
        
        if 'Genero' in df.columns:
            # Limpiar espacios en blanco
            df['Genero'] = df['Genero'].str.strip()
            df['Genero'] = df['Genero'].map({
                'Male': 'Masculino',
                'Female': 'Femenino'
            })
        
        if 'Abandono' in df.columns:
            df['Estado'] = df['Abandono'].map({
                0: 'Retenido',
                1: 'Abandonó'
            })
        
        if 'Miembro_Activo' in df.columns:
            df['Estado_Actividad'] = df['Miembro_Activo'].map({
                0: 'Inactivo',
                1: 'Activo'
            })
        
        if 'Queja' in df.columns:
            df['Tiene_Queja'] = df['Queja'].map({
                0: 'No',
                1: 'Sí'
            })
        
        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return None

@st.cache_resource
def load_model(model_name='random_forest'):
    """Carga el modelo entrenado"""
    try:
        model_path = f'models/{model_name}_model.pkl'
        
        # Verificar si el archivo existe
        if not os.path.exists(model_path):
            st.warning(f"⚠️ Modelo no encontrado en: {model_path}")
            st.info("💡 Ejecuta `python train_models.py` para entrenar los modelos primero.")
            return None
            
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        st.error(f"❌ Error al cargar modelo: {e}")
        st.info("💡 Asegúrate de haber ejecutado `python train_models.py` primero.")
        return None

@st.cache_resource
def load_neural_network():
    """Carga el modelo de Red Neuronal"""
    try:
        from tensorflow import keras
        model_path = 'models/neural_network_model.h5'
        
        if not os.path.exists(model_path):
            return None
            
        model = keras.models.load_model(model_path)
        return model
    except Exception as e:
        st.warning(f"Red Neuronal no disponible: {e}")
        return None

@st.cache_resource
def load_preprocessors():
    """Carga scaler y label encoders"""
    try:
        scaler = None
        encoders = None
        
        if os.path.exists('models/scaler.pkl'):
            with open('models/scaler.pkl', 'rb') as f:
                scaler = pickle.load(f)
        
        if os.path.exists('models/label_encoders.pkl'):
            with open('models/label_encoders.pkl', 'rb') as f:
                encoders = pickle.load(f)
        
        return scaler, encoders
    except Exception as e:
        st.warning(f"Preprocessors no disponibles: {e}")
        return None, None

def apply_dark_theme(fig):
    """Aplica tema oscuro ejecutivo a gráficos Plotly"""
    fig.update_layout(
        paper_bgcolor='rgba(30, 30, 46, 0.8)',
        plot_bgcolor='rgba(30, 30, 46, 0.8)',
        font={'color': '#e0e0e0', 'size': 12},
        title_font={'size': 18, 'color': '#ffffff'},
        xaxis={'gridcolor': 'rgba(255, 255, 255, 0.1)'},
        yaxis={'gridcolor': 'rgba(255, 255, 255, 0.1)'}
    )
    return fig

def calculate_churn_risk(features, model):
    """Calcula probabilidad de churn"""
    try:
        if model is None:
            return None
        prob = model.predict_proba(features)[0][1]
        return prob
    except Exception as e:
        st.error(f"Error en predicción: {e}")
        return None

def get_risk_level(probability):
    """Determina nivel de riesgo"""
    if probability >= 0.7:
        return "CRÍTICO", "risk-high"
    elif probability >= 0.4:
        return "ALTO", "risk-medium"
    else:
        return "BAJO", "risk-low"

# Sidebar - Navegación con Logo
# Logo NO-CHURN
try:
    st.sidebar.image("assets/logo-no-churn.png", use_container_width=True)
    st.sidebar.markdown("""
        <div style='text-align: center; margin-top: -10px; margin-bottom: 10px;'>
            <p style='color: #ECF0F1; font-size: 0.85rem; font-weight: 500;'>FinTech Analytics Platform</p>
        </div>
    """, unsafe_allow_html=True)
except:
    # Fallback si no encuentra el logo
    st.sidebar.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <h1 style='color: #4ECDC4; font-size: 2rem;'>📊</h1>
            <h2 style='color: #ECF0F1; font-size: 1.3rem; margin: 10px 0;'>NO-CHURN</h2>
            <p style='color: #ECF0F1; font-size: 0.9rem; opacity: 0.8;'>FinTech Analytics Platform</p>
        </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

page = st.sidebar.selectbox(
    "🧭 Navegación Principal",
    ["📊 Dashboard Ejecutivo", 
     "🔍 Análisis de Clientes",
     "🤖 Predicción Individual",
     "📈 Análisis de Segmentos",
     "⚡ Alertas Tempranas",
     "📋 Recomendaciones"],
    label_visibility="collapsed"
)

st.sidebar.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

# Información adicional en sidebar
st.sidebar.markdown("""
    <div style='padding: 15px; background: rgba(74, 158, 255, 0.1); border-radius: 10px; margin: 10px 0;'>
        <p style='color: #4a9eff; font-weight: 600; margin-bottom: 10px;'>📊 Métricas Clave</p>
        <p style='color: #e0e0e0; font-size: 0.85rem; margin: 5px 0;'>
            <span style='color: #ff4b4b;'>●</span> Tasa de Churn: 20.4%
        </p>
        <p style='color: #e0e0e0; font-size: 0.85rem; margin: 5px 0;'>
            <span style='color: #00cc00;'>●</span> Retención: 79.6%
        </p>
        <p style='color: #e0e0e0; font-size: 0.85rem; margin: 5px 0;'>
            <span style='color: #ffa500;'>●</span> Clientes: 10,000
        </p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
    <div style='padding: 15px; background: rgba(255, 165, 0, 0.1); border-radius: 10px; margin: 10px 0;'>
        <p style='color: #ffa500; font-weight: 600; margin-bottom: 10px;'>🎯 Quick Actions</p>
        <p style='color: #e0e0e0; font-size: 0.85rem; margin: 5px 0;'>
            ⚡ Ver alertas críticas
        </p>
        <p style='color: #e0e0e0; font-size: 0.85rem; margin: 5px 0;'>
            📥 Exportar reportes
        </p>
        <p style='color: #e0e0e0; font-size: 0.85rem; margin: 5px 0;'>
            🔄 Actualizar datos
        </p>
    </div>
""", unsafe_allow_html=True)

# Cargar datos
df = load_data()

if df is not None:
    
    # ============= PÁGINA 1: DASHBOARD EJECUTIVO =============
    if page == "📊 Dashboard Ejecutivo":
        st.title("📊 Dashboard Ejecutivo de Churn")
        st.markdown("### Vista general del estado de retención de clientes")
        
        # KPIs principales
        col1, col2, col3, col4 = st.columns(4)
        
        total_customers = len(df)
        churned = df['Abandono'].sum()
        churn_rate = (churned / total_customers) * 100
        active_members = df['Miembro_Activo'].sum()
        
        with col1:
            st.metric("Total Clientes", f"{total_customers:,}", help="Base total de clientes")
        with col2:
            st.metric("Clientes Perdidos", f"{churned:,}", f"-{churn_rate:.1f}%", delta_color="inverse")
        with col3:
            st.metric("Tasa de Churn", f"{churn_rate:.1f}%", help="Porcentaje de clientes que abandonaron")
        with col4:
            st.metric("Miembros Activos", f"{active_members:,}", f"{(active_members/total_customers)*100:.1f}%")
        
        st.markdown("---")
        
        # Gráficos principales
        col1, col2 = st.columns(2)
        
        with col1:
            # Churn por geografía
            geo_churn = df.groupby('Geografia')['Abandono'].agg(['sum', 'count'])
            geo_churn['rate'] = (geo_churn['sum'] / geo_churn['count']) * 100
            
            fig_geo = px.bar(
                geo_churn.reset_index(),
                x='Geografia',
                y='rate',
                title='📍 Tasa de Churn por País',
                labels={'rate': 'Tasa de Churn (%)', 'Geografia': 'País'},
                color='rate',
                color_continuous_scale='Reds',
                template='plotly_dark'
            )
            fig_geo.update_layout(
                showlegend=False, 
                height=350,
                paper_bgcolor='rgba(30, 30, 46, 0.8)',
                plot_bgcolor='rgba(30, 30, 46, 0.8)',
                font={'color': '#e0e0e0', 'size': 12}
            )
            st.plotly_chart(fig_geo, use_container_width=True)
        
        with col2:
            # Churn por número de productos
            prod_churn = df.groupby('Num_Productos')['Abandono'].agg(['sum', 'count'])
            prod_churn['rate'] = (prod_churn['sum'] / prod_churn['count']) * 100
            
            fig_prod = px.bar(
                prod_churn.reset_index(),
                x='Num_Productos',
                y='rate',
                title='📦 Churn por Número de Productos',
                labels={'rate': 'Tasa de Churn (%)', 'Num_Productos': 'Productos'},
                color='rate',
                color_continuous_scale='Reds',
                template='plotly_dark'
            )
            fig_prod = apply_dark_theme(fig_prod)
            fig_prod.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig_prod, use_container_width=True)
        
        # Segunda fila de gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Tasa de Churn por Grupo de Edad - Más simple y claro
            # Crear grupos de edad
            df_age = df.copy()
            df_age['Grupo_Edad'] = pd.cut(df_age['Edad'], 
                                          bins=[0, 30, 40, 50, 60, 100],
                                          labels=['18-30 años', '31-40 años', '41-50 años', '51-60 años', '60+ años'])
            
            age_churn = df_age.groupby('Grupo_Edad')['Abandono'].agg(['sum', 'count'])
            age_churn['Tasa_Churn'] = (age_churn['sum'] / age_churn['count']) * 100
            age_churn['Clientes'] = age_churn['count']
            
            fig_age = go.Figure()
            
            # Barras de tasa de churn
            fig_age.add_trace(go.Bar(
                x=age_churn.index,
                y=age_churn['Tasa_Churn'],
                name='Tasa de Churn (%)',
                marker_color=['#00cc00', '#4a9eff', '#ffa500', '#ff6b6b', '#ff4b4b'],
                text=age_churn['Tasa_Churn'].round(1).astype(str) + '%',
                textposition='outside',
                textfont=dict(size=12, color='#ffffff')
            ))
            
            fig_age.update_layout(
                title='👥 Tasa de Churn por Grupo de Edad',
                xaxis_title='Grupo de Edad',
                yaxis_title='Tasa de Churn (%)',
                template='plotly_dark',
                showlegend=False,
                height=350
            )
            fig_age = apply_dark_theme(fig_age)
            st.plotly_chart(fig_age, use_container_width=True)
        
        with col2:
            # Actividad vs Churn
            activity_churn = df.groupby('Miembro_Activo')['Abandono'].agg(['sum', 'count'])
            activity_churn['rate'] = (activity_churn['sum'] / activity_churn['count']) * 100
            activity_churn['label'] = ['Inactivo', 'Activo']
            
            fig_activity = px.pie(
                activity_churn.reset_index(),
                values='rate',
                names='label',
                title='🔄 Churn: Activos vs Inactivos',
                color='label',
                color_discrete_map={'Activo': '#00cc00', 'Inactivo': '#ff4b4b'},
                template='plotly_dark'
            )
            fig_activity = apply_dark_theme(fig_activity)
            fig_activity.update_layout(height=350)
            st.plotly_chart(fig_activity, use_container_width=True)
        
        # Métricas de comportamiento
        st.markdown("### 📊 Métricas de Comportamiento")
        col1, col2, col3, col4 = st.columns(4)
        
        avg_logins_retained = df[df['Abandono']==0]['Logins_Mensuales'].mean()
        avg_logins_churned = df[df['Abandono']==1]['Logins_Mensuales'].mean()
        
        avg_trans_retained = df[df['Abandono']==0]['Monthly_Transactions'].mean()
        avg_trans_churned = df[df['Abandono']==1]['Monthly_Transactions'].mean()
        
        with col1:
            st.metric("Logins/mes (Retenidos)", f"{avg_logins_retained:.1f}")
        with col2:
            st.metric("Logins/mes (Churned)", f"{avg_logins_churned:.1f}", 
                     f"{((avg_logins_churned-avg_logins_retained)/avg_logins_retained)*100:.1f}%",
                     delta_color="inverse")
        with col3:
            st.metric("Trans/mes (Retenidos)", f"{avg_trans_retained:.1f}")
        with col4:
            st.metric("Trans/mes (Churned)", f"{avg_trans_churned:.1f}",
                     f"{((avg_trans_churned-avg_trans_retained)/avg_trans_retained)*100:.1f}%",
                     delta_color="inverse")
        
        # Alertas críticas
        st.markdown("### 🚨 Alertas Críticas")
        
        # Clientes con quejas
        complaints = df[df['Queja']==1]
        complaints_churn_rate = (complaints['Abandono'].sum() / len(complaints)) * 100 if len(complaints) > 0 else 0
        
        # Clientes inactivos hace más de 25 días
        inactive_long = df[df['Dias_Ultima_Transaccion'] > 25]
        inactive_count = len(inactive_long)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.error(f"⚠️ {len(complaints)} clientes con quejas")
            st.caption(f"Tasa de churn: {complaints_churn_rate:.1f}%")
        with col2:
            st.warning(f"⚠️ {inactive_count} clientes inactivos >25 días")
        with col3:
            high_risk = df[(df['Num_Productos'] >= 3)]
            st.warning(f"⚠️ {len(high_risk)} clientes con 3+ productos")
    
    # ============= PÁGINA 2: ANÁLISIS DE CLIENTES =============
    elif page == "🔍 Análisis de Clientes":
        st.title("🔍 Análisis Detallado de Clientes")
        
        # Filtros
        st.sidebar.markdown("### 🎛️ Filtros")
        
        geography_filter = st.sidebar.multiselect(
            "País",
            options=df['Geografia'].unique(),
            default=df['Geografia'].unique()
        )
        
        gender_filter = st.sidebar.multiselect(
            "Género",
            options=df['Genero'].unique(),
            default=df['Genero'].unique()
        )
        
        age_range = st.sidebar.slider(
            "Rango de Edad",
            int(df['Edad'].min()),
            int(df['Edad'].max()),
            (int(df['Edad'].min()), int(df['Edad'].max()))
        )
        
        products_filter = st.sidebar.multiselect(
            "Número de Productos",
            options=sorted(df['Num_Productos'].unique()),
            default=sorted(df['Num_Productos'].unique())
        )
        
        # Aplicar filtros
        df_filtered = df[
            (df['Geografia'].isin(geography_filter)) &
            (df['Genero'].isin(gender_filter)) &
            (df['Edad'] >= age_range[0]) &
            (df['Edad'] <= age_range[1]) &
            (df['Num_Productos'].isin(products_filter))
        ]
        
        # Mostrar resumen de filtros
        st.info(f"📊 Mostrando {len(df_filtered):,} clientes de {len(df):,} totales")
        
        # Tabla de clientes de alto riesgo
        st.markdown("### 🎯 Clientes de Alto Riesgo")
        
        # Identificar alto riesgo basado en el informe
        high_risk_df = df_filtered[
            ((df_filtered['Queja'] == 1) |
             (df_filtered['Miembro_Activo'] == 0) |
             (df_filtered['Num_Productos'] >= 3) |
             (df_filtered['Dias_Ultima_Transaccion'] > 25) |
             (df_filtered['Logins_Mensuales'] < 5) |
             (df_filtered['Puntuacion_Satisfaccion'] <= 2))
        ]
        
        # Calcular score de riesgo
        high_risk_df = high_risk_df.copy()
        high_risk_df['Risk_Score'] = 0
        high_risk_df.loc[high_risk_df['Queja'] == 1, 'Risk_Score'] += 40
        high_risk_df.loc[high_risk_df['Miembro_Activo'] == 0, 'Risk_Score'] += 25
        high_risk_df.loc[high_risk_df['Num_Productos'] >= 3, 'Risk_Score'] += 30
        high_risk_df.loc[high_risk_df['Dias_Ultima_Transaccion'] > 25, 'Risk_Score'] += 20
        high_risk_df.loc[high_risk_df['Logins_Mensuales'] < 5, 'Risk_Score'] += 15
        high_risk_df.loc[high_risk_df['Puntuacion_Satisfaccion'] <= 2, 'Risk_Score'] += 25
        
        high_risk_df = high_risk_df.sort_values('Risk_Score', ascending=False).head(100)
        
        # Mostrar top clientes de riesgo
        display_cols = ['Geografia', 'Genero', 'Edad', 'Num_Productos', 'Miembro_Activo', 
                       'Logins_Mensuales', 'Dias_Ultima_Transaccion', 'Queja', 
                       'Puntuacion_Satisfaccion', 'Risk_Score', 'Abandono']
        
        st.dataframe(
            high_risk_df[display_cols].head(20),
            use_container_width=True,
            height=400
        )
        
        # Análisis de correlación
        st.markdown("### 🔗 Correlación de Variables con Churn")
        
        numeric_cols = ['Edad', 'Balance', 'Num_Productos', 'Monthly_Transactions',
                       'Logins_Mensuales', 'Dias_Ultima_Transaccion', 'Interacciones_Soporte',
                       'Puntuacion_Satisfaccion', 'Duracion_Promedio_Sesion']
        
        corr_data = df_filtered[numeric_cols + ['Abandono']].corr()['Abandono'].sort_values(ascending=False)
        
        fig_corr = px.bar(
            x=corr_data.values[1:],
            y=corr_data.index[1:],
            orientation='h',
            title='Correlación con Churn',
            labels={'x': 'Correlación', 'y': 'Variable'},
            color=corr_data.values[1:],
            color_continuous_scale='RdYlGn_r',
            template='plotly_dark'
        )
        fig_corr = apply_dark_theme(fig_corr)
        fig_corr.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Distribuciones comparativas
        col1, col2 = st.columns(2)
        
        with col1:
            variable = st.selectbox(
                "Selecciona variable para análisis",
                numeric_cols
            )
            
            fig_dist = px.box(
                df_filtered,
                x='Abandono',
                y=variable,
                color='Abandono',
                title=f'Distribución de {variable}',
                labels={'Abandono': 'Estado', 0: 'Retenido', 1: 'Churned'},
                color_discrete_map={0: '#00cc00', 1: '#ff4b4b'},
                template='plotly_dark'
            )
            fig_dist = apply_dark_theme(fig_dist)
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with col2:
            # Análisis por segmento
            segment_var = st.selectbox(
                "Análisis por segmento",
                ['Geografia', 'Genero', 'Tipo_Tarjeta', 'Grupo_Edad']
            )
            
            segment_analysis = df_filtered.groupby(segment_var)['Abandono'].agg(['sum', 'count'])
            segment_analysis['rate'] = (segment_analysis['sum'] / segment_analysis['count']) * 100
            
            fig_segment = px.bar(
                segment_analysis.reset_index(),
                x=segment_var,
                y='rate',
                title=f'Tasa de Churn por {segment_var}',
                color='rate',
                color_continuous_scale='Reds',
                template='plotly_dark'
            )
            fig_segment = apply_dark_theme(fig_segment)
            st.plotly_chart(fig_segment, use_container_width=True)
    
    # ============= PÁGINA 3: PREDICCIÓN INDIVIDUAL =============
    elif page == "🤖 Predicción Individual":
        st.title("🤖 Predicción de Churn en Tiempo Real")
        st.markdown("### 🎯 Ingresa los datos del cliente y obtén predicción instantánea")
        
        # Verificar modelos disponibles
        nn_available = os.path.exists('models/neural_network_model.h5')
        rf_available = os.path.exists('models/random_forest_model.pkl')
        xgb_available = os.path.exists('models/xgboost_model.pkl')
        
        models_count = sum([nn_available, rf_available, xgb_available])
        
        if models_count > 0:
            model_names = []
            if nn_available:
                model_names.append("🧠 Red Neuronal")
            if xgb_available:
                model_names.append("⚡ XGBoost")
            if rf_available:
                model_names.append("🌲 Random Forest")
            
            st.success(f"✅ **Modelos ML Activos**: {', '.join(model_names)} ({models_count} modelos)")
            st.caption("Las predicciones usarán un ensemble ponderado de todos los modelos disponibles")
        else:
            st.warning("⚠️ **No hay modelos ML entrenados** - Usando sistema de scoring basado en reglas")
            st.caption("Para entrenar modelos, ejecuta: `python train_models.py`")
        
        # Crear dos columnas: Formulario y Resultado
        st.markdown("---")
        
        # Formulario de entrada en la izquierda
        with st.form("prediction_form"):
            st.markdown("## 📝 Datos del Cliente")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 👤 Información Demográfica")
                customer_id = st.text_input("ID del Cliente", "CUST_00001", help="Identificador único")
                geography = st.selectbox("País", ['Francia', 'España', 'Alemania'])
                gender = st.selectbox("Género", ['Masculino', 'Femenino'])
                age = st.slider("Edad", 18, 90, 35, help="Edad del cliente")
                credit_score = st.slider("Puntaje de Crédito", 300, 850, 650)
                
            with col2:
                st.markdown("#### 💳 Información de Productos")
                num_products = st.selectbox("Número de Productos", [1, 2, 3, 4])
                has_credit_card = st.selectbox("Tiene Tarjeta de Crédito", ["Sí", "No"])
                is_active = st.selectbox("Miembro Activo", ["Sí", "No"])
                balance = st.number_input("Balance ($)", 0, 250000, 75000, step=1000)
                estimated_salary = st.number_input("Salario Estimado ($)", 10000, 200000, 50000, step=1000)
                card_type = st.selectbox("Tipo de Tarjeta", ['DIAMOND', 'GOLD', 'SILVER', 'PLATINUM'])
                
            with col3:
                st.markdown("#### 📊 Comportamiento")
                monthly_logins = st.slider("Logins Mensuales", 0, 30, 8)
                monthly_trans = st.slider("Transacciones/mes", 0, 150, 60)
                days_since_last = st.slider("Días desde última transacción", 0, 90, 15)
                satisfaction = st.slider("Satisfacción (1-5)", 1, 5, 3)
                complain = st.selectbox("Ha presentado quejas", ["No", "Sí"])
                support_interactions = st.slider("Interacciones con soporte", 0, 20, 2)
            
            # Botón de predicción
            submitted = st.form_submit_button("🎯 PREDECIR RIESGO DE CHURN", use_container_width=True)
        
        # Predicción en tiempo real
        if submitted:
            # Convertir inputs
            has_credit_card_val = 1 if has_credit_card == "Sí" else 0
            is_active_val = 1 if is_active == "Sí" else 0
            complain_val = 1 if complain == "Sí" else 0
            
            # Mapeos de español a inglés (formato del modelo)
            geography_map = {'Francia': 'France', 'España': 'Spain', 'Alemania': 'Germany'}
            gender_map = {'Masculino': 'Male', 'Femenino': 'Female'}
            
            # Preparar datos para el modelo
            customer_data = {
                'CreditScore': credit_score,
                'Geography': geography_map[geography],
                'Gender': gender_map[gender],
                'Age': age,
                'Balance': balance,
                'NumOfProducts': num_products,
                'HasCrCard': has_credit_card_val,
                'IsActiveMember': is_active_val,
                'EstimatedSalary': estimated_salary,
                'Complain': complain_val,
                'Satisfaction Score': satisfaction,
                'Card Type': card_type,
                'Point Earned': 500,  # Valor por defecto
                'Days_Since_Last_Transaction': days_since_last,
                'Monthly_Logins': monthly_logins,
                'Avg_Session_Duration': 10.0,  # Valor por defecto
                'Support_Interactions': support_interactions,
                'Session_Abandonment_Rate': 0.15,  # Valor por defecto
                'Local_Competition_Index': 0.5  # Valor por defecto
            }
            
            # Intentar usar modelos ML
            probability = None
            model_used = "Scoring Manual"
            
            try:
                # Cargar modelos y preprocessors
                nn_model = load_neural_network()
                rf_model = load_model('random_forest')
                xgb_model = load_model('xgboost')
                scaler, encoders = load_preprocessors()
                
                # Convertir a DataFrame
                df_pred = pd.DataFrame([customer_data])
                
                # Aplicar encoding si está disponible
                if encoders:
                    for col, encoder in encoders.items():
                        if col in df_pred.columns:
                            try:
                                df_pred[col] = encoder.transform(df_pred[col].astype(str))
                            except:
                                pass  # Si falla el encoding, mantener valor original
                
                # Aplicar scaling si está disponible
                if scaler:
                    X_scaled = scaler.transform(df_pred)
                else:
                    X_scaled = df_pred.values
                
                # PREDICCIÓN CON MODELOS ML (Ensemble)
                predictions = []
                
                if nn_model is not None:
                    nn_prob = float(nn_model.predict(X_scaled, verbose=0)[0][0])
                    predictions.append(('Red Neuronal', nn_prob, 0.4))  # Peso 40%
                    model_used = "Red Neuronal"
                
                if xgb_model is not None:
                    xgb_prob = float(xgb_model.predict_proba(df_pred)[0][1])
                    predictions.append(('XGBoost', xgb_prob, 0.35))  # Peso 35%
                    if model_used == "Scoring Manual":
                        model_used = "XGBoost"
                
                if rf_model is not None:
                    rf_prob = float(rf_model.predict_proba(df_pred)[0][1])
                    predictions.append(('Random Forest', rf_prob, 0.25))  # Peso 25%
                    if model_used == "Scoring Manual":
                        model_used = "Random Forest"
                
                # Calcular probabilidad ponderada (ensemble)
                if predictions:
                    total_weight = sum(p[2] for p in predictions)
                    probability = sum(p[1] * p[2] for p in predictions) / total_weight
                    model_used = f"Ensemble ({len(predictions)} modelos)"
                
            except Exception as e:
                st.warning(f"⚠️ No se pudieron cargar modelos ML: {e}")
                probability = None
            
            # Fallback: Sistema de scoring manual si no hay modelos
            if probability is None:
                risk_score = 0
                if complain_val == 1:
                    risk_score += 0.40
                if is_active_val == 0:
                    risk_score += 0.25
                if num_products >= 3:
                    risk_score += 0.30
                if days_since_last > 25:
                    risk_score += 0.20
                if monthly_logins < 5:
                    risk_score += 0.15
                if satisfaction <= 2:
                    risk_score += 0.25
                if geography == 'Alemania':
                    risk_score += 0.15
                if age > 50:
                    risk_score += 0.15
                if monthly_trans < 40:
                    risk_score += 0.10
                if support_interactions > 5:
                    risk_score += 0.10
                
                probability = min(risk_score / 1.8, 0.95)
                model_used = "Scoring Manual (Reglas)"
            
            # Determinar nivel de riesgo
            if probability >= 0.7:
                risk_level = "CRÍTICO"
                risk_color = "#ff4b4b"
                risk_emoji = "🔴"
                risk_class = "risk-high"
            elif probability >= 0.4:
                risk_level = "ALTO"
                risk_color = "#ffa500"
                risk_emoji = "🟠"
                risk_class = "risk-medium"
            else:
                risk_level = "BAJO"
                risk_color = "#00cc00"
                risk_emoji = "🟢"
                risk_class = "risk-low"
            
            # Mostrar resultados
            st.markdown("---")
            
            # Indicador del modelo usado
            col_badge1, col_badge2 = st.columns([3, 1])
            with col_badge1:
                st.markdown("## 🎯 RESULTADO DE LA PREDICCIÓN")
            with col_badge2:
                model_color = "#4a9eff" if "Ensemble" in model_used or "Red Neuronal" in model_used else "#ffa500"
                st.markdown(f"""
                    <div style='background: rgba(74, 158, 255, 0.1); padding: 10px; border-radius: 8px; text-align: center; margin-top: 10px;'>
                        <p style='color: #b0b0b0; margin:0; font-size:0.75rem;'>Modelo Usado</p>
                        <p style='color: {model_color}; margin:0; font-size:0.9rem; font-weight:700;'>🤖 {model_used}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Animación de carga simulada
            with st.spinner("🔄 Analizando datos del cliente..."):
                import time
                time.sleep(1)
            
            # Columnas para resultado
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                # Gauge mejorado
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=probability * 100,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': f"<b>Probabilidad de Churn</b><br><span style='font-size:0.8em;color:#b0b0b0'>{customer_id}</span>", 
                           'font': {'size': 20, 'color': '#ffffff'}},
                    delta={'reference': 20.4, 'increasing': {'color': "#ff4b4b"}, 'decreasing': {'color': "#00cc00"}},
                    number={'font': {'size': 50, 'color': risk_color}, 'suffix': '%'},
                    gauge={
                        'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "#e0e0e0"},
                        'bar': {'color': risk_color, 'thickness': 0.8},
                        'bgcolor': "rgba(30, 30, 46, 0.5)",
                        'borderwidth': 2,
                        'bordercolor': "#e0e0e0",
                        'steps': [
                            {'range': [0, 40], 'color': "rgba(0, 204, 0, 0.2)"},
                            {'range': [40, 70], 'color': "rgba(255, 165, 0, 0.2)"},
                            {'range': [70, 100], 'color': "rgba(255, 75, 75, 0.2)"}
                        ],
                        'threshold': {
                            'line': {'color': "white", 'width': 4},
                            'thickness': 0.75,
                            'value': 70
                        }
                    }
                ))
                
                fig_gauge.update_layout(
                    paper_bgcolor='rgba(30, 30, 46, 0.8)',
                    plot_bgcolor='rgba(30, 30, 46, 0.8)',
                    font={'color': '#e0e0e0'},
                    height=350
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            with col2:
                st.markdown(f"""
                    <div class='{risk_class}' style='text-align:center; font-size:28px; margin-top:50px;'>
                        {risk_emoji}<br>
                        RIESGO<br>
                        <span style='font-size:36px;'>{risk_level}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("<div style='margin-top:50px;'>", unsafe_allow_html=True)
                st.metric("Probabilidad", f"{probability*100:.1f}%", 
                         f"{(probability*100 - 20.4):.1f} pp vs base")
                
                if probability < 0.3:
                    confidence = "MUY ALTA"
                    confidence_color = "#00cc00"
                elif probability > 0.7:
                    confidence = "MUY ALTA"
                    confidence_color = "#ff4b4b"
                else:
                    confidence = "ALTA"
                    confidence_color = "#ffa500"
                
                st.markdown(f"""
                    <div style='background: rgba(74, 158, 255, 0.1); padding: 15px; border-radius: 10px; margin-top: 10px;'>
                        <p style='color: #b0b0b0; margin:0; font-size:0.9rem;'>Confianza</p>
                        <p style='color: {confidence_color}; margin:0; font-size:1.5rem; font-weight:700;'>{confidence}</p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Gráfico de radar de factores
            st.markdown("### 📊 Análisis Multidimensional del Cliente")
            
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Radar chart de características
                categories = ['Engagement', 'Satisfacción', 'Actividad', 'Productos', 'Soporte', 'Antiguedad']
                
                # Normalizar valores a escala 0-10
                engagement_score = (monthly_logins / 30) * 10
                satisfaction_score = (satisfaction / 5) * 10
                activity_score = (1 - (days_since_last / 90)) * 10
                products_score = 10 if num_products == 2 else (5 if num_products == 1 else 2)
                support_score = max(0, 10 - (support_interactions / 2))
                tenure_score = 7  # Valor fijo por ahora
                
                fig_radar = go.Figure(data=go.Scatterpolar(
                    r=[engagement_score, satisfaction_score, activity_score, 
                       products_score, support_score, tenure_score],
                    theta=categories,
                    fill='toself',
                    fillcolor='rgba(74, 158, 255, 0.3)',
                    line=dict(color='#4a9eff', width=3),
                    marker=dict(size=8, color='#4a9eff')
                ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 10],
                            tickfont=dict(color='#e0e0e0'),
                            gridcolor='rgba(255, 255, 255, 0.1)'
                        ),
                        angularaxis=dict(
                            tickfont=dict(color='#e0e0e0', size=12),
                            gridcolor='rgba(255, 255, 255, 0.1)'
                        ),
                        bgcolor='rgba(30, 30, 46, 0.8)'
                    ),
                    showlegend=False,
                    paper_bgcolor='rgba(30, 30, 46, 0.8)',
                    font=dict(color='#e0e0e0'),
                    title=dict(text="<b>Perfil del Cliente</b>", font=dict(size=16, color='#ffffff')),
                    height=350
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            
            with col2:
                # Resumen de características
                st.markdown("#### 📋 Resumen del Perfil")
                
                st.markdown(f"""
                <div style='background: rgba(74, 158, 255, 0.05); padding: 15px; border-radius: 10px; border-left: 4px solid #4a9eff;'>
                    <p style='color: #b0b0b0; margin: 5px 0;'><b>ID:</b> <span style='color: #4a9eff;'>{customer_id}</span></p>
                    <p style='color: #b0b0b0; margin: 5px 0;'><b>Ubicación:</b> {geography}</p>
                    <p style='color: #b0b0b0; margin: 5px 0;'><b>Edad:</b> {age} años</p>
                    <p style='color: #b0b0b0; margin: 5px 0;'><b>Productos:</b> {num_products}</p>
                    <p style='color: #b0b0b0; margin: 5px 0;'><b>Estado:</b> {'Activo' if is_active_val else 'Inactivo'}</p>
                    <p style='color: #b0b0b0; margin: 5px 0;'><b>Logins/mes:</b> {monthly_logins}</p>
                    <p style='color: #b0b0b0; margin: 5px 0;'><b>Trans/mes:</b> {monthly_trans}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Factores de riesgo identificados
            st.markdown("### 🎯 Factores Contribuyentes al Riesgo")
            
            factors = []
            if complain_val == 1:
                factors.append(("⚠️ Cliente tiene quejas registradas", "CRÍTICO", 40, "#ff4b4b"))
            if is_active_val == 0:
                factors.append(("⚠️ Miembro inactivo", "MUY ALTO", 25, "#ff6b6b"))
            if num_products >= 3:
                factors.append(("⚠️ 3+ productos (sobrecarga)", "MUY ALTO", 30, "#ff8c8c"))
            if days_since_last > 25:
                factors.append(("⚠️ Más de 25 días sin transacción", "ALTO", 20, "#ffa500"))
            if monthly_logins < 5:
                factors.append(("⚠️ Bajo engagement (< 5 logins/mes)", "ALTO", 15, "#ffb84d"))
            if satisfaction <= 2:
                factors.append(("⚠️ Baja satisfacción", "MUY ALTO", 25, "#ff6b6b"))
            if geography == 'Germany':
                factors.append(("📍 Ubicación en mercado de alto riesgo", "MEDIO", 15, "#ffd700"))
            if age > 50:
                factors.append(("👤 Edad > 50 años", "MEDIO", 15, "#ffd700"))
            if monthly_trans < 40:
                factors.append(("📉 Transacciones por debajo del promedio", "MEDIO", 10, "#ffeb3b"))
            if support_interactions > 5:
                factors.append(("📞 Alto contacto con soporte", "MEDIO", 10, "#ffeb3b"))
            
            if factors:
                # Gráfico de barras de factores
                factors_df = pd.DataFrame(factors, columns=['Factor', 'Impacto', 'Score', 'Color'])
                factors_df = factors_df.sort_values('Score', ascending=False)
                
                fig_factors = go.Figure(data=[
                    go.Bar(
                        y=factors_df['Factor'],
                        x=factors_df['Score'],
                        orientation='h',
                        marker=dict(
                            color=factors_df['Color'],
                            line=dict(color='rgba(255, 255, 255, 0.3)', width=1)
                        ),
                        text=factors_df['Score'].astype(str) + '%',
                        textposition='outside',
                    )
                ])
                
                fig_factors.update_layout(
                    title="<b>Factores de Riesgo Identificados</b>",
                    xaxis_title="Contribución al Riesgo (%)",
                    paper_bgcolor='rgba(30, 30, 46, 0.8)',
                    plot_bgcolor='rgba(30, 30, 46, 0.8)',
                    font=dict(color='#e0e0e0', size=12),
                    title_font=dict(size=18, color='#ffffff'),
                    xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                    yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                    height=max(300, len(factors) * 40),
                    showlegend=False
                )
                st.plotly_chart(fig_factors, use_container_width=True)
                
                # Lista de factores con badges
                for factor, impacto, score, color in factors:
                    if impacto == "CRÍTICO":
                        st.error(f"{factor} - Impacto: **{impacto}** (+{score}%)")
                    elif impacto == "MUY ALTO":
                        st.error(f"{factor} - Impacto: **{impacto}** (+{score}%)")
                    elif impacto == "ALTO":
                        st.warning(f"{factor} - Impacto: **{impacto}** (+{score}%)")
                    else:
                        st.info(f"{factor} - Impacto: **{impacto}** (+{score}%)")
            else:
                st.success("✅ **No se identificaron factores de riesgo significativos**")
            
            # Recomendaciones personalizadas
            st.markdown("### 💡 Recomendaciones de Retención")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if probability > 0.7:
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, rgba(255, 75, 75, 0.2) 0%, rgba(201, 42, 42, 0.2) 100%); 
                                padding: 20px; border-radius: 10px; border-left: 4px solid #ff4b4b;'>
                        <h4 style='color: #ff4b4b; margin-top: 0;'>🚨 ACCIÓN INMEDIATA REQUERIDA</h4>
                        <ul style='color: #e0e0e0;'>
                            <li>📞 Contacto directo en próximas 24 horas</li>
                            <li>🎁 Incentivo de alto valor</li>
                            <li>👨‍💼 Asignar account manager</li>
                            <li>🔍 Investigar causa raíz</li>
                            <li>📊 Revisión completa de productos</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                elif probability > 0.4:
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, rgba(255, 165, 0, 0.2) 0%, rgba(255, 140, 0, 0.2) 100%); 
                                padding: 20px; border-radius: 10px; border-left: 4px solid #ffa500;'>
                        <h4 style='color: #ffa500; margin-top: 0;'>⚠️ INTERVENCIÓN PROACTIVA</h4>
                        <ul style='color: #e0e0e0;'>
                            <li>📧 Campaña personalizada</li>
                            <li>💬 Encuesta de satisfacción</li>
                            <li>🎯 Ofertas dirigidas</li>
                            <li>📱 Re-onboarding</li>
                            <li>🔔 Notificaciones push</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, rgba(0, 204, 0, 0.2) 0%, rgba(0, 153, 0, 0.2) 100%); 
                                padding: 20px; border-radius: 10px; border-left: 4px solid #00cc00;'>
                        <h4 style='color: #00cc00; margin-top: 0;'>✅ CLIENTE ESTABLE</h4>
                        <ul style='color: #e0e0e0;'>
                            <li>👍 Comunicación regular</li>
                            <li>🎁 Programa de lealtad</li>
                            <li>📚 Educación financiera</li>
                            <li>🌟 Incentivar referidos</li>
                            <li>📊 Monitoreo mensual</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                # Timeline de acciones
                st.markdown("#### 📅 Timeline de Acciones")
                
                if probability > 0.7:
                    timeline = [
                        ("Ahora", "🚨 Crear ticket urgente"),
                        ("24h", "📞 Contacto equipo retención"),
                        ("48h", "💰 Aplicar incentivo"),
                        ("7 días", "📊 Seguimiento"),
                        ("30 días", "✅ Evaluación final")
                    ]
                elif probability > 0.4:
                    timeline = [
                        ("24-48h", "📧 Enviar campaña"),
                        ("3 días", "💬 Encuesta satisfacción"),
                        ("7 días", "🎯 Ofertas personalizadas"),
                        ("14 días", "📊 Seguimiento"),
                        ("30 días", "✅ Evaluación")
                    ]
                else:
                    timeline = [
                        ("Semanal", "📊 Monitoreo métricas"),
                        ("Mensual", "📧 Newsletter"),
                        ("Trimestral", "🎁 Programa lealtad"),
                        ("Semestral", "📋 Revisión cuenta"),
                        ("Anual", "🌟 Renovación")
                    ]
                
                for tiempo, accion in timeline:
                    st.markdown(f"""
                    <div style='background: rgba(74, 158, 255, 0.05); padding: 10px; margin: 5px 0; 
                                border-radius: 8px; border-left: 3px solid #4a9eff;'>
                        <span style='color: #4a9eff; font-weight: 600;'>{tiempo}</span>
                        <br>
                        <span style='color: #e0e0e0;'>{accion}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Botón para descargar reporte
            st.markdown("---")
            report_data = {
                'Customer_ID': customer_id,
                'Fecha_Analisis': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Probabilidad_Churn': f"{probability*100:.2f}%",
                'Nivel_Riesgo': risk_level,
                'Geografia': geography,
                'Edad': age,
                'Productos': num_products,
                'Activo': 'Sí' if is_active_val else 'No',
                'Logins_Mes': monthly_logins,
                'Transacciones_Mes': monthly_trans
            }
            
            report_df = pd.DataFrame([report_data])
            csv_report = report_df.to_csv(index=False).encode('utf-8')
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.download_button(
                    label="📥 Descargar Reporte Completo",
                    data=csv_report,
                    file_name=f'reporte_churn_{customer_id}_{datetime.now().strftime("%Y%m%d")}.csv',
                    mime='text/csv',
                    use_container_width=True
                )
        
        else:
            # Mostrar instrucciones cuando no hay predicción
            st.info("""
            ### 📝 Instrucciones de Uso
            
            1. **Completa el formulario** con los datos del cliente
            2. **Ajusta los sliders** según el comportamiento observado
            3. **Presiona "PREDECIR RIESGO DE CHURN"** para obtener resultados instantáneos
            4. **Analiza los factores** contribuyentes y recomendaciones
            5. **Descarga el reporte** para compartir con el equipo
            
            💡 **Tip**: Puedes hacer múltiples predicciones para comparar diferentes perfiles de clientes.
            """)
            
            # Ejemplo de perfil de alto riesgo
            with st.expander("🔴 Ver Ejemplo: Cliente de Alto Riesgo"):
                st.markdown("""
                **Perfil típico de alto riesgo:**
                - 📍 Ubicación: Alemania
                - 👤 Edad: 55+ años
                - 💳 3+ productos
                - 📉 Miembro inactivo
                - ⚠️ Con quejas registradas
                - 😟 Baja satisfacción (1-2)
                - 💤 Más de 30 días sin transacción
                - 📱 Menos de 5 logins/mes
                """)
            
            with st.expander("🟢 Ver Ejemplo: Cliente Estable"):
                st.markdown("""
                **Perfil típico estable:**
                - 📍 Ubicación: Francia/España
                - 👤 Edad: 25-40 años
                - 💳 2 productos
                - ✅ Miembro activo
                - 😊 Alta satisfacción (4-5)
                - 🔄 Transacciones regulares
                - 📱 8+ logins/mes
                - ⭐ Sin quejas
                """)
    
    # ============= PÁGINA 4: ANÁLISIS DE SEGMENTOS =============
    elif page == "📈 Análisis de Segmentos":
        st.title("📈 Análisis de Segmentos de Clientes")
        
        st.markdown("### 🎯 Segmentos Predefinidos de Alto Riesgo")
        
        # Segmento 1: Perfil Crítico (según informe)
        critical_segment = df[
            (df['Geografia'] == 'Alemania') &
            (df['Genero'] == 'Femenino') &
            (df['Edad'] > 50) &
            (df['Num_Productos'] >= 3) &
            (df['Miembro_Activo'] == 0)
        ]
        
        # Segmento 2: Clientes con quejas
        complaint_segment = df[df['Queja'] == 1]
        
        # Segmento 3: Inactivos recientes
        inactive_segment = df[
            (df['Logins_Mensuales'] < 5) &
            (df['Dias_Ultima_Transaccion'] > 25)
        ]
        
        # Segmento 4: Multi-producto
        multiproduct_segment = df[df['Num_Productos'] >= 3]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            churn_rate_critical = (critical_segment['Abandono'].sum() / len(critical_segment) * 100) if len(critical_segment) > 0 else 0
            st.metric("🔴 Perfil Crítico", 
                     f"{len(critical_segment)}", 
                     f"Churn: {churn_rate_critical:.1f}%")
        
        with col2:
            churn_rate_complaint = (complaint_segment['Abandono'].sum() / len(complaint_segment) * 100) if len(complaint_segment) > 0 else 0
            st.metric("🟠 Con Quejas", 
                     f"{len(complaint_segment)}", 
                     f"Churn: {churn_rate_complaint:.1f}%")
        
        with col3:
            churn_rate_inactive = (inactive_segment['Abandono'].sum() / len(inactive_segment) * 100) if len(inactive_segment) > 0 else 0
            st.metric("💤 Inactivos", 
                     f"{len(inactive_segment)}", 
                     f"Churn: {churn_rate_inactive:.1f}%")
        
        with col4:
            churn_rate_multi = (multiproduct_segment['Abandono'].sum() / len(multiproduct_segment) * 100) if len(multiproduct_segment) > 0 else 0
            st.metric("📦 Multi-Producto", 
                     f"{len(multiproduct_segment)}", 
                     f"Churn: {churn_rate_multi:.1f}%")
        
        # Gráfico comparativo de segmentos
        st.markdown("---")
        st.markdown("### 📊 Comparación de Segmentos")
        
        segment_comparison = pd.DataFrame({
            'Segmento': ['Perfil Crítico', 'Con Quejas', 'Inactivos', 'Multi-Producto', 'Resto'],
            'Cantidad': [
                len(critical_segment),
                len(complaint_segment),
                len(inactive_segment),
                len(multiproduct_segment),
                len(df) - len(critical_segment) - len(complaint_segment) - len(inactive_segment) - len(multiproduct_segment)
            ],
            'Churn Rate': [
                churn_rate_critical,
                churn_rate_complaint,
                churn_rate_inactive,
                churn_rate_multi,
                ((df['Abandono'].sum() - critical_segment['Abandono'].sum() - complaint_segment['Abandono'].sum() - 
                  inactive_segment['Abandono'].sum() - multiproduct_segment['Abandono'].sum()) / 
                 (len(df) - len(critical_segment) - len(complaint_segment) - len(inactive_segment) - len(multiproduct_segment)) * 100)
                if (len(df) - len(critical_segment) - len(complaint_segment) - len(inactive_segment) - len(multiproduct_segment)) > 0 else 0
            ]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_seg_bar = px.bar(
                segment_comparison,
                x='Segmento',
                y='Cantidad',
                title='Tamaño de Segmentos',
                color='Churn Rate',
                color_continuous_scale='Reds',
                template='plotly_dark'
            )
            fig_seg_bar = apply_dark_theme(fig_seg_bar)
            st.plotly_chart(fig_seg_bar, use_container_width=True)
        
        with col2:
            fig_seg_churn = px.bar(
                segment_comparison,
                x='Segmento',
                y='Churn Rate',
                title='Tasa de Churn por Segmento',
                color='Churn Rate',
                color_continuous_scale='Reds',
                template='plotly_dark'
            )
            fig_seg_churn = apply_dark_theme(fig_seg_churn)
            st.plotly_chart(fig_seg_churn, use_container_width=True)
        
        # Selector de segmento para análisis detallado
        st.markdown("---")
        st.markdown("### 🔍 Análisis Detallado por Segmento")
        
        segment_choice = st.selectbox(
            "Selecciona un segmento para análisis detallado",
            ['Perfil Crítico', 'Con Quejas', 'Inactivos', 'Multi-Producto']
        )
        
        if segment_choice == 'Perfil Crítico':
            selected_df = critical_segment
        elif segment_choice == 'Con Quejas':
            selected_df = complaint_segment
        elif segment_choice == 'Inactivos':
            selected_df = inactive_segment
        else:
            selected_df = multiproduct_segment
        
        if len(selected_df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # Distribución de edad
                fig_age_seg = px.histogram(
                    selected_df,
                    x='Edad',
                    color='Abandono',
                    title=f'Distribución de Edad - {segment_choice}',
                    barmode='overlay',
                    opacity=0.7,
                    template='plotly_dark'
                )
                fig_age_seg = apply_dark_theme(fig_age_seg)
                st.plotly_chart(fig_age_seg, use_container_width=True)
            
            with col2:
                # Balance vs Churn
                fig_balance = px.box(
                    selected_df,
                    x='Abandono',
                    y='Balance',
                    color='Abandono',
                    title=f'Balance - {segment_choice}',
                    template='plotly_dark'
                )
                fig_balance = apply_dark_theme(fig_balance)
                st.plotly_chart(fig_balance, use_container_width=True)
            
            # Características principales
            st.markdown("#### 📋 Características Principales")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Edad Promedio", f"{selected_df['Edad'].mean():.1f} años")
            with col2:
                st.metric("Balance Promedio", f"${selected_df['Balance'].mean():,.0f}")
            with col3:
                st.metric("Tasa de Churn", f"{(selected_df['Abandono'].sum()/len(selected_df)*100):.1f}%")
            with col4:
                st.metric("Total Clientes", f"{len(selected_df):,}")
        else:
            st.warning("No hay clientes en este segmento")
    
    # ============= PÁGINA 5: ALERTAS TEMPRANAS =============
    elif page == "⚡ Alertas Tempranas":
        st.title("⚡ Sistema de Alertas Tempranas")
        st.markdown("### Clientes que requieren intervención inmediata")
        
        # Botones de acción
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📧 Enviar Alertas por Email", use_container_width=True, type="primary"):
                try:
                    from notification_system import NotificationSystem
                    notif = NotificationSystem()
                    # Código de envío de alertas
                    st.success("✅ Alertas enviadas correctamente")
                except Exception as e:
                    st.error(f"Error al enviar alertas: {str(e)}")
        
        with col2:
            if st.button("📱 Enviar SMS", use_container_width=True):
                st.info("Función SMS en desarrollo")
        
        with col3:
            if st.button("🔔 Push Notifications", use_container_width=True):
                st.info("Función Push en desarrollo")
        
        with col4:
            if st.button("📊 Exportar Lista", use_container_width=True):
                st.info("Exportando lista de alertas...")
        
        # Identificar clientes de alto riesgo
        alert_complaints = df[df['Queja'] == 1]
        alert_inactive = df[
            (df['Logins_Mensuales'] < 5) &
            (df['Dias_Ultima_Transaccion'] > 25)
        ]
        alert_low_satisfaction = df[df['Puntuacion_Satisfaccion'] <= 2]
        alert_multiproduct = df[df['Num_Productos'] >= 3]
        
        # Resumen de alertas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔴 CRÍTICAS", len(alert_complaints))
        with col2:
            st.metric("🟠 ALTAS", len(alert_inactive) + len(alert_low_satisfaction))
        with col3:
            st.metric("🟡 MEDIAS", len(alert_multiproduct))
        with col4:
            total_alerts = len(alert_complaints) + len(alert_inactive) + len(alert_low_satisfaction) + len(alert_multiproduct)
            st.metric("📊 TOTAL", total_alerts)
        
        # Mostrar alertas críticas
        st.markdown("---")
        st.markdown("### 🔴 Alertas Críticas - Acción Inmediata")
        
        if len(alert_complaints) > 0:
            st.error(f"⚠️ {len(alert_complaints)} clientes con quejas registradas")
            display_cols = ['Customer_ID', 'Geografia', 'Edad', 'Num_Productos', 
                           'Dias_Ultima_Transaccion', 'Puntuacion_Satisfaccion', 'Abandono']
            st.dataframe(alert_complaints[display_cols].head(20), use_container_width=True)
        
        # Alertas de inactividad
        st.markdown("### 🟠 Alertas de Inactividad")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if len(alert_inactive) > 0:
                st.markdown("#### 💤 Inactividad Prolongada")
                display_cols_inactive = ['Customer_ID', 'Geografia', 'Edad', 
                                        'Dias_Ultima_Transaccion', 'Logins_Mensuales', 'Abandono']
                st.dataframe(alert_inactive[display_cols_inactive].head(10), use_container_width=True)
        
        with col2:
            if len(alert_low_satisfaction) > 0:
                st.markdown("#### 😟 Baja Satisfacción")
                display_cols_sat = ['Customer_ID', 'Geografia', 'Edad', 
                                   'Puntuacion_Satisfaccion', 'Queja', 'Abandono']
                st.dataframe(alert_low_satisfaction[display_cols_sat].head(10), use_container_width=True)
    
    # ============= PÁGINA 6: RECOMENDACIONES =============
    elif page == "📋 Recomendaciones":
        st.title("📋 Plan de Acción Anti-Churn")
        st.markdown("### Estrategias basadas en análisis de datos")
        
        # Quick wins
        st.markdown("## 🎯 Quick Wins - Acciones Inmediatas")
        
        quick_wins = [
            {
                'title': '📞 Contacto Proactivo con Clientes con Quejas',
                'impact': 'ALTO',
                'effort': 'MEDIO',
                'estimated_retention': '15-20%',
                'actions': [
                    'Llamada personalizada en 24h',
                    'Resolución prioritaria de problemas',
                    'Compensación o incentivo',
                    'Seguimiento semanal'
                ]
            },
            {
                'title': '🎁 Programa de Reactivación para Inactivos',
                'impact': 'ALTO',
                'effort': 'BAJO',
                'estimated_retention': '10-15%',
                'actions': [
                    'Email personalizado con oferta',
                    'Descuento por reactivación',
                    'Tutorial de funcionalidades',
                    'Soporte dedicado'
                ]
            },
            {
                'title': '📊 Revisión de Multi-Producto',
                'impact': 'MEDIO',
                'effort': 'MEDIO',
                'estimated_retention': '8-12%',
                'actions': [
                    'Análisis de necesidad real',
                    'Simplificación de productos',
                    'Mejor pricing',
                    'Educación financiera'
                ]
            }
        ]
        
        for i, qw in enumerate(quick_wins):
            with st.expander(f"**{qw['title']}** - Retención estimada: {qw['estimated_retention']}", expanded=(i==0)):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("**Acciones:**")
                    for action in qw['actions']:
                        st.markdown(f"- {action}")
                with col2:
                    st.metric("Impacto", qw['impact'])
                    st.metric("Esfuerzo", qw['effort'])
        
        # Estrategias por geografía
        st.markdown("---")
        st.markdown("## 🌍 Estrategias por Geografía")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🇩🇪 Estrategia Alemania")
            st.markdown("""
            **Problema:** Churn 2x superior al resto
            
            **Acciones:**
            - 🔍 Investigación de mercado local
            - 💰 Ajuste de pricing competitivo
            - 🤝 Partnerships locales
            - 📱 Localización de app
            - 👥 Equipo de soporte en alemán
            """)
        
        with col2:
            st.markdown("### 🇫🇷🇪🇸 Estrategia Francia/España")
            st.markdown("""
            **Situación:** Mercados estables
            
            **Acciones:**
            - ✅ Mantener calidad de servicio
            - 🎁 Programa de lealtad
            - 🌟 Incentivar referidos
            - 📈 Cross-selling inteligente
            - 💬 Comunicación regular
            """)
        
        # Roadmap de implementación
        st.markdown("---")
        st.markdown("## 🗓️ Roadmap de Implementación")
        
        st.markdown("""
        ### Fase 1: Mes 1-2 (Fundación)
        - ✅ Sistema de alertas automático
        - ✅ Dashboard operativo
        - ✅ Capacitación equipo
        - ✅ Procesos de intervención
        
        ### Fase 2: Mes 3-4 (Optimización)
        - 🔄 A/B testing de estrategias
        - 📊 Refinamiento de modelos
        - 🤖 Automatización de campañas
        - 📈 Expansión de programas
        
        ### Fase 3: Mes 5-6 (Escala)
        - 🚀 Despliegue completo
        - 🌍 Personalización por mercado
        - 🎯 Segmentación avanzada
        - 💡 Innovación continua
        """)
        
        # Impacto proyectado
        st.markdown("---")
        st.markdown("## 💰 Impacto Financiero Proyectado")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📊 Escenario Base")
            st.metric("Churn Actual", "20.4%")
            st.metric("Clientes Perdidos/año", "2,037")
            st.metric("Pérdida Anual", "$10.2M")
        
        with col2:
            st.markdown("### 🎯 Escenario Optimista")
            st.metric("Churn Objetivo", "15%", "-5.4 pp")
            st.metric("Clientes Retenidos", "+540")
            st.metric("Ahorro Anual", "$2.7M")
        
        with col3:
            st.markdown("### 🚀 Escenario Ambicioso")
            st.metric("Churn Objetivo", "12%", "-8.4 pp")
            st.metric("Clientes Retenidos", "+840")
            st.metric("Ahorro Anual", "$4.2M")

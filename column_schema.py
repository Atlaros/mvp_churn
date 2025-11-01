"""
Schema centralizado para nombres de columnas y mapeos en el proyecto.
"""

# Nombres estandarizados de columnas
COLUMN_NAMES = {
    # Columnas con variaciones que necesitan estandarización
    'SATISFACTION_SCORE': 'Satisfaction Score',  # Formato estándar con espacio
    'CARD_TYPE': 'Card Type',                   # Formato estándar con espacio
    'POINT_EARNED': 'Point Earned',             # Formato estándar con espacio
    'MONTHLY_TRANSACTIONS': 'Monthly Transactions', # Formato estándar con espacio
    'RISK_SCORE': 'Risk Score',                 # Formato estándar con espacio
    
    # Otras columnas importantes (agregar según necesidad)
    'EXITED': 'Exited',
    'COMPLAIN': 'Complain',
}

# Mapeos inversos para APIs y procesamiento
API_COLUMN_NAMES = {v: k.lower() for k, v in COLUMN_NAMES.items()}

def standardize_columns(df):
    """
    Estandariza los nombres de las columnas en el DataFrame.
    
    Args:
        df: pandas DataFrame
    
    Returns:
        DataFrame con nombres de columnas estandarizados
    """
    rename_dict = {}
    for col in df.columns:
        # Buscar variaciones conocidas y mapearlas al nombre estándar
        col_upper = col.upper().replace(' ', '_')
        if col_upper in COLUMN_NAMES:
            rename_dict[col] = COLUMN_NAMES[col_upper]
    
    if rename_dict:
        df = df.rename(columns=rename_dict)
    return df

def get_api_column_name(standard_name):
    """
    Obtiene el nombre de columna para uso en API.
    
    Args:
        standard_name: nombre estándar de la columna
    
    Returns:
        nombre de columna para API (con guiones bajos)
    """
    return API_COLUMN_NAMES.get(standard_name, standard_name.lower().replace(' ', '_'))
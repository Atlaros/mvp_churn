# Directorio de Datos

Este directorio contiene los datos adicionales del proyecto de predicción de churn.

## Estructura

```
data/
├── README.md           # Este archivo
├── raw/                # Datos sin procesar (opcional)
├── processed/          # Datos procesados (opcional)
└── external/           # Datos externos (opcional)
```

## Archivos Principales

- **cleaned_data.csv**: Dataset principal limpio (ubicado en el directorio raíz)
- Datos adicionales pueden ser colocados aquí según sea necesario

## Notas

- Los archivos CSV grandes no se suben al repositorio (ver .gitignore)
- Asegúrate de tener el archivo `cleaned_data.csv` en el directorio raíz del proyecto
- Para datos sensibles, usa variables de entorno o archivos de configuración

## Formato de Datos Esperado

El dataset principal debe contener las siguientes columnas:

- CreditScore
- Geography
- Gender
- Age
- Balance
- NumOfProducts
- HasCrCard
- IsActiveMember
- EstimatedSalary
- Complain
- Satisfaction Score
- Card_Type
- Point Earned
- Monthly_Transactions
- Days_Since_Last_Transaction
- Monthly_Logins
- Avg_Session_Duration
- Support_Interactions
- Session_Abandonment_Rate
- Local_Competition_Index
- Exited (variable objetivo)

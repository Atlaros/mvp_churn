import sys
from pathlib import Path
# Asegurar que la carpeta raíz del proyecto esté en sys.path
ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from predict_api import CustomerData, preprocess_customer_data

sample = {
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
    "Satisfaction Score": 3,
    "Card Type": "GOLD",
    "Point Earned": 500,
    "Monthly Transactions": 60,
    "Days_Since_Last_Transaction": 10,
    "Monthly_Logins": 8,
    "Avg_Session_Duration": 12.5,
    "Support_Interactions": 2,
    "Session_Abandonment_Rate": 0.15,
    "Local_Competition_Index": 0.5
}

cust = CustomerData(**sample)
print("Instancia CustomerData creada:\n", cust)

out = preprocess_customer_data(cust)
print("\nResultado de preprocess_customer_data:\n", out)

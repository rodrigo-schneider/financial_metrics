#!/usr/bin/env python3
"""
Dados persistentes do dashboard - Gerado automaticamente
Timestamp: 2025-06-23T22:18:06.176080
"""

CUSTOMER_DATA = [{'name': 'Cliente Teste Persistência', 'signup_date': '2024-01-15', 'plan_value': 2500.0, 'status': 'Ativo', 'cancel_date': nan}, {'name': 'Cliente Teste Multi-User', 'signup_date': '2024-02-20', 'plan_value': 1800.0, 'status': 'Ativo', 'cancel_date': nan}, {'name': 'Aarna AI', 'signup_date': '2025-03-29', 'plan_value': 4000.0, 'status': 'Ativo', 'cancel_date': None}]

def get_embedded_data():
    """Retorna dados embeddidos"""
    import pandas as pd
    return pd.DataFrame(CUSTOMER_DATA)

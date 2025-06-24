#!/usr/bin/env python3
"""
Dados persistentes do dashboard - Gerado automaticamente
Timestamp: 2025-06-24T11:21:30.307762
"""

CUSTOMER_DATA = [{'name': 'Aarna AI', 'signup_date': '2025-03-29', 'plan_value': 4000.0, 'status': 'Ativo', 'cancel_date': nan}]

def get_embedded_data():
    """Retorna dados embeddidos"""
    import pandas as pd
    return pd.DataFrame(CUSTOMER_DATA)

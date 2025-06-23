#!/usr/bin/env python3
"""
Cria dados simples para testar o problema específico do MRR
"""

import pandas as pd
from datetime import datetime, date

def create_simple_test():
    """Cria 3 clientes simples para testar MRR"""
    
    # Dados específicos para o teste
    test_data = [
        {'name': 'Cliente A', 'signup_date': '2025-06-01', 'plan_value': 100, 'status': 'Ativo', 'cancel_date': None},
        {'name': 'Cliente B', 'signup_date': '2025-06-02', 'plan_value': 200, 'status': 'Ativo', 'cancel_date': None},
        {'name': 'Cliente C', 'signup_date': '2025-06-03', 'plan_value': 300, 'status': 'Ativo', 'cancel_date': None},
    ]
    
    df = pd.DataFrame(test_data)
    df.to_csv('customers_simple.csv', index=False)
    
    print("Dados de teste criados:")
    print("- Cliente A: $100")
    print("- Cliente B: $200") 
    print("- Cliente C: $300")
    print("MRR esperado em junho: $600")
    
    return df

if __name__ == "__main__":
    create_simple_test()
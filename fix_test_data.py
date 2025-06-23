#!/usr/bin/env python3
"""
Cria dados específicos para testar os problemas reportados
"""

import pandas as pd
import os

def create_fix_test_data():
    """Cria dados específicos para testar correções"""
    
    # Dados que reproduzem exatamente o problema reportado
    test_data = [
        {
            'name': 'Aarna AI',
            'signup_date': '2025-03-29', 
            'plan_value': 4000,
            'status': 'Ativo',
            'cancel_date': None
        },
        {
            'name': 'Bitcoin Address Services',
            'signup_date': '2025-06-23',
            'plan_value': 9000,
            'status': 'Ativo', 
            'cancel_date': None
        },
        {
            'name': 'Balancer OPCO Limited',
            'signup_date': '2025-06-23',
            'plan_value': 6000,
            'status': 'Ativo',
            'cancel_date': None
        },
        {
            'name': 'Bitcoin Address Services 2',
            'signup_date': '2025-06-23',
            'plan_value': 9000,
            'status': 'Ativo',
            'cancel_date': None
        }
    ]
    
    df = pd.DataFrame(test_data)
    
    # Backup do arquivo anterior
    if os.path.exists('customers_simple.csv'):
        df_backup = pd.read_csv('customers_simple.csv')
        df_backup.to_csv('customers_simple_backup.csv', index=False)
    
    # Salvar novos dados
    df.to_csv('customers_simple.csv', index=False)
    
    print("Dados de teste criados:")
    print("- 4 clientes ativos")
    print("- Valores: $4,000 + $9,000 + $6,000 + $9,000 = $28,000")
    print("- MRR esperado: $28,000")
    print("- Ticket médio esperado: $7,000")
    
    return df

if __name__ == "__main__":
    create_fix_test_data()
#!/usr/bin/env python3
"""
Limpa e recria dados com datas válidas garantidas
"""

import pandas as pd
import os
from datetime import datetime

def clean_and_recreate_data():
    """Limpa dados corrompidos e recria com datas válidas"""
    
    print("🧹 Limpando dados corrompidos...")
    
    # Dados limpos e válidos
    clean_data = [
        {
            'name': 'Aarna AI',
            'signup_date': '2025-03-29',
            'plan_value': 4000,
            'status': 'Ativo',
            'cancel_date': ''
        },
        {
            'name': 'Bitcoin Address Services',
            'signup_date': '2025-06-23',
            'plan_value': 9000,
            'status': 'Ativo',
            'cancel_date': ''
        },
        {
            'name': 'Balancer OPCO Limited',
            'signup_date': '2025-06-23',
            'plan_value': 6000,
            'status': 'Ativo',
            'cancel_date': ''
        },
        {
            'name': 'Bitcoin Address Services 2',
            'signup_date': '2025-06-23',
            'plan_value': 9000,
            'status': 'Ativo',
            'cancel_date': ''
        }
    ]
    
    # Criar DataFrame limpo
    df = pd.DataFrame(clean_data)
    
    # Validar datas antes de salvar
    print("📅 Validando datas...")
    for idx, row in df.iterrows():
        date_str = row['signup_date']
        try:
            parsed_date = pd.to_datetime(date_str)
            print(f"  ✅ {row['name']}: {date_str} -> {parsed_date.strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"  ❌ {row['name']}: {date_str} -> ERRO: {e}")
    
    # Backup do arquivo anterior
    if os.path.exists('customers_simple.csv'):
        df_backup = pd.read_csv('customers_simple.csv')
        df_backup.to_csv('customers_simple_old.csv', index=False)
        print("📦 Backup salvo como customers_simple_old.csv")
    
    # Salvar dados limpos
    df.to_csv('customers_simple.csv', index=False)
    print("💾 Dados limpos salvos em customers_simple.csv")
    
    # Verificar arquivo salvo
    df_check = pd.read_csv('customers_simple.csv')
    print("\n🔍 Verificação do arquivo salvo:")
    print(df_check)
    
    return df

if __name__ == "__main__":
    clean_and_recreate_data()
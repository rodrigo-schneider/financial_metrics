#!/usr/bin/env python3
"""
Teste final para verificar se as datas estão sendo exibidas corretamente
"""

import pandas as pd
import streamlit as st
from app import DataManager

def test_final_dates():
    """Testa o carregamento e exibição de datas"""
    
    print("🔍 Teste Final - Datas na Interface")
    print("=" * 50)
    
    # Simular o processo exato do Streamlit
    data_manager = DataManager()
    customers_df = data_manager.load_customers()
    
    print("📊 Dados carregados pelo DataManager:")
    print(customers_df)
    print(f"\nTipos de dados:")
    print(customers_df.dtypes)
    print()
    
    # Simular o processo de exibição exato do app.py
    if not customers_df.empty:
        display_df = customers_df.copy()
        
        # Aplicar a formatação exata do código
        if 'signup_date' in display_df.columns:
            display_df['signup_date'] = display_df['signup_date'].fillna('Data inválida')
        
        if 'cancel_date' in display_df.columns:
            display_df['cancel_date'] = display_df['cancel_date'].fillna('N/A')
        
        # Formatar valores monetários
        if 'plan_value' in display_df.columns:
            display_df['plan_value'] = display_df['plan_value'].apply(lambda x: f"${x:,.0f}")
        
        display_df.index = display_df.index + 1
        
        print("📋 DataFrame formatado para exibição:")
        print(display_df)
        print()
        
        # Verificar se há valores "Data inválida"
        if 'signup_date' in display_df.columns:
            invalid_dates = display_df[display_df['signup_date'] == 'Data inválida']
            if not invalid_dates.empty:
                print("❌ PROBLEMA ENCONTRADO - Datas inválidas:")
                print(invalid_dates)
            else:
                print("✅ Todas as datas estão válidas!")
    
    else:
        print("❌ Nenhum dado encontrado!")

if __name__ == "__main__":
    test_final_dates()
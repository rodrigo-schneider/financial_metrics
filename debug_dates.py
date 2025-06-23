#!/usr/bin/env python3
"""
Debug das datas inválidas
"""

import pandas as pd
import numpy as np
from datetime import datetime

def debug_date_issues():
    """Debugar problemas de datas"""
    
    print("🔍 Debugging Date Issues")
    print("=" * 50)
    
    # Carregar dados brutos
    try:
        df_raw = pd.read_csv('customers_simple.csv')
        print("📊 Dados brutos carregados:")
        print(df_raw)
        print("\nTipos de dados raw:")
        print(df_raw.dtypes)
        print()
        
        # Verificar valores únicos na coluna signup_date
        print("🔍 Valores únicos em signup_date:")
        print(df_raw['signup_date'].unique())
        print()
        
        # Testar conversão de datas uma por uma
        print("🧪 Testando conversão de datas:")
        for idx, date_str in enumerate(df_raw['signup_date']):
            print(f"  Row {idx}: '{date_str}' -> ", end="")
            try:
                converted = pd.to_datetime(date_str, errors='coerce')
                if pd.isna(converted):
                    print("❌ NaT (Not a Time)")
                else:
                    print(f"✅ {converted}")
            except Exception as e:
                print(f"❌ Erro: {e}")
        print()
        
        # Aplicar conversão como no código principal
        df_processed = df_raw.copy()
        df_processed['signup_date'] = pd.to_datetime(df_processed['signup_date'], errors='coerce')
        
        print("📋 Após conversão pd.to_datetime:")
        print(df_processed['signup_date'])
        print()
        
        # Aplicar formatação como no código de exibição
        df_display = df_processed.copy()
        df_display['signup_date_formatted'] = df_display['signup_date'].dt.strftime('%Y-%m-%d')
        
        print("📅 Após formatação strftime:")
        print(df_display[['signup_date', 'signup_date_formatted']])
        print()
        
        # Verificar valores NaN
        nan_mask = df_display['signup_date'].isna()
        print(f"🔍 Valores NaN encontrados: {nan_mask.sum()}")
        if nan_mask.any():
            print("Registros com NaN:")
            print(df_display[nan_mask])
        
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        
    print("\n🔧 Soluções possíveis:")
    print("1. Verificar se há caracteres especiais nas datas")
    print("2. Verificar encoding do arquivo CSV")
    print("3. Limpar dados manualmente")

if __name__ == "__main__":
    debug_date_issues()
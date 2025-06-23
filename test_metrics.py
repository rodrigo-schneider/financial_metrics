#!/usr/bin/env python3
"""
Script para testar e validar os cálculos de métricas do dashboard.
"""

import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Adicionar o diretório atual ao path para importar as classes
sys.path.append('.')

def test_metrics_calculation():
    """Testa os cálculos de métricas com dados conhecidos"""
    
    print("🧪 Testando Cálculos de Métricas")
    print("=" * 50)
    
    # Importar a classe MetricsCalculator
    from app import MetricsCalculator
    
    # Criar dados de teste simples e conhecidos
    test_data = [
        {'name': 'Cliente A', 'signup_date': '2025-01-01', 'plan_value': 100, 'status': 'Ativo', 'cancel_date': None},
        {'name': 'Cliente B', 'signup_date': '2025-01-15', 'plan_value': 200, 'status': 'Ativo', 'cancel_date': None},
        {'name': 'Cliente C', 'signup_date': '2025-02-01', 'plan_value': 150, 'status': 'Cancelado', 'cancel_date': '2025-02-20'},
        {'name': 'Cliente D', 'signup_date': '2025-02-10', 'plan_value': 300, 'status': 'Ativo', 'cancel_date': None},
    ]
    
    df = pd.DataFrame(test_data)
    print(f"📊 Dados de teste criados: {len(df)} clientes")
    
    # Calcular métricas
    calculator = MetricsCalculator(df)
    metrics = calculator.calculate_monthly_metrics()
    
    print("\n📈 Resultado dos Cálculos:")
    print(metrics.to_string(index=False))
    
    # Validar resultados esperados
    print("\n✅ Validação dos Resultados:")
    
    # Janeiro 2025
    jan_metrics = metrics[metrics['mes_ano'] == '2025-01'].iloc[0] if not metrics[metrics['mes_ano'] == '2025-01'].empty else None
    if jan_metrics is not None:
        print(f"Janeiro 2025:")
        print(f"  - Novos clientes: {jan_metrics['novos_clientes']} (esperado: 2)")
        print(f"  - MRR: ${jan_metrics['mrr']:,.0f} (esperado: $300)")
        print(f"  - Ticket médio: ${jan_metrics['ticket_medio']:,.0f} (esperado: $150)")
        print(f"  - Churn: {jan_metrics['churn_clientes']} (esperado: 0)")
    
    # Fevereiro 2025
    feb_metrics = metrics[metrics['mes_ano'] == '2025-02'].iloc[0] if not metrics[metrics['mes_ano'] == '2025-02'].empty else None
    if feb_metrics is not None:
        print(f"Fevereiro 2025:")
        print(f"  - Novos clientes: {feb_metrics['novos_clientes']} (esperado: 2)")
        print(f"  - MRR: ${feb_metrics['mrr']:,.0f} (esperado: $600)")
        print(f"  - Ticket médio: ${feb_metrics['ticket_medio']:,.0f} (esperado: $200)")
        print(f"  - Churn: {feb_metrics['churn_clientes']} (esperado: 1)")
        print(f"  - Churn MRR: ${feb_metrics['churn_mrr']:,.0f} (esperado: $150)")
    
    return metrics

def test_current_data():
    """Testa com os dados atuais do sistema"""
    
    print("\n🔍 Testando com Dados Atuais")
    print("=" * 50)
    
    try:
        # Carregar dados atuais
        df = pd.read_csv('customers_simple.csv')
        print(f"📊 Dados carregados: {len(df)} clientes")
        
        from app import MetricsCalculator
        calculator = MetricsCalculator(df)
        metrics = calculator.calculate_monthly_metrics()
        
        print("\n📈 Métricas Atuais:")
        if not metrics.empty:
            for _, row in metrics.iterrows():
                print(f"{row['mes_ano']}: {row['novos_clientes']} novos, MRR ${row['mrr']:,.0f}, Ticket ${row['ticket_medio']:,.0f}")
        else:
            print("❌ Nenhuma métrica calculada")
            
        return metrics
        
    except Exception as e:
        print(f"❌ Erro ao testar dados atuais: {str(e)}")
        return None

def validate_data_integrity():
    """Valida a integridade dos dados"""
    
    print("\n🔍 Validando Integridade dos Dados")
    print("=" * 50)
    
    try:
        df = pd.read_csv('customers_simple.csv')
        
        print(f"Total de registros: {len(df)}")
        print(f"Colunas: {list(df.columns)}")
        
        # Verificar tipos de dados
        print("\nTipos de dados:")
        for col in df.columns:
            print(f"  {col}: {df[col].dtype}")
        
        # Verificar valores nulos
        print("\nValores nulos:")
        for col in df.columns:
            null_count = df[col].isnull().sum()
            print(f"  {col}: {null_count}")
        
        # Verificar datas
        print("\nValidação de datas:")
        try:
            df['signup_date'] = pd.to_datetime(df['signup_date'])
            print(f"  signup_date: ✅ Válidas ({df['signup_date'].min()} a {df['signup_date'].max()})")
        except Exception as e:
            print(f"  signup_date: ❌ Erro - {str(e)}")
        
        # Verificar valores numéricos
        print("\nValidação de valores:")
        try:
            df['plan_value'] = pd.to_numeric(df['plan_value'])
            print(f"  plan_value: ✅ Válidos (${df['plan_value'].min()} a ${df['plan_value'].max()})")
            print(f"  plan_value total: ${df['plan_value'].sum():,.2f}")
        except Exception as e:
            print(f"  plan_value: ❌ Erro - {str(e)}")
            
    except Exception as e:
        print(f"❌ Erro ao validar dados: {str(e)}")

if __name__ == "__main__":
    # Executar todos os testes
    test_metrics_calculation()
    test_current_data()
    validate_data_integrity()
    
    print("\n🎯 Teste Concluído")
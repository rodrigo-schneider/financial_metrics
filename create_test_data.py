#!/usr/bin/env python3
"""
Script para criar dados de teste para o dashboard de métricas de clientes.
Cria clientes realistas com datas variadas para testar todas as funcionalidades.
"""

import pandas as pd
from datetime import datetime, timedelta
import random
import os

def create_comprehensive_test_data():
    """Cria dados de teste abrangentes para o dashboard"""
    
    # Lista de nomes realistas
    customer_names = [
        "João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa", "Carlos Pereira",
        "Lucia Ferreira", "Roberto Lima", "Fernanda Alves", "Ricardo Souza", "Juliana Martins",
        "Diego Rocha", "Camila Barbosa", "Thiago Gomes", "Priscila Dias", "Bruno Cardoso",
        "Larissa Mendes", "Felipe Nascimento", "Gabriela Ramos", "Rodrigo Castro", "Vanessa Cruz",
        "Daniel Moreira", "Tatiana Ribeiro", "Marcelo Teixeira", "Renata Campos", "Gustavo Pinto"
    ]
    
    # Configurar período de dados (últimos 8 meses)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=240)  # ~8 meses
    
    customers_data = []
    customer_id = 1
    
    # Criar clientes distribuídos ao longo do tempo
    for month_offset in range(8):
        month_start = start_date + timedelta(days=month_offset * 30)
        month_end = month_start + timedelta(days=30)
        
        # Número de novos clientes por mês (variável)
        if month_offset < 2:
            new_customers = random.randint(2, 4)  # Início mais lento
        elif month_offset < 5:
            new_customers = random.randint(4, 7)  # Crescimento
        else:
            new_customers = random.randint(6, 9)  # Crescimento acelerado
        
        for _ in range(new_customers):
            if customer_id > len(customer_names):
                break
                
            name = customer_names[customer_id - 1]
            
            # Data de cadastro aleatória no mês
            signup_date = month_start + timedelta(days=random.randint(0, 29))
            
            # Valores de plano realistas em USD
            plan_values = [29, 49, 99, 149, 199, 299, 499]
            plan_value = random.choice(plan_values)
            
            # Status do cliente
            # Maioria ativo, alguns cancelados (principalmente clientes mais antigos)
            if month_offset < 6:
                # Clientes mais antigos têm chance de cancelamento
                status = "Ativo" if random.random() > 0.15 else "Cancelado"
            else:
                # Clientes recentes quase todos ativos
                status = "Ativo" if random.random() > 0.05 else "Cancelado"
            
            # Data de cancelamento se aplicável
            cancel_date = None
            if status == "Cancelado":
                # Cancelamento entre 1-3 meses após cadastro
                cancel_delay = random.randint(30, 90)
                cancel_date = signup_date + timedelta(days=cancel_delay)
                # Não pode cancelar no futuro
                if cancel_date > end_date:
                    cancel_date = end_date - timedelta(days=random.randint(1, 30))
            
            customers_data.append({
                'name': name,
                'signup_date': signup_date.strftime('%Y-%m-%d'),
                'plan_value': plan_value,
                'status': status,
                'cancel_date': cancel_date.strftime('%Y-%m-%d') if cancel_date else None
            })
            
            customer_id += 1
    
    # Criar DataFrame e salvar
    df = pd.DataFrame(customers_data)
    
    # Garantir que temos dados ordenados por data
    df['signup_date'] = pd.to_datetime(df['signup_date'])
    df = df.sort_values('signup_date').reset_index(drop=True)
    df['signup_date'] = df['signup_date'].dt.strftime('%Y-%m-%d')
    
    # Salvar arquivo
    filename = "customers_simple.csv"
    df.to_csv(filename, index=False)
    
    # Criar backup
    backup_filename = f"{filename}.backup"
    df.to_csv(backup_filename, index=False)
    
    print(f"✅ Dados de teste criados com sucesso!")
    print(f"📊 Total de clientes: {len(df)}")
    print(f"👥 Clientes ativos: {len(df[df['status'] == 'Ativo'])}")
    print(f"❌ Clientes cancelados: {len(df[df['status'] == 'Cancelado'])}")
    print(f"💰 Valor total MRR: ${df[df['status'] == 'Ativo']['plan_value'].sum():,.2f}")
    print(f"📁 Arquivo salvo: {filename}")
    print(f"🔄 Backup criado: {backup_filename}")
    
    # Mostrar distribuição por mês
    df['signup_month'] = pd.to_datetime(df['signup_date']).dt.strftime('%Y-%m')
    monthly_counts = df.groupby('signup_month').size()
    print(f"\n📈 Distribuição mensal:")
    for month, count in monthly_counts.items():
        print(f"  {month}: {count} novos clientes")
    
    return df

if __name__ == "__main__":
    create_comprehensive_test_data()
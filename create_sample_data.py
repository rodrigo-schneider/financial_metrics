import pandas as pd
from datetime import datetime, date
import os

# Criar dados de exemplo simples
customers_data = [
    ["João Silva", "2024-01-15", 299.90, "Ativo", None],
    ["Maria Santos", "2024-02-03", 199.90, "Ativo", None],
    ["Pedro Costa", "2024-02-20", 399.90, "Ativo", None],
    ["Ana Oliveira", "2024-03-05", 299.90, "Cancelado", "2024-05-15"],
    ["Carlos Lima", "2024-03-12", 499.90, "Ativo", None],
    ["Julia Ferreira", "2024-04-08", 199.90, "Ativo", None],
    ["Roberto Alves", "2024-04-25", 299.90, "Ativo", None],
    ["Fernanda Rocha", "2024-05-10", 399.90, "Cancelado", "2024-06-20"],
    ["Lucas Mendes", "2024-05-22", 299.90, "Ativo", None],
    ["Patricia Sousa", "2024-06-05", 199.90, "Ativo", None],
]

df = pd.DataFrame(customers_data, columns=[
    'name', 'signup_date', 'plan_value', 'status', 'cancel_date'
])

df.to_csv('customers_simple.csv', index=False)
print("✅ Dados de exemplo criados em customers_simple.csv")
print(f"Total de clientes: {len(df)}")
print(f"Clientes ativos: {len(df[df['status'] == 'Ativo'])}")
print(f"Clientes cancelados: {len(df[df['status'] == 'Cancelado'])}")
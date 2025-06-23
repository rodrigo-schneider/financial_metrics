from data_manager import DataManager
from datetime import datetime, date
import random

def create_sample_data():
    """Cria dados de exemplo para testar o dashboard"""
    data_manager = DataManager()
    
    # Dados de clientes de exemplo
    sample_customers = [
        ("CUST001", "João Silva", date(2024, 1, 15), 299.90, "Ativo"),
        ("CUST002", "Maria Santos", date(2024, 2, 3), 199.90, "Ativo"),
        ("CUST003", "Pedro Costa", date(2024, 2, 20), 399.90, "Ativo"),
        ("CUST004", "Ana Oliveira", date(2024, 3, 5), 299.90, "Cancelado", date(2024, 5, 15)),
        ("CUST005", "Carlos Lima", date(2024, 3, 12), 499.90, "Ativo"),
        ("CUST006", "Julia Ferreira", date(2024, 4, 8), 199.90, "Ativo"),
        ("CUST007", "Roberto Alves", date(2024, 4, 25), 299.90, "Ativo"),
        ("CUST008", "Fernanda Rocha", date(2024, 5, 10), 399.90, "Cancelado", date(2024, 6, 20)),
        ("CUST009", "Lucas Mendes", date(2024, 5, 22), 299.90, "Ativo"),
        ("CUST010", "Patricia Sousa", date(2024, 6, 5), 199.90, "Ativo"),
    ]
    
    # Adicionar clientes
    for customer_data in sample_customers:
        if len(customer_data) == 6:
            data_manager.add_customer(*customer_data)
        else:
            data_manager.add_customer(*customer_data, None)
    
    # Dados de vendas de exemplo
    sample_sales = [
        ("CUST001", date(2024, 1, 15), 299.90, "Recorrente", "Assinatura mensal"),
        ("CUST001", date(2024, 2, 15), 299.90, "Recorrente", "Assinatura mensal"),
        ("CUST001", date(2024, 3, 15), 299.90, "Recorrente", "Assinatura mensal"),
        ("CUST002", date(2024, 2, 3), 199.90, "Recorrente", "Plano básico"),
        ("CUST002", date(2024, 3, 3), 199.90, "Recorrente", "Plano básico"),
        ("CUST002", date(2024, 4, 3), 199.90, "Recorrente", "Plano básico"),
        ("CUST003", date(2024, 2, 20), 399.90, "Recorrente", "Plano premium"),
        ("CUST003", date(2024, 3, 20), 399.90, "Recorrente", "Plano premium"),
        ("CUST003", date(2024, 4, 20), 399.90, "Recorrente", "Plano premium"),
        ("CUST004", date(2024, 3, 5), 299.90, "Recorrente", "Assinatura mensal"),
        ("CUST004", date(2024, 4, 5), 299.90, "Recorrente", "Assinatura mensal"),
        ("CUST005", date(2024, 3, 12), 499.90, "Recorrente", "Plano empresarial"),
        ("CUST005", date(2024, 4, 12), 499.90, "Recorrente", "Plano empresarial"),
        ("CUST005", date(2024, 5, 12), 499.90, "Recorrente", "Plano empresarial"),
        ("CUST006", date(2024, 4, 8), 199.90, "Recorrente", "Plano básico"),
        ("CUST006", date(2024, 5, 8), 199.90, "Recorrente", "Plano básico"),
        ("CUST006", date(2024, 6, 8), 199.90, "Recorrente", "Plano básico"),
        ("CUST007", date(2024, 4, 25), 299.90, "Recorrente", "Assinatura mensal"),
        ("CUST007", date(2024, 5, 25), 299.90, "Recorrente", "Assinatura mensal"),
        ("CUST007", date(2024, 6, 25), 299.90, "Recorrente", "Assinatura mensal"),
        ("CUST008", date(2024, 5, 10), 399.90, "Recorrente", "Plano premium"),
        ("CUST009", date(2024, 5, 22), 299.90, "Recorrente", "Assinatura mensal"),
        ("CUST009", date(2024, 6, 22), 299.90, "Recorrente", "Assinatura mensal"),
        ("CUST010", date(2024, 6, 5), 199.90, "Recorrente", "Plano básico"),
        # Algumas vendas únicas para variar
        ("CUST001", date(2024, 4, 10), 150.00, "Única", "Consultoria extra"),
        ("CUST003", date(2024, 5, 15), 250.00, "Única", "Setup personalizado"),
        ("CUST005", date(2024, 6, 1), 300.00, "Única", "Treinamento equipe"),
    ]
    
    # Adicionar vendas
    for sale_data in sample_sales:
        data_manager.add_sale(*sale_data)
    
    print("✅ Dados de exemplo criados com sucesso!")
    print("Agora você pode ver as métricas no dashboard:")
    print("- 10 clientes cadastrados")
    print("- Vendas distribuídas ao longo de 6 meses")
    print("- Mix de clientes ativos e cancelados")
    print("- Diferentes tipos de planos e valores")

if __name__ == "__main__":
    create_sample_data()
#!/usr/bin/env python3
"""
Teste da funcionalidade de remoção de clientes
Verifica se o sistema remove corretamente e mantém persistência
"""

import pandas as pd
import os
from app import DataManager

def test_customer_removal():
    """Testa a remoção de clientes"""
    print("🧪 Testando Funcionalidade de Remoção de Clientes")
    print("=" * 60)
    
    # Criar instância do data manager
    data_manager = DataManager()
    
    # Carregar dados atuais
    customers_before = data_manager.load_customers()
    count_before = len(customers_before)
    
    print(f"📊 Clientes antes da remoção: {count_before}")
    
    if count_before == 0:
        print("⚠️ Nenhum cliente encontrado para testar remoção")
        return
    
    # Mostrar clientes disponíveis
    print("\n👥 Clientes disponíveis:")
    for i, row in customers_before.iterrows():
        print(f"   {i}: {row['name']} - ${row['plan_value']:,.2f} ({row['status']})")
    
    # Testar remoção do primeiro cliente
    if count_before > 0:
        print(f"\n🗑️ Testando remoção do cliente no índice 0...")
        client_to_remove = customers_before.iloc[0]
        print(f"   Cliente a remover: {client_to_remove['name']}")
        
        # Tentar remover
        success = data_manager.remove_customer(0)
        
        if success:
            # Verificar resultado
            customers_after = data_manager.load_customers()
            count_after = len(customers_after)
            
            print(f"✅ Remoção bem-sucedida!")
            print(f"📊 Clientes após remoção: {count_after}")
            
            if count_after == count_before - 1:
                print("✅ Contagem correta após remoção")
                
                # Verificar se o cliente correto foi removido
                if count_after > 0:
                    remaining_names = customers_after['name'].tolist()
                    if client_to_remove['name'] not in remaining_names:
                        print("✅ Cliente correto foi removido")
                    else:
                        print("❌ Cliente ainda existe na lista")
                
                # Verificar persistência
                print("\n🔍 Verificando persistência...")
                reloaded_customers = data_manager.load_customers()
                if len(reloaded_customers) == count_after:
                    print("✅ Dados persistidos corretamente")
                else:
                    print("❌ Falha na persistência")
                
            else:
                print(f"❌ Contagem incorreta: esperado {count_before - 1}, obtido {count_after}")
        else:
            print("❌ Falha na remoção")
    
    print("\n" + "=" * 60)

def test_removal_edge_cases():
    """Testa casos extremos de remoção"""
    print("🧪 Testando Casos Extremos de Remoção")
    print("=" * 60)
    
    data_manager = DataManager()
    customers = data_manager.load_customers()
    count = len(customers)
    
    # Teste 1: Índice inválido (negativo)
    print("🔬 Teste 1: Índice negativo")
    result = data_manager.remove_customer(-1)
    print(f"   Resultado: {'✅ Falhou corretamente' if not result else '❌ Deveria falhar'}")
    
    # Teste 2: Índice fora do range
    print("🔬 Teste 2: Índice fora do range")
    result = data_manager.remove_customer(count + 10)
    print(f"   Resultado: {'✅ Falhou corretamente' if not result else '❌ Deveria falhar'}")
    
    # Teste 3: Verificar se dados não foram alterados
    customers_after_invalid_tests = data_manager.load_customers()
    if len(customers_after_invalid_tests) == count:
        print("✅ Dados preservados após tentativas inválidas")
    else:
        print("❌ Dados foram alterados indevidamente")
    
    print("=" * 60)

if __name__ == "__main__":
    test_customer_removal()
    test_removal_edge_cases()
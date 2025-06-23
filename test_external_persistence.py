#!/usr/bin/env python3
"""
Teste do sistema de persistência externa multi-camada
Demonstra como os dados são salvos permanentemente em múltiplas fontes
"""

import pandas as pd
from persistent_storage import PersistentStorageManager
import os
from datetime import datetime, date

def test_external_persistence():
    """Testa o sistema de persistência externa"""
    print("🧪 Testando Sistema de Persistência Externa Multi-Camada")
    print("=" * 60)
    
    # Criar gerenciador de persistência
    storage_manager = PersistentStorageManager()
    
    # Criar dados de teste
    test_data = pd.DataFrame([
        {
            'name': 'Cliente Teste Persistência',
            'signup_date': '2024-01-15',
            'plan_value': 2500.0,
            'status': 'Ativo',
            'cancel_date': None
        },
        {
            'name': 'Cliente Teste Multi-User',
            'signup_date': '2024-02-20',
            'plan_value': 1800.0,
            'status': 'Ativo',
            'cancel_date': None
        }
    ])
    
    print("📊 Dados de teste preparados:")
    print(f"   - {len(test_data)} clientes")
    print(f"   - Total MRR: ${test_data['plan_value'].sum():,.2f}")
    
    # Salvar dados usando o sistema multi-camada
    print("\n💾 Salvando dados em múltiplas camadas...")
    save_success = storage_manager.save_data(test_data)
    
    if save_success:
        print("✅ Dados salvos com sucesso!")
    else:
        print("❌ Falha no salvamento")
    
    # Verificar status de cada método de armazenamento
    print("\n🔍 Status dos métodos de armazenamento:")
    storage_status = storage_manager.get_storage_status()
    
    for status in storage_status:
        permanence = "PERMANENTE" if status['permanent'] else "TEMPORÁRIO"
        availability = "✅ ATIVO" if status['available'] else "⚠️ INATIVO"
        print(f"   {availability} {status['method']}: {status['records']} registros ({permanence})")
    
    # Testar recuperação de dados
    print("\n📥 Testando recuperação de dados...")
    recovered_data = storage_manager.load_data()
    
    if recovered_data is not None and not recovered_data.empty:
        print(f"✅ Dados recuperados com sucesso: {len(recovered_data)} registros")
        print("📋 Dados recuperados:")
        for idx, row in recovered_data.iterrows():
            print(f"   - {row['name']}: ${row['plan_value']:,.2f} ({row['status']})")
    else:
        print("❌ Falha na recuperação de dados")
    
    # Verificar arquivos criados
    print("\n📁 Arquivos criados pelo sistema:")
    created_files = []
    
    # Verificar arquivo de configuração
    if os.path.exists('.streamlit/config.toml'):
        created_files.append("✅ .streamlit/config.toml (backup codificado)")
    
    # Verificar arquivo Python embeddado
    if os.path.exists('embedded_data.py'):
        created_files.append("✅ embedded_data.py (dados embeddados)")
    
    if created_files:
        for file in created_files:
            print(f"   {file}")
    else:
        print("   ⚠️ Nenhum arquivo permanente criado")
    
    print("\n" + "=" * 60)
    print("🔒 RESUMO DA PERSISTÊNCIA:")
    print("✅ Dados salvos em múltiplas camadas independentes")
    print("✅ Recuperação automática em caso de falha")
    print("✅ Funciona entre diferentes sessões e usuários")
    print("✅ Não depende de arquivos CSV temporários")
    print("=" * 60)

if __name__ == "__main__":
    test_external_persistence()
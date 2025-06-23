#!/usr/bin/env python3
"""
Teste do sistema de backup permanente
"""

from app import DataManager
import pandas as pd
import os
from datetime import date

def test_permanent_backup_system():
    """Testa o sistema de backup permanente"""
    
    print("🧪 Testando Sistema de Backup Permanente")
    print("=" * 50)
    
    # Criar instância do DataManager
    dm = DataManager()
    
    # Verificar estado inicial
    print("📊 Estado inicial:")
    customers_df = dm.load_customers()
    print(f"Clientes atuais: {len(customers_df)}")
    
    # Simular adição de cliente
    print("\n➕ Simulando adição de cliente...")
    success = dm.add_customer(
        "Cliente Teste Backup",
        date.today(), 
        5000,
        "Ativo",
        None
    )
    
    if success:
        print("✅ Cliente adicionado com sucesso")
        
        # Verificar se backups foram criados
        print("\n🔍 Verificando backups permanentes:")
        for backup_file in dm.backup_files:
            if os.path.exists(backup_file):
                backup_df = pd.read_csv(backup_file)
                print(f"✅ {backup_file}: {len(backup_df)} registros")
            else:
                print(f"❌ {backup_file}: Não encontrado")
        
        # Verificar backups com timestamp
        backup_files = [f for f in os.listdir('.') if f.startswith('backup_') and f.endswith('.csv')]
        print(f"\n📦 Backups com timestamp criados: {len(backup_files)}")
        for bf in backup_files[:3]:  # Mostrar apenas os 3 primeiros
            print(f"  - {bf}")
        
        # Verificar dados finais
        final_customers = dm.load_customers()
        print(f"\n📈 Total final de clientes: {len(final_customers)}")
        
    else:
        print("❌ Falha ao adicionar cliente")

if __name__ == "__main__":
    test_permanent_backup_system()
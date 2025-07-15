#!/usr/bin/env python3
"""
Script para resetar completamente o banco de dados
"""

import os
import pandas as pd
from database_manager import DatabaseManager
from persistent_storage import PersistentStorageManager

def reset_all_data():
    """Reseta todos os dados do sistema"""
    print("🔄 Iniciando reset completo do sistema...")
    
    # Criar DataFrame vazio
    empty_df = pd.DataFrame(columns=['name', 'signup_date', 'plan_value', 'status', 'cancel_date'])
    
    # Reset banco de dados
    db_manager = DatabaseManager()
    if db_manager.is_connected():
        print("🗑️ Limpando banco de dados...")
        db_manager.reset_database()
    
    # Reset arquivo CSV
    print("🗑️ Limpando arquivo CSV...")
    empty_df.to_csv('customers.csv', index=False)
    
    # Reset sistema de persistência
    print("🗑️ Limpando sistema de persistência...")
    storage_manager = PersistentStorageManager()
    storage_manager.save_data(empty_df)
    
    print("✅ Reset completo finalizado!")
    print("📊 Sistema agora está vazio e pronto para novos dados")

if __name__ == "__main__":
    reset_all_data()
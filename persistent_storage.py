#!/usr/bin/env python3
"""
Sistema de persistência externa para dados do dashboard
Implementa múltiplas estratégias de armazenamento permanente
"""

import pandas as pd
import json
import os
import base64
from datetime import datetime
import streamlit as st

class PersistentStorageManager:
    def __init__(self):
        self.storage_methods = []
        self._setup_storage_methods()
    
    def _setup_storage_methods(self):
        """Configura métodos de armazenamento disponíveis"""
        
        # Método 1: Streamlit Session State (temporário mas funcional)
        self.storage_methods.append({
            'name': 'session_state',
            'description': 'Streamlit Session State',
            'save_func': self._save_to_session_state,
            'load_func': self._load_from_session_state,
            'permanent': False
        })
        
        # Método 2: Base64 encoding em arquivo de configuração
        self.storage_methods.append({
            'name': 'encoded_config',
            'description': 'Arquivo de configuração codificado',
            'save_func': self._save_to_encoded_config,
            'load_func': self._load_from_encoded_config,
            'permanent': True
        })
        
        # Método 3: JSON embeddado no código (fallback)
        self.storage_methods.append({
            'name': 'embedded_json',
            'description': 'JSON embeddado no código',
            'save_func': self._save_to_embedded_json,
            'load_func': self._load_from_embedded_json,
            'permanent': True
        })
    
    def save_data(self, df):
        """Salva dados usando todos os métodos disponíveis"""
        success_count = 0
        
        for method in self.storage_methods:
            try:
                method['save_func'](df)
                success_count += 1
                print(f"✅ Dados salvos em: {method['description']}")
            except Exception as e:
                print(f"❌ Falha em {method['description']}: {e}")
        
        return success_count > 0
    
    def load_data(self):
        """Carrega dados do primeiro método disponível"""
        for method in self.storage_methods:
            try:
                df = method['load_func']()
                if df is not None and not df.empty:
                    print(f"✅ Dados carregados de: {method['description']}")
                    return df
            except Exception as e:
                print(f"⚠️ Falha ao carregar de {method['description']}: {e}")
                continue
        
        # Retornar DataFrame vazio se nenhum método funcionou
        return pd.DataFrame(columns=['name', 'signup_date', 'plan_value', 'status', 'cancel_date'])
    
    def _save_to_session_state(self, df):
        """Salva no Streamlit Session State"""
        if 'customer_data' not in st.session_state:
            st.session_state.customer_data = {}
        
        st.session_state.customer_data = {
            'data': df.to_dict('records'),
            'timestamp': datetime.now().isoformat()
        }
    
    def _load_from_session_state(self):
        """Carrega do Streamlit Session State"""
        if 'customer_data' in st.session_state and st.session_state.customer_data:
            data = st.session_state.customer_data['data']
            return pd.DataFrame(data)
        return None
    
    def _save_to_encoded_config(self, df):
        """Salva em arquivo de configuração codificado"""
        config_data = {
            'app_config': {
                'version': '1.0',
                'theme': 'default'
            },
            'data_backup': base64.b64encode(df.to_json().encode()).decode(),
            'timestamp': datetime.now().isoformat()
        }
        
        with open('.streamlit/config.toml', 'a') as f:
            f.write(f"\n# Data backup: {config_data['timestamp']}\n")
            f.write(f"# backup_data = \"{config_data['data_backup']}\"\n")
    
    def _load_from_encoded_config(self):
        """Carrega de arquivo de configuração codificado"""
        try:
            if os.path.exists('.streamlit/config.toml'):
                with open('.streamlit/config.toml', 'r') as f:
                    content = f.read()
                    # Procurar linha de backup mais recente
                    lines = content.split('\n')
                    for line in reversed(lines):
                        if line.startswith('# backup_data = '):
                            encoded_data = line.split('"')[1]
                            json_data = base64.b64decode(encoded_data).decode()
                            return pd.read_json(json_data)
        except:
            pass
        return None
    
    def _save_to_embedded_json(self, df):
        """Salva criando arquivo Python com dados embeddidos"""
        data_dict = df.to_dict('records')
        
        python_code = f'''#!/usr/bin/env python3
"""
Dados persistentes do dashboard - Gerado automaticamente
Timestamp: {datetime.now().isoformat()}
"""

CUSTOMER_DATA = {data_dict}

def get_embedded_data():
    """Retorna dados embeddidos"""
    import pandas as pd
    return pd.DataFrame(CUSTOMER_DATA)
'''
        
        with open('embedded_data.py', 'w') as f:
            f.write(python_code)
    
    def _load_from_embedded_json(self):
        """Carrega de arquivo Python com dados embeddidos"""
        try:
            if os.path.exists('embedded_data.py'):
                import embedded_data
                return embedded_data.get_embedded_data()
        except:
            pass
        return None
    
    def get_storage_status(self):
        """Retorna status dos métodos de armazenamento"""
        status = []
        for method in self.storage_methods:
            try:
                df = method['load_func']()
                record_count = len(df) if df is not None and not df.empty else 0
                status.append({
                    'method': method['description'],
                    'permanent': method['permanent'],
                    'records': record_count,
                    'available': record_count > 0
                })
            except:
                status.append({
                    'method': method['description'],
                    'permanent': method['permanent'],
                    'records': 0,
                    'available': False
                })
        
        return status
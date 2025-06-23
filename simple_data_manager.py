import pandas as pd
import os
from datetime import datetime
import streamlit as st

class SimpleDataManager:
    def __init__(self):
        self.customers_file = "customers_simple.csv"
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Garante que o arquivo CSV existe"""
        if not os.path.exists(self.customers_file):
            # Criar arquivo de clientes vazio com estrutura simplificada
            customers_df = pd.DataFrame(columns=[
                'name', 'signup_date', 'plan_value', 'status', 'cancel_date'
            ])
            customers_df.to_csv(self.customers_file, index=False)
    
    def load_customers(self):
        """Carrega dados de clientes"""
        try:
            df = pd.read_csv(self.customers_file)
            if not df.empty:
                df['signup_date'] = pd.to_datetime(df['signup_date'])
                df['cancel_date'] = pd.to_datetime(df['cancel_date'], errors='coerce')
            return df
        except Exception as e:
            return pd.DataFrame(columns=['name', 'signup_date', 'plan_value', 'status', 'cancel_date'])
    
    def add_customer(self, name, signup_date, plan_value, status, cancel_date=None):
        """Adiciona um novo cliente"""
        try:
            df = self.load_customers()
            
            new_customer = pd.DataFrame({
                'name': [name],
                'signup_date': [signup_date],
                'plan_value': [plan_value],
                'status': [status],
                'cancel_date': [cancel_date if cancel_date else None]
            })
            
            df = pd.concat([df, new_customer], ignore_index=True)
            df.to_csv(self.customers_file, index=False)
            return True
        except Exception as e:
            return False
    
    def remove_customer(self, index):
        """Remove um cliente pelo índice"""
        try:
            df = self.load_customers()
            df = df.drop(df.index[index])
            df.to_csv(self.customers_file, index=False)
            return True
        except Exception as e:
            return False
    
    def update_customer_status(self, index, new_status, cancel_date=None):
        """Atualiza status do cliente"""
        try:
            df = self.load_customers()
            df.loc[index, 'status'] = new_status
            if cancel_date:
                df.loc[index, 'cancel_date'] = cancel_date
            df.to_csv(self.customers_file, index=False)
            return True
        except Exception as e:
            return False
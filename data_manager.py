import pandas as pd
import os
from datetime import datetime
import streamlit as st

class DataManager:
    def __init__(self):
        self.customers_file = "customers.csv"
        self.sales_file = "sales.csv"
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Garante que os arquivos CSV existam"""
        if not os.path.exists(self.customers_file):
            # Crear arquivo de clientes vazio
            customers_df = pd.DataFrame(columns=[
                'customer_id', 'name', 'signup_date', 'plan_value', 
                'status', 'cancel_date'
            ])
            customers_df.to_csv(self.customers_file, index=False)
        
        if not os.path.exists(self.sales_file):
            # Crear arquivo de vendas vazio
            sales_df = pd.DataFrame(columns=[
                'customer_id', 'date', 'value', 'type', 'description'
            ])
            sales_df.to_csv(self.sales_file, index=False)
    
    def load_customers(self):
        """Carrega dados de clientes"""
        try:
            df = pd.read_csv(self.customers_file)
            if not df.empty:
                df['signup_date'] = pd.to_datetime(df['signup_date'])
                df['cancel_date'] = pd.to_datetime(df['cancel_date'], errors='coerce')
            return df
        except Exception as e:
            st.error(f"Erro ao carregar clientes: {e}")
            return pd.DataFrame()
    
    def load_sales(self):
        """Carrega dados de vendas"""
        try:
            df = pd.read_csv(self.sales_file)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
            return df
        except Exception as e:
            st.error(f"Erro ao carregar vendas: {e}")
            return pd.DataFrame()
    
    def add_customer(self, customer_id, name, signup_date, plan_value, status, cancel_date=None):
        """Adiciona um novo cliente"""
        try:
            df = self.load_customers()
            
            # Verifica se cliente já existe
            if not df.empty and customer_id in df['customer_id'].values:
                return False
            
            new_customer = pd.DataFrame({
                'customer_id': [customer_id],
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
            st.error(f"Erro ao adicionar cliente: {e}")
            return False
    
    def add_sale(self, customer_id, date, value, sale_type, description=""):
        """Adiciona uma nova venda"""
        try:
            # Verifica se cliente existe
            customers_df = self.load_customers()
            if customers_df.empty or customer_id not in customers_df['customer_id'].values:
                return False
            
            sales_df = self.load_sales()
            
            new_sale = pd.DataFrame({
                'customer_id': [customer_id],
                'date': [date],
                'value': [value],
                'type': [sale_type],
                'description': [description]
            })
            
            sales_df = pd.concat([sales_df, new_sale], ignore_index=True)
            sales_df.to_csv(self.sales_file, index=False)
            return True
        except Exception as e:
            st.error(f"Erro ao adicionar venda: {e}")
            return False
    
    def remove_customer(self, customer_id):
        """Remove um cliente"""
        try:
            df = self.load_customers()
            df = df[df['customer_id'] != customer_id]
            df.to_csv(self.customers_file, index=False)
            
            # Remove vendas associadas
            sales_df = self.load_sales()
            sales_df = sales_df[sales_df['customer_id'] != customer_id]
            sales_df.to_csv(self.sales_file, index=False)
            
            return True
        except Exception as e:
            st.error(f"Erro ao remover cliente: {e}")
            return False
    
    def remove_sale(self, sale_index):
        """Remove uma venda pelo índice"""
        try:
            df = self.load_sales()
            df = df.drop(df.index[sale_index])
            df.to_csv(self.sales_file, index=False)
            return True
        except Exception as e:
            st.error(f"Erro ao remover venda: {e}")
            return False
    
    def update_customer_status(self, customer_id, new_status, cancel_date=None):
        """Atualiza status do cliente"""
        try:
            df = self.load_customers()
            mask = df['customer_id'] == customer_id
            df.loc[mask, 'status'] = new_status
            if cancel_date:
                df.loc[mask, 'cancel_date'] = cancel_date
            df.to_csv(self.customers_file, index=False)
            return True
        except Exception as e:
            st.error(f"Erro ao atualizar cliente: {e}")
            return False

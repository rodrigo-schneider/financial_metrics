#!/usr/bin/env python3
"""
Gerenciador de banco de dados PostgreSQL (Supabase)
Sistema de persistência permanente na nuvem
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Float, Date, Integer
from sqlalchemy.exc import SQLAlchemyError
import streamlit as st
from datetime import datetime
import traceback

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.metadata = MetaData()
        self._setup_connection()
        self._setup_tables()
    
    def _setup_connection(self):
        """Configura conexão com o banco de dados"""
        try:
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                st.warning("⚠️ DATABASE_URL not configured. Using local CSV storage.")
                return
            
            # Configurar SSL para Supabase
            if 'supabase' in database_url:
                database_url += "?sslmode=require"
            
            self.engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False  # Set to True for debugging SQL queries
            )
            
            # Testar conexão
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            print("✅ Conexão com banco de dados estabelecida")
            
        except Exception as e:
            print(f"❌ Erro ao conectar com banco: {e}")
            self.engine = None
    
    def _setup_tables(self):
        """Cria tabelas se não existirem"""
        if not self.engine:
            return
        
        try:
            # Definir estrutura da tabela customers
            self.customers_table = Table(
                'customers',
                self.metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('name', String(255), nullable=False),
                Column('signup_date', Date, nullable=False),
                Column('plan_value', Float, nullable=False),
                Column('status', String(50), nullable=False),
                Column('cancel_date', Date, nullable=True),
                extend_existing=True
            )
            
            # Criar tabelas
            self.metadata.create_all(self.engine)
            print("✅ Tabelas do banco criadas/verificadas")
            
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")
    
    def is_connected(self):
        """Verifica se está conectado ao banco"""
        return self.engine is not None
    
    def save_customers(self, df):
        """Salva dados de clientes no banco"""
        if not self.is_connected():
            return False
        
        try:
            # Limpar dados existentes e inserir novos
            with self.engine.connect() as conn:
                conn.execute(text("DELETE FROM customers"))
                
                # Inserir novos dados
                for _, row in df.iterrows():
                    # Converter datas para o formato correto
                    signup_date = pd.to_datetime(row['signup_date']).date() if pd.notna(row['signup_date']) else None
                    cancel_date = pd.to_datetime(row['cancel_date']).date() if pd.notna(row['cancel_date']) else None
                    
                    conn.execute(
                        text("""
                            INSERT INTO customers (name, signup_date, plan_value, status, cancel_date)
                            VALUES (:name, :signup_date, :plan_value, :status, :cancel_date)
                        """),
                        {
                            'name': str(row['name']),
                            'signup_date': signup_date,
                            'plan_value': float(row['plan_value']),
                            'status': str(row['status']),
                            'cancel_date': cancel_date
                        }
                    )
                
                conn.commit()
            
            print(f"✅ {len(df)} clientes salvos no banco de dados")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar no banco: {e}")
            traceback.print_exc()
            return False
    
    def load_customers(self):
        """Carrega dados de clientes do banco"""
        if not self.is_connected():
            return pd.DataFrame()
        
        try:
            query = """
                SELECT name, signup_date, plan_value, status, cancel_date
                FROM customers
                ORDER BY id
            """
            
            df = pd.read_sql(query, self.engine)
            
            # Converter colunas de data
            if not df.empty:
                df['signup_date'] = pd.to_datetime(df['signup_date'], errors='coerce')
                df['cancel_date'] = pd.to_datetime(df['cancel_date'], errors='coerce')
            
            print(f"✅ {len(df)} clientes carregados do banco de dados")
            return df
            
        except Exception as e:
            print(f"❌ Erro ao carregar do banco: {e}")
            return pd.DataFrame()
    
    def test_connection(self):
        """Testa conexão e retorna status detalhado"""
        if not self.engine:
            return {
                'connected': False,
                'error': 'Engine não inicializado - DATABASE_URL não configurada'
            }
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version_info = result.fetchone()[0]
                
                # Verificar se tabela existe
                table_check = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'customers'
                    )
                """))
                table_exists = table_check.fetchone()[0]
                
                # Contar registros
                if table_exists:
                    count_result = conn.execute(text("SELECT COUNT(*) FROM customers"))
                    record_count = count_result.fetchone()[0]
                else:
                    record_count = 0
                
                return {
                    'connected': True,
                    'version': version_info,
                    'table_exists': table_exists,
                    'record_count': record_count,
                    'url_host': self.engine.url.host
                }
                
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }
    
    def get_connection_status(self):
        """Retorna status de conexão formatado para exibição"""
        status = self.test_connection()
        
        if status['connected']:
            return f"""
            ✅ **Conectado ao Banco PostgreSQL**
            - Host: {status['url_host']}
            - Tabela 'customers': {'✅ Existe' if status['table_exists'] else '❌ Não existe'}
            - Registros salvos: {status['record_count']}
            """
        else:
            return f"""
            ❌ **Não conectado ao banco**
            - Erro: {status['error']}
            - Usando armazenamento local CSV
            """
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date
import os
import calendar
import shutil
from persistent_storage import PersistentStorageManager
from database_manager import DatabaseManager

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Métricas de Clientes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gerenciador de dados robusto com validações
class DataManager:
    def __init__(self):
        self.customers_file = "customers_simple.csv"
        self.backup_files = [
            "customers_permanent_backup.csv",
            "customers_recovery_backup.csv", 
            "customers_master_backup.csv"
        ]
        self.persistent_storage = PersistentStorageManager()
        self.database_manager = DatabaseManager()
        self._ensure_permanent_storage()
        self._ensure_file_exists()
    
    def _ensure_permanent_storage(self):
        """Sistema de recuperação automática de dados permanentes"""
        try:
            # Verificar se existe backup permanente
            for backup_file in self.backup_files:
                if os.path.exists(backup_file):
                    # Recuperar dados do backup mais recente
                    backup_df = pd.read_csv(backup_file)
                    if not backup_df.empty:
                        # Restaurar arquivo principal se não existir ou estiver vazio
                        if not os.path.exists(self.customers_file):
                            backup_df.to_csv(self.customers_file, index=False)
                            print(f"🔄 Dados recuperados de {backup_file}")
                        else:
                            # Verificar se arquivo principal tem menos dados que backup
                            main_df = pd.read_csv(self.customers_file)
                            if len(main_df) < len(backup_df):
                                backup_df.to_csv(self.customers_file, index=False)
                                print(f"🔄 Dados atualizados de {backup_file}")
                        break
        except Exception as e:
            print(f"⚠️ Erro na recuperação automática: {e}")
    
    def _create_permanent_backups(self, df):
        """Cria backups permanentes em múltiplos arquivos"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for backup_file in self.backup_files:
            try:
                df.to_csv(backup_file, index=False)
                # Criar backup com timestamp também
                timestamped_backup = f"backup_{timestamp}_{backup_file}"
                df.to_csv(timestamped_backup, index=False)
            except Exception as e:
                print(f"⚠️ Erro ao criar backup {backup_file}: {e}")
    
    def _ensure_file_exists(self):
        """Garante que o arquivo CSV existe com estrutura correta"""
        try:
            if not os.path.exists(self.customers_file):
                customers_df = pd.DataFrame(columns=[
                    'name', 'signup_date', 'plan_value', 'status', 'cancel_date'
                ])
                customers_df.to_csv(self.customers_file, index=False)
            else:
                # Verificar se arquivo tem estrutura correta
                df = pd.read_csv(self.customers_file)
                expected_columns = ['name', 'signup_date', 'plan_value', 'status', 'cancel_date']
                if not all(col in df.columns for col in expected_columns):
                    # Recriar arquivo com estrutura correta
                    customers_df = pd.DataFrame(columns=expected_columns)
                    customers_df.to_csv(self.customers_file, index=False)
        except Exception as e:
            # Em caso de erro, criar arquivo novo
            customers_df = pd.DataFrame(columns=[
                'name', 'signup_date', 'plan_value', 'status', 'cancel_date'
            ])
            customers_df.to_csv(self.customers_file, index=False)
    
    def load_customers(self):
        """Carrega dados de clientes com prioridade: Banco → Sistema externo → CSV local"""
        try:
            # 1. Tentar carregar do banco de dados primeiro (mais confiável)
            if self.database_manager.is_connected():
                df = self.database_manager.load_customers()
                if not df.empty:
                    df = self._process_loaded_data(df)
                    print("✅ Dados carregados do banco PostgreSQL")
                    return df
            
            # 2. Tentar carregar do sistema de persistência externa
            df = self.persistent_storage.load_data()
            if df is not None and not df.empty:
                df = self._process_loaded_data(df)
                
                # Sincronizar com banco de dados se disponível
                if self.database_manager.is_connected():
                    self.database_manager.save_customers(df)
                    print("🔄 Dados sincronizados com banco PostgreSQL")
                
                print("✅ Dados carregados de: " + self.persistent_storage.last_successful_method)
                return df
            
            # 3. Se não conseguir carregar do sistema externo, tentar CSV local
            if os.path.exists(self.customers_file):
                df = pd.read_csv(self.customers_file)
                if not df.empty:
                    df = self._process_loaded_data(df)
                    
                    # Salvar em ambos os sistemas
                    self.persistent_storage.save_data(df)
                    if self.database_manager.is_connected():
                        self.database_manager.save_customers(df)
                        print("🔄 Dados migrados para banco PostgreSQL")
                    
                    print(f"🔄 Dados atualizados de {self.customers_file}")
                    return df
            
            # Se nenhum dado existir, criar estrutura vazia
            self._ensure_file_exists()
            return pd.DataFrame(columns=['name', 'signup_date', 'plan_value', 'status', 'cancel_date'])
            
        except Exception as e:
            print(f"Erro no carregamento: {e}")
            return pd.DataFrame(columns=['name', 'signup_date', 'plan_value', 'status', 'cancel_date'])
    
    def _process_loaded_data(self, df):
        """Processa dados carregados garantindo tipos corretos"""
        try:
            df['plan_value'] = pd.to_numeric(df['plan_value'], errors='coerce')
            df['plan_value'] = df['plan_value'].fillna(0)
        except:
            df['plan_value'] = 0
        
        return df
    
    def add_customer(self, name, signup_date, plan_value, status, cancel_date=None):
        """Adiciona cliente com validações e salvamento ultra-robusto"""
        try:
            # Validações de entrada
            if not name or not name.strip():
                return False
            
            if not isinstance(plan_value, (int, float)) or plan_value <= 0:
                return False
            
            if status not in ['Ativo', 'Cancelado']:
                return False
            
            # Carregar dados existentes
            df = self.load_customers()
            original_length = len(df)
            
            # Preparar novo cliente
            new_customer_data = {
                'name': str(name).strip(),
                'signup_date': pd.to_datetime(signup_date).strftime('%Y-%m-%d'),
                'plan_value': float(plan_value),
                'status': str(status),
                'cancel_date': pd.to_datetime(cancel_date).strftime('%Y-%m-%d') if cancel_date else None
            }
            
            # Criar DataFrame para novo cliente
            new_customer = pd.DataFrame([new_customer_data])
            
            # Concatenar dados
            df = pd.concat([df, new_customer], ignore_index=True)
            expected_length = original_length + 1
            
            # Criar backups permanentes ANTES de salvar
            self._create_permanent_backups(df)
            
            # Salvar no banco de dados (prioridade)
            database_save_success = False
            if self.database_manager.is_connected():
                database_save_success = self.database_manager.save_customers(df)
            
            # Salvar no sistema de persistência externa (backup)
            external_save_success = self.persistent_storage.save_data(df)
            
            # Criar múltiplos backups temporários também
            backup_file = f"{self.customers_file}.backup"
            backup_file2 = f"{self.customers_file}.backup2"
            backup_file3 = f"{self.customers_file}.backup3"
            
            if os.path.exists(self.customers_file):
                shutil.copy2(self.customers_file, backup_file)
                shutil.copy2(self.customers_file, backup_file2)
                shutil.copy2(self.customers_file, backup_file3)
            
            # Salvar dados com verificação tripla
            success_count = 0
            
            # Tentativa 1: Salvar arquivo principal
            try:
                df.to_csv(self.customers_file, index=False)
                # Verificar imediatamente
                test_df = pd.read_csv(self.customers_file)
                if len(test_df) == expected_length and test_df.iloc[-1]['name'] == name:
                    success_count += 1
            except:
                pass
            
            # Tentativa 2: Salvar arquivo de segurança 1
            temp_file1 = f"{self.customers_file}.temp1"
            try:
                df.to_csv(temp_file1, index=False)
                test_df = pd.read_csv(temp_file1)
                if len(test_df) == expected_length and test_df.iloc[-1]['name'] == name:
                    success_count += 1
                    # Se o principal falhou, usar este como principal
                    if success_count == 1:
                        shutil.copy2(temp_file1, self.customers_file)
            except:
                pass
            
            # Tentativa 3: Salvar arquivo de segurança 2
            temp_file2 = f"{self.customers_file}.temp2"
            try:
                df.to_csv(temp_file2, index=False)
                test_df = pd.read_csv(temp_file2)
                if len(test_df) == expected_length and test_df.iloc[-1]['name'] == name:
                    success_count += 1
                    # Se os anteriores falharam, usar este como principal
                    if success_count == 1:
                        shutil.copy2(temp_file2, self.customers_file)
            except:
                pass
            
            # Verificação final múltipla
            final_verification = False
            try:
                final_df = pd.read_csv(self.customers_file)
                if len(final_df) == expected_length:
                    last_customer = final_df.iloc[-1]
                    if (last_customer['name'] == name and 
                        last_customer['plan_value'] == plan_value and
                        last_customer['status'] == status):
                        final_verification = True
            except:
                pass
            
            # Limpar arquivos temporários
            for temp_file in [temp_file1, temp_file2]:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
            
            # Se falhou completamente, tentar restaurar do melhor backup
            if not final_verification or success_count == 0:
                for backup in [backup_file, backup_file2, backup_file3]:
                    try:
                        if os.path.exists(backup):
                            shutil.copy2(backup, self.customers_file)
                            break
                    except:
                        continue
                return False
            
            print(f"✅ Cliente adicionado - Banco: {'OK' if database_save_success else 'N/A'}, Sistema externo: {'OK' if external_save_success else 'FALHOU'}")
            return True
            
        except Exception as e:
            print(f"Erro ao adicionar cliente: {e}")
            # Última tentativa de restauração
            for backup in [f"{self.customers_file}.backup", 
                          f"{self.customers_file}.backup2", 
                          f"{self.customers_file}.backup3"]:
                try:
                    if os.path.exists(backup):
                        shutil.copy2(backup, self.customers_file)
                        break
                except:
                    continue
            return False
    
    def remove_customer(self, index):
        """Remove cliente com validações e persistência externa"""
        try:
            df = self.load_customers()
            
            if df.empty or index < 0 or index >= len(df):
                print(f"Erro: Índice inválido {index} para DataFrame com {len(df)} registros")
                return False
            
            # Backup antes de remover
            self._create_permanent_backups(df)
            backup_file = f"{self.customers_file}.backup"
            if os.path.exists(self.customers_file):
                shutil.copy2(self.customers_file, backup_file)
            
            # Remover cliente pelo índice
            df_updated = df.drop(df.index[index]).reset_index(drop=True)
            
            # Salvar no banco de dados (prioridade)
            database_save_success = False
            if self.database_manager.is_connected():
                database_save_success = self.database_manager.save_customers(df_updated)
            
            # Salvar no sistema de persistência externa (backup)
            external_save_success = self.persistent_storage.save_data(df_updated)
            
            # Salvar localmente (backup local)
            df_updated.to_csv(self.customers_file, index=False)
            
            # Verificar se a remoção foi bem-sucedida
            df_verify = self.load_customers()
            if len(df_verify) == len(df) - 1:
                print(f"✅ Cliente removido - Banco: {'OK' if database_save_success else 'N/A'}, Sistema externo: {'OK' if external_save_success else 'FALHOU'}")
                return True
            else:
                print(f"❌ Falha na verificação: esperado {len(df) - 1}, obtido {len(df_verify)}")
                return False
            
        except Exception as e:
            print(f"Erro ao remover cliente: {e}")
            # Restaurar backup em caso de erro
            backup_file = f"{self.customers_file}.backup"
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, self.customers_file)
            return False
    
    def update_customer(self, index, name, signup_date, plan_value, status, cancel_date=None):
        """Atualiza dados completos do cliente com validações e salvamento ultra-robusto"""
        try:
            df = self.load_customers()
            
            if df.empty or index < 0 or index >= len(df):
                print(f"Erro: Índice inválido {index} para DataFrame com {len(df)} registros")
                return False
            
            # Backup antes de atualizar
            self._create_permanent_backups(df)
            backup_file = f"{self.customers_file}.backup"
            if os.path.exists(self.customers_file):
                shutil.copy2(self.customers_file, backup_file)
            
            # Atualizar dados do cliente
            df.loc[index, 'name'] = name
            df.loc[index, 'signup_date'] = signup_date
            df.loc[index, 'plan_value'] = plan_value
            df.loc[index, 'status'] = status
            df.loc[index, 'cancel_date'] = cancel_date if cancel_date else None
            
            # Salvar no banco de dados (prioridade)
            database_save_success = False
            if self.database_manager.is_connected():
                database_save_success = self.database_manager.save_customers(df)
            
            # Salvar no sistema de persistência externa (backup)
            external_save_success = self.persistent_storage.save_data(df)
            
            # Salvar localmente (backup local)
            df.to_csv(self.customers_file, index=False)
            
            # Verificar se a atualização foi bem-sucedida
            df_verify = self.load_customers()
            if len(df_verify) == len(df) and df_verify.loc[index, 'name'] == name:
                print(f"✅ Cliente atualizado - Banco: {'OK' if database_save_success else 'N/A'}, Sistema externo: {'OK' if external_save_success else 'FALHOU'}")
                return True
            else:
                print(f"❌ Falha na verificação da atualização")
                return False
            
        except Exception as e:
            print(f"Erro ao atualizar cliente: {e}")
            # Restaurar backup em caso de erro
            backup_file = f"{self.customers_file}.backup"
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, self.customers_file)
            return False

# Calculadora de métricas corrigida e robusta
class MetricsCalculator:
    def __init__(self, customers_df):
        self.customers_df = customers_df.copy()
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepara e valida os dados para cálculos"""
        if self.customers_df.empty:
            return
            
        # Garantir que as datas estão no formato datetime
        self.customers_df['signup_date'] = pd.to_datetime(self.customers_df['signup_date'], errors='coerce')
        self.customers_df['cancel_date'] = pd.to_datetime(self.customers_df['cancel_date'], errors='coerce')
        
        # Garantir que plan_value é numérico
        self.customers_df['plan_value'] = pd.to_numeric(self.customers_df['plan_value'], errors='coerce')
        self.customers_df['plan_value'] = self.customers_df['plan_value'].fillna(0)
        
        # Remover linhas com dados inválidos
        self.customers_df = self.customers_df.dropna(subset=['signup_date'])
    
    def calculate_monthly_metrics(self):
        if self.customers_df.empty:
            return pd.DataFrame()
        
        start_date, end_date = self._get_analysis_period()
        months = self._generate_month_list(start_date, end_date)
        
        metrics_list = []
        for month_date in months:
            month_str = month_date.strftime('%Y-%m')
            new_customers = self._calculate_new_customers(month_date)
            mrr = self._calculate_mrr(month_date)
            avg_ticket = self._calculate_avg_ticket(month_date)
            churn_customers, churn_mrr = self._calculate_churn(month_date)
            
            metrics_list.append({
                'mes_ano': month_str,
                'novos_clientes': int(new_customers),
                'mrr': float(mrr),
                'ticket_medio': float(avg_ticket),
                'churn_clientes': int(churn_customers),
                'churn_mrr': float(churn_mrr)
            })
        
        return pd.DataFrame(metrics_list)
    
    def _get_analysis_period(self):
        """Determina o período de análise com base nos dados"""
        if self.customers_df.empty:
            now = datetime.now()
            return now.replace(day=1), now
        
        # Encontrar a primeira data de cadastro
        min_signup = self.customers_df['signup_date'].min()
        
        # Encontrar a data mais recente (cadastro ou cancelamento)
        max_date = self.customers_df['signup_date'].max()
        cancel_dates = self.customers_df['cancel_date'].dropna()
        if not cancel_dates.empty:
            max_cancel = cancel_dates.max()
            max_date = max(max_date, max_cancel)
        
        # Garantir que analisamos até o mês atual
        now = datetime.now()
        end_date = max(max_date, now)
        
        # Converter para primeiro dia do mês
        start_date = min_signup.replace(day=1)
        end_date = end_date.replace(day=1)
        
        return start_date, end_date
    
    def _generate_month_list(self, start_date, end_date):
        """Gera lista de primeiros dias de cada mês no período"""
        months = []
        current = start_date
        
        while current <= end_date:
            months.append(current)
            # Avançar para o próximo mês
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        return months
    
    def _calculate_new_customers(self, month_date):
        """Calcula novos clientes que se cadastraram no mês"""
        month_start = month_date.replace(day=1)
        month_end = self._get_month_end(month_date)
        
        new_customers = self.customers_df[
            (self.customers_df['signup_date'] >= month_start) &
            (self.customers_df['signup_date'] <= month_end)
        ]
        
        return len(new_customers)
    
    def _calculate_mrr(self, month_date):
        """Calcula MRR (clientes ativos no final do mês)"""
        month_end = self._get_month_end(month_date)
        
        # Clientes que já tinham se cadastrado até o final do mês
        # E que não tinham cancelado até o final do mês
        active_customers = self.customers_df[
            (self.customers_df['signup_date'] <= month_end) &
            (
                (self.customers_df['cancel_date'].isna()) |
                (self.customers_df['cancel_date'] > month_end)
            )
        ]
        
        return active_customers['plan_value'].sum()
    
    def _calculate_avg_ticket(self, month_date):
        """Calcula ticket médio dos clientes ativos no final do mês"""
        month_end = self._get_month_end(month_date)
        
        active_customers = self.customers_df[
            (self.customers_df['signup_date'] <= month_end) &
            (
                (self.customers_df['cancel_date'].isna()) |
                (self.customers_df['cancel_date'] > month_end)
            )
        ]
        
        if active_customers.empty:
            return 0.0
        
        return active_customers['plan_value'].mean()
    
    def _calculate_churn(self, month_date):
        """Calcula churn de clientes e MRR no mês - apenas clientes com 2+ meses"""
        month_start = month_date.replace(day=1)
        month_end = self._get_month_end(month_date)
        
        # Clientes que cancelaram durante o mês
        canceled_this_month = self.customers_df[
            (self.customers_df['cancel_date'] >= month_start) &
            (self.customers_df['cancel_date'] <= month_end) &
            (self.customers_df['cancel_date'].notna())
        ].copy()
        
        if canceled_this_month.empty:
            return 0, 0.0
        
        # Filtrar apenas clientes que ficaram pelo menos 2 meses
        # Calcular diferença em meses entre signup_date e cancel_date
        def months_between(start_date, end_date):
            return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        
        # Aplicar filtro de 2+ meses
        churned_customers = canceled_this_month[
            canceled_this_month.apply(
                lambda row: months_between(row['signup_date'], row['cancel_date']) >= 2, 
                axis=1
            )
        ]
        
        churn_count = len(churned_customers)
        churn_value = churned_customers['plan_value'].sum()
        
        return churn_count, churn_value
    
    def calculate_ltv_metrics(self):
        """Calcula métricas de LTV (Lifetime Value) dos clientes"""
        if self.customers_df.empty:
            return {
                'ltv_medio': 0.0,
                'ltv_clientes_ativos': 0.0,
                'ltv_clientes_cancelados': 0.0,
                'tempo_vida_medio_meses': 0.0,
                'total_clientes_analisados': 0
            }
        
        # Calcular LTV para cada cliente
        ltv_data = []
        current_date = pd.Timestamp.now()
        
        for _, cliente in self.customers_df.iterrows():
            signup_date = cliente['signup_date']
            cancel_date = cliente['cancel_date']
            plan_value = cliente['plan_value']
            
            # Determinar data final (cancelamento ou data atual)
            end_date = cancel_date if pd.notna(cancel_date) else current_date
            
            # Calcular meses de vida do cliente
            months_active = max(1, (end_date.year - signup_date.year) * 12 + (end_date.month - signup_date.month))
            
            # LTV = valor mensal × meses ativos
            ltv = plan_value * months_active
            
            ltv_data.append({
                'cliente': cliente['name'],
                'ltv': ltv,
                'months_active': months_active,
                'plan_value': plan_value,
                'is_active': pd.isna(cancel_date),
                'signup_date': signup_date,
                'cancel_date': cancel_date
            })
        
        ltv_df = pd.DataFrame(ltv_data)
        
        # Calcular métricas agregadas
        ltv_medio = ltv_df['ltv'].mean()
        ltv_clientes_ativos = ltv_df[ltv_df['is_active']]['ltv'].mean() if ltv_df['is_active'].any() else 0
        ltv_clientes_cancelados = ltv_df[~ltv_df['is_active']]['ltv'].mean() if (~ltv_df['is_active']).any() else 0
        tempo_vida_medio = ltv_df['months_active'].mean()
        
        return {
            'ltv_medio': ltv_medio,
            'ltv_clientes_ativos': ltv_clientes_ativos,
            'ltv_clientes_cancelados': ltv_clientes_cancelados,
            'tempo_vida_medio_meses': tempo_vida_medio,
            'total_clientes_analisados': len(ltv_df),
            'ltv_detalhado': ltv_df
        }
    
    def _get_month_end(self, month_date):
        """Retorna o último momento do mês"""
        last_day = calendar.monthrange(month_date.year, month_date.month)[1]
        return month_date.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

# Funções de visualização simplificadas e mais visuais
def create_visualizations(monthly_metrics):
    if monthly_metrics.empty:
        return {}
    
    colors = {'primary': '#3b82f6', 'success': '#10b981', 'warning': '#f59e0b', 'danger': '#ef4444'}
    
    # 1. Gráfico de novos clientes por mês - simplificado
    fig_customers = go.Figure()
    
    # Filtrar apenas dados com valores > 0 para evitar poluição visual
    customers_filtered = monthly_metrics[monthly_metrics['novos_clientes'] > 0].copy()
    
    fig_customers.add_trace(go.Bar(
        x=customers_filtered['mes_ano'],
        y=customers_filtered['novos_clientes'],
        name='Novos Clientes',
        marker_color=colors['primary'],
        text=customers_filtered['novos_clientes'],
        texttemplate='<b>%{text}</b>',
        textposition='outside',
        textfont=dict(size=18, color='black', family='Arial Black'),
        marker=dict(
            line=dict(color='white', width=2),
            opacity=0.95
        ),
        width=0.6
    ))
    
    fig_customers.update_layout(
        title=dict(
            text='👥 NOVOS CLIENTES POR MÊS',
            font=dict(size=24, family='Arial Black', color='#2c3e50'),
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            title=dict(text='MÊS', font=dict(size=16, family='Arial Black')),
            tickfont=dict(size=14, family='Arial Black'),
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=False,
            tickangle=0
        ),
        yaxis=dict(
            title=dict(text='QUANTIDADE', font=dict(size=16, family='Arial Black')),
            tickfont=dict(size=14, family='Arial Black'),
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=True,
            rangemode='tozero'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        height=450,
        margin=dict(t=80, b=60, l=80, r=50)
    )
    
    # 2. Gráfico de MRR - linha simplificada
    fig_mrr = go.Figure()
    
    # Filtrar apenas dados com MRR > 0
    mrr_filtered = monthly_metrics[monthly_metrics['mrr'] > 0].copy()
    
    fig_mrr.add_trace(go.Scatter(
        x=mrr_filtered['mes_ano'],
        y=mrr_filtered['mrr'],
        mode='lines+markers+text',
        name='MRR',
        line=dict(color=colors['success'], width=6),
        marker=dict(
            size=16,
            color=colors['success'],
            line=dict(color='white', width=3),
            symbol='circle'
        ),
        text=mrr_filtered['mrr'],
        texttemplate='<b>$%{text:,.0f}</b>',
        textposition='top center',
        textfont=dict(size=18, color='black', family='Arial Black')
    ))
    
    fig_mrr.update_layout(
        title=dict(
            text='💰 FATURAMENTO MENSAL (MRR)',
            font=dict(size=24, family='Arial Black', color='#2c3e50'),
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            title=dict(text='MÊS', font=dict(size=16, family='Arial Black')),
            tickfont=dict(size=14, family='Arial Black'),
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=False,
            tickangle=0
        ),
        yaxis=dict(
            title=dict(text='RECEITA (USD)', font=dict(size=16, family='Arial Black')),
            tickfont=dict(size=14, family='Arial Black'),
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=True,
            tickformat='$,.0f',
            rangemode='tozero'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        height=450,
        margin=dict(t=80, b=60, l=100, r=50)
    )
    
    # 3. Gráfico de ticket médio - barras simplificadas
    fig_ticket = go.Figure()
    
    # Filtrar dados com ticket médio > 0
    ticket_filtered = monthly_metrics[monthly_metrics['ticket_medio'] > 0].copy()
    
    fig_ticket.add_trace(go.Bar(
        x=ticket_filtered['mes_ano'],
        y=ticket_filtered['ticket_medio'],
        name='Ticket Médio',
        marker_color=colors['warning'],
        text=ticket_filtered['ticket_medio'],
        texttemplate='<b>$%{text:,.0f}</b>',
        textposition='outside',
        textfont=dict(size=18, color='black', family='Arial Black'),
        marker=dict(
            line=dict(color='white', width=2),
            opacity=0.95
        ),
        width=0.6
    ))
    
    fig_ticket.update_layout(
        title=dict(
            text='🎯 TICKET MÉDIO POR MÊS',
            font=dict(size=24, family='Arial Black', color='#2c3e50'),
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            title=dict(text='MÊS', font=dict(size=16, family='Arial Black')),
            tickfont=dict(size=14, family='Arial Black'),
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=False,
            tickangle=0
        ),
        yaxis=dict(
            title=dict(text='VALOR (USD)', font=dict(size=16, family='Arial Black')),
            tickfont=dict(size=14, family='Arial Black'),
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=True,
            tickformat='$,.0f',
            rangemode='tozero'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        height=450,
        margin=dict(t=80, b=60, l=100, r=50)
    )
    
    # 4. Gráfico de churn - simplificado
    # Calcular taxa de churn percentual
    monthly_metrics['churn_rate'] = (monthly_metrics['churn_clientes'] / monthly_metrics['novos_clientes'].cumsum()) * 100
    monthly_metrics['churn_rate'] = monthly_metrics['churn_rate'].fillna(0)
    
    # Filtrar dados com churn > 0 ou taxa > 0
    churn_filtered = monthly_metrics[(monthly_metrics['churn_clientes'] > 0) | (monthly_metrics['churn_rate'] > 0)].copy()

    fig_churn = make_subplots(
        specs=[[{"secondary_y": True}]],
        subplot_titles=['']
    )
    
    # Churn de clientes (quantidade) - barras simplificadas
    if len(churn_filtered) > 0:
        fig_churn.add_trace(
            go.Bar(
                x=churn_filtered['mes_ano'],
                y=churn_filtered['churn_clientes'],
                name='Quantidade',
                marker_color=colors['danger'],
                text=churn_filtered['churn_clientes'],
                texttemplate='<b>%{text}</b>',
                textposition='outside',
                textfont=dict(size=18, color='black', family='Arial Black'),
                marker=dict(
                    line=dict(color='white', width=2),
                    opacity=0.95
                ),
                width=0.6
            ),
            secondary_y=False
        )
        
        # Churn percentual - linha simplificada
        fig_churn.add_trace(
            go.Scatter(
                x=churn_filtered['mes_ano'],
                y=churn_filtered['churn_rate'],
                mode='lines+markers+text',
                name='Percentual',
                line=dict(color='#ff6b6b', width=6),
                marker=dict(
                    size=16,
                    color='#ff6b6b',
                    line=dict(color='white', width=3),
                    symbol='diamond'
                ),
                text=churn_filtered['churn_rate'],
                texttemplate='<b>%{text:.1f}%</b>',
                textposition='top center',
                textfont=dict(size=18, color='black', family='Arial Black')
            ),
            secondary_y=True
        )
    
    fig_churn.update_xaxes(
        title_text="MÊS",
        title_font=dict(size=16, family='Arial Black'),
        tickfont=dict(size=14, family='Arial Black'),
        gridcolor='rgba(0,0,0,0.1)',
        showgrid=False,
        tickangle=0
    )
    fig_churn.update_yaxes(
        title_text="CLIENTES",
        title_font=dict(size=16, family='Arial Black', color=colors['danger']),
        tickfont=dict(size=14, family='Arial Black'),
        gridcolor='rgba(0,0,0,0.1)',
        showgrid=True,
        rangemode='tozero',
        secondary_y=False
    )
    fig_churn.update_yaxes(
        title_text="TAXA (%)",
        title_font=dict(size=16, family='Arial Black', color='#ff6b6b'),
        tickfont=dict(size=14, family='Arial Black'),
        rangemode='tozero',
        secondary_y=True
    )
    
    fig_churn.update_layout(
        title=dict(
            text='📉 CHURN MENSAL (QUANTIDADE + PERCENTUAL)',
            font=dict(size=24, family='Arial Black', color='#2c3e50'),
            x=0.5,
            y=0.95
        ),
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=80, b=60, l=100, r=100),
        legend=dict(
            x=0.02, y=0.98,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='rgba(0,0,0,0.3)',
            borderwidth=1,
            font=dict(size=14, family='Arial Black')
        )
    )
    
    return {
        'novos_clientes': fig_customers,
        'mrr': fig_mrr,
        'ticket_medio': fig_ticket,
        'churn': fig_churn
    }

# Inicializar dados
@st.cache_resource
def init_data_manager():
    return DataManager()

data_manager = init_data_manager()

# Interface principal
st.title("📊 Dashboard de Métricas de Clientes")
st.markdown("💵 **Valores exibidos em USD**")
st.markdown("---")

st.sidebar.title("Navegação")
page = st.sidebar.selectbox(
    "Selecione uma página:",
    ["Dashboard", "Inserir Dados", "Editar Cliente", "Gerenciar Dados", "Admin Database", "Exportar Relatórios"]
)

if page == "Dashboard":
    st.header("📈 Visão Geral das Métricas")
    
    customers_df = data_manager.load_customers()
    
    if customers_df.empty:
        st.warning("⚠️ Nenhum dado encontrado. Por favor, insira alguns dados na seção 'Inserir Dados'.")
    else:
        calculator = MetricsCalculator(customers_df)
        
        monthly_metrics = calculator.calculate_monthly_metrics()
        
        if not monthly_metrics.empty:
            # Cards de métricas principais - mais visuais
            st.subheader("📊 Resumo Atual")
            
            latest_month = monthly_metrics['mes_ano'].max()
            latest_data = monthly_metrics[monthly_metrics['mes_ano'] == latest_month].iloc[0]
            
            # Calcular totais gerais corretamente (valores diretos em USD)
            total_customers = len(customers_df)
            active_customers_df = customers_df[customers_df['status'] == 'Ativo']
            active_customers = len(active_customers_df)
            
            # Calcular MRR atual baseado em clientes ativos
            current_mrr = active_customers_df['plan_value'].sum() if not active_customers_df.empty else 0
            
            # Usar dados calculados ou MRR direto dos clientes ativos
            total_mrr_usd = current_mrr
            avg_ticket_usd = active_customers_df['plan_value'].mean() if not active_customers_df.empty else 0
            churn_count = latest_data['churn_clientes']
            churn_mrr_usd = latest_data['churn_mrr']
            
            # Cards grandes e visuais com valores em USD
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           padding: 25px; border-radius: 15px; text-align: center; color: white; margin-bottom: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
                    <h2 style="margin: 0; font-size: 3.5em; font-weight: 900;">{total_customers}</h2>
                    <p style="margin: 10px 0 0 0; font-size: 1.2em; font-weight: bold;">TOTAL CLIENTES</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                           padding: 25px; border-radius: 15px; text-align: center; color: white; margin-bottom: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
                    <h2 style="margin: 0; font-size: 3.5em; font-weight: 900;">{active_customers}</h2>
                    <p style="margin: 10px 0 0 0; font-size: 1.2em; font-weight: bold;">CLIENTES ATIVOS</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                           padding: 25px; border-radius: 15px; text-align: center; color: white; margin-bottom: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
                    <h2 style="margin: 0; font-size: 3.5em; font-weight: 900;">${total_mrr_usd:,.0f}</h2>
                    <p style="margin: 10px 0 0 0; font-size: 1.2em; font-weight: bold;">MRR ATUAL (USD)</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                           padding: 25px; border-radius: 15px; text-align: center; color: white; margin-bottom: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
                    <h2 style="margin: 0; font-size: 3.5em; font-weight: 900;">${avg_ticket_usd:,.0f}</h2>
                    <p style="margin: 10px 0 0 0; font-size: 1.2em; font-weight: bold;">TICKET MÉDIO (USD)</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Linha adicional com métricas de churn
            st.markdown("### 📊 Métricas de Churn do Último Mês")
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); 
                           padding: 20px; border-radius: 10px; text-align: center; color: white; margin-bottom: 10px;">
                    <h3 style="margin: 0; font-size: 2.8em; font-weight: bold;">{churn_count}</h3>
                    <p style="margin: 5px 0 0 0; font-size: 1em;">CANCELAMENTOS</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col6:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%); 
                           padding: 20px; border-radius: 10px; text-align: center; color: white; margin-bottom: 10px;">
                    <h3 style="margin: 0; font-size: 2.8em; font-weight: bold;">${churn_mrr_usd:,.0f}</h3>
                    <p style="margin: 5px 0 0 0; font-size: 1em;">MRR PERDIDO (USD)</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col7:
                churn_rate = (churn_count / max(active_customers, 1)) * 100 if active_customers > 0 else 0
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%); 
                           padding: 20px; border-radius: 10px; text-align: center; color: white; margin-bottom: 10px;">
                    <h3 style="margin: 0; font-size: 2.8em; font-weight: bold;">{churn_rate:.1f}%</h3>
                    <p style="margin: 5px 0 0 0; font-size: 1em;">TAXA DE CHURN</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col8:
                growth_rate = latest_data['novos_clientes'] - churn_count
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #00b894 0%, #00a085 100%); 
                           padding: 20px; border-radius: 10px; text-align: center; color: white; margin-bottom: 10px;">
                    <h3 style="margin: 0; font-size: 2.8em; font-weight: bold;">+{growth_rate}</h3>
                    <p style="margin: 5px 0 0 0; font-size: 1em;">CRESCIMENTO LÍQUIDO</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Gráficos simplificados
            st.subheader("📈 Evolução Mensal")
            
            visualizations = create_visualizations(monthly_metrics)
            
            # Gráficos limpos em grid 2x2
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico 1: Novos Clientes (mais limpo)
                fig_customers = go.Figure()
                
                # Filtrar dados com valor > 0 para não mostrar barras zeradas
                customers_data = monthly_metrics[monthly_metrics['novos_clientes'] > 0]
                
                if not customers_data.empty:
                    fig_customers.add_trace(go.Bar(
                        x=customers_data['mes_ano'],
                        y=customers_data['novos_clientes'],
                        marker_color='#3b82f6',
                        text=customers_data['novos_clientes'],
                        texttemplate='%{text}',
                        textposition='outside',
                        textfont=dict(size=14, color='black'),
                        width=0.6
                    ))
                
                fig_customers.update_layout(
                    title='👥 Novos Clientes',
                    xaxis_title='Mês',
                    yaxis_title='Quantidade',
                    height=350,
                    showlegend=False,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(t=50, b=40, l=40, r=40),
                    font=dict(size=12)
                )
                
                st.plotly_chart(fig_customers, use_container_width=True)
                
                # Gráfico 3: Ticket Médio (mais limpo)
                fig_ticket = go.Figure()
                
                ticket_data = monthly_metrics[monthly_metrics['ticket_medio'] > 0]
                
                if not ticket_data.empty:
                    fig_ticket.add_trace(go.Bar(
                        x=ticket_data['mes_ano'],
                        y=ticket_data['ticket_medio'],
                        marker_color='#f59e0b',
                        text=ticket_data['ticket_medio'],
                        texttemplate='$%{text:,.0f}',
                        textposition='outside',
                        textfont=dict(size=14, color='black'),
                        width=0.6
                    ))
                
                fig_ticket.update_layout(
                    title='🎯 Ticket Médio',
                    xaxis_title='Mês',
                    yaxis_title='Valor (USD)',
                    height=350,
                    showlegend=False,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(t=50, b=40, l=60, r=40),
                    font=dict(size=12),
                    yaxis=dict(tickformat='$,.0f')
                )
                
                st.plotly_chart(fig_ticket, use_container_width=True)
            
            with col2:
                # Gráfico 2: MRR (mais limpo)
                fig_mrr = go.Figure()
                
                mrr_data = monthly_metrics[monthly_metrics['mrr'] > 0]
                
                if not mrr_data.empty:
                    fig_mrr.add_trace(go.Scatter(
                        x=mrr_data['mes_ano'],
                        y=mrr_data['mrr'],
                        mode='lines+markers',
                        line=dict(color='#10b981', width=4),
                        marker=dict(size=10, color='#10b981'),
                        text=mrr_data['mrr'],
                        texttemplate='$%{text:,.0f}',
                        textposition='top center',
                        textfont=dict(size=14, color='black')
                    ))
                
                fig_mrr.update_layout(
                    title='💰 MRR Mensal',
                    xaxis_title='Mês',
                    yaxis_title='Receita (USD)',
                    height=350,
                    showlegend=False,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(t=50, b=40, l=60, r=40),
                    font=dict(size=12),
                    yaxis=dict(tickformat='$,.0f')
                )
                
                st.plotly_chart(fig_mrr, use_container_width=True)
                
                # Gráfico 4: Churn (mais limpo)
                fig_churn = go.Figure()
                
                churn_data = monthly_metrics[monthly_metrics['churn_clientes'] > 0]
                
                if not churn_data.empty:
                    # Calcular taxa de churn
                    churn_data = churn_data.copy()
                    churn_data['churn_rate'] = (churn_data['churn_clientes'] / monthly_metrics['novos_clientes'].cumsum() * 100).fillna(0)
                    
                    fig_churn.add_trace(go.Bar(
                        x=churn_data['mes_ano'],
                        y=churn_data['churn_clientes'],
                        marker_color='#ef4444',
                        text=[f"{int(qty)}<br>({rate:.1f}%)" for qty, rate in zip(churn_data['churn_clientes'], churn_data['churn_rate'])],
                        textposition='outside',
                        textfont=dict(size=12, color='black'),
                        width=0.6
                    ))
                
                fig_churn.update_layout(
                    title='📉 Churn (Quantidade + %)',
                    xaxis_title='Mês',
                    yaxis_title='Clientes Perdidos',
                    height=350,
                    showlegend=False,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(t=50, b=40, l=40, r=40),
                    font=dict(size=12)
                )
                
                st.plotly_chart(fig_churn, use_container_width=True)
            
            # Seção de LTV (Lifetime Value)
            st.subheader("💎 Análise de LTV (Lifetime Value)")
            
            # Calcular métricas de LTV
            ltv_metrics = calculator.calculate_ltv_metrics()
            
            # Exibir KPIs de LTV em colunas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="💰 LTV Médio Geral",
                    value=f"${ltv_metrics['ltv_medio']:,.0f}",
                    help="Valor médio que cada cliente gera durante sua vida útil"
                )
            
            with col2:
                st.metric(
                    label="🟢 LTV Clientes Ativos",
                    value=f"${ltv_metrics['ltv_clientes_ativos']:,.0f}",
                    help="LTV médio dos clientes que ainda estão ativos"
                )
            
            with col3:
                st.metric(
                    label="🔴 LTV Clientes Cancelados",
                    value=f"${ltv_metrics['ltv_clientes_cancelados']:,.0f}",
                    help="LTV médio dos clientes que cancelaram"
                )
            
            with col4:
                st.metric(
                    label="⏱️ Tempo Médio de Vida",
                    value=f"{ltv_metrics['tempo_vida_medio_meses']:.1f} meses",
                    help="Tempo médio que um cliente permanece ativo"
                )
            
            # Gráfico de distribuição de LTV
            if ltv_metrics['total_clientes_analisados'] > 0:
                ltv_df = ltv_metrics['ltv_detalhado']
                
                # Criar gráfico de histograma de LTV
                fig_ltv_hist = go.Figure()
                
                fig_ltv_hist.add_trace(go.Histogram(
                    x=ltv_df['ltv'],
                    nbinsx=20,
                    marker_color='#8b5cf6',
                    opacity=0.7,
                    name='Distribuição de LTV'
                ))
                
                fig_ltv_hist.update_layout(
                    title='📊 Distribuição de LTV dos Clientes',
                    xaxis_title='LTV (USD)',
                    yaxis_title='Quantidade de Clientes',
                    height=400,
                    showlegend=False,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(t=50, b=40, l=40, r=40),
                    font=dict(size=12),
                    xaxis=dict(tickformat='$,.0f')
                )
                
                st.plotly_chart(fig_ltv_hist, use_container_width=True)
                
                # Gráfico de comparação LTV vs Tempo de Vida
                fig_ltv_scatter = go.Figure()
                
                # Separar clientes ativos e cancelados
                active_customers = ltv_df[ltv_df['is_active']]
                churned_customers = ltv_df[~ltv_df['is_active']]
                
                if not active_customers.empty:
                    fig_ltv_scatter.add_trace(go.Scatter(
                        x=active_customers['months_active'],
                        y=active_customers['ltv'],
                        mode='markers',
                        marker=dict(size=10, color='#10b981'),
                        name='Clientes Ativos',
                        text=active_customers['cliente'],
                        hovertemplate='<b>%{text}</b><br>Tempo: %{x} meses<br>LTV: $%{y:,.0f}<extra></extra>'
                    ))
                
                if not churned_customers.empty:
                    fig_ltv_scatter.add_trace(go.Scatter(
                        x=churned_customers['months_active'],
                        y=churned_customers['ltv'],
                        mode='markers',
                        marker=dict(size=10, color='#ef4444'),
                        name='Clientes Cancelados',
                        text=churned_customers['cliente'],
                        hovertemplate='<b>%{text}</b><br>Tempo: %{x} meses<br>LTV: $%{y:,.0f}<extra></extra>'
                    ))
                
                fig_ltv_scatter.update_layout(
                    title='💹 LTV vs Tempo de Vida (Clientes)',
                    xaxis_title='Tempo de Vida (meses)',
                    yaxis_title='LTV (USD)',
                    height=400,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(t=50, b=40, l=60, r=40),
                    font=dict(size=12),
                    yaxis=dict(tickformat='$,.0f')
                )
                
                st.plotly_chart(fig_ltv_scatter, use_container_width=True)
            
            # Tabela detalhada com todos os dados solicitados em USD
            st.subheader("📋 Dados Mensais Detalhados")
            
            # Criar tabela com todos os dados em USD (sem conversão)
            detailed_data = monthly_metrics.copy()
            detailed_data['MRR (USD)'] = detailed_data['mrr'].apply(lambda x: f"${x:,.0f}")
            detailed_data['Ticket Médio (USD)'] = detailed_data['ticket_medio'].apply(lambda x: f"${x:,.0f}")
            detailed_data['Churn MRR (USD)'] = detailed_data['churn_mrr'].apply(lambda x: f"${x:,.0f}")
            detailed_data['Churn Rate (%)'] = (detailed_data['churn_clientes'] / detailed_data['novos_clientes'].cumsum() * 100).fillna(0).apply(lambda x: f"{x:.1f}%")
            
            # Selecionar e renomear colunas para exibição
            table_data = detailed_data[['mes_ano', 'novos_clientes', 'MRR (USD)', 'Ticket Médio (USD)', 'churn_clientes', 'Churn MRR (USD)', 'Churn Rate (%)']].copy()
            table_data.columns = ['MÊS', 'NOVOS CLIENTES', 'FATURAMENTO MRR', 'TICKET MÉDIO', 'CHURN QTD', 'CHURN MRR', 'CHURN %']
            
            # Aplicar estilo customizado à tabela
            styled_table = table_data.style.set_properties(**{
                'background-color': '#f8f9fa',
                'color': '#2c3e50',
                'font-weight': 'bold',
                'font-size': '14px',
                'text-align': 'center'
            }).set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#3498db'), ('color', 'white'), ('font-weight', 'bold'), ('font-size', '16px'), ('text-align', 'center')]},
                {'selector': 'td', 'props': [('padding', '12px')]},
                {'selector': 'tr:hover', 'props': [('background-color', '#e8f4fd')]}
            ])
            
            st.dataframe(styled_table, use_container_width=True, hide_index=True)
        else:
            st.info("📊 Aguardando dados para calcular métricas mensais.")

elif page == "Inserir Dados":
    st.header("📝 Adicionar Novo Cliente")
    
    # Status do sistema integrado (Banco + Persistência Externa)
    current_customers = data_manager.load_customers()
    total_records = len(current_customers)
    db_connected = data_manager.database_manager.is_connected()
    
    # Verificar backups locais
    backup_count = sum(1 for backup_file in data_manager.backup_files if os.path.exists(backup_file))
    
    # Verificar sistemas externos
    storage_status = data_manager.persistent_storage.get_storage_status()
    external_methods = sum(1 for status in storage_status if status['available'])
    
    # Exibir status unificado
    if db_connected:
        status_color = "#d4edda"
        border_color = "#c3e6cb" 
        text_color = "#155724"
        icon = "🔒"
        title = "Sistema de Persistência Permanente Ativo"
        subtitle = f"Banco PostgreSQL conectado + {external_methods} sistemas de backup"
    else:
        status_color = "#fff3cd"
        border_color = "#ffeaa7"
        text_color = "#856404"
        icon = "⚠️"
        title = "Sistema de Backup Ativo (Configurar Banco)"
        subtitle = f"{external_methods} sistemas de persistência + {backup_count} backups locais"
    
    st.markdown(f"""
    <div style="background: {status_color}; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid {border_color};">
        <h5 style="margin-top: 0; color: {text_color};">{icon} {title}</h5>
        <p style="margin-bottom: 5px; color: {text_color};">📊 <strong>{total_records} clientes</strong> protegidos</p>
        <p style="margin-bottom: 0; color: {text_color}; font-size: 12px;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar status dos arquivos
    with st.expander("🔍 Status dos Arquivos (Diagnóstico)", expanded=False):
        customers_df = data_manager.load_customers()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Clientes Cadastrados", len(customers_df))
        
        with col2:
            file_exists = os.path.exists(data_manager.customers_file)
            st.metric("Arquivo Principal", "✅ OK" if file_exists else "❌ Erro")
        
        with col3:
            backup_exists = os.path.exists(f"{data_manager.customers_file}.backup")
            st.metric("Backup Disponível", "✅ OK" if backup_exists else "⚠️ Nenhum")
        
        # Mostrar detalhes técnicos
        st.write(f"**Arquivo:** {data_manager.customers_file}")
        st.write(f"**Tamanho:** {os.path.getsize(data_manager.customers_file) if file_exists else 0} bytes")
        
        if len(customers_df) > 0:
            st.write("**Últimos 3 clientes:**")
            display_recent = customers_df.tail(3)[['name', 'plan_value', 'status']].copy()
            display_recent['plan_value'] = display_recent['plan_value'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(display_recent, use_container_width=True, hide_index=True)
    
    # Formulário mais visual e simples
    st.markdown("""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h4 style="margin-top: 0; color: #333;">Preencha os dados do cliente</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Usar formulário sem auto-submit para permitir interatividade
    col1, col2 = st.columns(2)
    
    with col1:
        customer_name = st.text_input(
            "Nome Completo", 
            placeholder="Ex: João Silva",
            help="Digite o nome completo do cliente",
            key="customer_name"
        )
        signup_date_str = st.text_input(
            "Data de Cadastro (DD/MM/AAAA)", 
            placeholder="Ex: 15/01/2024",
            help="Data quando o cliente se cadastrou",
            key="signup_date_str"
        )
    
    with col2:
        plan_value_str = st.text_input(
            "Valor do Plano Mensal (USD)", 
            placeholder="Ex: 4.000,00 ou 4000.00",
            help="Valor que o cliente paga por mês (aceita vírgula ou ponto)",
            key="plan_value_str"
        )
        status = st.selectbox(
            "Status do Cliente", 
            ["Ativo", "Cancelado"],
            help="Situação atual do cliente",
            key="status"
        )
    
    # Mostrar data de cancelamento automaticamente quando status for "Cancelado"
    cancel_date_str = None
    if status == "Cancelado":
        cancel_date_str = st.text_input(
            "Data de Cancelamento (DD/MM/AAAA)", 
            placeholder="Ex: 23/06/2025",
            help="Data quando o cliente cancelou",
            key="cancel_date_str"
        )
    
    # Botão de submissão
    if st.button(
        "➕ Adicionar Cliente",
        use_container_width=True,
        type="primary"
    ):
        # Validações e conversões detalhadas no frontend
        errors = []
        parsed_signup_date = None
        parsed_cancel_date = None
        parsed_plan_value = None
        
        # Validar nome
        if not customer_name or not customer_name.strip():
            errors.append("❌ Nome do cliente é obrigatório")
        
        # Validar e converter valor do plano
        if not plan_value_str or not plan_value_str.strip():
            errors.append("❌ Valor do plano é obrigatório")
        else:
            try:
                # Lógica melhorada para aceitar formatos brasileiros e americanos
                value_str = plan_value_str.strip()
                
                # Se contém vírgula, assumir formato brasileiro (1.000,00)
                if "," in value_str:
                    # Remover pontos (milhares) e converter vírgula para ponto decimal
                    value_clean = value_str.replace(".", "").replace(",", ".")
                else:
                    # Formato americano ou simples (1000.00 ou 1000)
                    value_clean = value_str
                
                parsed_plan_value = float(value_clean)
                if parsed_plan_value <= 0:
                    errors.append("❌ Valor do plano deve ser maior que zero")
            except ValueError:
                errors.append("❌ Valor do plano inválido (use formato: 4.000,00 ou 4000.00)")
        
        # Validar e converter data de cadastro
        if not signup_date_str or not signup_date_str.strip():
            errors.append("❌ Data de cadastro é obrigatória")
        else:
            try:
                # Aceitar formato DD/MM/AAAA
                day, month, year = signup_date_str.split("/")
                parsed_signup_date = date(int(year), int(month), int(day))
            except ValueError:
                errors.append("❌ Data de cadastro inválida (use formato: DD/MM/AAAA)")
        
        # Validar data de cancelamento se necessário
        if status == "Cancelado":
            if not cancel_date_str or not cancel_date_str.strip():
                errors.append("❌ Data de cancelamento é obrigatória para clientes cancelados")
            else:
                try:
                    day, month, year = cancel_date_str.split("/")
                    parsed_cancel_date = date(int(year), int(month), int(day))
                    if parsed_signup_date and parsed_cancel_date < parsed_signup_date:
                        errors.append("❌ Data de cancelamento não pode ser anterior à data de cadastro")
                except ValueError:
                    errors.append("❌ Data de cancelamento inválida (use formato: DD/MM/AAAA)")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            # Mostrar dados que serão salvos para confirmação
            with st.expander("📋 Dados que serão salvos:", expanded=True):
                st.write(f"**Nome:** {customer_name}")
                st.write(f"**Data de Cadastro:** {parsed_signup_date.strftime('%d/%m/%Y') if parsed_signup_date else 'Data inválida'}")
                st.write(f"**Valor Mensal:** ${parsed_plan_value:,.2f} USD")
                st.write(f"**Status:** {status}")
                if parsed_cancel_date:
                    st.write(f"**Data de Cancelamento:** {parsed_cancel_date.strftime('%d/%m/%Y')}")
                
                # Processo de salvamento com feedback em tempo real
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Dados antes do salvamento
                customers_before = data_manager.load_customers()
                count_before = len(customers_before)
                
                status_text.text("🔄 Preparando salvamento...")
                progress_bar.progress(10)
                
                # Tentar salvar com monitoramento
                status_text.text("💾 Salvando cliente...")
                progress_bar.progress(30)
                
                success = data_manager.add_customer(
                    customer_name, parsed_signup_date, parsed_plan_value, status, parsed_cancel_date
                )
                
                progress_bar.progress(60)
                status_text.text("🔍 Verificando integridade dos dados...")
                
                # Verificação detalhada pós-salvamento
                customers_after = data_manager.load_customers()
                count_after = len(customers_after)
                
                progress_bar.progress(80)
                
                # Log detalhado do processo
                log_container = st.container()
                
                if success and count_after > count_before:
                    # Sucesso confirmado
                    progress_bar.progress(100)
                    status_text.text("✅ Cliente salvo com sucesso!")
                    
                    # Verificar se é realmente o cliente correto
                    latest_customer = customers_after.iloc[-1]
                    if (latest_customer['name'] == customer_name and 
                        abs(latest_customer['plan_value'] - parsed_plan_value) < 0.01):
                        
                        with log_container:
                            st.success("🎉 Cliente adicionado com sucesso!")
                            
                            # Mostrar dados salvos
                            st.info(f"""
                            **Dados Confirmados:**
                            - Nome: {latest_customer['name']}
                            - Valor: ${latest_customer['plan_value']:,.2f} USD
                            - Status: {latest_customer['status']}
                            - Total de clientes: {count_after}
                            """)
                        
                        st.balloons()
                        st.rerun()
                    else:
                        with log_container:
                            st.error("⚠️ Dados salvos não conferem. Verificando...")
                            st.write(f"Esperado: {customer_name}, ${parsed_plan_value}")
                            st.write(f"Salvo: {latest_customer['name']}, ${latest_customer['plan_value']}")
                else:
                    # Falha no salvamento
                    progress_bar.progress(100)
                    status_text.text("❌ Falha no salvamento")
                    
                    with log_container:
                        st.error("❌ Erro ao salvar cliente")
                        
                        # Log detalhado para debugging
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Diagnóstico:**")
                            st.write(f"- Retorno da função: {success}")
                            st.write(f"- Clientes antes: {count_before}")
                            st.write(f"- Clientes depois: {count_after}")
                            st.write(f"- Arquivo existe: {os.path.exists(data_manager.customers_file)}")
                        
                        with col2:
                            st.write("**Arquivos de Backup:**")
                            backups = [
                                f"{data_manager.customers_file}.backup",
                                f"{data_manager.customers_file}.backup2", 
                                f"{data_manager.customers_file}.backup3"
                            ]
                            for backup in backups:
                                exists = os.path.exists(backup)
                                st.write(f"- {backup.split('.')[-1]}: {'✅' if exists else '❌'}")
                        
                        # Opção para ver dados raw
                        if st.checkbox("🔍 Ver dados raw do arquivo"):
                            try:
                                with open(data_manager.customers_file, 'r') as f:
                                    content = f.read()
                                st.text_area("Conteúdo do arquivo:", content, height=200)
                            except Exception as e:
                                st.error(f"Erro ao ler arquivo: {str(e)}")
                
                # Limpar progress bar após um tempo
                import time
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()

elif page == "Editar Cliente":
    st.header("✏️ Editar Cliente Existente")
    
    # Carregar dados atuais
    customers_df = data_manager.load_customers()
    
    if customers_df.empty:
        st.warning("⚠️ Nenhum cliente encontrado. Adicione clientes primeiro na seção 'Inserir Dados'.")
    else:
        # Seleção do cliente para editar
        st.subheader("📋 Selecione o cliente para editar")
        
        # Mostrar tabela de clientes para seleção
        display_df = customers_df.copy()
        display_df['plan_value'] = display_df['plan_value'].apply(lambda x: f"${x:,.2f}")
        display_df['signup_date'] = pd.to_datetime(display_df['signup_date']).dt.strftime('%d/%m/%Y')
        display_df['cancel_date'] = pd.to_datetime(display_df['cancel_date'], errors='coerce').dt.strftime('%d/%m/%Y')
        display_df['cancel_date'] = display_df['cancel_date'].fillna('--')
        
        # Renomear colunas para exibição
        display_df = display_df.rename(columns={
            'name': 'Nome',
            'signup_date': 'Data Cadastro',
            'plan_value': 'Valor Mensal',
            'status': 'Status',
            'cancel_date': 'Data Cancelamento'
        })
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Seleção por índice
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_index = st.selectbox(
                "Selecione o cliente pelo índice (número da linha)",
                options=list(range(len(customers_df))),
                format_func=lambda x: f"{x} - {customers_df.iloc[x]['name']} (${customers_df.iloc[x]['plan_value']:,.2f})"
            )
        
        with col2:
            if st.button("🔄 Atualizar Lista", use_container_width=True):
                st.rerun()
        
        # Formulário de edição
        if selected_index is not None:
            st.subheader("✏️ Editar dados do cliente")
            
            # Carregar dados do cliente selecionado
            selected_customer = customers_df.iloc[selected_index]
            
            # Mostrar dados atuais
            st.info(f"**Cliente selecionado:** {selected_customer['name']} - Índice {selected_index}")
            
            # Formulário de edição
            col1, col2 = st.columns(2)
            
            with col1:
                edit_name = st.text_input(
                    "Nome Completo",
                    value=selected_customer['name'],
                    placeholder="Ex: João Silva",
                    help="Digite o nome completo do cliente",
                    key="edit_name"
                )
                
                # Converter data para string no formato brasileiro
                current_signup = pd.to_datetime(selected_customer['signup_date']).strftime('%d/%m/%Y')
                edit_signup_date_str = st.text_input(
                    "Data de Cadastro (DD/MM/AAAA)",
                    value=current_signup,
                    placeholder="Ex: 15/01/2024",
                    help="Data quando o cliente se cadastrou",
                    key="edit_signup_date"
                )
            
            with col2:
                edit_plan_value_str = st.text_input(
                    "Valor do Plano Mensal (USD)",
                    value=f"{selected_customer['plan_value']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                    placeholder="Ex: 4.000,00 ou 4000.00",
                    help="Valor que o cliente paga por mês",
                    key="edit_plan_value"
                )
                
                edit_status = st.selectbox(
                    "Status do Cliente",
                    ["Ativo", "Cancelado"],
                    index=0 if selected_customer['status'].lower() == 'ativo' else 1,
                    help="Situação atual do cliente",
                    key="edit_status"
                )
            
            # Data de cancelamento (se necessário)
            edit_cancel_date_str = None
            if edit_status == "Cancelado":
                current_cancel = ""
                if pd.notna(selected_customer['cancel_date']):
                    current_cancel = pd.to_datetime(selected_customer['cancel_date']).strftime('%d/%m/%Y')
                
                edit_cancel_date_str = st.text_input(
                    "Data de Cancelamento (DD/MM/AAAA)",
                    value=current_cancel,
                    placeholder="Ex: 23/06/2025",
                    help="Data quando o cliente cancelou",
                    key="edit_cancel_date"
                )
            
            # Comparação de dados
            st.subheader("🔄 Comparação de Alterações")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Dados Atuais:**")
                st.write(f"- Nome: {selected_customer['name']}")
                st.write(f"- Data Cadastro: {current_signup}")
                st.write(f"- Valor: ${selected_customer['plan_value']:,.2f}")
                st.write(f"- Status: {selected_customer['status']}")
                if pd.notna(selected_customer['cancel_date']):
                    cancel_display = pd.to_datetime(selected_customer['cancel_date']).strftime('%d/%m/%Y')
                    st.write(f"- Data Cancelamento: {cancel_display}")
            
            with col2:
                st.write("**Novos Dados:**")
                st.write(f"- Nome: {edit_name}")
                st.write(f"- Data Cadastro: {edit_signup_date_str}")
                st.write(f"- Valor: {edit_plan_value_str}")
                st.write(f"- Status: {edit_status}")
                if edit_cancel_date_str:
                    st.write(f"- Data Cancelamento: {edit_cancel_date_str}")
            
            # Botão de atualização
            if st.button("💾 Salvar Alterações", use_container_width=True, type="primary"):
                # Validações
                errors = []
                parsed_signup_date = None
                parsed_cancel_date = None
                parsed_plan_value = None
                
                # Validar nome
                if not edit_name or not edit_name.strip():
                    errors.append("❌ Nome do cliente é obrigatório")
                
                # Validar valor
                if not edit_plan_value_str or not edit_plan_value_str.strip():
                    errors.append("❌ Valor do plano é obrigatório")
                else:
                    try:
                        value_str = edit_plan_value_str.strip()
                        if "," in value_str:
                            value_clean = value_str.replace(".", "").replace(",", ".")
                        else:
                            value_clean = value_str
                        parsed_plan_value = float(value_clean)
                        if parsed_plan_value <= 0:
                            errors.append("❌ Valor do plano deve ser maior que zero")
                    except ValueError:
                        errors.append("❌ Valor do plano inválido")
                
                # Validar data de cadastro
                if not edit_signup_date_str or not edit_signup_date_str.strip():
                    errors.append("❌ Data de cadastro é obrigatória")
                else:
                    try:
                        day, month, year = edit_signup_date_str.split("/")
                        parsed_signup_date = date(int(year), int(month), int(day))
                    except ValueError:
                        errors.append("❌ Data de cadastro inválida (use formato: DD/MM/AAAA)")
                
                # Validar data de cancelamento
                if edit_status == "Cancelado":
                    if not edit_cancel_date_str or not edit_cancel_date_str.strip():
                        errors.append("❌ Data de cancelamento é obrigatória para clientes cancelados")
                    else:
                        try:
                            day, month, year = edit_cancel_date_str.split("/")
                            parsed_cancel_date = date(int(year), int(month), int(day))
                            if parsed_signup_date and parsed_cancel_date < parsed_signup_date:
                                errors.append("❌ Data de cancelamento não pode ser anterior à data de cadastro")
                        except ValueError:
                            errors.append("❌ Data de cancelamento inválida")
                
                # Mostrar erros ou processar atualização
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Processar atualização
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("🔄 Atualizando cliente...")
                    progress_bar.progress(30)
                    
                    success = data_manager.update_customer(
                        selected_index,
                        edit_name,
                        parsed_signup_date,
                        parsed_plan_value,
                        edit_status,
                        parsed_cancel_date
                    )
                    
                    progress_bar.progress(80)
                    
                    if success:
                        progress_bar.progress(100)
                        status_text.text("✅ Cliente atualizado com sucesso!")
                        
                        st.success("🎉 Cliente atualizado com sucesso!")
                        st.balloons()
                        
                        # Limpar e recarregar
                        import time
                        time.sleep(1)
                        progress_bar.empty()
                        status_text.empty()
                        st.rerun()
                    else:
                        progress_bar.progress(100)
                        status_text.text("❌ Falha na atualização")
                        st.error("❌ Erro ao atualizar cliente. Tente novamente.")
                        
                        # Limpar progress bar
                        import time
                        time.sleep(2)
                        progress_bar.empty()
                        status_text.empty()

elif page == "Gerenciar Dados":
    st.header("🗂️ Gerenciar Dados Existentes")
    
    st.subheader("👥 Clientes Cadastrados")
    customers_df = data_manager.load_customers()
    
    if not customers_df.empty:
        display_df = customers_df.copy()
        
        # Formatar datas de forma simples e direta
        if 'signup_date' in display_df.columns:
            display_df['signup_date'] = display_df['signup_date'].fillna('Data inválida')
        
        if 'cancel_date' in display_df.columns:
            display_df['cancel_date'] = display_df['cancel_date'].fillna('N/A')
        
        # Formatar valores monetários
        if 'plan_value' in display_df.columns:
            display_df['plan_value'] = display_df['plan_value'].apply(lambda x: f"${x:,.0f}")
        
        display_df.index = display_df.index + 1
        st.dataframe(display_df, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🗑️ Remover Cliente")
            if len(customers_df) > 0:
                customer_to_remove = st.selectbox(
                    "Selecione o cliente para remover:",
                    options=range(len(customers_df)),
                    format_func=lambda x: f"{x+1}. {customers_df.iloc[x]['name']} - R$ {customers_df.iloc[x]['plan_value']:.2f}"
                )
                
                if st.button("Remover Cliente"):
                    if data_manager.remove_customer(customer_to_remove):
                        st.success("✅ Cliente removido com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao remover cliente.")
    else:
        st.info("📊 Nenhum cliente cadastrado.")

elif page == "Admin Database":
    st.header("🔧 Administração do Banco de Dados")
    
    # Verificar conexão do banco
    if not data_manager.database_manager.is_connected():
        st.error("❌ Banco de dados não conectado. Configurar DATABASE_URL primeiro.")
        st.stop()
    
    # Obter estatísticas do banco
    stats = data_manager.database_manager.get_database_stats()
    
    if stats:
        st.subheader("📊 Estatísticas Atuais do Banco")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Registros", stats['total'])
        
        with col2:
            st.metric("Clientes Ativos", stats['active'])
        
        with col3:
            if stats['duplicates'] > 0:
                st.metric("⚠️ Possíveis Duplicatas", stats['duplicates'])
            else:
                st.metric("✅ Duplicatas", "0")
        
        # Alerta sobre duplicatas
        if stats['duplicates'] > 0:
            st.error(f"⚠️ **PROBLEMA DETECTADO**: {stats['duplicates']} grupos de dados duplicados encontrados no banco!")
        
        st.markdown("---")
        
        # Operações de limpeza
        st.subheader("🧹 Operações de Limpeza")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Limpar Duplicatas**")
            st.write("Remove registros duplicados mantendo apenas o primeiro de cada cliente.")
            
            if st.button("🗑️ Limpar Duplicatas", type="primary"):
                with st.spinner("Limpando duplicatas..."):
                    success = data_manager.database_manager.clean_duplicate_data()
                    
                    if success:
                        st.success("✅ Duplicatas removidas com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao remover duplicatas")
        
        with col2:
            st.write("**Reset Completo**")
            st.write("⚠️ **CUIDADO**: Remove TODOS os dados do banco!")
            
            if st.button("🔥 RESETAR BANCO", type="secondary"):
                st.warning("⚠️ Esta operação irá apagar TODOS os dados!")
                
                if st.button("✅ Confirmar Reset", type="primary"):
                    with st.spinner("Resetando banco..."):
                        success = data_manager.database_manager.reset_database()
                        
                        if success:
                            st.success("✅ Banco resetado com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao resetar banco")
        
        st.markdown("---")
        
        # Sincronização
        st.subheader("🔄 Sincronização de Dados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Dados Locais → Banco**")
            customers_df = data_manager.load_customers()
            st.write(f"Clientes no CSV local: {len(customers_df)}")
            
            if st.button("📤 Sincronizar Local → Banco"):
                with st.spinner("Sincronizando dados..."):
                    success = data_manager.database_manager.save_customers(customers_df)
                    
                    if success:
                        st.success("✅ Dados sincronizados com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro na sincronização")
        
        with col2:
            st.write("**Restaurar Dados Limpos**")
            st.write("Carrega dados básicos (30 clientes) para teste")
            
            if st.button("🔄 Restaurar Dados Limpos"):
                with st.spinner("Restaurando dados limpos..."):
                    # Carregar dados limpos
                    try:
                        clean_df = pd.read_csv('clean_customers.csv')
                        
                        # Salvar no banco
                        success = data_manager.database_manager.save_customers(clean_df)
                        
                        if success:
                            # Também salvar localmente
                            clean_df.to_csv(data_manager.customers_file, index=False)
                            st.success("✅ Dados limpos restaurados com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao restaurar dados limpos")
                    except Exception as e:
                        st.error(f"❌ Erro ao restaurar: {str(e)}")
        
        st.markdown("---")
        
        # Logs e informações técnicas
        st.subheader("🔍 Informações Técnicas")
        
        with st.expander("Ver Logs de Conexão"):
            status = data_manager.database_manager.get_connection_status()
            st.text(status)
        
        with st.expander("Testar Conexão"):
            if st.button("🔄 Testar Agora"):
                result = data_manager.database_manager.test_connection()
                st.json(result)
    
    else:
        st.error("❌ Não foi possível obter estatísticas do banco")

elif page == "Exportar Relatórios":
    st.header("📊 Exportar Relatórios")
    
    customers_df = data_manager.load_customers()
    
    if not customers_df.empty:
        calculator = MetricsCalculator(customers_df)
        monthly_metrics = calculator.calculate_monthly_metrics()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📁 Dados de Clientes")
            csv_customers = customers_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Baixar Dados de Clientes (CSV)",
                data=csv_customers,
                file_name=f"clientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            st.subheader("📈 Métricas Calculadas")
            if not monthly_metrics.empty:
                csv_metrics = monthly_metrics.to_csv(index=False)
                st.download_button(
                    label="⬇️ Baixar Métricas Mensais (CSV)",
                    data=csv_metrics,
                    file_name=f"metricas_mensais_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        st.markdown("---")
        st.subheader("🔗 Compartilhamento")
        st.info("💡 **Dica**: Para compartilhar este dashboard com colegas, basta compartilhar a URL desta aplicação. Todos os dados inseridos estarão disponIveis em tempo real.")
        
    else:
        st.warning("⚠️ Nenhum dado disponível para exportação.")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Dashboard de Métricas de Clientes | Atualizado em tempo real"
    "</div>",
    unsafe_allow_html=True
)

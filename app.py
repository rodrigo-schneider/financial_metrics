import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import os
import calendar

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Métricas de Clientes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gerenciador de dados simplificado
class DataManager:
    def __init__(self):
        self.customers_file = "customers_simple.csv"
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        if not os.path.exists(self.customers_file):
            customers_df = pd.DataFrame(columns=[
                'name', 'signup_date', 'plan_value', 'status', 'cancel_date'
            ])
            customers_df.to_csv(self.customers_file, index=False)
    
    def load_customers(self):
        try:
            df = pd.read_csv(self.customers_file)
            if not df.empty:
                df['signup_date'] = pd.to_datetime(df['signup_date'])
                df['cancel_date'] = pd.to_datetime(df['cancel_date'], errors='coerce')
            return df
        except:
            return pd.DataFrame(columns=['name', 'signup_date', 'plan_value', 'status', 'cancel_date'])
    
    def add_customer(self, name, signup_date, plan_value, status, cancel_date=None):
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
        except:
            return False
    
    def remove_customer(self, index):
        try:
            df = self.load_customers()
            df = df.drop(index)
            df.to_csv(self.customers_file, index=False)
            return True
        except:
            return False

# Calculadora de métricas simplificada
class MetricsCalculator:
    def __init__(self, customers_df):
        self.customers_df = customers_df
    
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
                'novos_clientes': new_customers,
                'mrr': mrr,
                'ticket_medio': avg_ticket,
                'churn_clientes': churn_customers,
                'churn_mrr': churn_mrr
            })
        
        return pd.DataFrame(metrics_list)
    
    def _get_analysis_period(self):
        dates = list(self.customers_df['signup_date'].dropna())
        cancel_dates = self.customers_df['cancel_date'].dropna()
        if not cancel_dates.empty:
            dates.extend(cancel_dates)
        
        if not dates:
            now = datetime.now()
            return now.replace(day=1), now
        
        min_date = min(dates).replace(day=1)
        end_date = datetime.now().replace(day=1)
        return min_date, end_date
    
    def _generate_month_list(self, start_date, end_date):
        months = []
        current = start_date
        while current <= end_date:
            months.append(current)
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        return months
    
    def _calculate_new_customers(self, month_date):
        month_start = month_date
        month_end = self._get_month_end(month_date)
        new_customers = self.customers_df[
            (self.customers_df['signup_date'] >= month_start) &
            (self.customers_df['signup_date'] <= month_end)
        ]
        return len(new_customers)
    
    def _calculate_mrr(self, month_date):
        month_end = self._get_month_end(month_date)
        active_customers = self.customers_df[
            (self.customers_df['signup_date'] <= month_end) &
            ((self.customers_df['cancel_date'].isna()) | 
             (self.customers_df['cancel_date'] > month_end))
        ]
        return active_customers['plan_value'].sum()
    
    def _calculate_avg_ticket(self, month_date):
        month_end = self._get_month_end(month_date)
        active_customers = self.customers_df[
            (self.customers_df['signup_date'] <= month_end) &
            ((self.customers_df['cancel_date'].isna()) | 
             (self.customers_df['cancel_date'] > month_end))
        ]
        return active_customers['plan_value'].mean() if not active_customers.empty else 0.0
    
    def _calculate_churn(self, month_date):
        month_start = month_date
        month_end = self._get_month_end(month_date)
        churned_customers = self.customers_df[
            (self.customers_df['cancel_date'] >= month_start) &
            (self.customers_df['cancel_date'] <= month_end)
        ]
        return len(churned_customers), churned_customers['plan_value'].sum()
    
    def _get_month_end(self, month_date):
        last_day = calendar.monthrange(month_date.year, month_date.month)[1]
        return month_date.replace(day=last_day, hour=23, minute=59, second=59)

# Funções de visualização simplificadas e mais visuais
def create_visualizations(monthly_metrics):
    if monthly_metrics.empty:
        return {}
    
    colors = {'primary': '#3b82f6', 'success': '#10b981', 'warning': '#f59e0b', 'danger': '#ef4444'}
    
    # Gráfico de novos clientes - mais simples e visual
    fig_customers = px.bar(
        monthly_metrics, x='mes_ano', y='novos_clientes',
        title='👥 Novos Clientes',
        color_discrete_sequence=[colors['primary']],
        text='novos_clientes'
    )
    fig_customers.update_traces(texttemplate='%{text}', textposition='outside')
    fig_customers.update_layout(
        showlegend=False, 
        height=350,
        xaxis_title="",
        yaxis_title="Clientes",
        title_font_size=18,
        title_x=0.5,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Gráfico de MRR - linha mais grossa e visual
    fig_mrr = px.line(
        monthly_metrics, x='mes_ano', y='mrr',
        title='💰 Receita Mensal (MRR)',
        markers=True, 
        color_discrete_sequence=[colors['success']],
        text='mrr'
    )
    fig_mrr.update_traces(
        line=dict(width=4),
        marker=dict(size=10),
        texttemplate='R$ %{text:,.0f}',
        textposition='top center'
    )
    fig_mrr.update_layout(
        showlegend=False, 
        height=350,
        xaxis_title="",
        yaxis_title="Receita (R$)",
        title_font_size=18,
        title_x=0.5,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Gráfico de ticket médio - área mais suave
    fig_ticket = px.bar(
        monthly_metrics, x='mes_ano', y='ticket_medio',
        title='🎯 Valor Médio por Cliente',
        color_discrete_sequence=[colors['warning']],
        text='ticket_medio'
    )
    fig_ticket.update_traces(
        texttemplate='R$ %{text:,.0f}',
        textposition='outside'
    )
    fig_ticket.update_layout(
        showlegend=False, 
        height=350,
        xaxis_title="",
        yaxis_title="Valor (R$)",
        title_font_size=18,
        title_x=0.5,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Gráfico de churn - simples com barras
    fig_churn = px.bar(
        monthly_metrics, x='mes_ano', y='churn_clientes',
        title='📉 Clientes que Cancelaram',
        color_discrete_sequence=[colors['danger']],
        text='churn_clientes'
    )
    fig_churn.update_traces(texttemplate='%{text}', textposition='outside')
    fig_churn.update_layout(
        showlegend=False, 
        height=350,
        xaxis_title="",
        yaxis_title="Cancelamentos",
        title_font_size=18,
        title_x=0.5,
        plot_bgcolor='white',
        paper_bgcolor='white'
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
st.markdown("---")

st.sidebar.title("Navegação")
page = st.sidebar.selectbox(
    "Selecione uma página:",
    ["Dashboard", "Inserir Dados", "Gerenciar Dados", "Exportar Relatórios"]
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
            
            # Calcular totais gerais
            total_customers = len(customers_df)
            active_customers = len(customers_df[customers_df['status'] == 'Ativo'])
            total_mrr = latest_data['mrr']
            avg_ticket = latest_data['ticket_medio']
            
            # Cards grandes e visuais
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           padding: 20px; border-radius: 10px; text-align: center; color: white; margin-bottom: 10px;">
                    <h3 style="margin: 0; font-size: 2.5em; font-weight: bold;">{total_customers}</h3>
                    <p style="margin: 5px 0 0 0; font-size: 1.1em;">Total de Clientes</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                           padding: 20px; border-radius: 10px; text-align: center; color: white; margin-bottom: 10px;">
                    <h3 style="margin: 0; font-size: 2.5em; font-weight: bold;">{active_customers}</h3>
                    <p style="margin: 5px 0 0 0; font-size: 1.1em;">Clientes Ativos</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                           padding: 20px; border-radius: 10px; text-align: center; color: white; margin-bottom: 10px;">
                    <h3 style="margin: 0; font-size: 2.5em; font-weight: bold;">R$ {total_mrr:,.0f}</h3>
                    <p style="margin: 5px 0 0 0; font-size: 1.1em;">Receita Mensal</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                           padding: 20px; border-radius: 10px; text-align: center; color: white; margin-bottom: 10px;">
                    <h3 style="margin: 0; font-size: 2.5em; font-weight: bold;">R$ {avg_ticket:,.0f}</h3>
                    <p style="margin: 5px 0 0 0; font-size: 1.1em;">Ticket Médio</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Gráficos simplificados
            st.subheader("📈 Evolução Mensal")
            
            visualizations = create_visualizations(monthly_metrics)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(visualizations['novos_clientes'], use_container_width=True)
                st.plotly_chart(visualizations['ticket_medio'], use_container_width=True)
            
            with col2:
                st.plotly_chart(visualizations['mrr'], use_container_width=True)
                st.plotly_chart(visualizations['churn'], use_container_width=True)
            
            # Tabela simplificada e mais visual
            st.subheader("📋 Resumo por Mês")
            
            # Formatar tabela de forma mais simples
            display_data = monthly_metrics[['mes_ano', 'novos_clientes', 'mrr', 'ticket_medio', 'churn_clientes']].copy()
            display_data.columns = ['Mês', 'Novos Clientes', 'Receita (R$)', 'Ticket Médio (R$)', 'Cancelamentos']
            
            # Formatar valores monetários
            for i in range(len(display_data)):
                display_data.iloc[i, 2] = f"R$ {display_data.iloc[i, 2]:,.0f}"  # Receita
                display_data.iloc[i, 3] = f"R$ {display_data.iloc[i, 3]:,.0f}"  # Ticket Médio
            
            st.dataframe(display_data, use_container_width=True, hide_index=True)
        else:
            st.info("📊 Aguardando dados para calcular métricas mensais.")

elif page == "Inserir Dados":
    st.header("📝 Adicionar Novo Cliente")
    
    # Formulário mais visual e simples
    st.markdown("""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h4 style="margin-top: 0; color: #333;">Preencha os dados do cliente</h4>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("customer_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            customer_name = st.text_input(
                "Nome Completo", 
                placeholder="Ex: João Silva",
                help="Digite o nome completo do cliente"
            )
            signup_date = st.date_input(
                "Data de Cadastro", 
                value=date.today(),
                help="Quando o cliente se cadastrou"
            )
        
        with col2:
            plan_value = st.number_input(
                "Valor do Plano Mensal (R$)", 
                min_value=0.0, 
                step=1.0,
                help="Quanto o cliente paga por mês"
            )
            status = st.selectbox(
                "Status do Cliente", 
                ["Ativo", "Cancelado"],
                help="Situação atual do cliente"
            )
        
        # Só mostrar data de cancelamento se status for "Cancelado"
        cancel_date = None
        if status == "Cancelado":
            cancel_date = st.date_input(
                "Data de Cancelamento", 
                value=date.today(),
                help="Quando o cliente cancelou"
            )
        
        # Botão mais visual
        submitted = st.form_submit_button(
            "➕ Adicionar Cliente",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if customer_name and plan_value > 0:
                success = data_manager.add_customer(
                    customer_name, signup_date, plan_value, status, cancel_date
                )
                if success:
                    st.success("Cliente adicionado com sucesso!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Erro ao adicionar cliente!")
            else:
                st.error("Preencha o nome e o valor do plano!")

elif page == "Gerenciar Dados":
    st.header("🗂️ Gerenciar Dados Existentes")
    
    st.subheader("👥 Clientes Cadastrados")
    customers_df = data_manager.load_customers()
    
    if not customers_df.empty:
        display_df = customers_df.copy()
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

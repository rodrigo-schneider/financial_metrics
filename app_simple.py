import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import os
from simple_data_manager import SimpleDataManager
from simple_metrics_calculator import SimpleMetricsCalculator
from visualizations import create_visualizations

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Métricas de Clientes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar gerenciador de dados simplificado
@st.cache_resource
def init_data_manager():
    return SimpleDataManager()

data_manager = init_data_manager()

# Título principal
st.title("📊 Dashboard de Métricas de Clientes")
st.markdown("---")

# Sidebar para navegação
st.sidebar.title("Navegação")
page = st.sidebar.selectbox(
    "Selecione uma página:",
    ["Dashboard", "Inserir Dados", "Gerenciar Dados", "Exportar Relatórios"]
)

if page == "Dashboard":
    st.header("📈 Visão Geral das Métricas")
    
    # Carregar dados
    customers_df = data_manager.load_customers()
    
    if customers_df.empty:
        st.warning("⚠️ Nenhum dado encontrado. Por favor, insira alguns dados na seção 'Inserir Dados'.")
    else:
        # Calcular métricas
        calculator = SimpleMetricsCalculator(customers_df)
        
        # Métricas mensais
        monthly_metrics = calculator.calculate_monthly_metrics()
        
        if not monthly_metrics.empty:
            # Criar visualizações
            visualizations = create_visualizations(monthly_metrics)
            
            # Layout em colunas para KPIs principais
            col1, col2, col3, col4 = st.columns(4)
            
            latest_month = monthly_metrics['mes_ano'].max()
            latest_data = monthly_metrics[monthly_metrics['mes_ano'] == latest_month].iloc[0]
            
            with col1:
                st.metric(
                    label="Novos Clientes (Último Mês)",
                    value=int(latest_data['novos_clientes']),
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="MRR (Último Mês)",
                    value=f"R$ {latest_data['mrr']:,.2f}",
                    delta=None
                )
            
            with col3:
                st.metric(
                    label="Ticket Médio (Último Mês)",
                    value=f"R$ {latest_data['ticket_medio']:,.2f}",
                    delta=None
                )
            
            with col4:
                total_active = len(customers_df[customers_df['status'] == 'Ativo'])
                churn_rate = (latest_data['churn_clientes'] / max(total_active, 1)) * 100 if total_active > 0 else 0
                st.metric(
                    label="Taxa de Churn (%)",
                    value=f"{churn_rate:.1f}%",
                    delta=None
                )
            
            st.markdown("---")
            
            # Gráficos principais
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(visualizations['novos_clientes'], use_container_width=True)
                st.plotly_chart(visualizations['ticket_medio'], use_container_width=True)
            
            with col2:
                st.plotly_chart(visualizations['mrr'], use_container_width=True)
                st.plotly_chart(visualizations['churn'], use_container_width=True)
            
            # Tabela de dados
            st.subheader("📋 Dados Detalhados")
            
            # Formatar dados para exibição
            display_data = monthly_metrics.copy()
            display_data['MRR'] = display_data['mrr'].apply(lambda x: f"R$ {x:,.2f}")
            display_data['Ticket Médio'] = display_data['ticket_medio'].apply(lambda x: f"R$ {x:,.2f}")
            display_data['Churn MRR'] = display_data['churn_mrr'].apply(lambda x: f"R$ {x:,.2f}")
            
            display_columns = {
                'mes_ano': 'Mês/Ano',
                'novos_clientes': 'Novos Clientes',
                'MRR': 'MRR',
                'Ticket Médio': 'Ticket Médio',
                'churn_clientes': 'Churn Clientes',
                'Churn MRR': 'Churn MRR'
            }
            
            st.dataframe(
                display_data[list(display_columns.keys())].rename(columns=display_columns),
                use_container_width=True
            )
        else:
            st.info("📊 Aguardando dados para calcular métricas mensais.")

elif page == "Inserir Dados":
    st.header("📝 Inserir Novos Dados")
    
    st.subheader("👥 Adicionar Cliente")
    
    with st.form("customer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            customer_name = st.text_input("Nome do Cliente", placeholder="Ex: João Silva")
            signup_date = st.date_input("Data de Cadastro", value=date.today())
            plan_value = st.number_input("Valor do Plano Mensal (R$)", min_value=0.0, step=0.01)
        
        with col2:
            status = st.selectbox("Status", ["Ativo", "Cancelado"])
            cancel_date = None
            if status == "Cancelado":
                cancel_date = st.date_input("Data de Cancelamento", value=date.today())
        
        submitted = st.form_submit_button("Adicionar Cliente")
        
        if submitted:
            if customer_name and plan_value > 0:
                success = data_manager.add_customer(
                    customer_name, signup_date, plan_value, status, cancel_date
                )
                if success:
                    st.success("✅ Cliente adicionado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao adicionar cliente!")
            else:
                st.error("❌ Por favor, preencha todos os campos obrigatórios.")

elif page == "Gerenciar Dados":
    st.header("🗂️ Gerenciar Dados Existentes")
    
    st.subheader("👥 Clientes Cadastrados")
    customers_df = data_manager.load_customers()
    
    if not customers_df.empty:
        # Mostrar dados com índice visível
        display_df = customers_df.copy()
        display_df.index = display_df.index + 1  # Começar índice em 1
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
        
        with col2:
            st.subheader("📝 Atualizar Status")
            if len(customers_df) > 0:
                customer_to_update = st.selectbox(
                    "Selecione o cliente para atualizar:",
                    options=range(len(customers_df)),
                    format_func=lambda x: f"{x+1}. {customers_df.iloc[x]['name']} - {customers_df.iloc[x]['status']}"
                )
                
                new_status = st.selectbox("Novo Status:", ["Ativo", "Cancelado"])
                new_cancel_date = None
                if new_status == "Cancelado":
                    new_cancel_date = st.date_input("Data de Cancelamento:", value=date.today())
                
                if st.button("Atualizar Status"):
                    if data_manager.update_customer_status(customer_to_update, new_status, new_cancel_date):
                        st.success("✅ Status atualizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao atualizar status.")
    else:
        st.info("📊 Nenhum cliente cadastrado.")

elif page == "Exportar Relatórios":
    st.header("📊 Exportar Relatórios")
    
    customers_df = data_manager.load_customers()
    
    if not customers_df.empty:
        calculator = SimpleMetricsCalculator(customers_df)
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
        st.info("💡 **Dica**: Para compartilhar este dashboard com colegas, basta compartilhar a URL desta aplicação. Todos os dados inseridos estarão disponíveis em tempo real.")
        
    else:
        st.warning("⚠️ Nenhum dado disponível para exportação.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Dashboard de Métricas de Clientes | Atualizado em tempo real"
    "</div>",
    unsafe_allow_html=True
)
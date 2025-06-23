import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import os
from data_manager import DataManager
from metrics_calculator import MetricsCalculator
from visualizations import create_visualizations

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Métricas de Clientes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar gerenciador de dados
@st.cache_resource
def init_data_manager():
    return DataManager()

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
    sales_df = data_manager.load_sales()
    
    if customers_df.empty and sales_df.empty:
        st.warning("⚠️ Nenhum dado encontrado. Por favor, insira alguns dados na seção 'Inserir Dados'.")
    else:
        # Calcular métricas
        calculator = MetricsCalculator(customers_df, sales_df)
        
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
                churn_rate = (latest_data['churn_clientes'] / max(latest_data['novos_clientes'], 1)) * 100
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
    
    tab1, tab2 = st.tabs(["Dados de Clientes", "Dados de Vendas"])
    
    with tab1:
        st.subheader("👥 Adicionar Cliente")
        
        with st.form("customer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                customer_id = st.text_input("ID do Cliente", placeholder="Ex: CUST001")
                customer_name = st.text_input("Nome do Cliente", placeholder="Ex: João Silva")
                signup_date = st.date_input("Data de Cadastro", value=date.today())
            
            with col2:
                plan_value = st.number_input("Valor do Plano (R$)", min_value=0.0, step=0.01)
                status = st.selectbox("Status", ["Ativo", "Cancelado"])
                cancel_date = st.date_input("Data de Cancelamento (se aplicável)", value=None)
            
            submitted = st.form_submit_button("Adicionar Cliente")
            
            if submitted:
                if customer_id and customer_name and plan_value > 0:
                    success = data_manager.add_customer(
                        customer_id, customer_name, signup_date, plan_value, 
                        status, cancel_date if status == "Cancelado" else None
                    )
                    if success:
                        st.success("✅ Cliente adicionado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Cliente já existe!")
                else:
                    st.error("❌ Por favor, preencha todos os campos obrigatórios.")
    
    with tab2:
        st.subheader("💰 Adicionar Venda")
        
        with st.form("sale_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                sale_customer_id = st.text_input("ID do Cliente", placeholder="Ex: CUST001")
                sale_date = st.date_input("Data da Venda", value=date.today())
                sale_value = st.number_input("Valor da Venda (R$)", min_value=0.0, step=0.01)
            
            with col2:
                sale_type = st.selectbox("Tipo", ["Recorrente", "Única"])
                description = st.text_area("Descrição", placeholder="Descrição da venda...")
            
            submitted_sale = st.form_submit_button("Adicionar Venda")
            
            if submitted_sale:
                if sale_customer_id and sale_value > 0:
                    success = data_manager.add_sale(
                        sale_customer_id, sale_date, sale_value, sale_type, description
                    )
                    if success:
                        st.success("✅ Venda adicionada com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao adicionar venda. Verifique se o cliente existe.")
                else:
                    st.error("❌ Por favor, preencha todos os campos obrigatórios.")

elif page == "Gerenciar Dados":
    st.header("🗂️ Gerenciar Dados Existentes")
    
    tab1, tab2 = st.tabs(["Clientes", "Vendas"])
    
    with tab1:
        st.subheader("👥 Clientes Cadastrados")
        customers_df = data_manager.load_customers()
        
        if not customers_df.empty:
            st.dataframe(customers_df, use_container_width=True)
            
            st.subheader("🗑️ Remover Cliente")
            customer_to_remove = st.selectbox(
                "Selecione o cliente para remover:",
                options=customers_df['customer_id'].tolist(),
                format_func=lambda x: f"{x} - {customers_df[customers_df['customer_id'] == x]['name'].iloc[0]}"
            )
            
            if st.button("Remover Cliente"):
                if data_manager.remove_customer(customer_to_remove):
                    st.success("✅ Cliente removido com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao remover cliente.")
        else:
            st.info("📊 Nenhum cliente cadastrado.")
    
    with tab2:
        st.subheader("💰 Vendas Registradas")
        sales_df = data_manager.load_sales()
        
        if not sales_df.empty:
            st.dataframe(sales_df, use_container_width=True)
            
            st.subheader("🗑️ Remover Venda")
            if len(sales_df) > 0:
                sale_to_remove = st.selectbox(
                    "Selecione a venda para remover:",
                    options=range(len(sales_df)),
                    format_func=lambda x: f"{sales_df.iloc[x]['customer_id']} - R$ {sales_df.iloc[x]['value']:,.2f} - {sales_df.iloc[x]['date']}"
                )
                
                if st.button("Remover Venda"):
                    if data_manager.remove_sale(sale_to_remove):
                        st.success("✅ Venda removida com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao remover venda.")
        else:
            st.info("📊 Nenhuma venda registrada.")

elif page == "Exportar Relatórios":
    st.header("📊 Exportar Relatórios")
    
    customers_df = data_manager.load_customers()
    sales_df = data_manager.load_sales()
    
    if not customers_df.empty or not sales_df.empty:
        calculator = MetricsCalculator(customers_df, sales_df)
        monthly_metrics = calculator.calculate_monthly_metrics()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📁 Dados Brutos")
            
            if not customers_df.empty:
                csv_customers = customers_df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Baixar Dados de Clientes (CSV)",
                    data=csv_customers,
                    file_name=f"clientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            if not sales_df.empty:
                csv_sales = sales_df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Baixar Dados de Vendas (CSV)",
                    data=csv_sales,
                    file_name=f"vendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
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

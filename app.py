import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
            
            # Calcular totais gerais (valores diretos em USD)
            total_customers = len(customers_df)
            active_customers = len(customers_df[customers_df['status'] == 'Ativo'])
            total_mrr_usd = latest_data['mrr']
            avg_ticket_usd = latest_data['ticket_medio']
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
                "Valor do Plano Mensal (USD)", 
                min_value=0.0, 
                step=1.0,
                help="Quanto o cliente paga por mês em dólares"
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

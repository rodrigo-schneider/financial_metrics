import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_visualizations(monthly_metrics):
    """Cria todas as visualizações para o dashboard"""
    
    if monthly_metrics.empty:
        return {}
    
    # Configuração de cores
    colors = {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e',
        'success': '#2ca02c',
        'danger': '#d62728',
        'warning': '#ff7f0e'
    }
    
    visualizations = {}
    
    # 1. Gráfico de Novos Clientes por Mês
    visualizations['novos_clientes'] = create_new_customers_chart(monthly_metrics, colors)
    
    # 2. Gráfico de MRR por Mês
    visualizations['mrr'] = create_mrr_chart(monthly_metrics, colors)
    
    # 3. Gráfico de Ticket Médio por Mês
    visualizations['ticket_medio'] = create_avg_ticket_chart(monthly_metrics, colors)
    
    # 4. Gráfico de Churn por Mês
    visualizations['churn'] = create_churn_chart(monthly_metrics, colors)
    
    return visualizations

def create_new_customers_chart(df, colors):
    """Cria gráfico de barras para novos clientes"""
    fig = px.bar(
        df,
        x='mes_ano',
        y='novos_clientes',
        title='📈 Novos Clientes por Mês',
        labels={'mes_ano': 'Mês/Ano', 'novos_clientes': 'Novos Clientes'},
        color_discrete_sequence=[colors['primary']]
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_tickangle=-45,
        title_font_size=16,
        title_x=0.5
    )
    
    # Adicionar valores nas barras
    fig.update_traces(
        texttemplate='%{y}',
        textposition='outside'
    )
    
    return fig

def create_mrr_chart(df, colors):
    """Cria gráfico de linha para MRR"""
    fig = px.line(
        df,
        x='mes_ano',
        y='mrr',
        title='💰 MRR (Monthly Recurring Revenue)',
        labels={'mes_ano': 'Mês/Ano', 'mrr': 'MRR (R$)'},
        markers=True,
        color_discrete_sequence=[colors['success']]
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_tickangle=-45,
        title_font_size=16,
        title_x=0.5
    )
    
    # Formatar valores do eixo Y
    fig.update_layout(yaxis=dict(tickformat=',.0f', tickprefix='R$ '))
    
    # Adicionar valores nos pontos
    fig.update_traces(
        texttemplate='R$ %{y:,.0f}',
        textposition='top center'
    )
    
    return fig

def create_avg_ticket_chart(df, colors):
    """Cria gráfico de área para ticket médio"""
    fig = px.area(
        df,
        x='mes_ano',
        y='ticket_medio',
        title='🎯 Ticket Médio por Mês',
        labels={'mes_ano': 'Mês/Ano', 'ticket_medio': 'Ticket Médio (R$)'},
        color_discrete_sequence=[colors['warning']]
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_tickangle=-45,
        title_font_size=16,
        title_x=0.5
    )
    
    # Formatar valores do eixo Y
    fig.update_layout(yaxis=dict(tickformat=',.2f', tickprefix='R$ '))
    
    return fig

def create_churn_chart(df, colors):
    """Cria gráfico combinado para churn (clientes e MRR)"""
    fig = make_subplots(
        specs=[[{"secondary_y": True}]],
        subplot_titles=['📉 Churn Mensal (Clientes e MRR)']
    )
    
    # Churn de clientes (barras)
    fig.add_trace(
        go.Bar(
            x=df['mes_ano'],
            y=df['churn_clientes'],
            name='Churn Clientes',
            marker_color=colors['danger'],
            opacity=0.7
        ),
        secondary_y=False
    )
    
    # Churn MRR (linha)
    fig.add_trace(
        go.Scatter(
            x=df['mes_ano'],
            y=df['churn_mrr'],
            mode='lines+markers',
            name='Churn MRR',
            line=dict(color=colors['secondary'], width=3),
            marker=dict(size=8)
        ),
        secondary_y=True
    )
    
    # Configurar eixos
    fig.update_xaxes(title_text="Mês/Ano", tickangle=-45)
    fig.update_yaxes(title_text="Churn Clientes", secondary_y=False)
    fig.update_yaxes(
        title_text="Churn MRR (R$)",
        secondary_y=True
    )
    fig.update_layout(yaxis2=dict(tickformat=',.0f', tickprefix='R$ '))
    
    fig.update_layout(
        height=400,
        title_font_size=16,
        title_x=0.5,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_kpi_card_chart(value, title, delta=None, format_type='number'):
    """Cria gráfico de KPI em formato de card"""
    if format_type == 'currency':
        display_value = f"R$ {value:,.2f}"
    elif format_type == 'percentage':
        display_value = f"{value:.1f}%"
    else:
        display_value = f"{value:,.0f}"
    
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="number+delta" if delta else "number",
        value=value,
        title={"text": title, "font": {"size": 20}},
        number={"font": {"size": 40}},
        delta={"reference": delta} if delta else None,
        domain={'x': [0, 1], 'y': [0, 1]}
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_trend_chart(df, metric_column, title, color):
    """Cria gráfico de tendência simples"""
    fig = px.line(
        df,
        x='mes_ano',
        y=metric_column,
        title=title,
        markers=True,
        color_discrete_sequence=[color]
    )
    
    fig.update_layout(
        showlegend=False,
        height=300,
        xaxis_tickangle=-45,
        title_font_size=14,
        title_x=0.5,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig

def create_comparison_chart(df, columns, title, chart_type='bar'):
    """Cria gráfico de comparação entre múltiplas métricas"""
    if chart_type == 'bar':
        fig = px.bar(
            df,
            x='mes_ano',
            y=columns,
            title=title,
            barmode='group'
        )
    else:
        fig = px.line(
            df,
            x='mes_ano',
            y=columns,
            title=title,
            markers=True
        )
    
    fig.update_layout(
        height=400,
        xaxis_tickangle=-45,
        title_font_size=16,
        title_x=0.5,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

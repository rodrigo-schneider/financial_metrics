import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar

class MetricsCalculator:
    def __init__(self, customers_df, sales_df):
        self.customers_df = customers_df
        self.sales_df = sales_df
    
    def calculate_monthly_metrics(self):
        """Calcula todas as métricas mensais"""
        if self.customers_df.empty and self.sales_df.empty:
            return pd.DataFrame()
        
        # Determinar período de análise
        start_date, end_date = self._get_analysis_period()
        
        # Gerar lista de meses
        months = self._generate_month_list(start_date, end_date)
        
        metrics_list = []
        
        for month_date in months:
            month_str = month_date.strftime('%Y-%m')
            
            # Calcular métricas para o mês
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
        """Determina o período de análise baseado nos dados disponíveis"""
        dates = []
        
        if not self.customers_df.empty:
            dates.extend(self.customers_df['signup_date'].dropna())
            cancel_dates = self.customers_df['cancel_date'].dropna()
            if not cancel_dates.empty:
                dates.extend(cancel_dates)
        
        if not self.sales_df.empty:
            dates.extend(self.sales_df['date'].dropna())
        
        if not dates:
            # Se não há dados, usar o mês atual
            now = datetime.now()
            return now.replace(day=1), now
        
        min_date = min(dates)
        max_date = max(dates)
        
        # Começar do primeiro dia do mês mais antigo
        start_date = min_date.replace(day=1)
        
        # Ir até o mês atual
        now = datetime.now()
        end_date = now.replace(day=1)
        
        return start_date, end_date
    
    def _generate_month_list(self, start_date, end_date):
        """Gera lista de primeiros dias de cada mês no período"""
        months = []
        current = start_date
        
        while current <= end_date:
            months.append(current)
            # Próximo mês
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        return months
    
    def _calculate_new_customers(self, month_date):
        """Calcula número de novos clientes no mês"""
        if self.customers_df.empty:
            return 0
        
        month_start = month_date
        month_end = self._get_month_end(month_date)
        
        new_customers = self.customers_df[
            (self.customers_df['signup_date'] >= month_start) &
            (self.customers_df['signup_date'] <= month_end)
        ]
        
        return len(new_customers)
    
    def _calculate_mrr(self, month_date):
        """Calcula MRR (Monthly Recurring Revenue) para o mês"""
        if self.customers_df.empty:
            return 0.0
        
        month_start = month_date
        month_end = self._get_month_end(month_date)
        
        # Clientes ativos no mês (cadastrados antes ou durante o mês e não cancelados antes do mês)
        active_customers = self.customers_df[
            (self.customers_df['signup_date'] <= month_end) &
            ((self.customers_df['cancel_date'].isna()) | 
             (self.customers_df['cancel_date'] > month_end))
        ]
        
        # Somar valores dos planos recorrentes
        mrr = active_customers['plan_value'].sum()
        
        # Adicionar vendas recorrentes do mês
        if not self.sales_df.empty:
            monthly_recurring_sales = self.sales_df[
                (self.sales_df['date'] >= month_start) &
                (self.sales_df['date'] <= month_end) &
                (self.sales_df['type'] == 'Recorrente')
            ]
            mrr += monthly_recurring_sales['value'].sum()
        
        return mrr
    
    def _calculate_avg_ticket(self, month_date):
        """Calcula ticket médio do mês"""
        if self.sales_df.empty:
            return 0.0
        
        month_start = month_date
        month_end = self._get_month_end(month_date)
        
        monthly_sales = self.sales_df[
            (self.sales_df['date'] >= month_start) &
            (self.sales_df['date'] <= month_end)
        ]
        
        if monthly_sales.empty:
            return 0.0
        
        # Agrupar por cliente para calcular ticket médio
        customer_totals = monthly_sales.groupby('customer_id')['value'].sum()
        
        return customer_totals.mean() if not customer_totals.empty else 0.0
    
    def _calculate_churn(self, month_date):
        """Calcula churn de clientes e MRR no mês"""
        if self.customers_df.empty:
            return 0, 0.0
        
        month_start = month_date
        month_end = self._get_month_end(month_date)
        
        # Clientes que cancelaram no mês
        churned_customers = self.customers_df[
            (self.customers_df['cancel_date'] >= month_start) &
            (self.customers_df['cancel_date'] <= month_end)
        ]
        
        churn_count = len(churned_customers)
        churn_mrr = churned_customers['plan_value'].sum()
        
        return churn_count, churn_mrr
    
    def _get_month_end(self, month_date):
        """Retorna o último dia do mês"""
        last_day = calendar.monthrange(month_date.year, month_date.month)[1]
        return month_date.replace(day=last_day, hour=23, minute=59, second=59)
    
    def get_summary_stats(self):
        """Retorna estatísticas resumidas"""
        monthly_metrics = self.calculate_monthly_metrics()
        
        if monthly_metrics.empty:
            return {}
        
        return {
            'total_customers': self.customers_df['customer_id'].nunique() if not self.customers_df.empty else 0,
            'active_customers': len(self.customers_df[self.customers_df['status'] == 'Ativo']) if not self.customers_df.empty else 0,
            'total_sales': self.sales_df['value'].sum() if not self.sales_df.empty else 0,
            'avg_monthly_mrr': monthly_metrics['mrr'].mean(),
            'avg_monthly_new_customers': monthly_metrics['novos_clientes'].mean(),
            'avg_churn_rate': (monthly_metrics['churn_clientes'].sum() / monthly_metrics['novos_clientes'].sum() * 100) if monthly_metrics['novos_clientes'].sum() > 0 else 0
        }

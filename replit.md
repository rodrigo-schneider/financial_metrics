# Customer Metrics Dashboard

## Overview

This is a Streamlit-based customer metrics dashboard application that provides comprehensive analytics for customer data and sales performance. The application is built using Python with a modular architecture that separates data management, metrics calculation, and visualization components.

## System Architecture

The application follows a clean, modular architecture with the following layers:

1. **Presentation Layer**: Streamlit web interface (`app.py`)
2. **Business Logic Layer**: Metrics calculation and data processing (`metrics_calculator.py`)
3. **Data Access Layer**: CSV file management (`data_manager.py`)
4. **Visualization Layer**: Chart generation using Plotly (`visualizations.py`)

### Technology Stack
- **Frontend**: Streamlit for web interface
- **Backend**: Python 3.11
- **Data Processing**: Pandas for data manipulation
- **Visualization**: Plotly for interactive charts
- **Data Storage**: CSV files (local file system)
- **Deployment**: Replit with autoscale deployment target

## Key Components

### 1. Main Application (`app.py`)
- Streamlit configuration and page layout
- Multi-page navigation (Dashboard, Insert Data, Manage Data, Export Reports)
- Integration of all components
- Caching for performance optimization

### 2. Data Manager (`data_manager.py`)
- CSV file operations for customers and sales data
- Data validation and error handling
- Automatic file creation if not exists
- Date parsing and data type conversion

### 3. Metrics Calculator (`metrics_calculator.py`)
- Monthly metrics computation including:
  - New customers acquisition
  - Monthly Recurring Revenue (MRR)
  - Average ticket value
  - Churn rates (customers and revenue)
- Time period analysis
- Data aggregation and statistical calculations

### 4. Visualizations (`visualizations.py`)
- Interactive chart creation using Plotly
- Multiple chart types (bar charts, line charts, etc.)
- Consistent color scheme and styling
- Responsive design for different screen sizes

## Data Flow

1. **Data Input**: Users input customer and sales data through Streamlit interface
2. **Data Storage**: Information is stored in CSV files (`customers.csv`, `sales.csv`)
3. **Data Loading**: DataManager loads and validates data from CSV files
4. **Metrics Calculation**: MetricsCalculator processes raw data into business metrics
5. **Visualization**: Charts are generated based on calculated metrics
6. **Display**: Streamlit renders the interactive dashboard

### Data Schema

**Customers Table**:
- `customer_id`: Unique identifier
- `name`: Customer name
- `signup_date`: Registration date
- `plan_value`: Subscription value
- `status`: Account status
- `cancel_date`: Cancellation date (if applicable)

**Sales Table**:
- `customer_id`: Foreign key to customers
- `date`: Transaction date
- `value`: Transaction amount
- `type`: Transaction type
- `description`: Transaction description

## External Dependencies

- **Streamlit**: Web framework for the dashboard interface
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualization library
- **NumPy**: Numerical computing support

## Deployment Strategy

The application is configured for deployment on Replit with:

- **Runtime**: Python 3.11 with Nix package management
- **Deployment Target**: Autoscale for automatic scaling
- **Port Configuration**: Runs on port 5000
- **Workflow**: Parallel execution with shell commands
- **Configuration**: Streamlit server configured for headless operation

The deployment uses a simple file-based storage system with CSV files, making it suitable for small to medium-scale applications. For production use with larger datasets, the architecture can be extended to support database backends.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

### June 23, 2025 - Sistema de Persistência Ultra-Robusto
- **Problema Resolvido**: Falha crítica na persistência de dados no ambiente de produção
- **Implementação**: Sistema de salvamento com backup triplo e verificação múltipla
- **Características**:
  - Backup automático em 3 arquivos diferentes antes de cada operação
  - Verificação tripla de integridade dos dados após salvamento
  - Sistema de recuperação automática em caso de falha
  - Monitoramento em tempo real com feedback visual detalhado
  - Logging completo para diagnóstico de problemas
- **Validações Implementadas**:
  - Verificação de entrada de dados no frontend
  - Validação de tipos e formatos
  - Confirmação de salvamento com comparação de dados
  - Sistema de rollback automático

### June 23, 2025 - Interface de Monitoramento
- **Adicionado**: Painel de diagnóstico em tempo real na seção "Inserir Dados"
- **Recursos**: Status de arquivos, contadores de clientes, verificação de backups
- **Feedback**: Barra de progresso e mensagens detalhadas durante operações
- **Debug**: Opções avançadas para visualizar dados raw e logs de erro

### June 23, 2025 - Correções Críticas de Métricas e Datas
- **MRR Corrigido**: Resolvido bug crítico onde MRR mostrava apenas valor do primeiro cliente ($4,000) em vez da soma total ($28,000)
- **Ticket Médio Corrigido**: Cálculo agora reflete corretamente a média de todos os clientes ativos ($7,000)
- **Datas Inválidas Eliminadas**: Sistema de formatação de datas completamente reformulado para eliminar "Data inválida"
- **Dados Limpos**: Arquivo CSV recriado com dados validados e sistema robusto de carregamento
- **Validação Completa**: Testes abrangentes confirmam precisão dos cálculos e exibição

## Changelog

Changelog:
- June 23, 2025. Initial setup with ultra-robust data persistence system
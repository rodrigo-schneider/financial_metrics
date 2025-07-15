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

### June 23, 2025 - Sistema de Persistência Externa Multi-Camada
- **Problema Resolvido**: Dados eram perdidos após algumas horas e não funcionavam para múltiplos usuários
- **Solução Final**: Sistema de persistência externa com múltiplas camadas independentes
- **Arquitetura da Solução**:
  - **Camada 1**: Streamlit Session State (temporário, para sessão atual)
  - **Camada 2**: Arquivo de configuração codificado (permanente, sobrevive a resets)
  - **Camada 3**: Arquivo Python com dados embeddados (permanente, independente de CSV)
  - **Camada 4**: Backups CSV locais (compatibilidade e debug)
- **Características Técnicas**:
  - Salvamento automático em 3+ métodos independentes a cada operação
  - Recuperação inteligente: tenta cada método até encontrar dados válidos
  - Funciona entre diferentes sessões, usuários e máquinas
  - Não depende de arquivos CSV temporários que podem ser perdidos
  - Monitoramento em tempo real de todas as camadas de armazenamento
- **Garantia Multi-Usuário**: Dados permanecem acessíveis independentemente de:
  - Reinicializações do sistema
  - Múltiplos usuários acessando de máquinas diferentes
  - Falhas em qualquer método de armazenamento individual
  - Ambiente de produção temporário do Replit

### June 23, 2025 - Interface Brasileira Otimizada
- **Problema Resolvido**: Campos de entrada não aceitavam formato brasileiro de valores e datas
- **Solução Implementada**: Sistema de parsing inteligente para formatos locais
- **Funcionalidades de Entrada**:
  - **Valores Monetários**: Aceita 4.000,00 (brasileiro) e 4000.00 (americano)
  - **Datas**: Formato DD/MM/AAAA (15/01/2024) em campos de texto
  - **Validação Inteligente**: Detecta automaticamente o formato de entrada
  - **Feedback Visual**: Mensagens de erro claras em português
- **Compatibilidade**: Funciona com copy/paste de planilhas e sistemas brasileiros
- **Validação Robusta**: Impede entrada de dados inválidos com mensagens específicas

### June 23, 2025 - Correção da Funcionalidade de Remoção
- **Problema Resolvido**: Remoção de clientes não funcionava corretamente
- **Solução Implementada**: Integração da remoção com sistema de persistência externa
- **Funcionalidades Corrigidas**:
  - **Remoção Segura**: Backup automático antes de cada operação de remoção
  - **Validação de Índices**: Rejeita corretamente índices inválidos ou fora do range
  - **Persistência Garantida**: Remoções salvas em múltiplas camadas permanentes
  - **Verificação de Integridade**: Confirma sucesso da operação antes de finalizar
- **Resultado**: Sistema de gerenciamento completo com adição e remoção funcionais

### June 24, 2025 - Implementação de Banco PostgreSQL Permanente
- **Solução Implementada**: Integração com Supabase PostgreSQL para persistência permanente na nuvem
- **Arquitetura da Solução**:
  - **Prioridade 1**: Banco PostgreSQL (Supabase) - armazenamento principal permanente
  - **Prioridade 2**: Sistema de persistência externa multi-camada - backup robusto
  - **Prioridade 3**: Arquivos CSV locais - backup de emergência
- **Funcionalidades Implementadas**:
  - **Conexão Automática**: Sistema detecta e conecta automaticamente ao banco
  - **Sincronização Inteligente**: Dados migram automaticamente entre sistemas
  - **Monitoramento em Tempo Real**: Status de conexão visível na interface
  - **Fallback Robusto**: Sistema continua funcionando mesmo se banco ficar offline
- **Benefícios**:
  - Dados permanentes na nuvem, acessíveis de qualquer lugar
  - Escalabilidade para múltiplos usuários simultâneos
  - Backup triplo garante zero perda de dados
  - Interface unificada para monitoramento de status

### July 15, 2025 - Funcionalidade de Edição de Clientes
- **Nova Página Implementada**: "Editar Cliente" no menu de navegação
- **Funcionalidades de Edição**:
  - **Seleção Visual**: Tabela com todos os clientes e seleção por índice
  - **Formulário Completo**: Edição de nome, data de cadastro, valor do plano, status e data de cancelamento
  - **Validações**: Mesmas validações da inserção (formatos brasileiros, datas, valores)
  - **Comparação Visual**: Lado a lado dos dados atuais vs novos dados
  - **Feedback em Tempo Real**: Barra de progresso e mensagens durante o salvamento
- **Persistência**: Integrada com sistema de backup triplo (PostgreSQL + Sistema externo + CSV)
- **Recálculo Automático**: Métricas são recalculadas automaticamente após edição
- **Interface**: Formulário intuitivo com validações e confirmação visual

### July 15, 2025 - Implementação de LTV (Lifetime Value)
- **Nova Métrica Adicionada**: Cálculo completo de LTV (Lifetime Value) para análise de rentabilidade
- **Funcionalidades Implementadas**:
  - **LTV Médio Geral**: Valor médio que cada cliente gera durante sua vida útil
  - **LTV Clientes Ativos**: LTV médio dos clientes que ainda estão ativos
  - **LTV Clientes Cancelados**: LTV médio dos clientes que cancelaram
  - **Tempo Médio de Vida**: Tempo médio que um cliente permanece ativo
- **Visualizações Criadas**:
  - Histograma de distribuição de LTV dos clientes
  - Gráfico scatter LTV vs Tempo de Vida (diferenciando ativos e cancelados)
- **Cálculo**: LTV = valor mensal do plano × meses de vida do cliente
- **Interface**: Seção dedicada no dashboard com 4 KPIs principais e 2 gráficos interativos

### July 15, 2025 - Modificação no Cálculo de Churn
- **Regra de Negócio Alterada**: Churn agora considera apenas clientes que permaneceram pelo menos 2 meses
- **Critério Implementado**: Clientes que cancelam no primeiro mês não são mais contabilizados como churn
- **Cálculo**: Diferença em meses entre `signup_date` e `cancel_date` deve ser >= 2 meses
- **Impacto**: Métricas de churn mais precisas, excluindo cancelamentos de teste ou desistências imediatas
- **Funcionalidade**: Sistema diferencia entre cancelamentos precoces e churn real

## Changelog

Changelog:
- July 15, 2025. Modified churn calculation to exclude first-month cancellations
- June 23, 2025. Initial setup with ultra-robust data persistence system
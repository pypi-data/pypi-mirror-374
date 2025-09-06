# MarcasBot - Multi-Agent AI Assistant Platform

MarcasBot is an advanced multi-agent AI system designed for CSSA brands, featuring specialized agents for sales analysis, market research, web search, and comprehensive research coordination. Built with LangGraph for agent orchestration, FastAPI for API services, and supporting both Databricks and OpenAI language models.

[![Python 3.12.3](https://img.shields.io/badge/python-3.12.3-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.5.3-ff6b35.svg)](https://langchain-ai.github.io/langgraph/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Architecture

### Bot Types
MarcasBot consists of four specialized bot implementations, each built on a unified `BaseBot` framework:

- **SalesBot** - Sales data analysis with SQL generation via Databricks Genie
- **MarketStudyBot** - Internal market research document analysis (2004-2024) using vector search
- **SearchBot** - Real-time web search and market intelligence via Tavily API
- **ResearchBot (SuperBot)** - Multi-agent coordinator combining internal studies with external research

### Core Framework Components

#### BaseBot Pattern
All bots inherit from `BaseBot`, providing:
- Unified CLI interface with interactive and single-query modes
- Session management with conversation context and memory summarization
- Query processing with error handling and retry logic
- MLflow integration for experiment tracking

#### BaseNode Patterns
Three node types handle different routing scenarios:
- **SimpleNode** - Always routes to the same target (e.g., synthesizer → supervisor)
- **ConditionalNode** - Routes based on response content detection (e.g., sales analyst → supervisor OR text_sql)
- **LoopingNode** - Loops back to self until "RESPUESTA FINAL" is detected

#### LangGraph Agent System
- **Supervisor Node** - LLM-based intelligent routing between specialized agents
- **Specialized Agent Nodes** - Domain-specific processing (sales analysis, market research, web search)
- **Synthesizer Node** - Quality-controlled response synthesis with citation validation and word count thresholds
- **References Collector** - Automated extraction and validation of document and URL citations

### Technical Capabilities
- **Multi-LLM Support** - Databricks (Llama 3.3 70B Instruct) and OpenAI (GPT-4o-mini, GPT-4.1-mini,GPT-4.1) with configurable routing
- **Quality Controls** - Citation validation, word count enforcement, and retry mechanisms
- **Reference Management** - Automated document extraction with validation and deduplication
- **Session Continuity** - Context-aware conversations with intelligent memory management
- **RESTful APIs** - FastAPI endpoints with automatic OpenAPI documentation
- **Microsoft Bot Framework** - Integration for Teams and other Microsoft services

## Installation

### Prerequisites
- Python 3.12.3
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd marcas_bot
```

### Step 2: Set Up Python Environment (Recommended)
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install MarcasBot
```bash
# Install the package in editable mode (for development)
pip install -e .

# Or, install with development dependencies
pip install -e .[dev]
```

### Step 4: Environment Configuration
1. Copy the environment template file:
   ```bash
   cp .env.example .env
   ```
2. Edit the `.env` file with your API keys and service configurations:
   ```bash
   nano .env  # Or use your preferred text editor
   ```

### Step 5: Verify Installation
```bash
# Test the command-line scripts
marcas_bot-sales --help
marcas_bot-market-study --help
marcas_bot-search --help
marcas_bot-research --help

# Verify that the package can be imported correctly
python -c "from main import SalesBot; print('Installation successful!')"
```

## Usage

### Command Line Interface (CLI)

#### Available CLI Commands
MarcasBot provides several specialized command-line interfaces:

```bash
# Sales Analysis Agent
marcas_bot-sales -i                    # Interactive sales analysis
marcas_bot-sales "query here"          # Direct sales query

# Market Research Agent
marcas_bot-market-study -i             # Interactive market research
marcas_bot-market-study "query here"   # Direct market research query

# Web Search Agent
marcas_bot-search -i                   # Interactive web search
marcas_bot-search "query here"         # Direct search query

# Research Coordinator (Multi-agent)
marcas_bot-research -i                 # Interactive research coordination
marcas_bot-research "query here"       # Direct research query
```

#### Interactive Mode (Recommended)
To start a conversational session with a bot:
```bash
# For Sales Analysis
marcas_bot-sales --interactive
# Alias for the above
marcas_bot-sales -i

# For Market Research
marcas_bot-market-study -i
```

#### Single Queries
To get a direct answer for a single question:
```bash
# Sales Analysis Examples
marcas_bot-sales "What are the sales trends for 2023?"
marcas_bot-sales "Compare revenue between 2022 and 2023"

# Market Research Examples
marcas_bot-market-study "Consumer behavior trends in soy products"

# To see step-by-step processing, use the --stream flag
marcas_bot-sales "Show me sales by product category" --stream
```

### API Server

#### Starting the Unified API Server
```bash
# Run the main API server (includes all engines)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### API Endpoints
The unified API provides multiple engine endpoints:

**Main Documentation**: `http://localhost:8000/docs`

**Core Endpoints**:
- `POST /api/query` - SuperBot (ResearchBot) queries
- `POST /api/sales/query` - SalesBot queries
- `POST /api/market-study/query` - MarketStudyBot queries  
- `POST /api/search/query` - SearchBot queries
- `GET /api/health` - Health check
- `POST /api/messages` - Microsoft Bot Framework integration

**Specialized Sales Endpoints**:
- `GET /api/sales/summary` - Sales overview
- `GET /api/sales/product/{product_name}` - Product performance analysis
- `GET /api/sales/regional` - Regional sales analysis
- `GET /api/sales/time-series` - Time series analysis

**Specialized Market Study Endpoints**:
- `GET /api/market-study/trends` - Market trends analysis
- `GET /api/market-study/consumer-behavior` - Consumer behavior insights
- `GET /api/market-study/competitive-analysis` - Competitive analysis
- `GET /api/market-study/brand-perception/{brand_name}` - Brand perception analysis

## Project Structure

```
marcasbot/
├── agents/                    # Specialized agent implementations
│   ├── analista_ventas.py    # Sales analysis agent
│   ├── experto_estudios.py   # Market study expert agent
│   ├── agente_web.py         # Web search agent
│   ├── synthesizer.py        # Response synthesis agent
│   ├── references_collector.py # Reference extraction agent
│   └── text_sql.py           # SQL generation agent
├── api/                       # FastAPI applications and engines
│   ├── main.py               # Unified API server
│   ├── marcas_engine.py      # MarcasBot (super) engine
│   ├── research_engine.py    # ResearchBot engine
│   ├── sales_engine.py       # SalesBot engine
│   ├── market_study_engine.py # MarketStudyBot engine
│   ├── search_engine.py      # SearchBot engine
│   └── bot_framework.py      # Microsoft Bot Framework integration
├── core/                      # Base classes and framework
│   ├── base_bot.py           # BaseBot framework
│   ├── base_engine.py        # BaseEngine for API wrappers
│   ├── base_node.py          # BaseNode patterns (Simple/Conditional/Looping)
│   └── base_agent.py         # LangGraph agent wrapper
├── main/                      # Bot implementations and CLI entry points
│   ├── sales_bot.py          # SalesBot implementation
│   ├── market_study_bot.py   # MarketStudyBot implementation
│   ├── search_bot.py         # SearchBot implementation
│   └── research_bot.py       # ResearchBot (SuperBot) implementation
├── nodes/                     # LangGraph processing nodes
│   ├── supervisor.py         # Intelligent routing supervisor
│   ├── synthesizer.py        # Quality-controlled synthesis node
│   ├── references_collector.py # Reference collection node
│   ├── sales.py              # Sales analysis node
│   ├── market_study.py       # Market study analysis node
│   ├── search.py             # Web search node
│   ├── research_team.py      # Research team coordination node
│   └── text_sql.py           # SQL generation node
├── utils/                     # Utility functions and helpers
│   ├── reference_extractor.py # Reference extraction utility
│   ├── session_manager.py    # Session and memory management
│   ├── logger.py             # Logging configuration
│   └── mlflow_cleanup.py     # MLflow cleanup utilities
├── schemas/                   # Data models and validation
│   ├── state.py              # LangGraph state schema
│   ├── api_query_request.py  # API request schemas
│   └── filter_sql_input.py   # SQL filtering schemas
├── config/                    # Configuration and prompts
│   ├── params.py             # Environment configuration
│   └── prompts.py            # Agent prompts and templates
├── models/                    # LLM model configurations
│   ├── agentic_llm.py        # Generic LLM wrapper
│   └── databricks_llm.py     # Databricks-specific LLM
└── requirements.txt           # Python dependencies
```

## Development

### Install Development Dependencies
```bash
pip install -e .[dev]
```

### Running Tests
```bash
# Run all tests
pytest

# Run a specific test file with more verbose output
pytest tests/test_session_memory.py -v

# Run tests with code coverage report
pytest --cov=main --cov=core
```

### Code Formatting
```bash
# Format code using Black
black .
```

## Configuration

Create a `.env` file based on the provided `.env.example` template:

```bash
cp .env.example .env
# Edit .env with your actual values
```

Required variables:

```env
# Environment
ENV=development  # Can be 'development' or 'production'

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Databricks Configuration
DATABRICKS_HOST=your_databricks_host.azuredatabricks.net
DATABRICKS_TOKEN=your_databricks_token_here

# LLM Configuration
EXPERTS_LLM=databricks  # or 'openai'
SUPERVISOR_LLM=openai   # or 'databricks'

# Vector Search / RAG
MARKET_STUDY_RAG_TABLE=your_schema.your_table.vector_search_table

# Delisoy Configuration
DELISOY_SELL_IN_GENIE_SPACE_ID=your_genie_space_id_here

# Bot Framework (Optional, for chatbot deployment)
MicrosoftAppId=your_microsoft_app_id_here
MicrosoftAppPassword=your_microsoft_app_password_here
MicrosoftAppTenantId=your_microsoft_app_tenant_id_here
```

## License

This is proprietary software owned by CSSA. All rights reserved.
